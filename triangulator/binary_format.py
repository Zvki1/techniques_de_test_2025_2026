"""Encodage et décodage des formats binaires PointSet et Triangles."""


def encode_pointset(points):
    """
    Encode un ensemble de points au format binaire.
    
    Args:
        points: Liste de tuples (x, y) représentant les points.
        
    Returns:
        bytes: Représentation binaire du PointSet.
        
    Raises:
        ValueError: Si les données sont invalides.
    """
    raise NotImplementedError("À implémenter")


def decode_pointset(data):
    """
    Décode un PointSet depuis son format binaire.
    
    Args:
        data: bytes représentant un PointSet.
        
    Returns:
        list: Liste de tuples (x, y).
        
    Raises:
        ValueError: Si les données sont invalides.
    """
    raise NotImplementedError("À implémenter")


def encode_triangles(points, triangles):
    """
    Encode un ensemble de triangles au format binaire.
    
    Args:
        points: Liste de tuples (x, y) représentant les sommets.
        triangles: Liste de tuples (i1, i2, i3) représentant les indices.
        
    Returns:
        bytes: Représentation binaire des Triangles.
        
    Raises:
        ValueError: Si les données sont invalides.
    """
    raise NotImplementedError("À implémenter")


def decode_triangles(data):
    """
    Décode des Triangles depuis leur format binaire.
    
    Args:
        data: bytes représentant des Triangles.
        
    Returns:
        tuple: (points, triangles) où points est une liste de tuples (x, y)
               et triangles est une liste de tuples (i1, i2, i3).
        
    Raises:
        ValueError: Si les données sont invalides.
    """
    raise NotImplementedError("À implémenter")