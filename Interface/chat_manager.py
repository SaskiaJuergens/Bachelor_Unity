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

    1. Please analyze whether important security-relevant information is missing in the previous dialogue or in the provided system model (e.g., DFD) that is necessary for a thorough threat analysis.  
    2. If such missing information exists, please formulate a clear and specific follow-up question for the user to answer, for example: "What has already been implemented?" or "Please describe the security measures of component X."  
    3. If you do not identify any missing information and everything seems sufficient, do not formulate a follow-up question.  
    4. Always create a list of 3-4 meaningful next steps the user can choose to continue the process, even if no additional information is needed. 
        Never leave this section empty.
    5. You must always strictly provide:
    1. A follow-up question to keep the conversation going and if there is missing context, needed for a better Threat Modeling.
    2. Next steps with a concrete, actionable recommendation for what the user should do next.
    3. Leerer Absatz

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
