import sys, os, csv, ast, random, time
from pathlib import Path
import pandas as pd
import time

# print(Path.cwd())

# from synthetic_data_generator import helper_fns as helper
try:
    sys.path.append('../../transcript_creation')
    from transcript_creation import helper_fns as helper
except ModuleNotFoundError:
    import helper_fns as helper

# import Langchain and Ollama
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# import ollama
# from ollama import Client
# client = Client(host='http://localhost:11435')

model1 = OllamaLLM(base_url="localhost:11435", model="llama3.1:70b-instruct-q4_0", temperature=0.3)
model2 = OllamaLLM(base_url="localhost:11435", model="llama3.1:70b-instruct-q4_0", temperature=0.3)

# model1 = "llama3.1:70b-instruct-q4_0"
# model2 = "llama3.1:70b-instruct-q4_0"

# model1_temp = 0.2
# model2_temp = 0.2


##### Prompt templates
starter_path = 'prompts/starter.txt'
questions_path = 'prompts/questions_test/Analysis/questions_1.txt'
patient_prompt_path = 'prompts/double_model_prompts/INSTRUCT/patient_prompt_v1.txt'
asst_prompt_path = 'prompts/double_model_prompts/INSTRUCT/assistant_prompt_v2.txt'
tracking_path = "./tracking.csv"

##### directory for interview outputs
out_dir = "transcripts/DM"
# Path(out_dir).mkdir(parents=True, exist_ok=True)

##############################
# HELPER FUNCTIONS
##############################

def update_msg_list(message_list, is_assistant, content):
    role = "assistant" if is_assistant else "user"
    message_list.append({"role": role, "content": content})
    return message_list

def swap_msg_list(message_list):
    '''Return the message list with Assistant/User role labels inversed.'''
    swapped_msg_list = []
    for msg in message_list:
        if msg["role"] == "assistant":
            swapped_msg_list.append({
                "role": "user",
                "content": msg["content"]
            })
        if msg["role"] == "user":
            swapped_msg_list.append({
                "role": "assistant",
                "content": msg["content"]
            })
    return swapped_msg_list

def extract_response_text(response):
    """
    Extract the portion of the response after 'RESPONSE:'.
    If 'RESPONSE:' is not found, return the whole response.
    """
    split_key = "RESPONSE:"
    if split_key in response:
        return response.split(split_key)[-1].strip()  # Take everything after 'RESPONSE:'
    else:
        return response.strip()  # Return the whole response if 'RESPONSE:' is missing

##############################
# INVOKING MODEL FUNCTIONS
##############################

def invoke_asst_model(message_list, prompt):
    '''
    model responds as an interviewer. 

    Parameters
    ----------
    message_list (list)
        message list with messages of dicts (with keys "role" and "content"). pass in list starting with an assistant message. e.g., with message_list[0][role] = "assistant".
    
    Returns
    -------
    patient_output (str)
        response of the model
    '''
    
    # add system commands
    system_msg = {"role": "system", "content": prompt}
    msgs = message_list.copy()
    msgs.insert(0, system_msg)
    # print(msgs)
    
    response = model1.invoke(msgs)
    # response = client.chat(
    #     prompt=msgs,
    #     model=model1,
    #     options=dict(temperature=model1_temp)
    # )
    
    # response = response['message']['content']
    print("------------------------------------------------------------")
    print("Assistant response: ", response)
    
    # Extract only the part after 'RESPONSE:'
    extracted_response = extract_response_text(response)
    print()
    print("Assistant extracted response: ", extracted_response)
    
    return extracted_response       

patient_msgs = []

def invoke_pat_model(message_list, prompt):
    '''
    model responds as a patient. 

    Parameters
    ----------
    message_list (list)
        message list with messages of dicts (with keys "role" and "content"). pass in list starting with an assistant message. 
        e.g., with message_list[0][role] = "assistant".
    
    Returns
    -------
    patient_output (str)
        response of the model
    total_cost (float)
        cost of the total interaction
    '''
    
    # swap roles as "user" acts as an interviewer and "assistant" is the patient
    swapped_list = swap_msg_list(message_list)
    
    # add system commands
    system_msg = {"role": "system", "content": prompt}
    msgs = swapped_list.copy()
    # if number of tokens in input is very large, remove beginning messages (method for predicting input???)

    msgs.insert(0, system_msg)
    
    response = model2.invoke(msgs)
    # response = client.chat(
    #     messages=msgs,
    #     model=model2,
    #     options=dict(temperature=model2_temp)
    # )
    # response = response['message']['content']
    print("------------------------------------------------------------")
    print("Patient response: ", response)
    
    # Extract only the part after 'RESPONSE:'
    extracted_response = extract_response_text(response)
    print()
    print("Patient extracted response: ", extracted_response)
    
    patient_msgs.append(extracted_response)
    print("Patient Messages: ", patient_msgs)
    
    return extracted_response 

##############################

# Function to facilitate the conversation
def chat_between_models(message_list, asst_prompt, patient_prompt, starter):
    # conduct the interview between two models until <STOP> condition is reached
    
    questions = Path(questions_path).read_text()
    asst_prompt = asst_prompt_str.replace(r"{questions}", questions)
    
    
    stop_condition = False
    turns = 0
    start = time.time()
    error_condition = False
    max_turns = 15
    
    while not stop_condition and turns < max_turns:
        time.sleep(1)
        
        # Construct the full prompt for the patient
        # print("Getting patient response...")
        # print(patient_prompt)
        patient_response = invoke_pat_model(message_list, patient_prompt)
        message_list = update_msg_list(message_list, is_assistant=False, content=patient_response)
        
        
        # Construct the full prompt for the interviewer
        # print("Getting assistant response...")
        if turns > 11:
            print("ALL LLM INPUT: ", message_list, asst_prompt)
        asst_response = invoke_asst_model(message_list, asst_prompt)
        message_list = update_msg_list(message_list, is_assistant=True, content=asst_response)
        
        print("Turn count: ", turns)

        stop_condition = (
            "Summary:" in asst_response or
            "To summarize:" in asst_response or
            "<STOP>" in asst_response
        )
        turns += 1
        
#     while turns < 8:
#         time.sleep(1)
        
#         # Construct the full prompt for the patient
#         print()
#         # print("PATIENT PROMPT: ")
#         # print(patient_prompt)
#         # print()
#         # print("MESSAGE LIST: ")
#         # print(message_list)
#         patient_response = invoke_pat_model(message_list, patient_prompt)
#         message_list = update_msg_list(message_list, is_assistant=False, content=patient_response)
        
#         # Construct the full prompt for the interviewer
#         # print("Getting assistant response...")
#         print()
#         # print("ASSISTANT PROMPT: ")
#         # print(asst_prompt)
#         # print()
#         # print("MESSAGE LIST: ")
#         # print (message_list)
#         asst_response = invoke_asst_model(message_list, asst_prompt)
#         message_list = update_msg_list(message_list, is_assistant=True, content=asst_response)
        
#         # error_condition = "Let's proceed with the interview" in asst_response
#         # print("ERROR: ASSISTANT OFF TRACK")
#         print("Turn count: ", turns)
#         # turns = 8

#         stop_condition = "<STOP>" in asst_response
#         turns += 1
        
    end = time.time()
    time_taken = end - start
    print("INTERVIEW HAS ENDED")
    print("SYSTEM: ")
    print("total time taken: ", time_taken)
    print("total tokens: ")
    return message_list

def interview_gen(patient: dict, output_id: str, out_dir=out_dir, tracking_path=tracking_path):
    """
    creates interviews based on the patients that are passed in. makes a json role/content file and a txt file of the transcript, and updates the tracking file to include patient details and interview file name.

    Params
    ------
    patient (dict):
        dict containing patient information, with each patient having at minimum keys "Clinician Name" and "Appointment Date"
    output_id (str):
        string present in the output file
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    ##### Prompt templates
    patient_prompt_str = Path(patient_prompt_path).read_text()
    asst_prompt_str = Path(asst_prompt_path).read_text()
    starter_str = Path(starter_path).read_text()
    # questions = Path(questions_path).read_text()

    ### hydrate starter
    clinician_name = patient["Clinician Name"]
    appt_date = patient["Appointment Date"]
    starter = starter_str.replace(r"{Clinician Name}", clinician_name)
    starter = starter.replace(r"{Date}", appt_date)

    ### hydrate assistant prompt
    # asst_prompt = asst_prompt_str.replace(r"{questions}", questions)

    ### hydrate patient prompt
    if "Edge Case Scenario" in patient:  # if there is an edge case
        edge_case = patient["Edge Case Scenario"]
        patient_prompt_str = patient_prompt_str.replace(r"{edge_case_scenario}", f"\n\n{edge_case}")
        ignore_keys = ["Clinician Name", "Appointment Date", 'Conversational Tone', 'Reason for Appointment']
    else:  # if there is no edge case
        edge_case = ""
        patient_prompt_str = patient_prompt_str.replace(r"{edge_case_scenario}", "")
        ignore_keys = ["Clinician Name", "Appointment Date", 'Conversational Tone', "Edge Case Scenario", 'Reason for Appointment']
    
    patient_string = helper.patient_to_str(patient, ignore_keys)
    patient_prompt = patient_prompt_str.replace(r"{patient_info}", patient_string)

    ### begin with starter message
    message_list_starter = [
        {"role": "assistant", "content": starter}
    ]
    message_list = message_list_starter
    
    # Run the chat
    conversation = chat_between_models(message_list, asst_prompt, patient_prompt, message_list)
    for message in conversation:
        print(message["content"])


# import sys, os, csv, ast, random, time
# from pathlib import Path
# import pandas as pd
# import time


# # print(Path.cwd())

# # from synthetic_data_generator import helper_fns as helper
# try:
#     sys.path.append('../../transcript_creation')
#     from transcript_creation import helper_fns as helper
# except ModuleNotFoundError:
#     import helper_fns as helper

# # Import Langchain and Ollama
# from langchain_ollama import OllamaLLM
# from langchain_core.prompts import ChatPromptTemplate

# model1 = OllamaLLM(model="llama3.1:8b", temperature = 0.5)
# model2 = OllamaLLM(model="llama3.1:8b", temperature = 0.5)

# ##### Prompt templates
# starter_path = 'prompts/starter.txt'
# questions_path = 'prompts/questionbank_v2.txt'
# patient_prompt_path = 'prompts/double_model_prompts/patient_prompt.txt'
# asst_prompt_path ='prompts/double_model_prompts/assistant_prompt_v2.txt'
# tracking_path="./tracking.csv"

# ##### directory for interview outputs
# out_dir = "transcripts/DM"
# # Path(out_dir).mkdir(parents = True, exist_ok = True)

# ##############################
# # HELPER FUNCTIONS
# ##############################

# def update_msg_list(message_list, is_assistant, content):
#     role = "assistant" if is_assistant else "user"
#     message_list.append({"role": role, "content": content})
#     return message_list

# def swap_msg_list(message_list):
#     '''Return the message list with Assistant/User role labels inversed.'''
#     swapped_msg_list = []
#     for msg in message_list:
#         if msg["role"] == "assistant":
#             swapped_msg_list.append({
#                 "role": "user",
#                 "content": msg["content"]
#             })
#         if msg["role"] == "user":
#             swapped_msg_list.append({
#                 "role": "assistant",
#                 "content": msg["content"]
#             })
#     return swapped_msg_list

# ##############################
# # INVOKING MODEL FUNCTIONS
# ##############################

# def invoke_asst_model(message_list, prompt):
#     '''
#     model responds as an interviewer. 

#     Parameters
#     ----------
#     message_list (list)
#         message list with messages of dicts (with keys "role" and "content"). pass in list starting with an assistant message. e.g., with message_list[0][role] = "assistant".
    
#     Returns
#     -------
#     patient_output (str)
#         response of the model
#     '''
    
#     #add system commands
#     system_msg = {"role": "system", "content": prompt}
#     msgs = message_list.copy()
#     msgs.insert(0, system_msg)
#     # print(msgs)
    
    
#     response = model1.invoke(msgs)
#     print("Assistant response: ", response)
    
#     return response       


# def invoke_pat_model(message_list, prompt):
#      '''
#     model responds as a patient. 

#     Parameters
#     ----------
#     message_list (list)
#         message list with messages of dicts (with keys "role" and "content"). pass in list starting with an assistant message. 
#         e.g., with message_list[0][role] = "assistant".
    
#     Returns
#     -------
#     patient_output (str)
#         response of the model
#     total_cost (float)
#         cost of the total interaction
#     '''
    
#     #swap roles as "user" acts as an interviewer and "assistant" is the patient
#     swapped_list = swap_msg_list(message_list)
    
#     #add system commands
#     system_msg = {"role": "system", "content": prompt}
#     msgs = swapped_list.copy()
#     #if number of tokens in input is very large, remove beginning messages (method for predicting input???)

#     msgs.insert(0, system_msg)
    
    
#     response = model2.invoke(msgs)
#     print("Patient response: ", response)
    
#     return response 

# ##############################

# # Function to facilitate the conversation
# def chat_between_models(message_list, asst_prompt, patient_prompt, starter):
    
#     #conduct the interview between two models until <STOP> condition is reached
#     stop_condition = False
#     # turns = 0
#     start = time.time()
    
        
#     while not stop_condition:
#         time.sleep(1)
        
#         # Construct the full prompt for the patient
#         print("Getting patient response...")
#         # print(patient_prompt)
#         patient_response = invoke_pat_model(message_list, patient_prompt)
#         message_list = update_msg_list(message_list, is_assistant=False, content=patient_response)
        
#         # Construct the full prompt for the interviewer
#         print("Getting assistant response...")
#         asst_response = invoke_asst_model(message_list, asst_prompt)
#         message_list = update_msg_list(message_list, is_assistant=True, content=asst_response)

        
        
#         stop_condition = "<STOP>" in assistant_response
#         # turns += 1
        
#     end= time.time()
#     time_taken = end-start
#     print("total time taken: ", time_taken)
#     print("total tokens: ")
#     return message_list



# def interview_gen(patient:dict,output_id:str, out_dir=out_dir, tracking_path=tracking_path):
#     """
#     creates interviews based on the patients that are passed in. makes a json role/content file and a txt file of the transcript, and updates the tracking file to include patient details and interview file name.

#     Params
#     ------
#     patient (dict):
#         dict containing patient information, with each patient having at minimum keys "Clinician Name" and "Appointment Date"
#     output_id (str):
#         string present in the output file
#     """
#     Path(out_dir).mkdir(parents = True, exist_ok = True)

#     ##### Prompt templates
#     patient_prompt_str = Path(patient_prompt_path).read_text()
#     asst_prompt_str = Path(asst_prompt_path).read_text()
#     starter_str = Path(starter_path).read_text()
#     questions = Path(questions_path).read_text()

#     ### hydrate starter
#     clinician_name = patient["Clinician Name"]
#     appt_date = patient["Appointment Date"]
#     starter = starter_str.replace(r"{Clinician Name}", clinician_name)
#     starter = starter.replace(r"{Date}", appt_date)

#     ### hydrate assistant prompt
#     asst_prompt = asst_prompt_str.replace(r"{questions}", questions)

#     ### hydrate patient prompt
#     if "Edge Case Scenario" in patient: #if there is an edge case
#         edge_case = patient["Edge Case Scenario"]
#         patient_prompt_str = patient_prompt_str.replace(r"{edge_case_scenario}", f"\n\n{edge_case}")
#         ignore_keys=["Clinician Name", "Appointment Date", 'Conversational Tone', 'Reason for Appointment']
#     else: #if there is no edge case
#         edge_case = ""
#         patient_prompt_str = patient_prompt_str.replace(r"{edge_case_scenario}", "")
#         ignore_keys=["Clinician Name", "Appointment Date", 'Conversational Tone', "Edge Case Scenario", 'Reason for Appointment']
    
#     patient_string = helper.patient_to_str(patient, ignore_keys)
#     patient_prompt = patient_prompt_str.replace(r"{patient_info}", patient_string)

#     ### begin with starter message
#     message_list_starter = [
#         {"role": "assistant", "content": starter,}
#     ]
#     message_list = message_list_starter
    
#     # Run the chat
#     conversation = chat_between_models(message_list, asst_prompt, patient_prompt, message_list)
#     for message in conversation:
#         print(message["content"])
   

        





# """ what you're doing rn--

# you are trying to create two separate history lists so that the assistant doesn't have access to the patient's prompt
# and vice versa

# last error was a complaint that invoke cannot take in lists... but we know it can? it has in the past with messages
# look into reforming the input into invoke_chat_model to see what is actually being put in there, possibly change to
# two separate invoke functions, one for each model.

# """
