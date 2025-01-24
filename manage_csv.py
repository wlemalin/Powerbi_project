import os
import re
import pandas as pd

def load_csv_dataframes(folder_path:str):
    """
    Load all CSV files from the specified folder into DataFrames.

    Parameters:
    folder_path (str): Path to the folder containing the CSV files.

    Returns:
    dict: A dictionary with file names (without extensions) as keys and DataFrames as values.
    """
    dataframes = {}

    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            try:
                df = pd.read_csv(file_path)
                base_name = os.path.splitext(file_name)[0]
                dataframes[base_name] = df
            except Exception as e:
                print(f"Error loading {file_name}: {e}")

    return dataframes

def dataframe_loop_decorator(func):
    """
    Decorator to automatically loop through a dictionary of DataFrames and apply a function.
    """
    def wrapper(dfs:dict, *args, **kwargs):
        results = {}
        for df_name, df in dfs.items():
            print(f"Processing DataFrame: {df_name}")
            result = func(df, df_name, *args, **kwargs)
            if result is not None:
                results[df_name] = result
        return results
    return wrapper

@dataframe_loop_decorator
def select_table(df, df_name:str, by_name=re.compile(r'.*8.*')):
    """
    Select DataFrames whose names match the regex pattern.

    Parameters:
    df (pd.DataFrame): The DataFrame to process.
    df_name (str): The name of the DataFrame.
    by_name (re.Pattern): Regex pattern to match the DataFrame's name.

    Returns:
    pd.DataFrame: The DataFrame if its name matches the regex, otherwise None.
    """
    if re.match(by_name, df_name):
        return df
    else: pass


@dataframe_loop_decorator
def select_column(df:pd.DataFrame, df_name):
    """
    Extract all names within parentheses from the column names of a DataFrame.

    Parameters:
    df (pd.DataFrame): The DataFrame to process.
    df_name (str): The name of the DataFrame (unused in this function).

    Returns:
    set: A set of unique names found within parentheses in the column names.
    """
    pattern = re.compile(r'\(([^)]+)\)')
    
    matches = set()
    for col in df.columns:
        match = pattern.search(col)
        if match:
            matches.add(match.group(1))
    
    return list(matches)


@dataframe_loop_decorator
def add_lc_endemics_column(df:pd.DataFrame, df_name, classe_dict):
    """
    Add a column for non-threatened species (LC endemics) for each class in the list.

    Parameters:
    df (pd.DataFrame): The DataFrame to process.
    classes_name (list): A list of class names (e.g., ['Mammals', 'Birds', 'Reptiles']).

    Returns:
    pd.DataFrame: The DataFrame with added columns for LC endemics.
    """
    classes_name = classe_dict[df_name]

    for cls in classes_name:
        total_col = f"Total endemics ({cls})"
        threatened_col = f"Threatened endemics ({cls})"
        ex_ew_col = f"EX & EW endemics ({cls})"
        lc_col = f"LC endemics ({cls})"

        if all(col in df.columns for col in [total_col, threatened_col, ex_ew_col]):
            df[lc_col] = df[total_col] - (df[threatened_col] + df[ex_ew_col])
        else:
            print(f"Warning: Required columns for class '{cls}' not found in the DataFrame.")
    
    return df

@dataframe_loop_decorator
def add_status(df: pd.DataFrame, df_name: str):
    """
    Adds a 'Status' column to the DataFrame by extracting the text within parentheses from the DataFrame's name.

    Parameters:
    df (pd.DataFrame): The DataFrame to modify.
    df_name (str): The name of the DataFrame.

    Returns:
    pd.DataFrame: The DataFrame with the 'Status' column added.
    """
    pattern = re.compile(r'\(([^)]+)\)')
    match = pattern.search(df_name)

    if match:
        status = match.group(1)
        df['Status'] = status
    else:
        print(f"No text within parentheses found in the DataFrame name: {df_name}")
    
    return df

def concat_all_dataframes(dfs: dict):
    """
    Concatenates all DataFrames from a dictionary into a single DataFrame.

    Parameters:
    dfs (dict): A dictionary of DataFrames, where the keys are the names of the DataFrames.

    Returns:
    pd.DataFrame: A single DataFrame containing all rows from the original DataFrames.
    """
    concatenated_df = pd.concat(dfs.values(), ignore_index=True)
    return concatenated_df

@dataframe_loop_decorator
def actualize_csv(df:pd.DataFrame, df_name, folder='Datas'):
    file_path = os.path.join(folder, f"{df_name}.csv")
    df.to_csv(file_path, index=False)
    return df

if __name__ == "__main__":

    # load all dataframes
    folder = "Datas"
    dfs = load_csv_dataframes(folder)

    # add LC col into all tables "8"
    dfs_8 = select_table(dfs, by_name=re.compile(r'.*8.*'))
    animals_classes = select_column(dfs=dfs_8)
    dfs_8 = add_lc_endemics_column(dfs=dfs_8, classe_dict=animals_classes)
    actualize_csv(dfs=dfs_8)

    # merge all tables "2" and create new column Status = (CR, EN, VU)
    dfs_2 = select_table(dfs, by_name=re.compile(r'.*2.*'))
    dfs_2 = add_status(dfs_2)
    actualize_csv(dfs=dfs_2)
    Table_time = concat_all_dataframes(dfs_2)
    Table_time.to_csv('Datas/Table_time.csv')
