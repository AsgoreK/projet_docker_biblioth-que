from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests
import os

app = Flask(__name__)
app.secret_key = "front_secret_key"

API_URL = os.environ.get("API_URL", "http://api:5006")
AUTH_URL = os.environ.get("AUTH_URL", "http://auth:5007")

@app.route("/")
def index():
    return render_template("index.html.j2")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        r = requests.post(f"{AUTH_URL}/login", json={"username": username, "password": password})
        if r.status_code == 200:
            data = r.json()
            token = data.get("token")
            if token:
                session["token"] = token
                flash("Connexion réussie.", "success")
                return redirect(url_for("index"))
            else:
                flash("Erreur lors de la récupération du token.", "danger")
        else:
            flash("Identifiants invalides.", "danger")
    return render_template("login.html.j2")

def get_headers():
    headers = {}
    token = session.get("token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

# cette fonctionnalité ne fonctionne pas, j'ai beaucoup de mal à l'intégrer 

### Utilisateurs

@app.route("/utilisateurs")
def utilisateurs():
    r = requests.get(f"{API_URL}/utilisateurs")
    if r.status_code == 200:
        data = r.json()
        return render_template("tableau.html.j2", name="utilisateurs", data=data, entity="utilisateur")
    flash("Impossible de récupérer les utilisateurs.", "danger")
    return redirect(url_for("index"))

@app.route("/utilisateur/ajouter", methods=["GET", "POST"])
def ajouter_utilisateur():
    if request.method == "POST":
        nom = request.form.get("nom")
        r = requests.post(f"{API_URL}/utilisateur/ajouter", data={"nom": nom}, headers=get_headers())
        if r.status_code == 201:
            flash("Utilisateur ajouté avec succès.", "success")
        else:
            flash("Erreur lors de l'ajout de l'utilisateur (connectez-vous?).", "danger")
        return redirect(url_for("utilisateurs"))
    return render_template("form_utilisateur.html.j2")

@app.route("/utilisateur/supprimer/<int:id>")
def supprimer_utilisateur(id):
    r = requests.delete(f"{API_URL}/utilisateur/{id}/supprimer", headers=get_headers())
    if r.status_code == 200:
        flash("Utilisateur supprimé avec succès.", "success")
    else:
        flash("Erreur lors de la suppression de l'utilisateur (connectez-vous?).", "danger")
    return redirect(url_for("utilisateurs"))

@app.route("/utilisateur/recherche", methods=["GET"])
def rechercher_utilisateur():
    query = request.args.get("query", "")
    if query:
        r = requests.get(f"{API_URL}/utilisateur/recherche", params={"query": query})
        if r.status_code == 200:
            data = r.json()
            return render_template("tableau.html.j2", name="utilisateurs (résultats)", data=data, entity="utilisateur")
    flash("Aucun résultat ou requête vide.", "info")
    return redirect(url_for("utilisateurs"))

### Auteurs

@app.route("/auteurs")
def auteurs():
    r = requests.get(f"{API_URL}/auteurs")
    if r.status_code == 200:
        data = r.json()
        return render_template("tableau.html.j2", name="auteurs", data=data, entity="auteur")
    flash("Impossible de récupérer les auteurs.", "danger")
    return redirect(url_for("index"))

@app.route("/auteur/ajouter", methods=["GET", "POST"])
def ajouter_auteur():
    if request.method == "POST":
        nom_auteur = request.form.get("nom_auteur")
        r = requests.post(f"{API_URL}/auteur/ajouter", data={"nom_auteur": nom_auteur}, headers=get_headers())
        if r.status_code == 201:
            flash("Auteur ajouté avec succès.", "success")
        else:
            flash("Erreur lors de l'ajout de l'auteur (connectez-vous?).", "danger")
        return redirect(url_for("auteurs"))
    return render_template("form_auteur.html.j2")

@app.route("/auteur/supprimer/<int:id>")
def supprimer_auteur(id):
    r = requests.delete(f"{API_URL}/auteur/{id}/supprimer", headers=get_headers())
    if r.status_code == 200:
        flash("Auteur supprimé avec succès.", "success")
    else:
        flash("Erreur lors de la suppression de l'auteur (connectez-vous?).", "danger")
    return redirect(url_for("auteurs"))

@app.route("/auteur/recherche", methods=["GET"])
def rechercher_auteur():
    query = request.args.get("query", "")
    if query:
        r = requests.get(f"{API_URL}/auteur/recherche", params={"query": query})
        if r.status_code == 200:
            data = r.json()
            return render_template("tableau.html.j2", name="auteurs (résultats)", data=data, entity="auteur")
    flash("Aucun résultat ou requête vide.", "info")
    return redirect(url_for("auteurs"))

### Livres

@app.route("/livres")
def livres():
    r = requests.get(f"{API_URL}/livres")
    if r.status_code == 200:
        data = r.json()
        return render_template("tableau.html.j2", name="livres", data=data, entity="livre")
    flash("Impossible de récupérer les livres.", "danger")
    return redirect(url_for("index"))

@app.route("/livre/ajouter", methods=["GET", "POST"])
def ajouter_livre():
    if request.method == "POST":
        titre = request.form.get("titre")
        pitch = request.form.get("pitch")
        date_public = request.form.get("date_public")
        auteur_id = request.form.get("auteur_id")
        r = requests.post(f"{API_URL}/livre/ajouter", data={
            "titre": titre,
            "pitch": pitch,
            "date_public": date_public,
            "auteur_id": auteur_id
        }, headers=get_headers())
        if r.status_code == 201:
            flash("Livre ajouté avec succès.", "success")
        else:
            flash("Erreur lors de l'ajout du livre (connectez-vous?).", "danger")
        return redirect(url_for("livres"))
    return render_template("form_livre.html.j2")

@app.route("/livre/supprimer/<int:id>")
def supprimer_livre(id):
    r = requests.delete(f"{API_URL}/livre/{id}/supprimer", headers=get_headers())
    if r.status_code == 200:
        flash("Livre supprimé avec succès.", "success")
    else:
        flash("Erreur lors de la suppression du livre (connectez-vous?).", "danger")
    return redirect(url_for("livres"))

@app.route("/livre/recherche", methods=["GET"])
def rechercher_livre():
    query = request.args.get("query", "")
    if query:
        r = requests.get(f"{API_URL}/livre/recherche", params={"query": query})
        if r.status_code == 200:
            data = r.json()
            return render_template("tableau.html.j2", name="livres (résultats)", data=data, entity="livre")
    flash("Aucun résultat ou requête vide.", "info")
    return redirect(url_for("livres"))

if __name__ == '__main__':
    app.run(port=5001, host="0.0.0.0", debug=True)