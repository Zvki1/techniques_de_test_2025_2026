"""Client pour communiquer avec le PointSetManager."""

import re
import urllib.error
import urllib.request


UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE
)


def _validate_uuid(pointset_id):
    """Valide le format d'un UUID.

    Args:
        pointset_id: Chaine a valider.

    Raises:
        ValueError: Si le format est invalide.
    """
    if not pointset_id or not isinstance(pointset_id, str):
        raise ValueError("UUID invalide: valeur vide ou non-string")

    if not UUID_PATTERN.match(pointset_id):
        raise ValueError(f"UUID invalide: {pointset_id}")


def get_pointset(pointset_id, manager_url="http://localhost:5000"):
    """Recupere un PointSet depuis le PointSetManager.

    Args:
        pointset_id: UUID du PointSet a recuperer.
        manager_url: URL du PointSetManager.

    Returns:
        bytes: Donnees binaires du PointSet.

    Raises:
        ValueError: Si l'UUID est invalide.
        ConnectionError: Si le PointSetManager est inaccessible.
        FileNotFoundError: Si le PointSet n'existe pas (404).
        RuntimeError: Pour les autres erreurs serveur.
    """
    _validate_uuid(pointset_id)

    url = f"{manager_url}/pointset/{pointset_id}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            raise FileNotFoundError(f"PointSet {pointset_id} non trouve") from e
        if e.code == 400:
            raise ValueError(f"Requete invalide: {pointset_id}") from e
        raise RuntimeError(f"Erreur serveur {e.code}") from e
    except urllib.error.URLError as e:
        raise ConnectionError(f"PointSetManager inaccessible: {e}") from e
    except TimeoutError as e:
        raise ConnectionError(f"Timeout de connexion: {e}") from e
