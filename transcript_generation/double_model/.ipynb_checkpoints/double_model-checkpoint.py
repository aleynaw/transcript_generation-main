import sys, os, csv, ast, random, time
from pathlib import Path
import pandas as pd
import time

from dotenv.main import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
openai_api_key = os.environ['OPENAI_API_KEY']

from openai import OpenAI

# print(Path.cwd())

# from synthetic_data_generator import helper_fns as helper
try:
    sys.path.append('../../transcript_creation')
    from transcript_creation import helper_fns as helper
except ModuleNotFoundError:
    import helper_fns as helper

####### gpt-4-turbo #######
model_name = "gpt-4-0125-preview"
pricing_in = 0.01 #per 1K tokens
pricing_out = 0.03 #per 1K tokens

##### OAI Model Information
###model_name = "gpt-3.5-turbo"
# model_name = "gpt-3.5-turbo-0125"
# pricing_in = 0.0005 #per 1K tokens
# pricing_out = 0.0015 #per 1K tokens

client1 = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=openai_api_key,
)

client2 = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=openai_api_key,
)

patient_temp = 0.5
asst_temp = 0.5

##### Prompt templates
starter_path = 'prompts/starter.txt'
questions_path = 'prompts/questionbank_v2.txt'
patient_prompt_path = 'prompts/double_model_prompts/patient_prompt.txt'
asst_prompt_path ='prompts/double_model_prompts/assistant_prompt_v2.txt'
tracking_path="./tracking.csv"

# starter_path = 'prompts/starter.txt'
# questions_path = 'prompts/questionbank_v1.txt'
# patient_prompt_path = 'prompts/double_model_prompts/patient_prompt.txt'
# asst_prompt_path ='prompts/double_model_prompts/assistant_prompt_v1.txt'
# tracking_path="./tracking_v2.csv"

##### directory for interview outputs
out_dir = "transcripts/DM"
# Path(out_dir).mkdir(parents = True, exist_ok = True)

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

def get_patient_response(message_list, prompt):
    '''
    model responds as a patient. 

    Parameters
    ----------
    message_list (list)
        message list with messages of dicts (with keys "role" and "content"). pass in list starting with an assistant message. e.g., with message_list[0][role] = "assistant".
    
    Returns
    -------
    patient_output (str)
        response of the model
    total_cost (float)
        cost of the total interaction
    '''
    #swap roles as "user" acts as an interviewer and "assistant" is the patient
    swapped_list = swap_msg_list(message_list)

    #add system commands
    system_msg = {"role": "system", "content": prompt}
    msgs = swapped_list.copy()
    #if number of tokens in input is very large, remove beginning messages (method for predicting input???)

    msgs.insert(0, system_msg)
    # print(msgs)

    #get completion
    patient_chat_completion = client1.chat.completions.create(
        messages=msgs,
        model=model_name,
        temperature=patient_temp,
    )
    patient_output = patient_chat_completion.choices[0].message.content
    tokens_in = int(patient_chat_completion.usage.prompt_tokens)
    tokens_out = int(patient_chat_completion.usage.completion_tokens)

    total_pricing = (tokens_in/1000)*pricing_in + (tokens_out/1000)*pricing_out

    return patient_output, total_pricing

def get_asst_response(message_list, prompt):
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
    total_cost (float)
        cost of the total interaction
    '''
    #add system commands
    system_msg = {"role": "system", "content": prompt}
    msgs = message_list.copy()
    msgs.insert(0, system_msg)
    # print(msgs)

    #get completion
    asst_chat_completion = client2.chat.completions.create(
        messages=msgs,
        model=model_name,
        temperature=asst_temp
    )
    asst_output = asst_chat_completion.choices[0].message.content
    tokens_in = int(asst_chat_completion.usage.prompt_tokens)
    tokens_out = int(asst_chat_completion.usage.completion_tokens)
    total_pricing = (tokens_in/1000)*pricing_in + (tokens_out/1000)*pricing_out

    return asst_output, total_pricing



def interview_gen(patient:dict,output_id:str, out_dir=out_dir, tracking_path=tracking_path):
    """
    creates interviews based on the patients that are passed in. makes a json role/content file and a txt file of the transcript, and updates the tracking file to include patient details and interview file name.

    Params
    ------
    patient (dict):
        dict containing patient information, with each patient having at minimum keys "Clinician Name" and "Appointment Date"
    output_id (str):
        string present in the output file
    """
    Path(out_dir).mkdir(parents = True, exist_ok = True)

    ##### Prompt templates
    patient_prompt_str = Path(patient_prompt_path).read_text()
    asst_prompt_str = Path(asst_prompt_path).read_text()
    starter_str = Path(starter_path).read_text()
    questions = Path(questions_path).read_text()

    ### hydrate starter
    clinician_name = patient["Clinician Name"]
    appt_date = patient["Appointment Date"]
    starter = starter_str.replace(r"{Clinician Name}", clinician_name)
    starter = starter.replace(r"{Date}", appt_date)

    ### hydrate assistant prompt
    asst_prompt = asst_prompt_str.replace(r"{questions}", questions)

    ### hydrate patient prompt
    if "Edge Case Scenario" in patient: #if there is an edge case
        edge_case = patient["Edge Case Scenario"]
        patient_prompt_str = patient_prompt_str.replace(r"{edge_case_scenario}", f"\n\n{edge_case}")
        ignore_keys=["Clinician Name", "Appointment Date", 'Conversational Tone', 'Reason for Appointment']
    else: #if there is no edge case
        edge_case = ""
        patient_prompt_str = patient_prompt_str.replace(r"{edge_case_scenario}", "")
        ignore_keys=["Clinician Name", "Appointment Date", 'Conversational Tone', "Edge Case Scenario", 'Reason for Appointment']
    
    patient_string = helper.patient_to_str(patient, ignore_keys)
    patient_prompt = patient_prompt_str.replace(r"{patient_info}", patient_string)

    ### begin with starter message
    message_list_starter = [
        {"role": "assistant", "content": starter,}
    ]
    message_list = message_list_starter

    #conduct the interview between two models until <STOP> condition is reached
    stop_condition = False
    total_cost = 0
    start = time.time()
    while not stop_condition:
        time.sleep(1)
        patient_output,patient_cost = get_patient_response(message_list, patient_prompt)
        message_list = update_msg_list(message_list, is_assistant=False, content=patient_output)
        total_cost += patient_cost
        #print("Patient:",patient_output)

        asst_output, asst_cost = get_asst_response(message_list, asst_prompt)
        total_cost += asst_cost
        message_list = update_msg_list(message_list, is_assistant=True, content=asst_output)
        #print("Assistant:",asst_output)
        stop_condition = "<STOP>" in asst_output
    end = time.time()
    time_taken = end-start
    print("total time taken:", time_taken)
    print("total cost for generating interview:", total_cost)

    #remove last two messages if "<STOP>" is the only content in the last message
    if message_list[-1]["content"].replace("<STOP>", "").strip() == "":
        message_list = message_list[:-2]
    else:
    #remove "<STOP>" statement
        cleaned_final_msg = {
            "role": "assistant",
            "content": message_list[-1]["content"].replace("<STOP>", "").strip()
            }
        message_list.pop()
        message_list.append(cleaned_final_msg)
    
    #save to json file
    # out_path = time.strftime("DM_%Y%m%d-%H%M%S_Interview")
    out_path = f"DM_{output_id}_Interview"
    helper.write_list_to_json(message_list, Path(out_dir,out_path + ".json"))
    try:
        #convert json to string and save as txt
        helper.write_str_to_txt(
            string=helper.transcript_json_to_str(
                Path(out_dir,out_path + ".json"),
                msg_separator="\n\n"),
            filepath=Path(out_dir,out_path + ".txt"))
    except Exception as e:
        print(e)
        messages_str='\n\n'.join(message_list)
        with open(str(Path(out_dir,out_path + ".txt")), "w") as text_file:
            text_file.write(messages_str)

    #update general csv
    helper.track_patient(
        interview_path=Path(out_path + ".json"),
        patient_str=patient_string,
        extra_info_dict={
            "total_cost": total_cost,
            "patient_temp": patient_temp,
            "assistant_temp": asst_temp,
            "time": time_taken,
            "edge_case": edge_case,
            "llm_model": model_name,
        },
        tracking_path=tracking_path)

# if __name__ == '__main__':
#     patients_df = pd.read_csv("../synthetic_data_generator/patients.csv", sep="|")
#     patients = [patient for idx, patient in patients_df.iterrows()] #each patient is a series
#     ##### select specific patient if desired
#     # patients = [patients[3]]
#     interview_gen(patients)