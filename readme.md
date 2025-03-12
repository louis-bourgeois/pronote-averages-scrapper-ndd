
Readme.md généré par chatGPT
Remarque : l'ensemble des commentaires et certaines parties du code ont été générées entièrement ou avec l'aide d'une intelligence artificielle telle que Claude 3.7 Sonnet ou ChatGPT o3-mini-high.

---

# Pronote Dashboard App

Pronote Dashboard App est une application web Flask qui permet de récupérer et d'afficher en temps réel les moyennes d'un élève depuis le système Pronote. Elle utilise Selenium pour scraper les informations depuis Pronote, BeautifulSoup pour l'extraction des données, et Server-Sent Events (SSE) pour mettre à jour dynamiquement le dashboard. L'interface affiche la moyenne pondérée globale, la moyenne du tronc commun (excluant les spécialités) et la moyenne des spécialités (calculée à partir des matières avec un coefficient de 15).

## Fonctionnalités

- **Mise à jour en temps réel :** La page du dashboard se remplit progressivement avec les informations dès leur disponibilité.
- **Interface moderne et responsive :** Utilisation d’un design modernisé (glassmorphism) et d’animations de chargement pour une meilleure expérience utilisateur.
- **Scraping automatisé :** Connexion à Pronote et extraction des moyennes via Selenium.
- **Sécurité renforcée :** Gestion des sessions via cookies signés (HTTPOnly, Secure, SameSite) pour éviter le stockage d’informations sensibles côté client.

## Technologies Utilisées

- Python 3
- Flask
- Selenium & ChromeDriver (Google Chrome ou Brave)
- BeautifulSoup
- Bootstrap 5 pour l’UI
- (Optionnel) PostgreSQL pour la persistance des utilisateurs

## Installation

1. **Cloner le dépôt :**

   ```bash
   git clone https://github.com/votre_nom_utilisateur/pronote-dashboard-app.git
   cd pronote-dashboard-app
   ```
2. **Créer et activer un environnement virtuel :**

   ```bash
   python -m venv venv
   source venv/bin/activate   # Sur Windows : venv\Scripts\activate
   ```
3. **Installer les dépendances :**

   ```bash
   pip install -r requirements.txt
   ```

   > Assurez-vous d'avoir Google Chrome installé à l'emplacement spécifié dans le code (`C:\Program Files\Google\Chrome\Application\chrome.exe`). Sinon, modifiez `chrome_options.binary_location` en conséquence.
   >

## Configuration

Créez un fichier `config.py` (si non fourni) avec, par exemple :

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'votre_clé_très_strong_a_remplacer')
    # Vous pouvez ajouter d'autres variables de configuration ici, notamment pour la BDD si besoin.


Pour la sécurité, définissez la variable d'environnement `SECRET_KEY` avec une valeur forte en production.

## Utilisation

### Lancer le Scraper et le Dashboard

1. **Démarrer l'application Flask :**

   ```bash
   flask run
```

2. **Accéder au dashboard :**

   Ouvrez votre navigateur et rendez-vous sur [http://127.0.0.1:5000/dashboard](http://127.0.0.1:5000/dashboard)

Le dashboard affichera immédiatement une carte avec des placeholders pour le nom et les moyennes (affichant « ••• ») ainsi qu'une animation de chargement. Les mises à jour se font en temps réel via SSE dès que le scraper récupère les informations depuis Pronote.

## Sécurité

- **Utilisation du mode headless :**En production, activez le mode headless dans Selenium en décommentant `chrome_options.add_argument("--headless")`.
- **Déploiement sécurisé :**
  Utilisez un serveur WSGI (comme Gunicorn ou uWSGI) derrière un reverse proxy (par exemple Nginx) pour la mise en production. Ne pas utiliser le serveur de développement Flask en production.

## Améliorations futures

- **Mise en cache** et optimisation du scraping pour réduire le temps de chargement.
- **Support multi-utilisateur amélioré**
- **Implémentation de la gestion de plusieurs comptes**
- **UI/UX amélioré** avec des notifications et des transitions plus fluides.
- **Gestion avancée des erreurs et gestion des inputs améliorées** côté client et serveur.

## License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.
