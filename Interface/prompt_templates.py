memory_prompt_template = """ Du bist ein hilfreicher KI-Assistent, der auf Deutsch antwortet.
Berücksichtige den bisherigen Gesprächsverlauf und beantworte die nächste Frage sinnvoll und präzise.
    Previous conversation: {history}
    Human: {human_input}
    AI: [/INST]"""