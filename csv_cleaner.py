import csv
import glob
import os
import re
import shutil

import pandas as pd


def extract_relevant_tables(*args):
    """
    Extracts relevant CSV filenames that match specific table numbers.

    Args:
        *args: Table numbers to match in filenames.

    Returns:
        list: List of matching CSV filenames.
    """
    pattern = re.compile(r'Table_(' + '|'.join(map(re.escape, args)) +
                         r')(?:_|$)')  # Regex to match desired table numbers
    relevant_files = []

    for filename in os.listdir('.'):
        if filename.endswith('.csv') and pattern.search(filename):
            relevant_files.append(filename)

    print("Matching files:", relevant_files)
    return relevant_files


def suppress_heading_rows(file_path, output_path):
    """
    Removes unnecessary heading rows from a CSV file and saves the cleaned version.

    Args:
        file_path (str): Path to the input CSV file.
        output_path (str): Path to save the cleaned CSV file.
    """
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        rows = list(reader)

    while rows:
        first_row = rows[0]  # Check the first row
        non_empty_cells = [cell.strip() for cell in first_row if cell.strip()]

        if (not non_empty_cells) or (len(non_empty_cells) == 1 and first_row[0].strip()):
            rows.pop(0)  # Remove the row
        else:
            break  # Stop if the row is not suppressible

    with open(output_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)


def transform_table(file_path, output_path):
    """
    Transforms a CSV table by removing duplicate rows and empty rows.

    Args:
        file_path (str): Path to the input CSV file.
        output_path (str): Path to save the transformed CSV file.
    """
    df = pd.read_csv(file_path, header=None)  # Treats all rows as plain data
    df = df.drop_duplicates()
    df = df.dropna(how='all')  # Drops rows where all cells are NaN or empty
    # Exclude header in output
    df.to_csv(output_path, index=False, header=False)
    print(
        f"Data transformed, duplicates and empty rows removed, and saved to '{output_path}'.")


def natural_sort_key(filename):
    # Extract only the last number before .csv
    match = re.match(r'.*_(\d+)\.csv$', filename)
    # Default to 1 if no number is found
    num_part = int(match.group(1)) if match else 1
    return num_part


def group_tables_by_identifier(files):
    grouped_files = {}
    for file in files:
        match = re.match(r'Table_(\d+[a-z]?)', file)
        if match:
            key = match.group(1)
            grouped_files.setdefault(key, []).append(file)

    # Sort each group by the last number before .csv
    for key in grouped_files:
        grouped_files[key] = sorted(grouped_files[key], key=natural_sort_key)

    return grouped_files


def merge_grouped_tables(grouped_files):
    for key, files in grouped_files.items():
        dataframes = [pd.read_csv(f, header=None) for f in files]
        max_cols = max(df.shape[1] for df in dataframes)
        dataframes = [df.reindex(columns=range(max_cols)) for df in dataframes]

        # Delete the original CSV files
        for f in files:
            os.remove(f)
            print(f"Deleted file: {f}")

        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_output = f"Table_{key}_merged.csv"
        combined_df.to_csv(combined_output, index=False,
                           header=False)  # Remove Unnamed columns
        print(
            f"CSV files {files} have been combined and saved as '{combined_output}'.")


def print_grouped_tables(grouped_files):
    for key, files in grouped_files.items():
        print(f"Group {key}: {files}")


def merge_two_line_header(input_file):
    """Lit un CSV, fusionne les deux premières lignes en tant qu'en-tête, et enregistre le résultat."""
    df = pd.read_csv(input_file, header=None)

    if len(df) < 2:
        print(
            f"Le fichier {input_file} a moins de 2 lignes, il ne sera pas traité.")
        return

    # Extraction des deux premières lignes
    header_row1 = df.iloc[0]  # Première ligne
    header_row2 = df.iloc[1]  # Deuxième ligne

    # Création de l'en-tête fusionné
    merged_header = []
    current_group = ""
    for col1, col2 in zip(header_row1, header_row2):
        if pd.notna(col1) and col1.strip():
            current_group = col1.strip()
        if pd.notna(col2) and col2.strip():
            merged_header.append(f"{col2.strip()} ({current_group})")
        else:
            # Conserver vide si pas de valeur en dessous
            merged_header.append("")

    # Mise à jour du DataFrame : suppression des deux premières lignes et affectation du nouvel en-tête
    df = df.iloc[2:].reset_index(drop=True)
    df.columns = merged_header

    # Sauvegarde du fichier modifié
    df.to_csv(input_file, index=False)
    print(f"Header fusionné et sauvegardé sous '{input_file}'.")


def tables_with_2_lines_header(*args):
    """Recherche les fichiers CSV correspondant au modèle donné et respectant la règle du dernier caractère."""
    pattern = re.compile(
        r'Table_(' + '|'.join(map(re.escape, args)) + r')(?:_|$)')  # Modèle regex
    relevant_files = []

    # Liste des fichiers .csv respectant le critère du dernier caractère
    for filename in os.listdir('.'):
        if filename.endswith('.csv') and pattern.search(filename):
            last_char = filename[-5]  # Le dernier caractère avant '.csv'
            if last_char.isalpha() or last_char == '1':
                relevant_files.append(filename)

    print("Fichiers correspondants:", relevant_files)
    return relevant_files


def add_regions(input_file: str):
    """
    Traite un fichier CSV en ajoutant une colonne 'Region' et en supprimant les lignes
    où seule la première colonne est remplie.

    :param input_file: Chemin du fichier CSV d'entrée
    :param output_file: Chemin du fichier CSV de sortie
    """
    df = pd.read_csv(input_file)
    mask = df.iloc[:, 1:].isna().all(axis=1) & df.iloc[:, 0].notna()
    indices_to_remove = df.index[mask]

    df["Region"] = df.iloc[:, 0].where(mask)
    df["Region"] = df["Region"].ffill()

    df = df.drop(indices_to_remove)
    df = df.reset_index(drop=True)

    df.rename(columns={df.columns[0]: "Country"}, inplace=True)
    df.to_csv(input_file, index=False)
    return df


def is_merged_number(cell: str) -> bool:
    """
    Vérifie si une cellule contient des nombres fusionnés avec un espace entre eux.
    """
    return bool(re.search(r'\d+ \d+', cell))


def split_merged_numbers(cell: str) -> tuple:
    """
    Sépare une cellule contenant des nombres fusionnés.
    """
    parts = cell.split()
    return parts[0], parts[1] if len(parts) > 1 else ""


def process_csv(input_file: str):
    """
    Lit un fichier CSV, détecte les cellules fusionnées et ajuste les colonnes.
    """
    with open(input_file, newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        rows = [row for row in reader]

    processed_rows = []
    for row in rows:
        new_row = []
        i = 0
        while i < len(row):
            if is_merged_number(row[i]):
                first_part, second_part = split_merged_numbers(row[i])
                new_row.append(first_part)
                if i + 1 < len(row):
                    row[i + 1] = second_part + " " + row[i + 1]
                else:
                    new_row.append(second_part)
            else:
                new_row.append(row[i])
            i += 1
        processed_rows.append(new_row)

    with open(input_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(processed_rows)


if __name__ == "__main__":
    # Process files for suppressing heading rows
    for file in extract_relevant_tables('7', '8b', '8c', '1b'):
        output_file = f"{file}"
        suppress_heading_rows(file, output_file)
        print(f"Heading rows suppressed and saved to '{output_file}'.")

    # Process files for transformation
    for file in extract_relevant_tables('1b', '8a', '8b', '8c', '8d'):
        output_file = f"{file}"
        transform_table(file, output_file)
        print(f"Processed and saved: {output_file}")

    # Run the grouping and merging process
    files_to_merge = extract_relevant_tables('7', '8b', '8c')
    grouped_files = group_tables_by_identifier(files_to_merge)
    print_grouped_tables(grouped_files)
    merge_grouped_tables(grouped_files)

    # Process files for transformation
    for file in extract_relevant_tables('7', '8b', '8c'):
        output_file = f"{file}"
        transform_table(file, output_file)
        print(f"Processed and saved: {output_file}")

    tables = tables_with_2_lines_header('1b', '8a', '8b', '8c', '8d')
    for table in tables:
        merge_two_line_header(table)

    dataframes = extract_relevant_tables('8a', '8b', '8c')
    for df in dataframes:
        add_regions(df)

    dataframes = extract_relevant_tables('8c')
    for df in dataframes:
        process_csv(df)
    print("Le fichier corrigé a été enregistré")

    ####################################################

    datas_dir = "./Datas"
    os.makedirs(datas_dir, exist_ok=True)
    # Recherche de tous les fichiers .csv dans le dossier courant
    csv_files = glob.glob("*.csv")
    for csv_file in csv_files:
        try:
            shutil.move(csv_file, os.path.join(datas_dir, csv_file))
            print(f"Déplacé : {csv_file} -> {datas_dir}/")
        except Exception as e:
            print(f"Erreur lors du déplacement de {csv_file} : {e}")

    print("Tous les fichiers CSV ont été déplacés.")
