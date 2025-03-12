# forms.py
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class LoginForm(FlaskForm):
    pronote_username = StringField(
        'Identifiant Pronote',
        validators=[
            DataRequired(message="Ce champ est requis."),
            Length(
                min=1, max=64, message="La longueur doit être comprise entre 1 et 64 caractères."),
            Regexp(
                r'^\w+$', message="Ce champ doit contenir uniquement des caractères alphanumériques ou underscore.")
        ]
    )
    pronote_password = PasswordField(
        'Mot de passe Pronote',
        validators=[
            DataRequired(message="Ce champ est requis."),
            Length(
                min=6, max=128, message="Le mot de passe doit faire entre 6 et 128 caractères.")
        ]
    )
    submit = SubmitField('Se connecter')
