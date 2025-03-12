from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   session, url_for)

from config import Config
from forms import LoginForm
from models import User, db
from scraper import get_weighted_averages

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Crée les tables (à n'exécuter qu'une fois ou en mode développement)
with app.app_context():
    db.create_all()


@app.route('/')
def index() -> 'redirect':
    """
    Redirige vers le dashboard si l'utilisateur est connecté, sinon vers la page de connexion.
    """
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login() -> 'HTML':
    form = LoginForm()
    if form.validate_on_submit():
        # Nettoyage et normalisation des inputs
        pronote_username = form.pronote_username.data.strip()
        pronote_password = form.pronote_password.data.strip()

        # On recherche l'utilisateur par son username
        user = User.query.filter_by(pronote_username=pronote_username).first()
        if not user:
            # S'il n'existe pas, on le crée avec les credentials saisis
            user = User(pronote_username=pronote_username,
                        pronote_password=pronote_password)
            db.session.add(user)
            db.session.commit()
        else:
            # Optionnel : on peut mettre à jour le mot de passe avec la nouvelle saisie
            user.pronote_password = pronote_password
            db.session.commit()

        # On connecte l'utilisateur sans vérifier le couple utilisateur/mot de passe
        session['user_id'] = user.id
        flash("Connecté avec succès.", "success")
        return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/dashboard')
def dashboard() -> 'HTML':
    """
    Affiche le dashboard.
    Cette page est accessible uniquement si l'utilisateur est connecté.
    Le dashboard s'affiche immédiatement et les moyennes sont récupérées via un appel AJAX.
    """
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')


@app.route('/get_averages')
def get_averages() -> 'json':
    if 'user_id' not in session:
        return jsonify({"error": "Non connecté"}), 403
    user = User.query.get(session['user_id'])
    overall, tronc, specialties, full_name = get_weighted_averages(
        user.pronote_username, user.pronote_password
    )

    error_message = None
    if overall is None and tronc is None and specialties is None and full_name is None:
        error_message = ("Erreur lors de l'extraction des notes : soit vos identifiants sont erronés, "
                         "soit vous n'avez pas encore de notes pour ce semestre.")

    return jsonify({
        "error": error_message,
        "overall": overall,
        "tronc": tronc,
        "specialties": specialties,
        "full_name": full_name
    })


@app.route('/logout')
def logout() -> 'redirect':
    """
    Déconnecte l'utilisateur en effaçant la session.
    Redirige ensuite vers la page de connexion.
    """
    session.clear()
    flash("Déconnecté.", "info")
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
