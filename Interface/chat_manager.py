import json
from langchain.schema.messages import HumanMessage, AIMessage, SystemMessage #https://api.python.langchain.com/en/latest/messages/langchain_core.messages.human.HumanMessage.html
from datetime import datetime
import re
import streamlit as st

#list comprehension 
#creating a list of the messages from the chat
#saving the list as a chat session
def save_chat_history_json(chat_history, file_path):
    with open(file_path, "w") as f:
        json_data = [message if isinstance(message, dict) else message.dict() for message in chat_history]

        json.dump(json_data, f) #speichern der liste

  

def load_chat_history_json(file_path):
    with open(file_path, "r") as f:
        json_data = json.load(f)
        messages = []
        for message in json_data:
            msg_type = message.get("type")
            if msg_type == "human":
                messages.append(HumanMessage(**message))
            elif msg_type == "ai":
                messages.append(AIMessage(**message))
            elif msg_type == "system":
                messages.append(SystemMessage(**message))
            else:
                # Ignoriere ungültige Einträge oder logge eine Warnung
                print(f"Unknown message type in history: {msg_type}")
        
        return messages


#session_state managment
def get_timestamp():
    return datetime.now().strftime("%Y_%m_%d_%H_%M_%S") #Year Month Day Hour Minute Second



def next_prompt_recommendation(chat_history, ask_gpt35_func, system_prompt):
    # Chatverlauf textuell zusammenfassen 
    chat_history_text = ""
    for m in chat_history.messages[-6:]: #nur letzten 6 Nachrichten
        #chat_history_text += f"{m.role}: {m.content}\n"
        role = getattr(m, "type", "unknown")
        chat_history_text += f"{role}: {m.content}\n"


    next_steps_prompt = f"""

    {chat_history_text}

    Please analyze whether important security-relevant information is missing in the previous dialogue or in the provided system model (e.g., DFD) that is necessary for a thorough threat analysis.  
   
    Your tasks:

    1. Answer the user’s question or fulfill their request on the IT security topic, but clearly indicate where important information is missing or incomplete for a thorough STRIDE threat modeling.
    2. Suggest explicitly which additional details, data, or context the user could provide to improve the accuracy and depth of the threat analysis (e.g., more detailed data flow diagrams, system architecture, specific technologies in use, user roles, or security controls).
    3. Propose practical next steps the user can take after receiving your initial analysis, such as further investigation, risk assessment, or mitigation strategies tailored to their knowledge level.
    4. Offer ideas for what the user might ask next to deepen or broaden the analysis, including any overlooked threat categories, potential attack vectors, or security considerations relevant to their scenario.
    5. Emphasize the importance of completeness and precision in the input information to achieve the best possible STRIDE threat modeling outcome.
    6. Format your response clearly and helpfully, using bullet points or short paragraphs to organize suggestions and recommendations.

    Use exactly this order, no extra explanations, no bullet points other than the numbered list.    
    """

    #GPT wird aufgerufen
    next_steps_text = ask_gpt35_func(
        user_input=next_steps_prompt,
        chat_history=chat_history.messages,
        system_prompt=system_prompt
    )

    #Die Optionen werden extrahiert (Regex)
    #option_lines sind die Auswahlmöglichkeiten
    #feedback_question ist nur der Titel über diesen Optionen
    option_lines = re.findall(r"^\d+\.\s*(.*)$", next_steps_text, re.MULTILINE)
    feedback_question = next_steps_text.split("\n")[-1].strip()

    return option_lines, feedback_question
