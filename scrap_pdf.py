import os
import requests
from bs4 import BeautifulSoup

# URL de la page contenant les fichiers PDF
url = "https://www.iucnredlist.org/resources/summary-statistics#Summary%20Tables"

# Crée un dossier pour enregistrer les fichiers PDF
output_folder = "iucn_pdfs"
os.makedirs(output_folder, exist_ok=True)

# Récupère le contenu HTML de la page
response = requests.get(url)
if response.status_code != 200:
    print(f"Erreur lors de l'accès à l'URL : {response.status_code}")
    exit()

# Parse le contenu HTML avec BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Trouve tous les liens PDF
pdf_links = soup.find_all('a', href=lambda href: href and href.endswith('.pdf'))

if not pdf_links:
    print("Aucun lien PDF trouvé.")
    exit()

# Télécharge chaque fichier PDF
for link in pdf_links:
    pdf_url = link['href']
    if not pdf_url.startswith('http'):
        # Complète l'URL relative si nécessaire
        pdf_url = f"https://www.iucnredlist.org{pdf_url}"
    
    pdf_name = pdf_url.split("/")[-1]
    pdf_path = os.path.join(output_folder, pdf_name)
    
    print(f"Téléchargement de {pdf_name} depuis {pdf_url}...")
    pdf_response = requests.get(pdf_url)
    
    if pdf_response.status_code == 200:
        with open(pdf_path, 'wb') as pdf_file:
            pdf_file.write(pdf_response.content)
        print(f"Enregistré sous {pdf_path}")
    else:
        print(f"Erreur lors du téléchargement de {pdf_name}")

print("Téléchargement terminé.")
