import streamlit as st 
import openai
import json

from streamlit_chat import message
from framingham10yr.framingham10yr import framingham_10year_risk

"""
# Welcome to the Heart Disease Risk Calculator!

This chatbot is here to help you understand your risk of heart disease. This is a serious topic; please do not use this calculator for fun.

This calculator uses the Framingham Heart Study (https://www.framinghamheartstudy.org/) as a base to calculate your 10 years heart disease risk through a calculator by videntity on Github (https://github.com/videntity/python-framingham10yr).

Answer the questions one by one, and if you have any questions for the chatbot, go ahead and ask them. Once you get your results back, we will provide you with some next steps and resources to follow.

Please contact us if you have any questions! 
"""

context = [ {'role':'system', 'content':"""Assume the role of a medical assistant. Please obtain the following information from the user, and 
fill in the  structure below. 
Obtain each property from the user ONE-BY-ONE, not all together, so
they don/'t feel overwhelmed. Use questions that reflect a kind medical assistant. For example, after asking about gender, 
move on to ask about age, and then cholesterol, and so on. The structure you must print out at the end is below. Fill in all of the ___ and 
fill in "True" or "False" for the last two properties.
///
{
   "sex":"____",
   "age":___,
   "total_cholesterol":___,
   "hdl_cholesterol":___,
   "systolic_blood_pressure":____,
   "smoker":"___",
   "blood_pressure_treatment":"____"
}
///
If they don\'t know their information, use the average measure for their age and put that in the structure. Otherwise, all other information in 
the format is required. We cannot proceed with the calculation without all the required data. Smoker and blood pressure treatment both must be
set in the JSON with "True" or "False".
Sex must be set in the JSON with either "male" or "female". If the user is non-binary, ask them for their assigned gender at birth.

After the conversation, return the data in THAT format ONLY. No other text should be in that message. Make sure to ask 
THE USER questions, one-by-one!

Once you are done with the conversation, please return a message that only contains the filled-in format. No ___ should be present, so if the user
didn\'t know a value, please fill it in for them using the average measure for their age. Don't let me down please and do this correctly.
"""} ]

openai.api_key = st.secrets["openai"]

def get_response_from_messages(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
    )
    return response.choices[0].message["content"]

def collect_messages(prompt):
    st.session_state.context.append({'role':'user', 'content':f"{prompt}"})
    response = get_response_from_messages(st.session_state.context) 
    st.session_state.context.append({'role':'assistant', 'content':f"{response}"})
    st.session_state.past.append(prompt)
    st.session_state.generated.append(response)

def check_for_risk():
   if "{" in st.session_state['generated'][-1]:
      last_message = st.session_state['generated'][-1]
      st.session_state.generated.pop()
   
      json_start = last_message.index('{')
      json_end = last_message.index('}')
      
      json_part = last_message[json_start:json_end+1]
      
      data = json.loads(json_part)
      
      gender = data["sex"]
      age = data["age"]
      total_cholesterol = data["total_cholesterol"]
      hdl_cholesterol = data["hdl_cholesterol"]
      systolic_bp = data["systolic_blood_pressure"]
      smoker = data["smoker"]
      bp_treatment = data["blood_pressure_treatment"]
   
      result = framingham_10year_risk(gender, age, total_cholesterol, hdl_cholesterol, systolic_bp, smoker, bp_treatment)
      if "OK" in result['message']:
         percent = result['percent_risk']
         st.session_state.context.append({'role':'system', 'content':"""The user's percent risk is """ + percent + """. Please restate 
         their risk in the format below:
   
         Your percent risk of heart disease is _____. 
   
         If the percent is very high, console the user after giving them the news and assure them everything will be okay.
         
         """})
         st.session_state.generated.append(get_response_from_messages(st.session_state['context']))
      elif "errors" in result['message']:
         errors = ' '.join(result['errors'])
         st.session_state.context.append({'role':'system', 'content':"""We could not proceeed due to these errors: """ + errors + """. 

         Please correct the errors with the user and print out the final JSON again.
      
         """})
         st.session_state.generated.append(get_response_from_messages(st.session_state['context']))

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
    input_text = st.text_input("You: ", "", key="input", clear_on_submit=True)
    return input_text

def clear_text():
    st.session_state["input"] = ""
    
# st.button("Clear text input", on_click=clear_text)

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
            check_for_risk()
