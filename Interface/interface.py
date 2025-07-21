import streamlit as st 
from llm_chain import load_normal_chain
from API_key import ask_gpt35, load_dotenv
from prompt_templates import memory_prompt_template
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
            "The user is a beginner in IT security (Level 1).\n"
            "- Assume that basic IT security concepts are not known.\n"
            "- Explain all terms (e.g., 'XSS', 'TLS', 'data flow') in simple language and using everyday analogies.\n"
            "- Use plain language, short sentences, and avoid technical jargon.\n"
            "- Add a brief embedded IT security expert profile to your response that explains what aspects are especially important in a security assessment (e.g., confidentiality, integrity, authenticity).\n"
            "- The goal is not only to warn the user but also to help them understand the basic idea behind the specific threat.\n"
        )

    elif user_level == 2:
        return (
            "The user has basic IT knowledge, but little specific knowledge of IT security (Level 2).\n"
            "- Provide simple explanations for all security-related terms and procedures.\n"
            "- Integrate definitions directly into the response (e.g., what a SQL injection is and how it works).\n"
            "- For each identified threat, include a didactically prepared note on why it is relevant and how it can be generally prevented.\n"
            "- Add a beginner IT security profile: key protection goals, typical types of threats, basic measures.\n"
        )

    elif user_level == 3:
        return (
            "The user has intermediate IT security knowledge (Level 3).\n"
            "- They know basic security concepts but still need clear guidance.\n"
            "- Provide practical but well-explained advice on threats and countermeasures.\n"
            "- Technical terms can be used but should occasionally be briefly explained.\n"
            "- Feel free to refer to known frameworks (e.g., STRIDE, OWASP Top 10), but without going into deep detail.\n"
        )

    elif user_level == 4:
        return (
            "The user is a software developer or computer scientist with implementation responsibility for IT security (Level 4).\n"
            "- Focus on concrete implementation tips and best practices.\n"
            "- Provide recommendations on security frameworks, libraries, or tools (e.g., OWASP Dependency-Check, CSP, OAuth2).\n"
            "- Skip basic explanations – assume that concepts like XSS or CSRF are already known.\n"
            "- Structured threat classifications (e.g., STRIDE or LINDDUN) are welcome.\n"
            "- Suggestions should be action-oriented and technically precise.\n"
        )

    elif user_level == 5:
        return (
            "The user is an IT security expert (Level 5).\n"
            "- Avoid didactic or simplified explanations.\n"
            "- Focus on relevant threats, edge cases, and in-depth analyses.\n"
            "- Provide concise notes, e.g., on unusual threat vectors or architectural issues.\n"
            "- You can assume the user is familiar with STRIDE, CIA, attack vectors, and security patterns.\n"
            "- The user does not need basic info, term definitions, or overly detailed explanations.\n"
            "- Optional: Spark discussion or confrontation through critical questions (challenge partner role).\n"
        )

    else:
        return (
            "Unknown security level – please provide a balanced explanation, neither too technical nor too superficial.\n"
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
            #if msg.get("role") == "system" and "user_level=" in msg.get("content", ""):
            if hasattr(msg, "type") and msg.type == "system" and hasattr(msg, "content") and "user_level=" in msg.content:

                try:
                    #st.session_state.user_level = int(msg["content"].split("user_level=")[-1].strip())
                    st.session_state.user_level = int(msg.content.split("user_level=")[-1].strip())

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

            llm_input = ""
            # Wenn JSON vorhanden ist, nimm json_raw, sonst nur die Frage
            if json_raw:
                llm_input = build_threat_analysis_prompt(json_raw=json_raw, user_input=st.session_state.input_query, user_level=st.session_state.user_level)
            
            else:
                llm_input = f"""{build_user_level_instructions(st.session_state.user_level)}
                    Question: {st.session_state.input_query}"""


            with chat_container:
                llm_response = llm_chain.run(llm_input)
                #llm_response = ask_gpt35(llm_input, llm_chain, system_prompt=memory_prompt_template)
                st.session_state.input_query = ""

                json_output = None 
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