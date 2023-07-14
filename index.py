import streamlit as st 
import openai

# pip install streamlit-chat  
from streamlit_chat import message

from framingham10yr.framingham10yr import framingham_10year_risk

"""
# Welcome to the Heart Disease Risk Calculator!

This chatbot is here to help you understand your risk of heart disease. This is a serious topic; please do not use this calculator for fun.

This calculator uses the Framingham Heart Study (https://www.framinghamheartstudy.org/) as a base to calculate your 10 years heart disease risk through a calculator by videntity on Github (https://github.com/videntity/python-framingham10yr).

Answer the questions one by one, and if you have any questions for the chatbot, go ahead and ask them. Once you get your results back, we will provide you with some next steps and resources to follow.

Please contact us if you have any questions!
"""

context = [ {'role':'user', 'content':"""Assume the role of a medical assistant. Please obtain the following information from the user, and 
fill in the JSON structure below. 
Obtain each property from the user one-by-one so
they don/'t feel overwhelmed, using questions that reflect a kind medical assistant. For example, after asking about gender, 
move on to ask about age, and then cholesterol, and so on.

{
"gender": ____, 
"age": _______, 
"total_cholesterol": _____,
"hdl_cholesterol": _______,
"systolic_blood_pressure": _______,
"current_smoker": ____,
"taking_blood_pressure_med_treatment": ____,
}
///
If they don\'t know their information, use the average measure for their age. Otherwise, all other information in 
the JSON format is required. We cannot proceed with the calculation without all the required data.
///
After the conversation, return the data in the JSON format below. Make sure to ask THE USER questions, one-by-one!
"""} ]

context = [ {'role':'system', 'content':"""I want you to act like Dr. Natalie Manning from Chicago Med by looking up her scripts and lines. I want you to respond and answer like Dr. Manning using the tone, manner and vocabulary she would use. Do not write any character explanations and don't introduce yourself as Dr. Manning. Only answer like Dr. Manning. Do not make conversation with yourself; do not answer your own questions. I will be the patient and you are gathering my information to calculate my CVD risk. Ask me questions to do so, one by one. Do not move on to the next properties without knowing the value as stated in the range for the properties before it. Gather the information as said in the range. Start by introducing me to the calculator, without saying your name. Then, ask me for these info, the JSON format that they are in is ["property name": range (measured value or not) (name to use)]: 
{"gender": female/male (N) (biological sex, not that biological sex is not gender), 
"age": 20-79 (N), 
"total_cholesterol": 120-320 (Y),
"hdl_cholesterol": 20-100 (Y),
"systolic_blood_pressure": 80-200 (Y),
"current_smoker": 0/1 (N),
"blood_pressure_med_treatment": 0/1 (N) (taking blood pressure medicine)}
For the measured values, tell me that it is fine if I don't know it. If I say I do not know the information, use the average measure for my age. If you have all the data, return it in the JSON format, such as {"property name": value,...}. Ask me questions one by one as Dr. Manning would, using varied responses.
"""} ]

openai.api_key = st.secrets["openai"]

def get_response_from_messages(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
        presence_penalty=0.6,
    )
    return response.choices[0].message["content"]

def collect_messages(prompt):
    st.session_state.context.append({'role':'user', 'content':f"{prompt}"})
    response = get_response_from_messages(st.session_state.context) 
    st.session_state.context.append({'role':'assistant', 'content':f"{response}"})
    st.session_state.past.append(prompt)
    st.session_state.generated.append(response)

response_container = st.container()
input_container = st.container()

# Storing the chat
if 'context' not in st.session_state:
     st.session_state['context'] = context[:]

if 'generated' not in st.session_state:
    response = get_response_from_messages(st.session_state['context'])
    st.session_state['generated'] = [response]
    st.session_state.context.append({'role':'assistant', 'content':f"{response}"})

if 'past' not in st.session_state:
    st.session_state['past'] = ["Hi!"]

# We will get the user's input by calling the get_text function
def get_text():
    input_text = st.text_input("You: ", "", key="input")
    return input_text

# Applying the user input box
with input_container:
    user_input = get_text()

with response_container:
    if user_input:
        collect_messages(user_input)
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state['generated'][i], key=str(i), logo='https://www.freepnglogos.com/uploads/heart-png/emoji-heart-33.png')
