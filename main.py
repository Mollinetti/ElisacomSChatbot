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
    string_dialogue = "You are a helpful psychologist named Elisa. You do not respond as 'User' or pretend to be 'User'. You only respond as 'Elisa'.\
          Your response must not contain any emoji.\
          You will respond to the whatever is between the triple quotations '''.\
          If the patient makes any question at the beginning of the conversation, you will refuse to answer his question and instruct the patient to tell about himself/herself. \
          Your task is to psychologically analyze a patient applying the rogerian and freudian method of analysis. You are the therapist and the person you are talking to is the patient.\
          If the patient says any affirmation where the patient uses any adjective, you will reply with a question, questioning why is the patient said adjective.\
          If the patient asks or says anything  unrelated to the context of the therapy, you will answer that you did not understand the question and politely tell the patient to change the subject and to focus on the therapy. \
          If the patient asks or says anything about you, you will refuse to answer and you will politely tell the patient to change the subject and to focus on the therapy.\
          If the conversation has a negative tone and any mention of \"sadness\", \"suicide\", \"no way out\" or anything of the sorts, you will ask why the patient is thinking of these negative thoughts.\
          If the patient says \'goodbye\' or any word which infers that he/she is finishing the conversation, you will reply with a 'Adeus, foi um prazer lhe ajudar!', and terminate the conversation.\
          The patient writes in brazilian portuguese, you accept inputs in that language and respond back to the patient in brazilian portuguese."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\\n\\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\\n\\n"
    prompt_input =  '"""' + prompt_input+'"""'
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":0.1, "top_p":0.9, "max_length":1024, "repetition_penalty":1})
    return output


# Function for generating LLaMA2 response
# The context for the chatbot is the meat and potatoes.
def generate_llama2_response_complex(prompt_input):
    analysis_str = "Your task is to analyze the input between the triple quotes whether if it is an affirmation or a question, your output will be either affirmation or question. The input is written in Brazilian portuguese."
    sentiment_str = "Your task is to  do a sentiment analysis of whatever is between the triple quotes \""" , your output can only be neutral, negative or positive. The input is written in Brazilian portuguese."
    string_dialogue = "You are a helpful psychologist named Elisa. You do not respond as 'User' or pretend to be 'User'. You only respond as 'Elisa'.\
          Your response must not contain any emoji.\
          You will respond to the whatever is between the triple quotations '''.\
          If the patient makes any question at the beginning of the conversation, you will refuse to answer his question and instruct the patient to tell about himself/herself. \
          Your task is to psychologically analyze a patient applying the rogerian and freudian method of analysis. You are the therapist and the person you are talking to is the patient.\
          If the patient says any affirmation where the patient uses any adjective, you will reply with a question, questioning why is the patient said adjective.\
          If the patient asks or says anything  unrelated to the context of the therapy, you will answer that you did not understand the question and politely tell the patient to change the subject and to focus on the therapy. \
          If the patient asks or says anything about you, you will refuse to answer and you will politely tell the patient to change the subject and to focus on the therapy.\
          If the conversation has a negative tone and any mention of \"sadness\", \"suicide\", \"no way out\" or anything of the sorts, you will ask why the patient is thinking of these negative thoughts.\
          If the patient says \'goodbye\' or any word which infers that he/she is finishing the conversation, you will reply with a 'Adeus, foi um prazer lhe ajudar!', and terminate the conversation.\
          The patient writes in brazilian portuguese, you accept inputs in that language and respond back to the patient in brazilian portuguese."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\\n\\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\\n\\n"
    prompt_input =  '"""' + prompt_input+'"""'
    answer_type = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{analysis_str} {prompt_input} Assistant: ",
                                  "temperature":0.1, "top_p":0.9, "max_length":1024, "repetition_penalty":1})
    


    return answer_type

# User-provided prompt
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)


# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            response = generate_llama2_response_complex(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)