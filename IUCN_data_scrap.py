import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Créer un dossier "Datas" dans le répertoire actuel
script_dir = os.path.dirname(os.path.abspath(__file__))
download_dir = os.path.join(script_dir, "Datas")
os.makedirs(download_dir, exist_ok=True)

# Configurer le WebDriver pour télécharger dans le dossier "Datas"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
prefs = {
    "download.default_directory": download_dir,  # Dossier de téléchargement
    "download.prompt_for_download": False,  # Ne pas demander confirmation
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True,
}
chrome_options.add_experimental_option("prefs", prefs)

# Lancer le WebDriver avec les options configurées
driver = webdriver.Chrome(options=chrome_options)

try:
    # URL de base
    base_url = 'https://www.iucnredlist.org/statistics'
    driver.get(base_url)

    wait = WebDriverWait(driver, 10)

    # Étape 1 : Télécharger le premier fichier CSV de la table principale
    first_csv_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 
        "button.dt-button.buttons-csv.buttons-html5")))
    first_csv_button.click()
    print("Premier fichier CSV téléchargé.")
    time.sleep(1)  # Attendre pour s'assurer que le fichier est téléchargé

    # Étape 2 : Récupérer toutes les sections pliées (h3)
    section_titles = driver.find_elements(By.CSS_SELECTOR, "h3.filter__section__title")
    print(f"Nombre total de sections trouvées : {len(section_titles)}")

    # Supprimer la première section qui est déjà déroulée
    section_titles = section_titles[1:]
    print(f"Nombre de sections à traiter (après suppression de la première) : {len(section_titles)}")

    # Étape 3 : Parcourir les sections restantes
    for index, title in enumerate(section_titles, start=1):
        # Dérouler la section actuelle
        driver.execute_script("arguments[0].scrollIntoView(true);", title)  # S'assurer que l'élément est visible
        title.click()  # Cliquer pour dérouler la section
        print(f"Section {index} déroulée.")

        # Trouver et cliquer sur le bouton "SHOW ALL" de la section déroulée
        show_all_links = driver.find_elements(By.XPATH, "//a[@class='nav-aside__item' and text()='SHOW ALL']")
        if len(show_all_links) > index - 1:  # Vérifier que le bouton "SHOW ALL" existe pour cette section
            show_all_links[index - 1].click()
            print(f"'SHOW ALL' {index} cliqué.")

            # Télécharger le fichier CSV correspondant
            csv_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 
                "button.dt-button.buttons-csv.buttons-html5")))
            csv_button.click()
            print(f"Fichier CSV {index} téléchargé.")
            time.sleep(1)  # Attendre pour s'assurer que le fichier est téléchargé

finally:
    # Fermer le WebDriver
    driver.quit()
    print(f"Script terminé. Les fichiers sont enregistrés dans : {download_dir}")
