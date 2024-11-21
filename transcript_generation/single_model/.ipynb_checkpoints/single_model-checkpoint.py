import os, sys
import random
import time
import pandas as pd
from dotenv.main import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
openai_api_key = os.environ['OPENAI_API_KEY']

from openai import OpenAI
from pathlib import Path

try:
    sys.path.append('../../transcript_creation')
    from transcript_creation import helper_fns as helper
except ModuleNotFoundError:
    import helper_fns as helper

# from pgen.patient_creator import patient_creator
# from pgen.patient_creator import get_clinician_name
# from pgen.patient_creator import get_appt_date

#### OAI Models
# Use llm_davinci for testing, less output tokens but cheaper)

####### gpt-4 #######
# model_name = "gpt-4"
# pricing_in = 0.03 #per 1K tokens
# pricing_out = 0.06 #per 1K tokens

####### gpt-4-turbo #######
model_name = "gpt-4-0125-preview"
pricing_in = 0.01 #per 1K tokens
pricing_out = 0.03 #per 1K tokens

####### gpt-3.5-turbo #######
###model_name = "gpt-3.5-turbo"
# model_name = "gpt-3.5-turbo-0125"
# pricing_in = 0.0005 #per 1K tokens
# pricing_out = 0.0015 #per 1K tokens

client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key=openai_api_key,
)

##### Prompt templates
starter_path = Path('prompts/starter.txt')
questions_path = Path('prompts/questionbank_v2.txt')
interview_path = Path('prompts/single_model_prompts/interview_prompt_v2.txt')
tracking_path = Path("./tracking.csv")
out_dir="transcripts/SM"

# starter_path = Path('prompts/starter.txt')
# questions_path = Path('prompts/questionbank_v1.txt')
# interview_path = Path('prompts/single_model_prompts/interview_prompt_v1.txt')
# tracking_path = Path("./tracking_v1.csv")
# out_dir="transcripts/SM"

def oai_interview_gen(patient:dict, temp = 0.5):
    '''
    Parameters
    ----------
    patient (dict):
        dict containing patient information, with each patient having at minimum keys "Clinician Name" and "Appointment Date"
    temp (float):
        temperature of the model

    Returns
    -------
    messages_list (list):
        a list of strings, representing back and forth conversation split by \n\n. starts with the assistant starter.
    oai_response (str):
        string output of the model response.
    temp (float):
        temperature of the model to generate the response (between 0-2)
    total_tokens (int):
        tokens used to generate total outcome
    total_cost (float):
        total cost of the API in dollars
    '''"transcripts/SM"
    #### prompts
    interview_gen = interview_path.read_text()
    questions = questions_path.read_text()
    starter = starter_path.read_text()

    clinician_name = patient["Clinician Name"]
    appt_date = patient["Appointment Date"]
    
    if "Edge Case Scenario" in patient:
        edge_case = patient["Edge Case Scenario"]
        interview_gen = interview_gen.replace(r"{edge_case_scenario}", f"\n\n{edge_case}")
        ignore_keys=["Clinician Name", "Appointment Date",  'Conversational Tone', "Edge Case Scenario", 'Reason for Appointment']
    else:
        edge_case = ""
        interview_gen = interview_gen.replace(r"{edge_case_scenario}", "")
        ignore_keys=["Clinician Name", "Appointment Date",  'Conversational Tone', 'Reason for Appointment']
    patient_str = helper.patient_to_str(patient, ignore_keys)

    ### hydrate the prompt
    starter = starter.replace(r"{Clinician Name}", clinician_name)
    starter = starter.replace(r"{Date}", appt_date)

    interview_gen = interview_gen.replace(r"{questions}", questions)
    interview_gen = interview_gen.replace(r"{interview_starter}", starter)
    interview_gen = interview_gen.replace(r"{patient_info}", patient_str)

    # if temp == "":
    #     temp = round((random.random())*0.5,2)+0.9 #ranges between 0.9-1.4
    
    ### get response from model
    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": interview_gen,}
        ],
        model=model_name,
        temperature=temp,
        # max_tokens=1600,
    )

    tokens_in = response.usage.prompt_tokens
    tokens_out = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    total_cost = (tokens_in/1000)*pricing_in + (tokens_out/1000)*pricing_out

    oai_response = response.choices[0].message.content

    complete_interview = oai_response
    messages_list = complete_interview.split("\n\n") #messages are separated by \n\n
    
    messages_list = helper.remove_duplicate_starters(messages_list)
    
    #insert messages accordingly
    messages_list.insert(0, f"Assistant: {starter}")
    # messages_list.insert(0, "User: (Patient has entered the chat.)")
    # messages_list.insert(0, f"System: {interview_gen}")
    
    return messages_list, oai_response, temp, total_tokens, total_cost

def interview_gen(patient:dict, output_id:str, out_dir=out_dir, tracking_path=tracking_path):
    '''
    create an interview using the single model generation method.

    Parameters
    ----------
    patient (dict):
        dict containing patient information, with each patient having at minimum keys "Clinician Name" and "Appointment Date"
    temp (float):
        temperature of the model
    '''
    ### get oai transcript
    start = time.time()
    messages_list, oai_response, temp, total_tokens, total_cost = oai_interview_gen(patient=patient)
    end = time.time()
    time_taken = end-start
    print("total cost for generating interview:", total_cost)
    print("total time taken:", time_taken)

    ### save transcript
    Path(out_dir).mkdir(parents = True, exist_ok = True)
    out_path = f"SM_{output_id}_Interview"

    #convert json to string and save as txt
    try:
        json_msg_list = helper.create_json_obj(messages_list)
        helper.write_list_to_json(json_msg_list, Path(out_dir,out_path + ".json"))
        helper.write_str_to_txt(
            string=helper.transcript_json_to_str(
                Path(out_dir,out_path + ".json"),
                msg_separator="\n\n"),
            filepath=Path(out_dir,out_path + ".txt"))
        
        patient_string = helper.patient_to_str(patient, ignore_keys=["Clinician Name", "Appointment Date", "Reason for Appointment"])
        try:
            patient_edge_case = patient["Edge Case Scenario"]
        except Exception as e:
            patient_edge_case = ""
        
    except Exception as e:
        print(e)
        with open(str(Path(out_dir,out_path + ".txt")), "w") as text_file:
            text_file.write(oai_response)
    
    #update general csv
    helper.track_patient(
        interview_path=Path(out_path + ".json"),
        patient_str=patient_string,
        extra_info_dict={
            "total_cost": total_cost,
            "temp": temp,
            "time": time_taken,
            "edge_case": patient_edge_case,
            "llm_model": model_name,
        },
        tracking_path=tracking_path)
    
    

def oai_summary_gen(transcript,
                temp=0.5,
        summary_path = 'prompts/summary_prompt.txt',
        template_path = 'prompts/summarization_template.txt',
        example_path = 'prompts/summary_example.txt'):
    '''
    Parameters
    ----------
    transcript (str)
        string of the transcript contents
    temperature (float)
        float between (0,2) for the model
    summary_path (str)
        path to prompt to be fed into OpenAI
    template_path (str)
        path to summarization template for the optional{template} field in the summary prompt
    example_path (str)
        path to an example for the optional {example} field in the summary prompt

    Returns
    -------
    oai_summary (str)
        formatted summary of the contents in the transcript
    temp (str)
        temperature of the model to generate the response (between 0-2)
    s_total_tokens (str)
        tokens used to generate total outcome
    s_total_cost (str)
        total cost of the API in dollars
    '''
    #import prompt
    summary_gen = Path(summary_path).read_text()
    template = Path(template_path).read_text()
    example = Path(example_path).read_text()

    #hydrate prompt
    summary_gen = summary_gen.replace(r"{template}", template)
    summary_gen = summary_gen.replace(r"{transcript}", transcript)
    summary_gen = summary_gen.replace(r"{example}", example)

    #call openAI
    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": summary_gen,}
        ],
        model=model_name,
        temperature=temp,
    )

    oai_summary = response.choices[0].message.content

    s_tokens_in = response.usage.prompt_tokens
    s_tokens_out = response.usage.completion_tokens
    s_total_tokens = str(response.usage.total_tokens)
    s_total_cost = str((s_tokens_in/1000)*pricing_in + (s_tokens_out/1000)*pricing_out)

    return oai_summary, temp, s_total_tokens, s_total_cost