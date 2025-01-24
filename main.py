
import subprocess

if __name__ == '__main__':
    scripts = ["scrap_pdf.py",
               "IUCN_data_scrap.py",
               "pdf_table_reader.py",
               "csv_cleaner.py",
               "manage_csv.py"]

    for script in scripts:
        try:
            print(f"Exécution de {script}...")
            subprocess.run(["python3", script], check=True)
            print(f"{script} terminé avec succès.\n")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de l'exécution de {script} : {e}")
            break
