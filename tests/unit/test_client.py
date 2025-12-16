"""Tests unitaires pour le client PointSetManager."""

import struct
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from triangulator.client import get_pointset


# =============================================================================
# Tests de Communication avec PointSetManager
# =============================================================================

class TestGetPointsetValidation:
    """Tests de validation des parametres."""

    def test_invalid_uuid_format_raises(self):
        """Test UUID invalide leve ValueError."""
        with pytest.raises(ValueError):
            get_pointset("invalid-uuid")

    def test_empty_uuid_raises(self):
        """Test UUID vide leve ValueError."""
        with pytest.raises(ValueError):
            get_pointset("")

    def test_uuid_too_short_raises(self):
        """Test UUID trop court leve ValueError."""
        with pytest.raises(ValueError):
            get_pointset("123")

    def test_valid_uuid_format_accepted(self, valid_uuid):
        """Test format UUID valide est accepte (mock la requete)."""
        mock_response = MagicMock()
        mock_response.read.return_value = struct.pack("<L", 0)
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_response
            result = get_pointset(valid_uuid)
            assert result is not None


class TestGetPointsetSuccess:
    """Tests des cas de succes."""

    def test_get_pointset_success_200(self, valid_uuid):
        """Test requete reussie (200 + PointSet binaire valide)."""
        pointset_data = struct.pack("<L", 3) + struct.pack("<ff", 0.0, 0.0) \
            + struct.pack("<ff", 1.0, 0.0) + struct.pack("<ff", 0.5, 1.0)

        mock_response = MagicMock()
        mock_response.read.return_value = pointset_data
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_response
            result = get_pointset(valid_uuid)

            assert isinstance(result, bytes)
            assert len(result) == 28

    def test_get_pointset_empty(self, valid_uuid):
        """Test recuperation PointSet vide."""
        mock_response = MagicMock()
        mock_response.read.return_value = struct.pack("<L", 0)
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_response
            result = get_pointset(valid_uuid)

            assert len(result) == 4


class TestGetPointsetErrors:
    """Tests des cas d erreur."""

    def test_get_pointset_not_found_404(self, valid_uuid):
        """Test PointSet inexistant (404) leve FileNotFoundError."""
        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="http://test/pointset/123",
                code=404,
                msg="Not Found",
                hdrs={},
                fp=BytesIO(b"")
            )

            with pytest.raises(FileNotFoundError):
                get_pointset(valid_uuid)

    def test_get_pointset_server_error_500(self, valid_uuid):
        """Test erreur serveur PointSetManager (500)."""
        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="http://test/pointset/123",
                code=500,
                msg="Internal Server Error",
                hdrs={},
                fp=BytesIO(b"")
            )

            with pytest.raises(RuntimeError):
                get_pointset(valid_uuid)

    def test_get_pointset_connection_error(self, valid_uuid):
        """Test serveur inaccessible leve ConnectionError."""
        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Connection refused")

            with pytest.raises(ConnectionError):
                get_pointset(valid_uuid)

    def test_get_pointset_timeout(self, valid_uuid):
        """Test timeout de connexion."""
        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = TimeoutError("Timeout")

            with pytest.raises(ConnectionError):
                get_pointset(valid_uuid)


class TestGetPointsetURLConstruction:
    """Tests de construction d URL."""

    def test_correct_url_called(self, valid_uuid):
        """Test que l URL correcte est appelee."""
        mock_response = MagicMock()
        mock_response.read.return_value = struct.pack("<L", 0)
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_response
            get_pointset(valid_uuid, manager_url="http://test-server:8080")

            call_url = mock_urlopen.call_args[0][0]
            assert valid_uuid in call_url
            assert "test-server:8080" in call_url

    def test_custom_manager_url(self, valid_uuid):
        """Test avec URL personnalisee du manager."""
        mock_response = MagicMock()
        mock_response.read.return_value = struct.pack("<L", 0)
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch("triangulator.client.urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.return_value = mock_response
            get_pointset(valid_uuid, manager_url="http://custom:9000")

            call_url = mock_urlopen.call_args[0][0]
            assert "custom:9000" in call_url
