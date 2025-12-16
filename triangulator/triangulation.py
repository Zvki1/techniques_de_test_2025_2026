"""Algorithme de triangulation."""


def _circumcircle(p1, p2, p3):
    """Calcule le cercle circonscrit d'un triangle.

    Args:
        p1: Tuple (x, y) du premier sommet.
        p2: Tuple (x, y) du deuxieme sommet.
        p3: Tuple (x, y) du troisieme sommet.

    Returns:
        tuple: (cx, cy, r_squared) centre et rayon au carre.
        None si les points sont alignes.
    """
    ax, ay = p1
    bx, by = p2
    cx, cy = p3

    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))

    if abs(d) < 1e-10:
        return None

    ax2_ay2 = ax * ax + ay * ay
    bx2_by2 = bx * bx + by * by
    cx2_cy2 = cx * cx + cy * cy

    ux = (ax2_ay2 * (by - cy) + bx2_by2 * (cy - ay) + cx2_cy2 * (ay - by)) / d
    uy = (ax2_ay2 * (cx - bx) + bx2_by2 * (ax - cx) + cx2_cy2 * (bx - ax)) / d

    r_squared = (ax - ux) ** 2 + (ay - uy) ** 2

    return (ux, uy, r_squared)


def _point_in_circumcircle(point, circumcircle):
    """Verifie si un point est dans le cercle circonscrit.

    Args:
        point: Tuple (x, y).
        circumcircle: Tuple (cx, cy, r_squared).

    Returns:
        bool: True si le point est dans le cercle.
    """
    cx, cy, r_squared = circumcircle
    px, py = point
    dist_squared = (px - cx) ** 2 + (py - cy) ** 2
    return dist_squared < r_squared


def _get_super_triangle(points):
    """Cree un super-triangle qui contient tous les points.

    Args:
        points: Liste de tuples (x, y).

    Returns:
        tuple: 3 tuples (x, y) formant le super-triangle.
    """
    min_x = min(p[0] for p in points)
    max_x = max(p[0] for p in points)
    min_y = min(p[1] for p in points)
    max_y = max(p[1] for p in points)

    dx = max_x - min_x
    dy = max_y - min_y
    delta = max(dx, dy, 1.0)

    mid_x = (min_x + max_x) / 2
    mid_y = (min_y + max_y) / 2

    p1 = (mid_x - 20 * delta, mid_y - delta)
    p2 = (mid_x, mid_y + 20 * delta)
    p3 = (mid_x + 20 * delta, mid_y - delta)

    return (p1, p2, p3)


def _are_collinear(points):
    """Verifie si tous les points sont alignes.

    Args:
        points: Liste de tuples (x, y).

    Returns:
        bool: True si tous les points sont alignes.
    """
    if len(points) < 3:
        return True

    x0, y0 = points[0]
    x1, y1 = points[1]

    for i in range(2, len(points)):
        x2, y2 = points[i]
        cross = (x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)
        if abs(cross) > 1e-10:
            return False

    return True


def triangulate(points):
    """Calcule la triangulation de Delaunay d'un ensemble de points 2D.

    Utilise l'algorithme de Bowyer-Watson.

    Args:
        points: Liste de tuples (x, y) representant les points.

    Returns:
        list: Liste de tuples (i1, i2, i3) representant les triangles
              par indices de sommets.

    Raises:
        ValueError: Si moins de 3 points ou si les points sont alignes.
    """
    if len(points) < 3:
        raise ValueError("Au moins 3 points sont requis")

    unique_points = list(set(points))
    if len(unique_points) < 3:
        raise ValueError("Au moins 3 points distincts sont requis")

    if _are_collinear(unique_points):
        raise ValueError("Les points sont alignes")

    {p: i for i, p in enumerate(points)}

    super_tri = _get_super_triangle(points)
    sp1, sp2, sp3 = super_tri

    all_points = list(points) + [sp1, sp2, sp3]
    n = len(points)

    triangles = [(n, n + 1, n + 2)]

    for i, point in enumerate(points):
        bad_triangles = []

        for tri in triangles:
            p1 = all_points[tri[0]]
            p2 = all_points[tri[1]]
            p3 = all_points[tri[2]]

            cc = _circumcircle(p1, p2, p3)
            if cc is not None and _point_in_circumcircle(point, cc):
                bad_triangles.append(tri)

        polygon = []
        for tri in bad_triangles:
            edges = [
                (tri[0], tri[1]),
                (tri[1], tri[2]),
                (tri[2], tri[0])
            ]
            for edge in edges:
                edge_reversed = (edge[1], edge[0])
                shared = False
                for other_tri in bad_triangles:
                    if other_tri == tri:
                        continue
                    other_edges = [
                        (other_tri[0], other_tri[1]),
                        (other_tri[1], other_tri[2]),
                        (other_tri[2], other_tri[0])
                    ]
                    if edge in other_edges or edge_reversed in other_edges:
                        shared = True
                        break
                if not shared:
                    polygon.append(edge)

        for tri in bad_triangles:
            triangles.remove(tri)

        for edge in polygon:
            new_tri = (edge[0], edge[1], i)
            triangles.append(new_tri)

    final_triangles = []
    for tri in triangles:
        if tri[0] < n and tri[1] < n and tri[2] < n:
            final_triangles.append(tri)

    return final_triangles
