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

context = [ {'role':'user', 'content':"""Assume the role of a medical assistant. Please obtain the following information from the user, and 
fill in the  structure below. 
Obtain each property from the user ONE-BY-ONE, not all together, so
they don/'t feel overwhelmed. Use questions that reflect a kind medical assistant. For example, after asking about gender, 
move on to ask about age, and then cholesterol, and so on. The structure you must print out at the end is below. Fill in all of the ___ and 
fill in "True" or "False" for the last two properties.
///
{
   "sex":"____",
   "age":___,
   "total_cholestrol":___,
   "hdl_cholestrol":___,
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

errorcontext = [ {'role':'system', 'content':"""I want you to act like Dr. Natalie Manning from Chicago Med by looking up her scripts and lines. I want you to respond and answer like Dr. Manning using the tone, manner and vocabulary she would use. Do not write any character explanations and don't introduce yourself as Dr. Manning. Only answer like Dr. Manning. Do not make conversation with yourself; do not answer your own questions. I will be the patient and you are gathering my information to calculate my CVD risk. Ask me questions to do so, one by one. Do not move on to the next properties without knowing the value as stated in the range for the properties before it. Gather the information as said in the range. Start by introducing me to the calculator, without saying your name. Then, ask me for these info, the JSON format that they are in is ["property name": range (measured value or not) (name to use)]: 
{"gender": female/male (N) (biological sex, not that biological sex is not gender), 
"age": 20-79 (N), 
"total_cholesterol": 120-320 (Y),
"hdl_cholesterol": 20-100 (Y),
"systolic_blood_pressure": 80-200 (Y),
"current_smoker": 0/1 (N),
"blood_pressure_med_treatment": 0/1 (N) (taking blood pressure medicine)}
For the measured values, tell me that it is fine if I don't know it. If I say I do not know the information, use the average measure for my age. If you have all the data, return it in the JSON format, such as {"property name": value,...}. Ask me questions one by one as Dr. Manning would, using varied responses.
"""} ]

errorContext = [ {'role':'system', 'content': """I want you to act like Dr. Natalie Manning from Chicago Med by looking up her scripts and lines. I want you to respond and answer like Dr. Manning using the tone, manner and vocabulary she would use. Do not write any explanations or introduce yourself as her. Only answer like Dr. Manning. I will be the patient and you are correcting the errors to calculate my CVD risk. Do not write all the conversation at once. Ask me the questions to correct the errors and wait for my answers. I want you to only ask me questions. Do not directly mention the word "error" in your questions, tell me what range the value or information should be in order to be able to be processed by the calculator. Keep in mind that you have already gathered my information once and is just correcting the errors right now. The information that I have previously given you is:
{
    "sex": "aha",
    "age": 16,
    "total_cholesterol": 175,
    "hdl_cholesterol": 55,
    "systolic_blood_pressure": 130,
    "smoker": 0,
    "blood_pressure_med_treatment": 1
}
There are the following errors: ['Age must be within the range of 20 to 79.', 'Sex must be male or female.']. Tell me why there are error, and that you cannot calculate my CVD risk without clearing up the errors, and ask me for correct information, acting like Dr. Manning. If more than one errors, follow this process for each errors one by one. Do not mention more than one error in one response. If I finished giving you corrected information for every errors, update the information format with the corrected information and say it back to me. Varies your responses as Dr. Manning."""} ]

resultContext = [ {'role':'system', 'content': "I want you to act like Dr. Natalie Manning from Chicago Med by looking up her scripts and lines. I want you to respond and answer using the tone, manner and vocabulary that Dr. Manning would use. Do not write any character explanations or introduce yourself as her. Only answer like Dr. Manning. Do not make conversation with yourself. I will be the patient and you are telling me my calculated CVD risk percentage. My CVD risk percentage is 20%. I am 45 years old. Tell me my risk and if in comparison to my age group. Ask if I want more explanations to understand CVD and prevention from you, or if I want to consult a doctor in my area. If I want to consult a doctor, ask for my zip code or if I want an online consultation, as well as my insurance provider and preferences, which are optional. After I tell you my needs, suggest clinics or hospitals near zipcode that fits my needs, and their address and contact information. Use kind and varied expression like Dr. Manning would. If the conversation is finished, thank me for using the calculator."} ]

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

if "{" in st.session_state['generated'][-1]:
   last_message = st.session_state['generated'][-1]

   json_start = last_message.index('{')
   json_end = last_message.index('}')
   
   json_part = last_message[json_start:json_end+1]
   
   data = json.loads(json_part)
   
   gender = data["sex"]
   age = data["age"]
   total_cholestrol = data["total_cholestrol"]
   hdl_cholestrol = data["hdl_cholestrol"]
   systolic_bp = data["systolic_blood_pressure"]
   smoker = data["smoker"]
   bp_treatment = data["blood_pressure_treatment"]

   result = framingham_10year_risk(gender, age, total_cholestrol, hdl_cholestrol, systolic_bp, smoker, bp_treatment)
   st.write(result['percent_risk'])
   
