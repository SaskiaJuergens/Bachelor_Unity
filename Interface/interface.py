import streamlit as st 
from llm_chain import load_normal_chain, ask_gpt35, load_dotenv
from langchain.schema import HumanMessage, AIMessage
from prompt_templates import memory_prompt_template
from langchain.memory import StreamlitChatMessageHistory
from chat_manager import save_chat_history_json, load_chat_history_json, get_timestamp, next_prompt_recommendation
from json_file_management import upload_json_file,  number_dfd_flows, extract_json_from_response, show_dfd_table, is_valid_json, check_dfd_completeness
import yaml
import os
import json
import re

config = {
    "openai_api_key": "",
    "chat_history_path": "chat_session/"
}


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
            "- Please explain technical terms briefly when used, and prefer common terms over abbreviations.\n"
            "- Avoid overly technical descriptions like 'MACs', 'PKI', or 'OAuth' unless you explain them in simple language."
        
        )

    elif user_level == 4:
        return (
            "The user is a software developer or computer scientist with implementation responsibility for IT security (Level 4).\n"
            "- Focus on concrete implementation tips and best practices.\n"
            "- Provide recommendations on security frameworks, libraries, or tools (e.g., OWASP Dependency-Check, CSP, OAuth2).\n"
            "- Skip basic explanations – assume that concepts like XSS or CSRF are already known.\n"
            "- Structured threat classifications (e.g., STRIDE or LINDDUN) are welcome.\n"
            "- Suggestions should be action-oriented and technically precise.\n"
            "- Output the STRIDE analysis as a structured JSON list. Example: \n" 
            "- DFD-Element: Edge 2 (from Process A to Storage B),\n" 
            "- STRIDE category: Information Disclosure,\n" 
            "- Description: Sensitive data is transferred without encryption.,\n" 
            "- Recommendation: Use TLS to secure the data in transit.\n"   
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
            "- Output the STRIDE analysis as a structured JSON list. Example: \n" 
            "- DFD-Element: Edge 2 (from Process A to Storage B),\n" 
            "- STRIDE category: Information Disclosure,\n" 
            "- Description: Sensitive data is transferred without encryption.,\n" 
            "- Recommendation: Use TLS to secure the data in transit.\n" 
        )

    else:
        return (
            "Unknown security level – please provide a balanced explanation, neither too technical nor too superficial.\n"
        )


def build_threat_analysis_prompt(json_raw: str, user_input: str, user_level: int) -> str:
    # Erstellt die Zielgruppen-Erklärung basierend auf dem Level
    user_level_instructions = build_user_level_instructions(user_level)

    #st.write("user_input 1:", user_input)

    # Falls der User nichts eingegeben hat -> Default-Frage 
    if user_input.strip() == "":
        user_input = "Please perform a STRIDE Threat Analysis based on the Data Flow Diagram (DFD) provided in a non-JSON format"
    
    #st.write("user_input 2:", user_input)

    if user_level >= 4:
        output_instruction = "Output the STRIDE analysis as a structured JSON list."
    else:
        output_instruction = (
            "Output the STRIDE analysis as a clear, well-formatted explanation in plain language, "
            "using bullet points and short paragraphs rather than JSON."
        )

    return f"""
    Question: {user_input}

    {user_level_instructions}

    Your tasks:
    1.Answer the question or fulfill the user's request for a IT-Security realted topic, but clearly indicate where information is missing or where, as an AI, 
    you may encounter limitations or challenges — especially in context-specific or highly detailed tasks. 
    2. Be transparent about your boundaries and limitations for you as a AI and provide the user with suggestions on what additional information is needed to deliver 
    a more accurate or helpful response.

    The user provided the following Data Flow Diagram (in JSON format):
    {json_raw}
    3. If you do a STRIDE THreat Modeling - then for each threat, include:
       - Which element of the DFD it affects (e.g., node or edge ID)
       - The STRIDE category
       - A short explanation of the risk
       - A recommendation for mitigation, appropriate to the user's knowledge level
       - (Optional) An example CVE that illustrates a comparable real-world vulnerability

    4. Output the STRIDE analysis as a structured JSON list suitable for the user knowledge Level.

    If the Question isn't about a IT-Security realted topic, clearify, that you don't help in other matters than IT-Security.
    """






############################################################################################
def main():
    st.title("AI-powered Threat Modeling")
    # Nutzerwissen abfragen (nur einmal beim Start)

    chat_container = st.container()
    st.sidebar.title("Chat Session")

    os.makedirs(config["chat_history_path"], exist_ok=True)
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
    if "input_query" not in st.session_state:
        st.session_state.input_query = ""
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""


    #####User Level######
    def update_user_level():
        st.session_state.user_level = st.session_state.slider_user_level

    if "user_level" not in st.session_state:
        st.session_state.user_level = None

    if st.session_state.session_key == "new session":
        st.select_slider(
            "Rate your IT security knowledge from 1 (Beginner) to 5 (Expert)",
            options=[1, 2, 3, 4, 5],
            key="slider_user_level",
            value=3,
            on_change=update_user_level
        )
        if st.session_state.user_level is None:
            st.session_state.user_level = 3  # Default
    else:
        # Bei bestehender Session aus History laden, falls noch nicht geladen
        if st.session_state.user_level is None:
            for msg in st.session_state.history:
                if hasattr(msg, "type") and msg.type == "system" and hasattr(msg, "content") and "user_level=" in msg.content:
                    try:
                        st.session_state.user_level = int(msg.content.split("user_level=")[-1].strip())
                        break
                    except:
                        st.session_state.user_level = 3  # Default




    index = chat_sessions.index(st.session_state.session_index_tracker)
    st.sidebar.selectbox("Choose a chat", chat_sessions, key="session_key", index=index, on_change=track_index)

    #lade den Chatverlauf vom bestehenden Chat
    if st.session_state.session_key != "new session":
        st.session_state.history = load_chat_history_json(config["chat_history_path"] + st.session_state.session_key)
        # user_level aus gespeicherter system message extrahieren
        for msg in st.session_state.history:
            if hasattr(msg, "type") and msg.type == "system" and hasattr(msg, "content") and "user_level=" in msg.content:

                try:
                    st.session_state.user_level = int(msg.content.split("user_level=")[-1].strip())

                    break
                except:
                    st.session_state.user_level = 3  # fallback
    else:
        st.session_state.history = []


    chat_history = StreamlitChatMessageHistory(key="history")
        
    #user_input = st.text_input("Ask a question...", key="user_input", on_change=set_send_input)
    user_input = st.text_input("Ask a question...", key="user_input", value=st.session_state.get("user_input", ""), on_change=set_send_input)


    # JSON-Upload und Verarbeitung
    json_raw, parsed_json = upload_json_file()
    if parsed_json:
        parsed_json = number_dfd_flows(parsed_json)
        json_raw = json.dumps(parsed_json, indent=2)


    ##### Send button #######
    send_button = st.button("Send", key="send_button")
    if send_button or st.session_state.send_input:   #Senden button betätigen
        llm_chain = load_chain(chat_history)

        user_query = st.session_state.input_query.strip()
        
        llm_input = build_threat_analysis_prompt(json_raw=json_raw, user_input=st.session_state.input_query, user_level=st.session_state.user_level)


        with chat_container:
            llm_response = llm_chain.run(llm_input) #LLM antowrtet

            st.session_state.input_query = ""

            json_output, answer_text = extract_json_from_response(llm_response)

            if json_output:
                st.code(json.dumps(json_output, indent=2), language="json")
                show_dfd_table(json_output)
            else:
                answer_text = llm_response.strip()
                json_output = None

               



    #loop over den bereits exestierenden Chatverlauf
    if chat_history.messages != []:
        with chat_container:
            st.write("Chat history:")
            for message in chat_history.messages:
                st.chat_message(message.type).write(message.content)

            llm_response = ""
            if llm_response:
                chat_history.messages.append(AIMessage(content=llm_response))


            # Interaktive Dialog - LLM fragt den User
            option_lines, feedback_question = next_prompt_recommendation(chat_history, ask_gpt35, memory_prompt_template)


            with st.expander("What do you wanna do next?", expanded=True):

                # Liste ausgeben statt Radio-Buttons
                for option in option_lines:
                    st.markdown(f"- {option}")
                    
                # next_action = st.radio(
                #     feedback_question,
                #     option_lines,
                #     #key=f"next_action_selection_{len(option_lines)}",
                #     index=None,
                #     key="next_action_selection"
                # )

                # feedback = st.radio(
                #     "Was this guidance helpful and sufficiently detailed?",
                #     ["Yes", "No"],
                #     #key=f"feedback_selection{len(chat_history.messages)}",
                #     index=None,
                #     key="next_action_selection"
                # )


                # if next_action:
                #     if feedback == "No":
                #         st.session_state.user_input = (
                #             "Answer more detailed for someone who has less IT-Security knowledge. "
                #             f"Previous answer: {chat_history.messages[-1].content}"
                #         )
                #     else:
                #         st.session_state.user_input = (
                #             "The last answer was satisfactory. Now please provide the user with additional ideas or practical tips on what steps they could or should take next."
                #             f"Previous answer: {chat_history.messages[-1].content}"
                #         )
                #     st.session_state.send_input = True
        




    #chat in session speichern
    save_chat_history()



if __name__ == "__main__":
    main()