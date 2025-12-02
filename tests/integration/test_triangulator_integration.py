"""Tests d'intégration du Triangulator."""

import struct
from unittest.mock import MagicMock, patch

import pytest

from triangulator.binary_format import decode_pointset, encode_pointset, encode_triangles
from triangulator.triangulation import triangulate


# =============================================================================
# 2. Tests d'Intégration
# =============================================================================

@pytest.mark.integration
class TestBinaryFormatAndTriangulation:
    """Tests d'intégration entre binary_format et triangulation."""

    def test_decode_then_triangulate(self):
        """Test : décode PointSet puis triangule."""
        # Créer des données binaires valides
        points_data = struct.pack("<I", 3)
        points_data += struct.pack("<ff", 0.0, 0.0)
        points_data += struct.pack("<ff", 1.0, 0.0)
        points_data += struct.pack("<ff", 0.5, 1.0)
        
        # Décoder
        points = decode_pointset(points_data)
        
        # Trianguler
        triangles = triangulate(points)
        
        assert len(triangles) == 1
        assert set(triangles[0]) == {0, 1, 2}

    def test_triangulate_then_encode(self, sample_points_square):
        """Test : triangule puis encode le résultat."""
        # Trianguler
        triangles = triangulate(sample_points_square)
        
        # Encoder le résultat
        encoded = encode_triangles(sample_points_square, triangles)
        
        assert len(encoded) > 0
        # Vérifier la structure basique
        nb_points = int.from_bytes(encoded[:4], byteorder="little")
        assert nb_points == 4

    def test_full_pipeline_encode_decode_triangulate_encode(self):
        """Test pipeline complet : encode → decode → triangulate → encode."""
        original_points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        
        # Étape 1 : Encoder les points
        encoded_points = encode_pointset(original_points)
        
        # Étape 2 : Décoder les points
        decoded_points = decode_pointset(encoded_points)
        
        # Étape 3 : Trianguler
        triangles = triangulate(decoded_points)
        
        # Étape 4 : Encoder le résultat final
        final_result = encode_triangles(decoded_points, triangles)
        
        assert len(final_result) > 0
        assert len(triangles) == 2  # Carré = 2 triangles


@pytest.mark.integration
class TestTriangulatorWithMockedPointSetManager:
    """Tests d'intégration avec PointSetManager mocké."""

    def test_full_pipeline_with_mock(self, sample_points_triangle):
        """Test pipeline complet avec mock du PointSetManager."""
        from triangulator.client import get_pointset
        
        # Préparer les données mockées
        encoded_pointset = encode_pointset(sample_points_triangle)
        
        with patch("triangulator.client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = encoded_pointset
            mock_requests.get.return_value = mock_response
            
            # Récupérer le PointSet
            pointset_data = get_pointset("123e4567-e89b-12d3-a456-426614174000")
            
            # Décoder
            points = decode_pointset(pointset_data)
            
            # Trianguler
            triangles = triangulate(points)
            
            # Encoder le résultat
            result = encode_triangles(points, triangles)
            
            assert len(triangles) == 1
            assert len(result) > 0

    def test_integration_handles_empty_pointset(self):
        """Test intégration avec PointSet vide."""
        from triangulator.client import get_pointset
        
        # PointSet vide
        encoded_pointset = struct.pack("<I", 0)
        
        with patch("triangulator.client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = encoded_pointset
            mock_requests.get.return_value = mock_response
            
            pointset_data = get_pointset("123e4567-e89b-12d3-a456-426614174000")
            points = decode_pointset(pointset_data)
            
            # La triangulation devrait échouer avec 0 points
            with pytest.raises(ValueError):
                triangulate(points)

    def test_integration_handles_pointset_not_found(self):
        """Test intégration quand PointSet n'existe pas."""
        from triangulator.client import get_pointset
        
        with patch("triangulator.client.requests") as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 404
            mock_response.json.return_value = {
                "code": "NOT_FOUND",
                "message": "PointSet not found"
            }
            mock_requests.get.return_value = mock_response
            
            with pytest.raises(FileNotFoundError):
                get_pointset("123e4567-e89b-12d3-a456-426614174000")

    def test_integration_handles_manager_unavailable(self):
        """Test intégration quand PointSetManager est inaccessible."""
        from triangulator.client import get_pointset
        
        with patch("triangulator.client.requests") as mock_requests:
            import requests
            mock_requests.get.side_effect = requests.exceptions.ConnectionError()
            
            with pytest.raises(ConnectionError):
                get_pointset("123e4567-e89b-12d3-a456-426614174000")


@pytest.mark.integration
class TestDataIntegrity:
    """Tests d'intégrité des données à travers le pipeline."""

    def test_point_coordinates_preserved(self):
        """Test que les coordonnées sont préservées à travers encode/decode."""
        original_points = [(1.5, 2.5), (-3.14, 42.0), (0.001, 999.999)]
        
        encoded = encode_pointset(original_points)
        decoded = decode_pointset(encoded)
        
        assert len(decoded) == len(original_points)
        for i, (x, y) in enumerate(original_points):
            assert decoded[i][0] == pytest.approx(x, rel=1e-5)
            assert decoded[i][1] == pytest.approx(y, rel=1e-5)

    def test_triangle_indices_preserved(self, sample_points_square):
        """Test que les indices de triangles sont préservés."""
        triangles = [(0, 1, 2), (0, 2, 3)]
        
        encoded = encode_triangles(sample_points_square, triangles)
        
        # Vérifier la structure
        assert len(encoded) > 0
        
        # Décoder et vérifier
        from triangulator.binary_format import decode_triangles
        decoded_points, decoded_triangles = decode_triangles(encoded)
        
        assert len(decoded_triangles) == 2
        assert decoded_triangles[0] == (0, 1, 2)
        assert decoded_triangles[1] == (0, 2, 3)
