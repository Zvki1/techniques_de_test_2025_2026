"""Application Flask pour le service Triangulator."""

from flask import Flask, jsonify, make_response

app = Flask(__name__)


@app.route("/triangulation/<pointset_id>", methods=["GET"])
def get_triangulation(pointset_id):
    """
    Calcule la triangulation pour un PointSet donné.
    
    Args:
        pointset_id: UUID du PointSet à trianguler.
        
    Returns:
        Response: Données binaires des triangles ou erreur JSON.
    """
    # TODO: Implémenter
    return jsonify({"code": "NOT_IMPLEMENTED", "message": "À implémenter"}), 500


@app.errorhandler(404)
def not_found(error):
    """Gère les erreurs 404."""
    return jsonify({"code": "NOT_FOUND", "message": "Route non trouvée"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Gère les erreurs 405."""
    return jsonify({"code": "METHOD_NOT_ALLOWED", "message": "Méthode non autorisée"}), 405


if __name__ == "__main__":
    app.run(debug=True)