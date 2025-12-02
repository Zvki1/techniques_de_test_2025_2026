"""Fixtures et helpers partagés pour les tests."""

import random
import struct

import pytest


# =============================================================================
# Fixtures de données de points
# =============================================================================

@pytest.fixture
def sample_points_triangle():
    """3 points formant un triangle simple."""
    return [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]


@pytest.fixture
def sample_points_square():
    """4 points formant un carré."""
    return [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]


@pytest.fixture
def sample_points_collinear():
    """3 points alignés (cas limite)."""
    return [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)]


@pytest.fixture
def sample_points_duplicate():
    """Points avec duplicata."""
    return [(0.0, 0.0), (1.0, 0.0), (1.0, 0.0), (0.5, 1.0)]


@pytest.fixture
def sample_points_100():
    """100 points aléatoires (seed fixe pour reproductibilité)."""
    random.seed(42)
    return [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(100)]


@pytest.fixture
def sample_points_1000():
    """1000 points aléatoires (seed fixe)."""
    random.seed(42)
    return [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(1000)]


@pytest.fixture
def sample_points_10000():
    """10000 points pour tests de performance."""
    random.seed(42)
    return [(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(10000)]


# =============================================================================
# Fixtures de données binaires
# =============================================================================

@pytest.fixture
def empty_pointset_bytes():
    """Bytes d'un PointSet vide."""
    return struct.pack("<I", 0)  # count = 0


@pytest.fixture
def single_point_bytes():
    """Bytes d'un PointSet avec 1 point (1.5, 2.5)."""
    return struct.pack("<I", 1) + struct.pack("<ff", 1.5, 2.5)


@pytest.fixture
def triangle_bytes():
    """Bytes d'un PointSet de 3 points formant un triangle."""
    points = [(0.0, 0.0), (1.0, 0.0), (0.5, 1.0)]
    data = struct.pack("<I", len(points))
    for x, y in points:
        data += struct.pack("<ff", x, y)
    return data


@pytest.fixture
def corrupted_pointset_bytes():
    """Bytes corrompus (déclare 1 point mais données incomplètes)."""
    return b"\x01\x00\x00\x00\xff"


@pytest.fixture
def insufficient_header_bytes():
    """Header incomplet (< 4 bytes)."""
    return b"\x01\x00"


# =============================================================================
# Fixtures pour l'API Flask
# =============================================================================

@pytest.fixture
def valid_uuid():
    """UUID valide pour les tests."""
    return "123e4567-e89b-12d3-a456-426614174000"


@pytest.fixture
def invalid_uuid():
    """UUID invalide pour les tests."""
    return "invalid-uuid-format"


# =============================================================================
# Helpers de validation
# =============================================================================

def is_valid_triangulation(points, triangles):
    """
    Vérifie qu'une triangulation est valide.
    
    Args:
        points: Liste de tuples (x, y).
        triangles: Liste de tuples (i1, i2, i3).
        
    Returns:
        bool: True si la triangulation est valide.
    """
    if len(points) < 3:
        return len(triangles) == 0
    
    # Vérifier que tous les indices sont valides
    for tri in triangles:
        for idx in tri:
            if idx < 0 or idx >= len(points):
                return False
        # Vérifier que les 3 indices sont différents
        if len(set(tri)) != 3:
            return False
    
    return True


def generate_random_points(n, seed=42, x_range=(0, 100), y_range=(0, 100)):
    """
    Génère n points aléatoires de manière reproductible.
    
    Args:
        n: Nombre de points.
        seed: Graine pour reproductibilité.
        x_range: Plage des coordonnées X.
        y_range: Plage des coordonnées Y.
        
    Returns:
        list: Liste de tuples (x, y).
    """
    random.seed(seed)
    return [
        (random.uniform(*x_range), random.uniform(*y_range))
        for _ in range(n)
    ]


def encode_pointset_manually(points):
    """
    Encode manuellement un PointSet (pour créer des données de test).
    
    Args:
        points: Liste de tuples (x, y).
        
    Returns:
        bytes: Représentation binaire.
    """
    data = struct.pack("<I", len(points))
    for x, y in points:
        data += struct.pack("<ff", x, y)
    return data


def encode_triangles_manually(points, triangles):
    """
    Encode manuellement des Triangles (pour créer des données de test).
    
    Args:
        points: Liste de tuples (x, y).
        triangles: Liste de tuples (i1, i2, i3).
        
    Returns:
        bytes: Représentation binaire.
    """
    data = encode_pointset_manually(points)
    data += struct.pack("<I", len(triangles))
    for i1, i2, i3 in triangles:
        data += struct.pack("<III", i1, i2, i3)
    return data
