import streamlit as st
import json

def upload_json_file():
    uploaded_file = st.file_uploader("Lade eine JSON-Datei hoch", type=["json"])
    
    if uploaded_file is not None:
        try:
            json_raw = uploaded_file.read().decode("utf-8")
            
            # Versuche, den JSON-Text zu parsen
            parsed_json = json.loads(json_raw)

            st.success("Datei erfolgreich hochgeladen.")
            
            # Rückgabe: sowohl originaler Text als auch strukturierte Daten
            return json_raw, parsed_json

        except Exception as e:
            st.error(f"Fehler beim Einlesen oder Parsen der Datei: {e}")
            return None, None

    return None, None