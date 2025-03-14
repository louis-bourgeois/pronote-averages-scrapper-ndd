import re
import time
from typing import Dict, Optional, Tuple

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def parse_full_name(raw_text: str) -> str:
    """
    Extrait et reformate le nom complet de l'élève à partir du texte brut.
    Par exemple, transforme :
      "Espace Élèves - BOURGEOIS Louis (1RE3)" en "Louis BOURGEOIS".
    """
    prefix: str = "Espace Élèves - "
    if raw_text.startswith(prefix):
        raw_text = raw_text[len(prefix):]
    # Supprime le texte entre parenthèses (généralement l'identifiant de classe)
    raw_text = re.sub(r"\s*\(.*\)$", "", raw_text).strip()
    parts = raw_text.split()
    if len(parts) >= 2:
        return " ".join(parts[1:] + [parts[0]])
    return raw_text


def get_weighted_averages(pronote_username: str, pronote_password: str) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[str]]:
    """
    Se connecte au portail Pronote, navigue vers la page "Mes notes" en mode "Par matière",
    extrait le nom complet et récupère les notes afin de calculer :
      - La moyenne globale pondérée.
      - La moyenne du tronc commun (pour les matières dont le coefficient n'est pas 15).
      - La moyenne des spécialités (pour les matières dont le coefficient est 15).

    Si aucune note n'est trouvée, la fonction réessaye plusieurs fois (avec un délai) avant d'abandonner.

    Parameters:
        pronote_username (str): Identifiant Pronote.
        pronote_password (str): Mot de passe Pronote.

    Returns:
        Tuple[Optional[float], Optional[float], Optional[float], Optional[str]]:
            overall_average: Moyenne globale pondérée.
            tronc_commun_average: Moyenne pondérée du tronc commun.
            specialties_average: Moyenne pondérée des matières avec coefficient 15.
            full_name: Nom complet de l'élève.
    """
    chrome_options: Options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.binary_location = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    service: Service = Service(ChromeDriverManager().install())
    driver: webdriver.Chrome = webdriver.Chrome(
        service=service, options=chrome_options)
    wait: WebDriverWait = WebDriverWait(driver, 20)

    overall_average: Optional[float] = None
    tronc_commun_average: Optional[float] = None
    specialties_average: Optional[float] = None
    full_name: Optional[str] = None

    def extract_grades() -> Dict[str, float]:
        page_source: str = driver.page_source
        soup: BeautifulSoup = BeautifulSoup(page_source, "html.parser")
        grade_blocks = soup.find_all("div", class_="zone-contenu-format")
        local_grades: Dict[str, float] = {}
        for block in grade_blocks:
            subject_elem = block.find("div", class_="zone-principale")
            if subject_elem:
                subject_span = subject_elem.find(
                    "span", class_="ie-titre-gros")
                if subject_span:

                    subject: str = subject_span.get_text(strip=True).upper()
                    note_val: Optional[float] = None
                    note_elem = block.find("div", class_="zone-complementaire")
                    if note_elem:
                        aria_label: Optional[str] = note_elem.get("aria-label")
                        if aria_label and "Moyenne élève" in aria_label:
                            try:
                                note_str: str = aria_label.split(
                                    ":")[1].strip().replace(",", ".")
                                note_val = float(note_str)
                            except Exception as e:
                                print(f"Erreur lors de la conversion pour {
                                      subject}: {e}")
                        if note_val is None:
                            note_div = note_elem.find(
                                "div", class_="ie-titre-gros")
                            if note_div:
                                try:
                                    note_val = float(note_div.get_text(
                                        strip=True).replace(",", "."))
                                except Exception as e:
                                    print(f"Erreur lors de la conversion pour {
                                          subject}: {e}")
                    if note_val is not None:
                        local_grades[subject] = note_val
        return local_grades

    try:
        driver.get("https://0593102b.index-education.net/pronote/eleve.html")
        wait.until(EC.visibility_of_element_located((By.ID, "id_29")))

        driver.find_element(By.ID, "id_29").send_keys(pronote_username)
        driver.find_element(By.ID, "id_30").send_keys(pronote_password)
        # Clique sur le bouton de connexion
        driver.find_element(By.ID, "id_18").click()

        # Vérification rapide du popup d'erreur en cas de mauvais identifiants
        try:
            WebDriverWait(driver, 0.1).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[2]/div[2]/div/div"))
            )
            print("Erreur: Identifiants incorrects détectés (popup présent).")
            raise Exception("Identifiants incorrects")
        except TimeoutException:
            # Si le popup n'est pas apparu dans les 3 secondes, on considère que la connexion est réussie
            print("Connexion réussie, page d'accueil chargée.")

        # Extraction du nom complet
        try:
            user_elem = wait.until(EC.visibility_of_element_located(
                (By.XPATH,
                 "/html/body/div[4]/div/div[1]/div/div[1]/div/div[2]/div[2]/div[2]/div[1]")
            ))
            raw_user: str = user_elem.text.strip()
            full_name = parse_full_name(raw_user)
            print("Nom complet récupéré :", full_name)
        except Exception as e:
            print("Erreur lors de la récupération du nom :", e)

        # Navigation vers "Mes notes"
        notes_menu = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//div[contains(@class, 'label-menu_niveau0') and contains(text(),'Notes')]")
        ))
        notes_menu.click()

        mes_notes = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//li[@aria-label='Détail de mes notes']")
        ))
        driver.execute_script("arguments[0].scrollIntoView(true);", mes_notes)
        driver.execute_script("arguments[0].click();", mes_notes)
        print("Clic sur 'Mes notes' effectué.")
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[4]/div/div[1]/div/div[5]/div[2]/label[2]/input")))
        time.sleep(0.5)
        # Sélection du mode "Par matière"
        par_matiere_span = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "/html/body/div[4]/div/div[1]/div/div[5]/div[2]/label[2]/span[2]")
        ))
        driver.execute_script(
            "arguments[0].scrollIntoView(true);", par_matiere_span)
        driver.execute_script("arguments[0].click();", par_matiere_span)
        print("Mode 'Par matière' sélectionné.")
        wait.until(EC.presence_of_element_located(
            (By.CLASS_NAME, "zone-contenu-format")))

        # Extraction des notes avec tentative de réessai
        grades: Dict[str, float] = extract_grades()
        retry_count = 0
        while len(grades) == 0 and retry_count < 2:
            print("Aucune note trouvée, réessai dans 3 secondes...")
            time.sleep(3)
            driver.refresh()
            # On attend que la page se recharge et que l'élément contenant les notes soit présent
            wait.until(EC.presence_of_element_located(
                (By.CLASS_NAME, "zone-contenu-format")))
            grades = extract_grades()
            retry_count += 1

        print("Notes extraites:", grades)

        # Définition des coefficients pour le calcul des moyennes.
        coefficients: Dict[str, int] = {
            "MATHEMATIQUES": 15,
            "PHYSIQUE-CHIMIE": 15,
            "NUMERIQUE ET SCIENCES INFORMATIQUES": 15,
            "ENSEIGN.SCIENTIFIQUE > ENS.SCIENT.SVT": 3,
            "ENSEIGN.SCIENTIFIQUE > ENS. SCIENT. PHYSIQUE": 3,
            "FRANCAIS": 10,
            "EPS": 6,
            "ANGLAIS LV1": 6,
            "ESPAGNOL LV2": 6,
            "HISTOIRE-GEOGRAPHIE": 6,
            "ENSEIGNEMENT MORAL ET CIVIQUE": 2
        }

        # Calcul des moyennes pondérées
        total_coef_all: int = 0
        total_points_all: float = 0.0
        total_coef_tronc: int = 0
        total_points_tronc: float = 0.0
        total_coef_spec: int = 0
        total_points_spec: float = 0.0

        for subject, note in grades.items():
            coef: Optional[int] = coefficients.get(subject)
            if coef is not None:
                total_coef_all += coef
                total_points_all += note * coef
                if coef == 15:
                    total_coef_spec += coef
                    total_points_spec += note * coef
                else:
                    total_coef_tronc += coef
                    total_points_tronc += note * coef
            else:
                print(f"Aucun coefficient défini pour: {subject}")

        if total_coef_all > 0:
            overall_average = total_points_all / total_coef_all
        if total_coef_tronc > 0:
            tronc_commun_average = total_points_tronc / total_coef_tronc
        if total_coef_spec > 0:
            specialties_average = total_points_spec / total_coef_spec

    except Exception as e:
        print("Erreur dans le scraper:", e)
    finally:
        driver.quit()

    return overall_average, tronc_commun_average, specialties_average, full_name


if __name__ == "__main__":
    print("Ce script doit être appelé via l'application (ex: Flask) avec des identifiants.")
