from flask import Flask, request, jsonify, abort
import sqlite3
import pathlib
import jwt
import datetime
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

SECRET_KEY = "votre_clé_secrète"

def get_connection():
    conn = sqlite3.connect(pathlib.Path(__file__).parent.absolute() / "bdd" / "database.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

@app.route("/")
def index():
    return jsonify({"message": "API d'auth en ligne. /login /register /protected"})

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        abort(400, "username et password sont requis.")

    conn = get_connection()
    cur = conn.cursor()
    existing = cur.execute("SELECT id FROM utilisateurs WHERE username = ?", (username,)).fetchone()
    if existing:
        abort(409, "Cet utilisateur existe déjà.")

    hash_pw = generate_password_hash(password)
    cur.execute("INSERT INTO utilisateurs (username, password_hash) VALUES (?, ?)", (username, hash_pw))
    conn.connection.commit()
    conn.close()
    return jsonify({"message": "Utilisateur créé avec succès"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        abort(400, "username et password requis.")
    username = data["username"]
    password = data["password"]

    conn = get_connection()
    cur = conn.cursor()
    user = cur.execute("SELECT id, password_hash FROM utilisateurs WHERE username = ?", (username,)).fetchone()
    conn.close()

    if not user:
        abort(401, "Identifiants invalides.")
    if not check_password_hash(user["password_hash"], password):
        abort(401, "Identifiants invalides.")

    token = create_token(user["id"])
    return jsonify({"message": "Authentification réussie", "token": token})

if __name__ == '__main__':
    app.run(port=5007, host="0.0.0.0", debug=True)