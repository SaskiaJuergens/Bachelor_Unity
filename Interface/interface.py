import streamlit as st 
from llm_chain import load_normal_chain
from langchain.memory import StreamlitChatMessageHistory
from chat_manager import save_chat_history_json, load_chat_history_json, get_timestamp
from json_file_management import upload_json_file
import yaml
import os
import re

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
        # user_level in die History speichern
        #if not any(msg.get("role") == "system" and "user_level" in msg.get("content", "") for msg in st.session_state.history):
        if not any(getattr(msg, "type", None) == "system" and "user_level" in getattr(msg, "content", "") for msg in st.session_state.history):
            st.session_state.history.insert(0, {
                "role": "system",
                "content": f"user_level={st.session_state.user_level}"
            })

        if st.session_state.session_key == "new session":
            st.session_state.new_session_key = get_timestamp() + ".json"
            save_chat_history_json(st.session_state.history, os.path.join(config["chat_history_path"] + st.session_state.new_session_key))
        else:
            save_chat_history_json(st.session_state.history, os.path.join(config["chat_history_path"] + st.session_state.session_key))

def build_user_level_instructions(user_level: int) -> str:
    if user_level == 1:
        return (
            "Der Nutzer ist IT-Sicherheitsanfänger (Level 1).\n"
            "- Gehe davon aus, dass grundlegende IT-Sicherheitskonzepte nicht bekannt sind.\n"
            "- Erkläre alle Begriffe (wie z. B. „XSS“, „TLS“, „Datenfluss“) möglichst einfach und mit Alltagsvergleichen.\n"
            "- Verwende einfache Sprache, kurze Sätze, und vermeide Fachjargon.\n"
            "- Ergänze deine Antwort mit einem kurzen, eingebetteten IT-Security-Expertenprofil, "
            "das erklärt, worauf in der Sicherheitsbewertung besonders geachtet wird (z. B. Vertraulichkeit, Integrität, Authentizität).\n"
            "- Ziel ist es, den Nutzer nicht nur zu warnen, sondern ihm auch die Grundidee hinter der jeweiligen Bedrohung verständlich zu machen.\n"
        )

    elif user_level == 2:
        return (
            "Der Nutzer hat grundlegendes IT-Wissen, aber wenig spezifisches Wissen in IT-Security (Level 2).\n"
            "- Gib einfache Erklärungen für alle sicherheitsrelevanten Begriffe und Verfahren.\n"
            "- Binde Definitionen direkt in die Antwort ein (z. B. was eine SQL-Injection ist und wie sie funktioniert).\n"
            "- Gib zu jeder gefundenen Bedrohung auch einen didaktisch aufbereiteten Hinweis, warum sie relevant ist und wie man sie grundsätzlich verhindern kann.\n"
            "- Ergänze die Antwort mit einem IT-Security-Einstiegsprofil: Wichtige Schutzziele, typische Bedrohungstypen, Basismaßnahmen.\n"
        )

    elif user_level == 3:
        return (
            "Der Nutzer hat mittleres IT-Sicherheitswissen (Level 3).\n"
            "- Er kennt grundlegende Sicherheitskonzepte, benötigt aber noch klare Orientierung.\n"
            "- Gib praxisnahe, aber gut erklärte Hinweise zu Bedrohungen und Gegenmaßnahmen.\n"
            "- Fachbegriffe dürfen verwendet werden, sollten aber gelegentlich kurz erläutert werden.\n"
            "- Verweise gerne auf bekannte Frameworks (z. B. STRIDE, OWASP Top 10), aber ohne tiefes Detail.\n"
        )

    elif user_level == 4:
        return (
            "Der Nutzer ist Softwareentwickler oder Informatiker mit Umsetzungsverantwortung für IT-Security (Level 4).\n"
            "- Konzentriere dich auf konkrete Umsetzungstipps und Best Practices.\n"
            "- Liefere Empfehlungen zu Sicherheitsframeworks, Bibliotheken oder Tools (z. B. OWASP Dependency-Check, CSP, OAuth2).\n"
            "- Verzichte auf grundlegende Erklärungen – setze voraus, dass Konzepte wie XSS oder CSRF bekannt sind.\n"
            "- Strukturierte Bedrohungsklassifikationen (z. B. STRIDE oder LINDDUN) sind willkommen.\n"
            "- Vorschläge sollten handlungsorientiert und technisch präzise sein.\n"
        )

    elif user_level == 5:
        return (
            "Der Nutzer ist IT-Security-Experte (Level 5).\n"
            "- Vermeide didaktische oder vereinfachte Erklärungen.\n"
            "- Konzentriere dich auf relevante Bedrohungen, Edge-Cases und tiefergehende Analysen.\n"
            "- Gib eher knappe Hinweise, z. B. auf ungewöhnliche Bedrohungsvektoren oder Architekturprobleme.\n"
            "- Du kannst davon ausgehen, dass der Nutzer STRIDE, CIA, Angriffsvektoren und Security Patterns kennt.\n"
            "- Optional: Wecke Diskussion oder Konfrontation durch kritische Rückfragen (Challenge-Partner-Rolle).\n"
        )

    else:
        return (
            "Unbekanntes Sicherheitslevel – bitte formuliere ausgewogen, weder zu technisch noch zu oberflächlich.\n"
        )

def build_threat_analysis_prompt(json_raw: str, user_input: str, user_level: int) -> str:
    # Erstellt die Zielgruppen-Erklärung basierend auf dem Level
    user_level_instructions = build_user_level_instructions(user_level)

    return f"""
    {user_level_instructions}

    The user provided the following Data Flow Diagram (in JSON format):
    {json_raw}

    Question: {user_input}

    Your tasks:
    1. Analyze the DFD above for potential security threats using the STRIDE model.
    2. For each threat, include:
       - Which element of the DFD it affects (e.g., node or edge ID)
       - The STRIDE category
       - A short explanation of the risk
       - A recommendation for mitigation, appropriate to the user's knowledge level
       - (Optional) An example CVE that illustrates a comparable real-world vulnerability

    Output the STRIDE analysis as a structured JSON list. Example:
    [
      {{
        "dfd_element": "Edge 2 (from Process A to Storage B)",
        "stride_category": "Information Disclosure",
        "description": "Sensitive data is transferred without encryption.",
        "recommendation": "Use TLS to secure the data in transit.",
        "example_cve": "CVE-2021-34527"
      }}
    ]

    3. At the end, generate an updated version of the Data Flow Diagram in the following JSON format:
    {{
      "nodes": [
        {{ "id": 1, "label": "User" }}
      ],
      "edges": [
        {{ "from": 1, "to": 2, "label": "User Input" }}
      ]
    }}

    Add the updated DFD JSON at the end of your answer."""


def main():
    st.title("AI-powered Threat Modeling")
    # Nutzerwissen abfragen (nur einmal beim Start)

    chat_container = st.container()
    st.sidebar.title("Chat Session")
    chat_sessions = ["new session"] + os.listdir(config["chat_history_path"])    


    #define send_input
    if "send_input" not in st.session_state:
        st.session_state.session_key = "new session"
        st.session_state.send_input = False
        st.session_state.user_question = ""
        st.session_state.new_session_key = None
        st.session_state.session_index_tracker = "new session"
    if st.session_state.session_key == "new session" and st.session_state.new_session_key != None:
        st.session_state.session_index_tracker = st.session_state.new_session_key
        st.session_state.new_session_key = None

    if "user_level" not in st.session_state:
        if st.session_state.session_key == "new session":
            st.session_state.user_level = st.select_slider(
                "Rate your IT security knowledge from 1 (Beginner) to 5 (Expert)",
                options=[1, 2, 3, 4, 5],
                value=3
            )
            st.markdown("---")
        else:
            st.session_state.user_level = 3  # Default fallback

    index = chat_sessions.index(st.session_state.session_index_tracker)
    st.sidebar.selectbox("Choose a chat", chat_sessions, key="session_key", index=index, on_change=track_index)

    #lade den Chatverlauf vom bestehenden Chat
    if st.session_state.session_key != "new session":
        st.session_state.history = load_chat_history_json(config["chat_history_path"] + st.session_state.session_key)
        # user_level aus gespeicherter system message extrahieren
        for msg in st.session_state.history:
            if msg.get("role") == "system" and "user_level=" in msg.get("content", ""):
                try:
                    st.session_state.user_level = int(msg["content"].split("user_level=")[-1].strip())
                    break
                except:
                    st.session_state.user_level = 3  # fallback
    else:
        st.session_state.history = []


    chat_history = StreamlitChatMessageHistory(key="history")
        
    user_input = st.text_input("Ask a question...", key="user_input", on_change=set_send_input)
    
    # JSON-Upload und Verarbeitung
    json_raw, parsed_json = upload_json_file()

    send_button = st.button("Send", key="send_button")
    if send_button or st.session_state.send_input:   #Senden button betätigen
        if st.session_state.input_query != "":

            llm_chain = load_chain(chat_history)
            #llm_chain = [{"role": m.role, "content": m.content} for m in chat_history.messages]


            user_level_instructions = build_user_level_instructions(st.session_state.user_level)
            threat_prompt = build_threat_analysis_prompt(json_raw, st.session_state.input_query, st.session_state.user_level)


            # Wenn JSON vorhanden ist, nimm json_raw, sonst nur die Frage
            if json_raw:
                llm_input = build_threat_analysis_prompt(json_raw=json_raw, user_input=st.session_state.input_query, user_level=st.session_state.user_level)
            
            else:
                lm_input = f"""{build_user_level_instructions(st.session_state.user_level)}
                    Question: {st.session_state.input_query}"""


            with chat_container:
                llm_response = llm_chain.run(llm_input)
                #llm_response = ask_gpt35(llm_input, llm_chain, system_prompt=memory_prompt_template)
                st.session_state.input_query = ""

                json_match = re.search(r"\{[\s\S]*?\}", llm_response)

                if json_match:
                    answer_text = llm_response[:json_match.start()].strip()
                    json_output = json_match.group().strip()
                if json_output:
                    st.code(json_output, language="json")
                else:
                    answer_text = llm_response.strip()
                    json_output = None

            # Interaktive Dialog - LLM fragt den User
            with st.expander("What would you like to do next?", expanded=True):
                next_action = st.radio(
                    "Please choose an option:",
                    ["Ask a new question", "Extend the DFD", "Repeat the analysis", "Nothing"],
                    key="next_action_selection"
                )

                if next_action == "Extend the DFD":
                    st.info("Please describe the additional components or data flows to include in the updated DFD.")
                    new_dfd_input = st.text_area("Additional DFD components or data flows:", key="dfd_extension_input")
                    if st.button("Update DFD"):
                        st.session_state.input_query = f"Please extend the DFD with the following information: {new_dfd_input}"
                        st.session_state.send_input = True

                elif next_action == "Repeat the analysis":
                    st.session_state.input_query = "Please repeat the threat analysis based on the current DFD."
                    st.session_state.send_input = True

                elif next_action == "Ask a new question":
                    st.info("You can ask your next question in the input field above.")

                elif next_action == "Nothing":
                    st.success("Alright. You can continue later at any time.")




    #loop over den bereits exestierenden Chatverlauf
    if chat_history.messages != []:
        with chat_container:
            st.write("Chat history:")
            for message in chat_history.messages:
                st.chat_message(message.type).write(message.content)

    
    #chat in session speichern
    save_chat_history()


if __name__ == "__main__":
    main()