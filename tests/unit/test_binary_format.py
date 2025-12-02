"""Tests unitaires pour le format binaire."""

import struct
import sys

import pytest

from triangulator.binary_format import (
    decode_pointset,
    decode_triangles,
    encode_pointset,
    encode_triangles,
)


class TestEncodePointSet:
    """Tests d'encodage PointSet."""

    def test_encode_vide(self):
        """Ensemble vide."""
        data = encode_pointset([])
        assert len(data) == 4
        assert int.from_bytes(data[:4], byteorder="little") == 0

    def test_encode_un_point(self):
        """Un seul point."""
        data = encode_pointset([(1.5, 2.5)])
        assert len(data) == 12
        assert int.from_bytes(data[:4], byteorder="little") == 1

    def test_encode_trois_points(self):
        """Trois points."""
        points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        data = encode_pointset(points)
        assert len(data) == 28
        assert int.from_bytes(data[:4], byteorder="little") == 3

    def test_encode_dix_points(self):
        """Dix points."""
        points = [(float(i), float(i)) for i in range(10)]
        data = encode_pointset(points)
        assert len(data) == 84

    def test_encode_cent_points(self, sample_points_100):
        """Cent points."""
        data = encode_pointset(sample_points_100)
        assert len(data) == 804

    def test_encode_valeurs_negatives(self):
        """Valeurs negatives."""
        points = [(-1.5, -2.5), (-100.0, 50.0)]
        data = encode_pointset(points)
        assert len(data) == 20

    def test_encode_valeurs_extremes(self):
        """Valeurs limites float."""
        points = [(sys.float_info.max, sys.float_info.min), (0.0, -0.0)]
        data = encode_pointset(points)
        assert len(data) == 20


class TestDecodePointSet:
    """Tests de decodage PointSet."""

    def test_decode_vide(self):
        """Ensemble vide."""
        data = struct.pack("<I", 0)
        assert decode_pointset(data) == []

    def test_decode_un_point(self):
        """Un point."""
        data = struct.pack("<I", 1) + struct.pack("<ff", 1.5, 2.5)
        points = decode_pointset(data)
        assert len(points) == 1
        assert points[0][0] == pytest.approx(1.5)
        assert points[0][1] == pytest.approx(2.5)

    def test_decode_plusieurs_points(self):
        """Plusieurs points."""
        original = [(0.0, 0.0), (1.0, 2.0), (3.0, 4.0)]
        data = struct.pack("<I", 3)
        for x, y in original:
            data += struct.pack("<ff", x, y)
        
        points = decode_pointset(data)
        assert len(points) == 3

    def test_decode_donnees_incompletes(self):
        """Donnees tronquees."""
        data = b"\x01\x00\x00\x00\xff"
        with pytest.raises(ValueError):
            decode_pointset(data)

    def test_decode_count_incorrect(self):
        """Nombre de points declare incorrect."""
        data = struct.pack("<I", 5) + struct.pack("<ff", 1.0, 2.0)
        with pytest.raises(ValueError):
            decode_pointset(data)

    def test_decode_header_incomplet(self):
        """Header trop court."""
        with pytest.raises(ValueError):
            decode_pointset(b"\x01\x00")

    def test_decode_vide_bytes(self):
        """Bytes vides."""
        with pytest.raises(ValueError):
            decode_pointset(b"")


class TestRoundtripPointSet:
    """Tests aller-retour encode/decode."""

    def test_roundtrip_vide(self):
        """Aller-retour vide."""
        original = []
        assert decode_pointset(encode_pointset(original)) == original

    def test_roundtrip_un_point(self):
        """Aller-retour un point."""
        original = [(1.5, 2.5)]
        decoded = decode_pointset(encode_pointset(original))
        assert decoded[0][0] == pytest.approx(1.5)
        assert decoded[0][1] == pytest.approx(2.5)

    def test_roundtrip_plusieurs_points(self, sample_points_triangle):
        """Aller-retour plusieurs points."""
        decoded = decode_pointset(encode_pointset(sample_points_triangle))
        assert len(decoded) == len(sample_points_triangle)

    def test_roundtrip_negatifs(self):
        """Aller-retour valeurs negatives."""
        original = [(-10.5, -20.5), (100.0, -50.0)]
        decoded = decode_pointset(encode_pointset(original))
        assert len(decoded) == 2


class TestEncodeTriangles:
    """Tests d'encodage Triangles."""

    def test_encode_zero_triangle(self):
        """Zero triangle."""
        points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        data = encode_triangles(points, [])
        assert len(data) == 32

    def test_encode_un_triangle(self):
        """Un triangle."""
        points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        triangles = [(0, 1, 2)]
        data = encode_triangles(points, triangles)
        assert len(data) == 44

    def test_encode_deux_triangles(self):
        """Deux triangles (carre)."""
        points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        triangles = [(0, 1, 2), (0, 2, 3)]
        data = encode_triangles(points, triangles)
        assert len(data) == 64

    def test_encode_index_invalide(self):
        """Index hors limite."""
        points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        with pytest.raises(ValueError):
            encode_triangles(points, [(0, 1, 5)])

    def test_encode_index_negatif(self):
        """Index negatif."""
        points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        with pytest.raises(ValueError):
            encode_triangles(points, [(0, -1, 2)])


class TestDecodeTriangles:
    """Tests de decodage Triangles."""

    def test_decode_valide(self):
        """Decodage valide."""
        points_data = struct.pack("<I", 3)
        points_data += struct.pack("<ff", 0.0, 0.0)
        points_data += struct.pack("<ff", 1.0, 0.0)
        points_data += struct.pack("<ff", 0.5, 1.0)
        triangles_data = struct.pack("<I", 1) + struct.pack("<III", 0, 1, 2)
        
        points, triangles = decode_triangles(points_data + triangles_data)
        assert len(points) == 3
        assert triangles[0] == (0, 1, 2)

    def test_decode_pointset_invalide(self):
        """Partie PointSet invalide."""
        with pytest.raises(ValueError):
            decode_triangles(b"\x05\x00")

    def test_decode_triangles_incomplets(self):
        """Triangles incomplets."""
        points_data = struct.pack("<I", 3)
        points_data += struct.pack("<ff", 0.0, 0.0)
        points_data += struct.pack("<ff", 1.0, 0.0)
        points_data += struct.pack("<ff", 0.5, 1.0)
        triangles_data = struct.pack("<I", 1) + struct.pack("<II", 0, 1)
        
        with pytest.raises(ValueError):
            decode_triangles(points_data + triangles_data)

    def test_decode_count_triangles_faux(self):
        """Nombre de triangles incorrect."""
        points_data = struct.pack("<I", 3)
        points_data += struct.pack("<ff", 0.0, 0.0)
        points_data += struct.pack("<ff", 1.0, 0.0)
        points_data += struct.pack("<ff", 0.5, 1.0)
        triangles_data = struct.pack("<I", 3) + struct.pack("<III", 0, 1, 2)
        
        with pytest.raises(ValueError):
            decode_triangles(points_data + triangles_data)

    def test_decode_index_hors_limite(self):
        """Index de sommet hors limite."""
        points_data = struct.pack("<I", 3)
        points_data += struct.pack("<ff", 0.0, 0.0)
        points_data += struct.pack("<ff", 1.0, 0.0)
        points_data += struct.pack("<ff", 0.5, 1.0)
        triangles_data = struct.pack("<I", 1) + struct.pack("<III", 0, 1, 10)
        
        with pytest.raises(ValueError):
            decode_triangles(points_data + triangles_data)


class TestRoundtripTriangles:
    """Tests aller-retour Triangles."""

    def test_roundtrip_un_triangle(self):
        """Aller-retour un triangle."""
        points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        triangles = [(0, 1, 2)]
        
        decoded_pts, decoded_tri = decode_triangles(encode_triangles(points, triangles))
        assert len(decoded_tri) == 1
        assert decoded_tri[0] == (0, 1, 2)

    def test_roundtrip_plusieurs_triangles(self, sample_points_square):
        """Aller-retour plusieurs triangles."""
        triangles = [(0, 1, 2), (0, 2, 3)]
        decoded_pts, decoded_tri = decode_triangles(encode_triangles(sample_points_square, triangles))
        assert len(decoded_tri) == 2

    def test_roundtrip_zero_triangle(self):
        """Aller-retour zero triangle."""
        points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
        decoded_pts, decoded_tri = decode_triangles(encode_triangles(points, []))
        assert len(decoded_tri) == 0
