"""Application Flask pour le service Triangulator."""

from flask import Flask, jsonify, make_response

from triangulator.binary_format import decode_pointset, encode_triangles
from triangulator.client import get_pointset
from triangulator.triangulation import triangulate

app = Flask(__name__)


@app.route("/triangulation/<pointset_id>", methods=["GET"])
def get_triangulation(pointset_id):
    """Calcule la triangulation pour un PointSet donne.

    Args:
        pointset_id: UUID du PointSet a trianguler.

    Returns:
        Response: Donnees binaires des triangles ou erreur JSON.
    """
    try:
        pointset_data = get_pointset(pointset_id)
    except ValueError as e:
        return jsonify({
            "code": "INVALID_UUID",
            "message": str(e)
        }), 400
    except FileNotFoundError as e:
        return jsonify({
            "code": "POINTSET_NOT_FOUND",
            "message": str(e)
        }), 404
    except ConnectionError as e:
        return jsonify({
            "code": "SERVICE_UNAVAILABLE",
            "message": f"PointSetManager inaccessible: {e}"
        }), 503

    try:
        points = decode_pointset(pointset_data)
    except ValueError as e:
        return jsonify({
            "code": "INVALID_POINTSET",
            "message": f"Format PointSet invalide: {e}"
        }), 500

    try:
        triangles = triangulate(points)
    except ValueError as e:
        return jsonify({
            "code": "TRIANGULATION_FAILED",
            "message": str(e)
        }), 500

    try:
        result_data = encode_triangles(points, triangles)
    except ValueError as e:
        return jsonify({
            "code": "ENCODING_FAILED",
            "message": str(e)
        }), 500

    response = make_response(result_data)
    response.headers["Content-Type"] = "application/octet-stream"
    return response


@app.errorhandler(404)
def not_found(error):
    """Gere les erreurs 404."""
    return jsonify({"code": "NOT_FOUND", "message": "Route non trouvee"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Gere les erreurs 405."""
    return jsonify({
        "code": "METHOD_NOT_ALLOWED",
        "message": "Methode non autorisee"
    }), 405


if __name__ == "__main__":
    app.run(debug=True)
