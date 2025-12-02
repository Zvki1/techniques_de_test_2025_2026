"""Client pour communiquer avec le PointSetManager."""


def get_pointset(pointset_id, manager_url="http://localhost:5000"):
    """
    Récupère un PointSet depuis le PointSetManager.
    
    Args:
        pointset_id: UUID du PointSet à récupérer.
        manager_url: URL du PointSetManager.
        
    Returns:
        bytes: Données binaires du PointSet.
        
    Raises:
        ValueError: Si l'UUID est invalide.
        ConnectionError: Si le PointSetManager est inaccessible.
        FileNotFoundError: Si le PointSet n'existe pas (404).
    """
    raise NotImplementedError("À implémenter")