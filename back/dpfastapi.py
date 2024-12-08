from flask import Flask, request, jsonify, abort
import sqlite3
import pathlib
import jwt
from functools import wraps

app = Flask(__name__)
SECRET_KEY = "votre_clé_secrète"  # Même clé que dans auth.py

def get_connection():
    conn = sqlite3.connect(pathlib.Path(__file__).parent.absolute()/"bdd"/"database.db")
    conn.row_factory = sqlite3.Row
    return conn

def token_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", None)
        if not auth_header:
            abort(401, "Token manquant.")
        parts = auth_header.split()
        if parts[0].lower() != "bearer" or len(parts) != 2:
            abort(401, "Format Authorization invalide.")
        token = parts[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id")
            if user_id is None:
                abort(401, "Token invalide.")
        except jwt.ExpiredSignatureError:
            abort(401, "Token expiré.")
        except jwt.InvalidTokenError:
            abort(401, "Token invalide.")
        return f(*args, **kwargs)
    return wrapper

@app.route("/")
def index():
    return jsonify({"message": "API principale en ligne. /utilisateurs, /auteurs, /livres"})

### Utilisateurs ###

@app.route("/utilisateurs", methods=["GET"])
def get_utilisateurs():
    conn = get_connection()
    cur = conn.cursor()
    utilisateurs = cur.execute("SELECT id, nom FROM utilisateurs").fetchall()
    conn.close()
    return jsonify([dict(u) for u in utilisateurs])

@app.route("/utilisateur/ajouter", methods=["POST"])
def add_utilisateur():
    nom = request.form.get('nom')
    if not nom:
        abort(400, "Le nom est requis.")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO utilisateurs (nom) VALUES (?)", (nom,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Utilisateur ajouté avec succès"}), 201

@app.route("/utilisateur/<int:utilisateur_id>/supprimer", methods=["DELETE"])
def delete_utilisateur(utilisateur_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM utilisateurs WHERE id = ?", (utilisateur_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Utilisateur supprimé avec succès"})

@app.route("/utilisateur/recherche")
def rechercher_utilisateur():
    query = request.args.get("query", "")
    conn = get_connection()
    cur = conn.cursor()
    utilisateurs = cur.execute("SELECT id, username, nom FROM utilisateurs WHERE nom LIKE ?", ('%' + query + '%',)).fetchall()
    conn.close()
    return jsonify([dict(u) for u in utilisateurs])

### Auteurs ###

@app.route("/auteurs", methods=["GET"])
def get_auteurs():
    conn = get_connection()
    cur = conn.cursor()
    auteurs = cur.execute("SELECT * FROM auteurs").fetchall()
    conn.close()
    return jsonify([dict(a) for a in auteurs])

@app.route("/auteur/ajouter", methods=["POST"])
def add_auteur():
    nom_auteur = request.form.get('nom_auteur')
    if not nom_auteur:
        abort(400, "Le nom de l'auteur est requis.")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO auteurs (nom_auteur) VALUES (?)", (nom_auteur,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Auteur ajouté avec succès"}), 201

@app.route("/auteur/<int:auteur_id>/supprimer", methods=["DELETE"])
def delete_auteur(auteur_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM auteurs WHERE id = ?", (auteur_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Auteur supprimé avec succès"})

@app.route("/auteur/recherche")
def rechercher_auteur():
    query = request.args.get("query", "")
    conn = get_connection()
    cur = conn.cursor()
    auteurs = cur.execute("SELECT * FROM auteurs WHERE nom_auteur LIKE ?", ('%' + query + '%',)).fetchall()
    conn.close()
    return jsonify([dict(a) for a in auteurs])

### Livres ###

@app.route("/livres", methods=["GET"])
def get_livres():
    conn = get_connection()
    cur = conn.cursor()
    livres = cur.execute("SELECT * FROM livres").fetchall()
    conn.close()
    return jsonify([dict(l) for l in livres])

@app.route("/livre/ajouter", methods=["POST"])
def add_livre():
    titre = request.form.get("titre")
    pitch = request.form.get("pitch")
    date_public = request.form.get("date_public")
    auteur_id = request.form.get("auteur_id")
    if not (titre and pitch and date_public and auteur_id):
        abort(400, "Tous les champs sont requis.")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO livres (titre, pitch, date_public, auteur_id) VALUES (?,?,?,?)",
                (titre, pitch, date_public, auteur_id))
    conn.commit()
    conn.close()
    return jsonify({"message": "Livre ajouté avec succès"}), 201

@app.route("/livre/<int:livre_id>/supprimer", methods=["DELETE"])
def delete_livre(livre_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM livres WHERE id = ?", (livre_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Livre supprimé avec succès"})

@app.route("/livre/recherche")
def rechercher_livre():
    query = request.args.get("query", "")
    conn = get_connection()
    cur = conn.cursor()
    livres = cur.execute("SELECT * FROM livres WHERE titre LIKE ?", ('%' + query + '%',)).fetchall()
    conn.close()
    return jsonify([dict(l) for l in livres])

if __name__ == '__main__':
    app.run(port=5006, host="0.0.0.0", debug=True)
