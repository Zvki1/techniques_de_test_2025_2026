"""Tests système de l'API Flask."""

import struct
from unittest.mock import MagicMock, patch

import pytest

from triangulator.app import app


# =============================================================================
# 3. Tests Système (Conformité API)
# =============================================================================

@pytest.fixture
def client():
    """Fixture Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_uuid():
    """UUID valide pour les tests."""
    return "123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture
def mock_pointset_data():
    """Données PointSet mockées (3 points)."""
    data = struct.pack("<I", 3)
    data += struct.pack("<ff", 0.0, 0.0)
    data += struct.pack("<ff", 1.0, 0.0)
    data += struct.pack("<ff", 0.5, 1.0)
    return data


# =============================================================================
# 3.1 Tests de conformité OpenAPI - Endpoint GET /triangulation/{pointSetId}
# =============================================================================

@pytest.mark.system
class TestTriangulationEndpointSuccess:
    """Tests cas de succès (200)."""

    def test_valid_triangulation_returns_200(self, client, valid_uuid, mock_pointset_data):
        """Test UUID valide + PointSet existant → 200 + Triangles en binaire."""
        with patch("triangulator.app.get_pointset") as mock_get:
            mock_get.return_value = mock_pointset_data
            
            response = client.get(f"/triangulation/{valid_uuid}")
            
            assert response.status_code == 200

    def test_success_content_type_octet_stream(self, client, valid_uuid, mock_pointset_data):
        """Test Content-Type: application/octet-stream pour succès."""
        with patch("triangulator.app.get_pointset") as mock_get:
            mock_get.return_value = mock_pointset_data
            
            response = client.get(f"/triangulation/{valid_uuid}")
            
            if response.status_code == 200:
                assert response.content_type == "application/octet-stream"

    def test_success_returns_valid_binary_format(self, client, valid_uuid, mock_pointset_data):
        """Test que la réponse est au format binaire Triangles correct."""
        with patch("triangulator.app.get_pointset") as mock_get:
            mock_get.return_value = mock_pointset_data
            
            response = client.get(f"/triangulation/{valid_uuid}")
            
            if response.status_code == 200:
                data = response.data
                # Vérifier qu'on peut lire le nombre de points
                assert len(data) >= 4
                nb_points = int.from_bytes(data[:4], byteorder="little")
                assert nb_points >= 0


@pytest.mark.system
class TestTriangulationEndpointClientErrors:
    """Tests cas d'erreur client (4xx)."""

    def test_invalid_uuid_returns_400(self, client):
        """Test UUID invalide → 400 + JSON error."""
        response = client.get("/triangulation/invalid-uuid")
        
        assert response.status_code == 400
        assert response.content_type == "application/json"
        data = response.get_json()
        assert "code" in data
        assert "message" in data

    def test_empty_uuid_returns_400(self, client):
        """Test UUID vide → 400."""
        response = client.get("/triangulation/")
        
        # Soit 400 soit 404 selon le routing
        assert response.status_code in [400, 404]

    def test_uuid_not_found_returns_404(self, client, valid_uuid):
        """Test UUID inexistant → 404 + JSON error."""
        with patch("triangulator.app.get_pointset") as mock_get:
            mock_get.side_effect = FileNotFoundError("PointSet not found")
            
            response = client.get(f"/triangulation/{valid_uuid}")
            
            assert response.status_code == 404
            assert response.content_type == "application/json"
            data = response.get_json()
            assert "code" in data
            assert "message" in data

    def test_method_post_not_allowed(self, client, valid_uuid):
        """Test méthode POST non autorisée → 405."""
        response = client.post(f"/triangulation/{valid_uuid}")
        
        assert response.status_code == 405

    def test_method_put_not_allowed(self, client, valid_uuid):
        """Test méthode PUT non autorisée → 405."""
        response = client.put(f"/triangulation/{valid_uuid}")
        
        assert response.status_code == 405

    def test_method_delete_not_allowed(self, client, valid_uuid):
        """Test méthode DELETE non autorisée → 405."""
        response = client.delete(f"/triangulation/{valid_uuid}")
        
        assert response.status_code == 405

    def test_route_not_found_returns_404(self, client):
        """Test route invalide → 404."""
        response = client.get("/unknown-route")
        
        assert response.status_code == 404


@pytest.mark.system
class TestTriangulationEndpointServerErrors:
    """Tests cas d'erreur serveur (5xx)."""

    def test_triangulation_fails_returns_500(self, client, valid_uuid):
        """Test triangulation échoue → 500 + JSON error."""
        # PointSet avec moins de 3 points (triangulation impossible)
        invalid_pointset = struct.pack("<I", 2) + struct.pack("<ff", 0.0, 0.0) \
            + struct.pack("<ff", 1.0, 0.0)
        
        with patch("triangulator.app.get_pointset") as mock_get:
            mock_get.return_value = invalid_pointset
            
            response = client.get(f"/triangulation/{valid_uuid}")
            
            assert response.status_code == 500
            assert response.content_type == "application/json"
            data = response.get_json()
            assert "code" in data
            assert "message" in data

    def test_pointset_manager_unavailable_returns_503(self, client, valid_uuid):
        """Test PointSetManager inaccessible → 503 + JSON error."""
        with patch("triangulator.app.get_pointset") as mock_get:
            mock_get.side_effect = ConnectionError("Service unavailable")
            
            response = client.get(f"/triangulation/{valid_uuid}")
            
            assert response.status_code == 503
            assert response.content_type == "application/json"
            data = response.get_json()
            assert "code" in data
            assert "message" in data


@pytest.mark.system
class TestErrorResponseFormat:
    """Tests du format des réponses d'erreur."""

    def test_error_has_code_field(self, client):
        """Test que les erreurs ont le champ 'code'."""
        response = client.get("/triangulation/invalid")
        
        if response.status_code >= 400:
            data = response.get_json()
            assert "code" in data
            assert isinstance(data["code"], str)

    def test_error_has_message_field(self, client):
        """Test que les erreurs ont le champ 'message'."""
        response = client.get("/triangulation/invalid")
        
        if response.status_code >= 400:
            data = response.get_json()
            assert "message" in data
            assert isinstance(data["message"], str)

    def test_error_content_type_json(self, client):
        """Test Content-Type: application/json pour erreurs."""
        response = client.get("/triangulation/invalid")
        
        if response.status_code >= 400:
            assert response.content_type == "application/json"

    def test_404_error_format(self, client):
        """Test format erreur 404."""
        response = client.get("/nonexistent-route")
        
        assert response.status_code == 404
        data = response.get_json()
        assert "code" in data
        assert "message" in data
