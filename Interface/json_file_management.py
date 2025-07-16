import streamlit as st
import json
import re

def upload_json_file():
    uploaded_file = st.file_uploader("Upload a JSON-file", type=["json"])
    
    if uploaded_file is not None:
        try:
            json_raw = uploaded_file.read().decode("utf-8")
            
            # Versuche, den JSON-Text zu parsen
            parsed_json = json.loads(json_raw)

            st.success("File successfully uploaded!")
            
            # Rückgabe: sowohl originaler Text als auch strukturierte Daten
            return json_raw, parsed_json

        except Exception as e:
            st.error(f"Error reading or parsen the file: {e}")
            return None, None

    return None, None

import re

# Versuche JSON aus der Antwort zu extrahieren
def extract_json_from_text(text):
    try:
        match = re.search(r'\{[\s\S]+\}', text)
        if match:
            return json.loads(match.group())
    except Exception as e:
        st.warning(f"Error with parsen the JSON-answer: {e}")
    return None
