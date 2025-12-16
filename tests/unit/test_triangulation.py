"""Tests unitaires pour l'algorithme de triangulation."""

import pytest

from triangulator.triangulation import triangulate


# =============================================================================
# 1.3 Tests de l'Algorithme de Triangulation
# =============================================================================

class TestTriangulationCasNormaux:
    """Tests des cas normaux de triangulation."""

    def test_triangulate_minimum_3_points(self, sample_points_triangle):
        """Test triangulation minimale : 3 points → 1 triangle."""
        triangles = triangulate(sample_points_triangle)

        assert len(triangles) == 1
        # Le triangle doit utiliser les 3 indices
        assert set(triangles[0]) == {0, 1, 2}

    def test_triangulate_square_4_points(self, sample_points_square):
        """Test triangulation carré : 4 points → 2 triangles."""
        triangles = triangulate(sample_points_square)

        assert len(triangles) == 2

    def test_triangulate_5_points(self):
        """Test triangulation de 5 points."""
        points = [
            (0.0, 0.0),
            (1.0, 0.0),
            (2.0, 0.0),
            (1.0, 1.0),
            (0.5, 0.5),
        ]
        triangles = triangulate(points)

        # Pour N points non-colinéaires, on a généralement 2N-5 à 2N-2 triangles
        # selon la disposition
        assert len(triangles) >= 1

    def test_triangulate_100_points(self, sample_points_100):
        """Test triangulation de 100 points."""
        triangles = triangulate(sample_points_100)

        # Doit produire des triangles
        assert len(triangles) > 0

        # Vérification basique : tous les indices sont valides
        for tri in triangles:
            for idx in tri:
                assert 0 <= idx < 100


class TestTriangulationCasLimites:
    """Tests des cas limites de triangulation."""

    def test_triangulate_less_than_3_points_raises(self):
        """Test < 3 points → Exception."""
        with pytest.raises(ValueError):
            triangulate([(0.0, 0.0)])

        with pytest.raises(ValueError):
            triangulate([(0.0, 0.0), (1.0, 1.0)])

    def test_triangulate_empty_raises(self):
        """Test ensemble vide → Exception."""
        with pytest.raises(ValueError):
            triangulate([])

    def test_triangulate_collinear_points(self, sample_points_collinear):
        """Test points alignés → Exception ou liste vide."""
        # Points colinéaires ne peuvent pas former de triangles
        # L'implémentation peut soit lever une exception, soit retourner []
        try:
            result = triangulate(sample_points_collinear)
            # Si pas d'exception, doit retourner une liste vide
            assert result == []
        except ValueError:
            # Exception acceptable pour points colinéaires
            pass

    def test_triangulate_collinear_same_x(self):
        """Test points alignés sur même X."""
        points = [(5.0, 0.0), (5.0, 1.0), (5.0, 2.0)]

        try:
            result = triangulate(points)
            assert result == []
        except ValueError:
            pass

    def test_triangulate_collinear_same_y(self):
        """Test points alignés sur même Y."""
        points = [(0.0, 5.0), (1.0, 5.0), (2.0, 5.0)]

        try:
            result = triangulate(points)
            assert result == []
        except ValueError:
            pass

    def test_triangulate_duplicate_points(self, sample_points_duplicate):
        """Test points en double → Dédoublonnage ou erreur."""
        # L'implémentation peut soit dédoublonner, soit lever une erreur
        try:
            result = triangulate(sample_points_duplicate)
            # Si ça fonctionne, on vérifie que le résultat est valide
            assert isinstance(result, list)
        except ValueError:
            # Exception acceptable pour points dupliqués
            pass

    def test_triangulate_all_same_point(self):
        """Test tous les points identiques."""
        points = [(1.0, 1.0), (1.0, 1.0), (1.0, 1.0)]

        with pytest.raises(ValueError):
            triangulate(points)


class TestTriangulationProprietesGeometriques:
    """Tests des propriétés géométriques de la triangulation."""

    def test_all_vertices_used(self, sample_points_triangle):
        """Test que tous les sommets sont utilisés dans au moins un triangle."""
        triangles = triangulate(sample_points_triangle)

        # Collecter tous les indices utilisés
        used_indices = set()
        for tri in triangles:
            used_indices.update(tri)

        # Tous les points doivent être utilisés
        assert used_indices == set(range(len(sample_points_triangle)))

    def test_valid_indices(self, sample_points_square):
        """Test que tous les indices sont dans les bornes."""
        triangles = triangulate(sample_points_square)
        n_points = len(sample_points_square)

        for tri in triangles:
            assert len(tri) == 3
            for idx in tri:
                assert 0 <= idx < n_points

    def test_no_degenerate_triangles(self, sample_points_100):
        """Test qu'il n'y a pas de triangles dégénérés (même sommet répété)."""
        triangles = triangulate(sample_points_100)

        for tri in triangles:
            # Un triangle valide a 3 sommets distincts
            assert len(set(tri)) == 3

    def test_triangle_indices_are_integers(self, sample_points_square):
        """Test que les indices sont des entiers."""
        triangles = triangulate(sample_points_square)

        for tri in triangles:
            for idx in tri:
                assert isinstance(idx, int)


class TestTriangulationFormesSpeciales:
    """Tests avec des formes géométriques spéciales."""

    def test_triangulate_rectangle(self):
        """Test triangulation d'un rectangle."""
        points = [(0.0, 0.0), (2.0, 0.0), (2.0, 1.0), (0.0, 1.0)]
        triangles = triangulate(points)

        assert len(triangles) == 2

    def test_triangulate_pentagon(self):
        """Test triangulation d'un pentagone convexe."""
        import math
        # Pentagone régulier
        points = [
            (math.cos(2 * math.pi * i / 5), math.sin(2 * math.pi * i / 5))
            for i in range(5)
        ]
        triangles = triangulate(points)

        assert len(triangles) == 3  # n-2 triangles pour polygone convexe

    def test_triangulate_hexagon(self):
        """Test triangulation d'un hexagone convexe."""
        import math
        # Hexagone régulier
        points = [
            (math.cos(2 * math.pi * i / 6), math.sin(2 * math.pi * i / 6))
            for i in range(6)
        ]
        triangles = triangulate(points)

        # Delaunay produit au moins n-2 triangles
        assert len(triangles) >= 4

    def test_triangulate_with_interior_point(self):
        """Test triangulation avec point intérieur."""
        # Carré avec point au centre
        points = [
            (0.0, 0.0),
            (1.0, 0.0),
            (1.0, 1.0),
            (0.0, 1.0),
            (0.5, 0.5),  # Point intérieur
        ]
        triangles = triangulate(points)

        # Doit produire plus de triangles qu'un simple carré
        assert len(triangles) >= 2
