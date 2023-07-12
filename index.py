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

context = [ {'role':'system', 'content':"""Assume the role of a medical assistant. Please obtain the following information from your user, who is your patient, and 
fill in the JSON structure below. 
Obtain each property one-by-one so
your patient doesn't feel overwhelmed, using questions that reflect a kind medical assistant.
{
"sex": either "male"/"female", 
"age": number in range 20-70  (if not in range, tell patient that our calculator is not made for their age), 
"total_cholesterol":  number in range 130-320, 
"hdl_cholesterol": number in range 20-100 ,  
"systolic_blood_pressure": number in range 90-200 , 
"smoker": 0/1, 
"blood_pressure_med_treatment": 0/1
}
///
If patient don't know following information, use the following number, adjust accordingly if they 
say that it is low or high. Also, provide information about clinics near them where they can obtain the information:
"total_cholesterol":  200, 
"hdl_cholesterol": 55 ,  
"systolic_blood_pressure": 130
Otherwise, all other information in the JSON format is required. We cannot proceed with the calculation without all the required data.
///
After the conversation, put the data into JSON format and print it out to me.
[Example:
Output: 
{
"sex": "female",
"age": 23,
"total_cholesterol": 175,
"hdl_cholesterol": 55,
"systolic_blood_pressure": 130,
"smoker": 0,
"blood_pressure_med_treatment": 1
}
]
///
ASK ME, THE USER, QUESTIONS ONE BY ONE!"""} ]

openai.api_key = st.secrets["openai"]

def generate_response(prompt):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def get_response_from_messages(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]

def collect_messages(prompt):
    context.append({'role':'user', 'content':f"{prompt}"})
    response = get_completion_from_messages(context) 
    context.append({'role':'assistant', 'content':f"{response}"})
    return context

    
#Creating the chatbot interface
st.title("chatBot : Streamlit + openAI")

# Storing the chat
if 'generated' not in st.session_state:
    response = generate_response(context)
    st.session_state['generated'] = [response]

if 'past' not in st.session_state:
    st.session_state['past'] = ['Hi!']

input_container = st.container()
response_container = st.container()

# We will get the user's input by calling the get_text function
def get_text():
    input_text = st.text_input("You: ", "", key="input")
    return input_text

## Applying the user input box
with input_container:
    user_input = get_text()

with response_container:
    if user_input:
        response = collect_messages(user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(response)
        
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state['generated'][i], key=str(i))

"""
Here is some information on the ASCVD Risk Calculator:

ASCVD: atherosclerotic cardiovascular disease, defined as coronary death or nonfatal myocardial infarction, or fatal or nonfatal stroke

Lifetime ASCVD Risk:

Estimates of lifetime risk for ASCVD are provided for adults 20 through 59 years of age and are shown as the lifetime risk for ASCVD for a 50-year-old without 
ASCVD who has the risk factor values entered at the initial visit. Because the primary use of these lifetime risk estimates is to facilitate the very important discussion 
regarding risk reduction through lifestyle change, the imprecision introduced is small enough to justify proceeding with lifestyle change counseling informed by these results.
"""
