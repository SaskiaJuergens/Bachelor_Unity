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


def number_dfd_flows(dfd_json):
    for i, edge in enumerate(dfd_json.get("edges", []), start=1):
        if "id" not in edge:
            edge["id"] = i
        if "name" not in edge:
            from_id = edge.get("from", "?")
            to_id = edge.get("to", "?")
            label = edge.get("label", "unnamed flow")
            edge["name"] = f"Flow {i}: {label} ({from_id} → {to_id})"
    return dfd_json

def extract_json_from_response(llm_response):
    #json block finden
    json_match = re.search(r"\{[\s\S]*?\}", llm_response)
    if json_match:
        try:
            json_output = json.loads(json_match.group())
            return json_output, llm_response[:json_match.start()].strip()
        except json.JSONDecodeError:
            return None, llm_response.strip()
    else:
        return None, llm_response.strip()
    
def show_dfd_table(dfd_json):
    import pandas as pd
    flows = dfd_json.get("edges", [])
    df = pd.DataFrame(flows)
    st.subheader("Datenflüsse im DFD:")
    st.table(df[["id", "name", "label", "from", "to"]])

def is_valid_json(output_str: str) -> bool:
    try:
        json.loads(output_str)
        return True
    except json.JSONDecodeError:
        return False

def check_dfd_completeness(dfd_json: dict) -> list:
    missing = []
    for edge in dfd_json.get("edges", []):
        if not edge.get("label"):
            missing.append(f"Missing label in edge {edge.get('id', '?')}")
        if not edge.get("from") or not edge.get("to"):
            missing.append(f"Incomplete edge definition: {edge}")
    return missing