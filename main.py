import streamlit as st
import replicate
import os

# App title
st.set_page_config(page_title="Elisa com S, a terapeuta Rogeriana não tão básica")

# Replicate Credentials
with st.sidebar:
    st.title('Elisa com S Chatbot')
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('chave API já providenciada!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input('Por favor digite sua chave API:', type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Por favor digite suas credenciais!', icon='⚠️')
        else:
            st.success('Pronto! Já pode inserir a sua pergunta!', icon='👉')
os.environ['REPLICATE_API_TOKEN'] = replicate_api

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Olá, eu sou Elisa, com S e serei sua terapeuta."}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Olá, eu sou Elisa, com S e serei sua terapeuta."}]
st.sidebar.button('Limpar chat', on_click=clear_chat_history)

# Function for generating LLaMA2 response
# The context for the chatbot is the meat and potatoes.
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant that is taking the role as a psychologist, named 'Elisa'. You do not respond as 'User' or pretend to be 'User'. You only respond as 'Elisa'.\
        Your task is to psychologically analyze a patient applying the rogerian and freudian method of analysis. You are the therapist and the user is the patient.\
        The user writes in brazilian portuguese, you accept inputs in that language and respond back to the user in brazilian portuguese.\
        If a the user says something that does not make any sense, or is somehow offensive, tell the user that you did not understand and ask the user to try again.\
        If the user says anything where there is any adjective related to something negative attributing to himself/herself, you will reply with a question, questioning why does the user feel like that adjective.\
        If the user asks or says anything about you, you will politely say that  the conversation is about the user not about yourself, and will politely tell the user to change the subject and to focus on the therapy.\
        If the user says \'goodbye\' or any word which infers that he/she is finishing the conversation, you will reply with a 'Adeus, foi um prazer lhe ajudar!', and terminate the conversation."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\\n\\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\\n\\n"
    prompt_input =  '"""' + prompt_input+'"""'
    output = replicate.run('a16z-infra/llama-2-13b-chat:2a7f981751ec7fdf87b5b91ad4db53683a98082e9ff7bfd12c8cd5ea85980a52', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":0.1, "top_p":0.9, "max_length":1024, "repetition_penalty":1})
    return output


# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)


# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)