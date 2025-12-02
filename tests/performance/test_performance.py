"""Tests de performance pour le Triangulator."""

import random
import time

import pytest

from triangulator.binary_format import decode_pointset, encode_pointset, encode_triangles
from triangulator.triangulation import triangulate


# =============================================================================
# 4. Tests de Performance
# =============================================================================

def generate_random_points(n, seed=42):
    """Génère n points aléatoires de manière reproductible."""
    random.seed(seed)
    return [(random.uniform(0, 1000), random.uniform(0, 1000)) for _ in range(n)]


# =============================================================================
# 4.1 Tests de montée en charge - Triangulation
# =============================================================================

@pytest.mark.performance
class TestTriangulationPerformance:
    """Tests de performance de l'algorithme de triangulation."""

    def test_triangulation_10_points(self):
        """Mesure temps triangulation de 10 points."""
        points = generate_random_points(10)
        
        start = time.perf_counter()
        triangles = triangulate(points)
        duration = time.perf_counter() - start
        
        print(f"\n[PERF] Triangulation 10 points: {duration:.4f}s")
        assert duration < 1.0
        assert len(triangles) > 0

    def test_triangulation_100_points(self):
        """Mesure temps triangulation de 100 points."""
        points = generate_random_points(100)
        
        start = time.perf_counter()
        triangles = triangulate(points)
        duration = time.perf_counter() - start
        
        print(f"\n[PERF] Triangulation 100 points: {duration:.4f}s")
        assert duration < 1.0
        assert len(triangles) > 0

    def test_triangulation_1000_points(self):
        """Mesure temps triangulation de 1000 points."""
        points = generate_random_points(1000)
        
        start = time.perf_counter()
        triangles = triangulate(points)
        duration = time.perf_counter() - start
        
        print(f"\n[PERF] Triangulation 1000 points: {duration:.4f}s")
        assert duration < 5.0
        assert len(triangles) > 0

    def test_triangulation_10000_points(self):
        """Mesure temps triangulation de 10000 points."""
        points = generate_random_points(10000)
        
        start = time.perf_counter()
        triangles = triangulate(points)
        duration = time.perf_counter() - start
        
        print(f"\n[PERF] Triangulation 10000 points: {duration:.4f}s")
        assert duration < 30.0
        assert len(triangles) > 0


# =============================================================================
# 4.2 Tests de performance - Encodage/Décodage
# =============================================================================

@pytest.mark.performance
class TestEncodingPerformance:
    """Tests de performance de l'encodage binaire."""

    def test_encode_100_points(self):
        """Mesure temps encodage de 100 points."""
        points = generate_random_points(100)
        
        start = time.perf_counter()
        data = encode_pointset(points)
        duration = time.perf_counter() - start
        
        print(f"\n[PERF] Encodage 100 points: {duration:.6f}s")
        assert duration < 0.1
        assert len(data) == 4 + 100 * 8

    def test_encode_1000_points(self):
        """Mesure temps encodage de 1000 points."""
        points = generate_random_points(1000)
        
        start = time.perf_counter()
        data = encode_pointset(points)
        duration = time.perf_counter() - start
        
        print(f"\n[PERF] Encodage 1000 points: {duration:.6f}s")
        assert duration < 0.5
        assert len(data) == 4 + 1000 * 8

    def test_encode_10000_points(self):
        """Mesure temps encodage de 10000 points."""
        points = generate_random_points(10000)
        
        start = time.perf_counter()
        data = encode_pointset(points)
        duration = time.perf_counter() - start
        
        print(f"\n[PERF] Encodage 10000 points: {duration:.6f}s")
        assert duration < 1.0
        assert len(data) == 4 + 10000 * 8


@pytest.mark.performance
class TestDecodingPerformance:
    """Tests de performance du décodage binaire."""

    def test_decode_100_points(self):
        """Mesure temps décodage de 100 points."""
        points = generate_random_points(100)
        data = encode_pointset(points)
        
        start = time.perf_counter()
        decoded = decode_pointset(data)
        duration = time.perf_counter() - start
        
        print(f"\n[PERF] Décodage 100 points: {duration:.6f}s")
        assert duration < 0.1
        assert len(decoded) == 100

    def test_decode_1000_points(self):
        """Mesure temps décodage de 1000 points."""
        points = generate_random_points(1000)
        data = encode_pointset(points)
        
        start = time.perf_counter()
        decoded = decode_pointset(data)
        duration = time.perf_counter() - start
        
        print(f"\n[PERF] Décodage 1000 points: {duration:.6f}s")
        assert duration < 0.5
        assert len(decoded) == 1000

    def test_decode_10000_points(self):
        """Mesure temps décodage de 10000 points."""
        points = generate_random_points(10000)
        data = encode_pointset(points)
        
        start = time.perf_counter()
        decoded = decode_pointset(data)
        duration = time.perf_counter() - start
        
        print(f"\n[PERF] Décodage 10000 points: {duration:.6f}s")
        assert duration < 1.0
        assert len(decoded) == 10000


# =============================================================================
# 4.3 Tests de performance - Pipeline complet
# =============================================================================

@pytest.mark.performance
class TestFullPipelinePerformance:
    """Tests de performance du pipeline complet."""

    def test_full_pipeline_100_points(self):
        """Mesure temps pipeline complet avec 100 points."""
        points = generate_random_points(100)
        
        start = time.perf_counter()
        
        # Encode
        encoded = encode_pointset(points)
        # Decode
        decoded = decode_pointset(encoded)
        # Triangulate
        triangles = triangulate(decoded)
        # Encode result
        result = encode_triangles(decoded, triangles)
        
        duration = time.perf_counter() - start
        
        print(f"\n[PERF] Pipeline complet 100 points: {duration:.4f}s")
        assert duration < 2.0
        assert len(result) > 0

    def test_full_pipeline_1000_points(self):
        """Mesure temps pipeline complet avec 1000 points."""
        points = generate_random_points(1000)
        
        start = time.perf_counter()
        
        encoded = encode_pointset(points)
        decoded = decode_pointset(encoded)
        triangles = triangulate(decoded)
        result = encode_triangles(decoded, triangles)
        
        duration = time.perf_counter() - start
        
        print(f"\n[PERF] Pipeline complet 1000 points: {duration:.4f}s")
        assert duration < 10.0
        assert len(result) > 0
