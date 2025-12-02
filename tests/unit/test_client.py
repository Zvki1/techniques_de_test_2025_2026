"""Tests unitaires pour le client PointSetManager."""

import struct
from unittest.mock import MagicMock, patch

import pytest

from triangulator.client import get_pointset


# =============================================================================
# 2.1 Tests de Communication avec PointSetManager
# =============================================================================

class TestGetPointsetValidation:
    """Tests de validation des paramètres."""

    def test_invalid_uuid_format_raises(self):
        """Test UUID invalide → ValueError."""
        with pytest.raises(ValueError):
            get_pointset("invalid-uuid")

    def test_empty_uuid_raises(self):
        """Test UUID vide → ValueError."""
        with pytest.raises(ValueError):
            get_pointset("")

    def test_uuid_too_short_raises(self):
        """Test UUID trop court → ValueError."""
        with pytest.raises(ValueError):
            get_pointset("123")

    def test_valid_uuid_format_accepted(self, valid_uuid):
        """Test format UUID valide est accepté (mock la requête)."""
        with patch("triangulator.client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = struct.pack("<I", 0)  # PointSet vide
            mock_requests.get.return_value = mock_response
            
            result = get_pointset(valid_uuid)
            assert result is not None


class TestGetPointsetSuccess:
    """Tests des cas de succès."""

    def test_get_pointset_success_200(self, valid_uuid):
        """Test requête réussie (200 + PointSet binaire valide)."""
        with patch("triangulator.client.requests") as mock_requests:
            # Simuler une réponse 200 avec PointSet valide
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = struct.pack("<I", 3) + struct.pack("<ff", 0.0, 0.0) \
                + struct.pack("<ff", 1.0, 0.0) + struct.pack("<ff", 0.5, 1.0)
            mock_requests.get.return_value = mock_response
            
            result = get_pointset(valid_uuid)
            
            assert isinstance(result, bytes)
            assert len(result) == 28  # 4 + 24

    def test_get_pointset_empty(self, valid_uuid):
        """Test récupération PointSet vide."""
        with patch("triangulator.client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = struct.pack("<I", 0)  # 0 points
            mock_requests.get.return_value = mock_response
            
            result = get_pointset(valid_uuid)
            
            assert len(result) == 4


class TestGetPointsetErrors:
    """Tests des cas d'erreur."""

    def test_get_pointset_not_found_404(self, valid_uuid):
        """Test PointSet inexistant (404) → FileNotFoundError."""
        with patch("triangulator.client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.json.return_value = {
                "code": "NOT_FOUND",
                "message": "PointSet not found"
            }
            mock_requests.get.return_value = mock_response
            
            with pytest.raises(FileNotFoundError):
                get_pointset(valid_uuid)

    def test_get_pointset_server_error_500(self, valid_uuid):
        """Test erreur serveur PointSetManager (500)."""
        with patch("triangulator.client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.json.return_value = {
                "code": "INTERNAL_ERROR",
                "message": "Internal server error"
            }
            mock_requests.get.return_value = mock_response
            
            with pytest.raises(Exception):  # ou RuntimeError selon implémentation
                get_pointset(valid_uuid)

    def test_get_pointset_connection_error(self, valid_uuid):
        """Test serveur inaccessible → ConnectionError."""
        with patch("triangulator.client.requests") as mock_requests:
            import requests
            mock_requests.get.side_effect = requests.exceptions.ConnectionError(
                "Connection refused"
            )
            
            with pytest.raises(ConnectionError):
                get_pointset(valid_uuid)

    def test_get_pointset_timeout(self, valid_uuid):
        """Test timeout de connexion."""
        with patch("triangulator.client.requests") as mock_requests:
            import requests
            mock_requests.get.side_effect = requests.exceptions.Timeout("Timeout")
            
            with pytest.raises((ConnectionError, TimeoutError)):
                get_pointset(valid_uuid)


class TestGetPointsetURLConstruction:
    """Tests de construction d'URL."""

    def test_correct_url_called(self, valid_uuid):
        """Test que l'URL correcte est appelée."""
        with patch("triangulator.client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = struct.pack("<I", 0)
            mock_requests.get.return_value = mock_response
            
            get_pointset(valid_uuid, manager_url="http://test-server:8080")
            
            # Vérifier l'URL appelée
            mock_requests.get.assert_called_once()
            call_args = mock_requests.get.call_args
            assert valid_uuid in str(call_args)

    def test_custom_manager_url(self, valid_uuid):
        """Test avec URL personnalisée du manager."""
        with patch("triangulator.client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = struct.pack("<I", 0)
            mock_requests.get.return_value = mock_response
            
            get_pointset(valid_uuid, manager_url="http://custom:9000")
            
            call_url = mock_requests.get.call_args[0][0]
            assert "custom:9000" in call_url
