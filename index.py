import streamlit as st
import openai
from framingham10yr.framingham10yr import framingham_10year_risk 

# pip install streamlit-chat  
from streamlit_chat import message

"""
# Welcome to the Heart Disease Risk Calculator!

This chatbot is here to help you understand your risk of heart disease. This is a serious topic; please do not use this calculator for fun.

Answer the questions one by one, and if you have any questions for the chatbot, go ahead and ask them. Once you get your results back, we will provide you with some next steps and resources to follow.

Please contact us if you have any questions!
"""
def framingham(datai): #get risk calculator result from dictionary (return a dictionary)
    return framingham_10year_risk(sex=datai['sex'], age=datai['age'], total_cholesterol=datai['total_cholesterol'], hdl_cholesterol=datai['hdl_cholesterol'],  systolic_blood_pressure=datai['systolic_blood_pressure'], smoker=datai['smoker'], blood_pressure_med_treatment=datai['blood_pressure_med_treatment'])

openai.api_key = st.secrets["openai"]

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]
    
# # Creating the chatbot interface
# st.title("Heart Disease Risk Chatbot")

# # Storing the chat

# if 'past' not in st.session_state:
#     st.session_state['past'] = []

# if 'generated' not in st.session_state:
#     st.session_state['generated'] = []

# # We will get the user's input by calling the get_text function
# def get_text():
#     input_text = st.text_input("You: ","", key="input")
#     return input_text

# user_input = get_text()

# if user_input:
#     output = generate_response(user_input)
#     # store the output 
#     st.session_state.generated.append(output)
#     st.session_state.past.append(user_input)

# if st.session_state['generated']:
    
#     for i in range(len(st.session_state['generated'])-1, -1, -1):
#         message(st.session_state["generated"][i], key=str(i))
#         message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')


def collect_messages(_):
    prompt = inp.value_input
    inp.value = ''
    context.append({'role':'user', 'content':f"{prompt}"})
    response = get_completion_from_messages(context) 
    context.append({'role':'assistant', 'content':f"{response}"})
    panels.append(
        pn.Row('User:', pn.pane.Markdown(prompt, width=600)))
    panels.append(
        pn.Row('Assistant:', pn.pane.Markdown(response, width=600, styles={'background-color': '#F6F6F6'})))
 
    return pn.Column(*panels)

context = [ {'role':'system', 'content':"""
Assume the role of a medical assistant. Please obtain the following information from your user, who is your patient, and fill in the JSON structure below. Obtain each property one-by-one so your patient doesn't feel overwhelmed, using questions that reflect a kind medical assistant.
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
If patient don't know following information, use the following number, adjust accordingly if they say that it is low or high. Also, provide information about clinics near them where they can obtain the information:
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
ASK ME, THE USER, QUESTIONS ONE BY ONE!
"""} ]  # accumulate messages


inp = pn.widgets.TextInput(value="Hi", placeholder='Enter text here…')
button_conversation = pn.widgets.Button(name="Chat!")

interactive_conversation = pn.bind(collect_messages, button_conversation)

dashboard = pn.Column(
    inp,
    pn.Row(button_conversation),
    pn.panel(interactive_conversation, loading_indicator=True, height=300),
)

dashboard

messages =  context.copy()
messages.append(
{'role':'system', 'content':'create a json summary of the previous food order. Itemize the price for each item\
 The fields should be 1) pizza, include size 2) list of toppings 3) list of drinks, include size   4) list of sides include size  5)total price '},    
)
 #The fields should be 1) pizza, price 2) list of toppings 3) list of drinks, include size include price  4) list of sides include size include price, 5)total price '},    

response = get_completion_from_messages(messages, temperature=0)
print(response)

#CATCHING ERROR PART
def chat_with_gpt(message):
    completion = openai.Completion.create(
        engine="text-davinci-003",  # Use the GPT-3.5 model
        prompt=message,
        max_tokens=50,  # Control the response length
        n=1,  # Generate a single response
        stop=None,  # Stop generating after this token
        temperature=0.7,  # Control the randomness of the response
    )

    response = completion.choices[0].text.strip()
    return response

def identify_error(message, json):
    response = chat_with_gpt("the JSON object is the following: " + str(json) +" there are these following errors: "+ str(message)+ "please tell me which property in the JSON object have an error")
    properties = ["sex","age","total_cholesterol","hdl_cholesterol","systolic_blood_pressure","smoker","blood_pressure_med_treatment"]
    errors = []
    for item in properties:
        if item in response:
            errors.append(item)
    return errors

def fix(message, info):
    info = {}
    original = info
    # Start the conversation with the user
    errors = identify_error(message,info)
    
    x = 0
    for error in errors:
        initial = "Assume the role of a kind medical assistant collecting info from your patient/user to calculate CVD risk. There is an error: " + message[x] + ". Tell the patient of the error and ask them for new, correct answer. If the patient tell you the corrected answer, please say '123DONE' [ASK ME, YOUR USER!]"
        response = chat_with_gpt(initial)
        while ('123DONE' not in response) :
            print (response)
            user_i = input("User: ")
            response = chat_with_gpt(user_i)
        endpoint = find("123DONE")
        print(response[0:endpoint])
        response = chat_with_gpt("What is the corrected value for " + error + " from the user? Answer with just the value e.g. '56'"")
        json[error] = response
        x += 1
    return info

while (result['status'] == 422) :
    data = fix(result['errors'], data)
    result = framingham(data)

"""
Here is some information on the ASCVD Risk Calculator:

ASCVD: atherosclerotic cardiovascular disease, defined as coronary death or nonfatal myocardial infarction, or fatal or nonfatal stroke

Lifetime ASCVD Risk:

Estimates of lifetime risk for ASCVD are provided for adults 20 through 59 years of age and are shown as the lifetime risk for ASCVD for a 50-year-old without 
ASCVD who has the risk factor values entered at the initial visit. Because the primary use of these lifetime risk estimates is to facilitate the very important discussion 
regarding risk reduction through lifestyle change, the imprecision introduced is small enough to justify proceeding with lifestyle change counseling informed by these results.
"""
