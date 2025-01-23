import pdfplumber
import pandas as pd
import os

def is_additional_header(row):
    """Vérifie si la première ligne est un en-tête supplémentaire."""
    non_empty_cells = sum(1 for cell in row if cell and cell.strip())
    return non_empty_cells <= 3

def process_pdf(pdf_file):
    """Extrait les tableaux d'un fichier PDF et les sauvegarde au format CSV."""
    pdf_name_cleaned = '_'.join(pdf_file.split("_")[2:]).split(".")[0]

    # Liste pour stocker les DataFrames de chaque tableau avec leur en-tête
    dataframes = []
    last_header = ""
    last_columns = []

    # Ouvrir le PDF avec pdfplumber
    with pdfplumber.open(pdf_file) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            print(f"Traitement de la page {i} de {pdf_file}...")
            tables = page.extract_tables()
            if not tables:
                continue
            for table in tables:
                if not table:  # Vérifie que le tableau n'est pas vide
                    continue
                header = ""
                if is_additional_header(table[0]):  # Vérifie si la première ligne est un en-tête supplémentaire
                    print(f"En-tête supplémentaire détecté dans le tableau de la page {i}.")
                    header_length = max((len(cell) for cell in table[0] if cell), default=0)
                    header = [cell for cell in table[0] if cell and len(cell) == header_length]
                    if header == last_header:
                        table = table[1:]  # Supprime l'en-tête supplémentaire
                        df = pd.DataFrame(table[1:], columns=table[0])
                        # Concaténer avec le dernier DataFrame de la liste
                        last_table, last_header = dataframes[-1]
                        concat_df = pd.concat([last_table, df], ignore_index=True)
                        dataframes.pop()
                        dataframes.append([concat_df, header])
                        continue  # Passer au tableau suivant
                    last_header = header
                    table = table[1:]  # Supprime l'en-tête supplémentaire

                if table:
                    df = pd.DataFrame(table[1:], columns=table[0])  # Première ligne comme en-têtes
                    columns = df.columns.tolist()
                    if columns == last_columns and header == "":
                        last_table, last_header = dataframes[-1]
                        concat_df = pd.concat([last_table, df], ignore_index=True)
                        dataframes.pop()
                        dataframes.append([concat_df, header])
                        continue  # Passer au tableau suivant
                    last_columns = columns
                    dataframes.append([df, header])

    # Filtrer les DataFrames ayant moins de 3 lignes
    dataframes = [(df, header) for df, header in dataframes if len(df) >= 3]

    # Sauvegarder les DataFrames extraits en fichiers CSV
    if dataframes:
        for idx, (df, header) in enumerate(dataframes, start=1):
            if header:
                header = '_'.join(header[0].replace(' ', '_').split('_')[:5])
                csv_filename = f"{pdf_name_cleaned}_{header}.csv"
            else:
                csv_filename = f"{pdf_name_cleaned}_{idx}.csv"

            csv_path = os.path.join('Datas', csv_filename)
            df.to_csv(csv_path, index=False)
            print(f"Tableau {idx} sauvegardé dans : {csv_filename}")
    else:
        print(f"Aucun tableau valide trouvé dans {pdf_file}.")

def process_directory(directory):
    """Traite tous les fichiers PDF dans un répertoire donné."""
    for file in os.listdir(directory):
        if file.endswith(".pdf"):
            process_pdf(os.path.join(directory, file))

# Exemple d'utilisation
if __name__ == "__main__":
    pdf_directory = "./test_ocr"  # Remplacez par le chemin de votre répertoire PDF
    process_directory(pdf_directory)
