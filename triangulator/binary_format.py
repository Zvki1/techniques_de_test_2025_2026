"""Encodage et decodage des formats binaires PointSet et Triangles."""

import struct


def encode_pointset(points):
    """Encode un ensemble de points au format binaire.

    Args:
        points: Liste de tuples (x, y) representant les points.

    Returns:
        bytes: Representation binaire du PointSet.
    """
    data = struct.pack("<L", len(points))
    for x, y in points:
        data += struct.pack("<ff", x, y)
    return data


def decode_pointset(data):
    """Decode un PointSet depuis son format binaire.

    Args:
        data: bytes representant un PointSet.

    Returns:
        list: Liste de tuples (x, y).

    Raises:
        ValueError: Si les donnees sont invalides.
    """
    if len(data) < 4:
        raise ValueError("Header incomplet")

    count = struct.unpack("<L", data[:4])[0]
    expected_size = 4 + count * 8

    if len(data) < expected_size:
        raise ValueError("Donnees incompletes")

    points = []
    offset = 4
    for _ in range(count):
        x, y = struct.unpack("<ff", data[offset:offset+8])
        points.append((x, y))
        offset += 8

    return points


def encode_triangles(points, triangles):
    """Encode un ensemble de triangles au format binaire.

    Args:
        points: Liste de tuples (x, y) représentant les sommets.
        triangles: Liste de tuples (i1, i2, i3) représentant les indices.

    Returns:
        bytes: Représentation binaire des Triangles.

    Raises:
        ValueError: Si les données sont invalides.
    """
    n_points = len(points)

    for tri in triangles:
        for idx in tri:
            if idx < 0 or idx >= n_points:
                raise ValueError(f"Index {idx} hors limite")

    data = encode_pointset(points)
    data += struct.pack("<L", len(triangles))

    for i1, i2, i3 in triangles:
        data += struct.pack("<LLL", i1, i2, i3)

    return data


def decode_triangles(data):
    """Décode des Triangles depuis leur format binaire.

    Args:
        data: bytes représentant des Triangles.

    Returns:
        tuple: (points, triangles) où points est une liste de tuples (x, y)
               et triangles est une liste de tuples (i1, i2, i3).

    Raises:
        ValueError: Si les données sont invalides.
    """
    points = decode_pointset(data)
    n_points = len(points)

    offset = 4 + n_points * 8

    if len(data) < offset + 4:
        raise ValueError("Header triangles manquant")

    n_triangles = struct.unpack("<L", data[offset:offset+4])[0]
    offset += 4

    expected_size = offset + n_triangles * 12
    if len(data) < expected_size:
        raise ValueError("Donnees triangles incompletes")

    triangles = []
    for _ in range(n_triangles):
        i1, i2, i3 = struct.unpack("<LLL", data[offset:offset+12])

        for idx in (i1, i2, i3):
            if idx >= n_points:
                raise ValueError(f"Index {idx} hors limite")

        triangles.append((i1, i2, i3))
        offset += 12

    return points, triangles
