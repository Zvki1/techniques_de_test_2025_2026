"""Tests d integration du Triangulator."""

import struct
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from triangulator.binary_format import decode_pointset, encode_pointset, encode_triangles
from triangulator.triangulation import triangulate


# =============================================================================
# Tests d Integration
# =============================================================================

@pytest.mark.integration
class TestBinaryFormatAndTriangulation:
    """Tests d integration entre binary_format et triangulation."""

    def test_decode_then_triangulate(self):
        """Test : decode PointSet puis triangule."""
        points_data = struct.pack("<L", 3)
        points_data += struct.pack("<ff", 0.0, 0.0)
        points_data += struct.pack("<ff", 1.0, 0.0)
        points_data += struct.pack("<ff", 0.5, 1.0)

        points = decode_pointset(points_data)
        triangles = triangulate(points)

        assert len(triangles) == 1
        assert set(triangles[0]) == {0, 1, 2}

    def test_triangulate_then_encode(self, sample_points_square):
        """Test : triangule puis encode le resultat."""
        triangles = triangulate(sample_points_square)
        encoded = encode_triangles(sample_points_square, triangles)

        assert len(encoded) > 0
        nb_points = int.from_bytes(encoded[:4], byteorder="little")
        assert nb_points == 4

    def test_full_pipeline_encode_decode_triangulate_encode(self):
        """Test pipeline complet : encode, decode, triangulate, encode."""
        original_points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

        encoded_points = encode_pointset(original_points)
        decoded_points = decode_pointset(encoded_points)
        triangles = triangulate(decoded_points)
        final_result = encode_triangles(decoded_points, triangles)

        assert len(final_result) > 0
        assert len(triangles) == 2


@pytest.mark.integration
class TestTriangulatorWithMockedPointSetManager:
    """Tests d integration avec PointSetManager mocke."""

    def test_full_pipeline_with_mock(self, sample_points_triangle):
        """Test pipeline complet avec mock du PointSetManager."""
        from triangulator.client import get_pointset

        encoded_pointset = encode_pointset(sample_points_triangle)

        mock_response = MagicMock()
        mock_response.read.return_value = encoded_pointset
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_response

            pointset_data = get_pointset("123e4567-e89b-12d3-a456-426614174000")
            points = decode_pointset(pointset_data)
            triangles = triangulate(points)
            result = encode_triangles(points, triangles)

            assert len(triangles) == 1
            assert len(result) > 0

    def test_integration_handles_empty_pointset(self):
        """Test integration avec PointSet vide."""
        from triangulator.client import get_pointset

        encoded_pointset = struct.pack("<L", 0)

        mock_response = MagicMock()
        mock_response.read.return_value = encoded_pointset
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_response

            pointset_data = get_pointset("123e4567-e89b-12d3-a456-426614174000")
            points = decode_pointset(pointset_data)

            with pytest.raises(ValueError):
                triangulate(points)

    def test_integration_handles_pointset_not_found(self):
        """Test integration quand PointSet n existe pas."""
        from triangulator.client import get_pointset

        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="http://test/pointset/123",
                code=404,
                msg="Not Found",
                hdrs={},
                fp=BytesIO(b"")
            )

            with pytest.raises(FileNotFoundError):
                get_pointset("123e4567-e89b-12d3-a456-426614174000")

    def test_integration_handles_manager_unavailable(self):
        """Test integration quand PointSetManager est inaccessible."""
        from triangulator.client import get_pointset

        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

            with pytest.raises(ConnectionError):
                get_pointset("123e4567-e89b-12d3-a456-426614174000")


@pytest.mark.integration
class TestDataIntegrity:
    """Tests d integrite des donnees a travers le pipeline."""

    def test_point_coordinates_preserved(self):
        """Test que les coordonnees sont preservees a travers encode/decode."""
        original_points = [(1.5, 2.5), (-3.14, 42.0), (0.001, 999.999)]

        encoded = encode_pointset(original_points)
        decoded = decode_pointset(encoded)

        assert len(decoded) == len(original_points)
        for i, (x, y) in enumerate(original_points):
            assert decoded[i][0] == pytest.approx(x, rel=1e-5)
            assert decoded[i][1] == pytest.approx(y, rel=1e-5)

    def test_triangle_indices_preserved(self, sample_points_square):
        """Test que les indices de triangles sont preserves."""
        triangles = [(0, 1, 2), (0, 2, 3)]

        encoded = encode_triangles(sample_points_square, triangles)
        assert len(encoded) > 0

        from triangulator.binary_format import decode_triangles
        decoded_points, decoded_triangles = decode_triangles(encoded)

        assert len(decoded_triangles) == 2
        assert decoded_triangles[0] == (0, 1, 2)
        assert decoded_triangles[1] == (0, 2, 3)
