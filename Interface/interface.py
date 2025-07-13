import streamlit as st 
from llm_chain import load_normal_chain
from langchain.memory import StreamlitChatMessageHistory
from chat_manager import save_chat_history_json, load_chat_history_json, get_timestamp
#from json_file_management import upload_json_file
import yaml
import os

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

def load_chain(chat_history):
    return load_normal_chain(chat_history)

def set_send_input():
    st.session_state.send_input = True
    clear_input_field()

def track_index():
    st.session_state.session_index_tracker = st.session_state.session_key

def clear_input_field():   
    st.session_state.input_query = st.session_state.user_input #letzten Input speichern
    st.session_state.user_input = "" #Input löschen  

def save_chat_history():
    if st.session_state.history != []:
        if st.session_state.session_key == "Neuer_Chat":
            st.session_state.new_session_key = get_timestamp() + ".json"  #speichern Chat mit Zeitstempel
            save_chat_history_json(st.session_state.history, os.path.join(config["chat_history_path"] + st.session_state.new_session_key))
        else:
            save_chat_history_json(st.session_state.history, os.path.join(config["chat_history_path"] + st.session_state.session_key))
 

def main():
    st.title("KI-gestütze Threat Modeling")
    chat_container = st.container()
    st.sidebar.title("Chat Sitzungen")
    chat_sessions = ["Neuer_Chat"] + os.listdir(config["chat_history_path"])    


    #define send_input
    if "send_input" not in st.session_state:
        st.session_state.session_key = "Neuer_Chat"
        st.session_state.send_input = False
        st.session_state.user_question = ""
        st.session_state.new_session_key = None
        st.session_state.session_index_tracker = "Neuer_Chat"
    if st.session_state.session_key == "Neuer_Chat" and st.session_state.new_session_key != None:
        st.session_state.session_index_tracker = st.session_state.new_session_key
        st.session_state.new_session_key = None


    index = chat_sessions.index(st.session_state.session_index_tracker)
    st.sidebar.selectbox("Wähle einen Chat", chat_sessions, key="session_key", index=index, on_change=track_index)

    #lade den Chatverlauf vom bestehenden Chat
    if st.session_state.session_key != "Neuer_Chat":
        st.session_state.history = load_chat_history_json(config["chat_history_path"] + st.session_state.session_key)
    else:
        st.session_state.history = []

    chat_history = StreamlitChatMessageHistory(key="history")
        
    user_input = st.text_input("Stelle eine Frage...", key="user_input", on_change=set_send_input)
    
    # JSON-Upload und Verarbeitung
    #json_raw, parsed_json, json_snippet = upload_json_file()
    #uploaded_json = st.sidebar.file_uploader("Upload an audio file", type=["wav", "mp3", "ogg"])

    send_button = st.button("Senden", key="send_button")
    if send_button or st.session_state.send_input:   #Senden button betätigen
        if st.session_state.input_query != "":

            llm_chain = load_chain(chat_history)

            #llm_response = "Anwort der LLM"
            with chat_container:
                llm_response = llm_chain.run(st.session_state.input_query )
                st.session_state.input_query = ""

    #loop over den bereits exestierenden Chatverlauf
    if chat_history.messages != []:
        with chat_container:
            st.write("Chatverlauf:")
            for message in chat_history.messages:
                st.chat_message(message.type).write(message.content)

    
    #chat in session speichern
    save_chat_history()


if __name__ == "__main__":
    main()