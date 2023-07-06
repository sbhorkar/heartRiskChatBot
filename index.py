import streamlit as st
import openai

# pip install streamlit-chat  
from streamlit_chat import message

"""
# Welcome to the Heart Disease Risk Calculator!

This chatbot is here to help you understand your risk of heart disease. This is a serious topic; please do not use this calculator for fun.

Answer the questions one by one, and if you have any questions for the chatbot, go ahead and ask them. Once you get your results back, we will provide you with some next steps and resources to follow.

Please contact us if you have any questions!
"""

openai.api_key = st.secrets["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"]

def generate_response(prompt):
    completions = openai.Completion.create(
        engine = "text-davinci-003",
        prompt = prompt,
        max_tokens = 1024,
        n = 1,
        stop = None,
        temperature=0.5,
    )
    message = completions.choices[0].text
    return message 
    
# Creating the chatbot interface
st.title("chatBot : Streamlit + openAI")

# Storing the chat
if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

# We will get the user's input by calling the get_text function
def get_text():
    input_text = st.text_input("You: ","Hello, how are you?", key="input")
    return input_text

user_input = get_text()

if user_input:
    output = generate_response(user_input)
    # store the output 
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

if st.session_state['generated']:
    
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')

"""
Here is some information on the ASCVD Risk Calculator:

ASCVD: atherosclerotic cardiovascular disease, defined as coronary death or nonfatal myocardial infarction, or fatal or nonfatal stroke

Lifetime ASCVD Risk:

Estimates of lifetime risk for ASCVD are provided for adults 20 through 59 years of age and are shown as the lifetime risk for ASCVD for a 50-year-old without 
ASCVD who has the risk factor values entered at the initial visit. Because the primary use of these lifetime risk estimates is to facilitate the very important discussion 
regarding risk reduction through lifestyle change, the imprecision introduced is small enough to justify proceeding with lifestyle change counseling informed by these results.
"""
