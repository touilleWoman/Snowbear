import csv
from pathlib import Path

import streamlit as st


def csv_to_dict(file_path):
    data_dict = {}
    with open(file_path, mode="r", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            data_dict[row[0]] = row[1]
    return data_dict


@st.cache_data
def charge_translations(lang="fr"):
    print("Loading translations")
    if lang == "en":
        file_name = "english_translations.csv"
    else:
        file_name = "french_translations.csv"

    # Get the directory of the current script
    script_dir = Path(__file__).resolve().parent

    # Construct the file path relative to the script's directory
    file_path = script_dir / "translation_files" / file_name
    trans_dict = csv_to_dict(file_path)
    return trans_dict
