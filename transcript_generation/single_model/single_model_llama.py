import os
import sys
import random
import time
from pathlib import Path
import pandas as pd
# from dotenv.main import load_dotenv, find_dotenv

# load_dotenv(find_dotenv())

try:
    sys.path.append('../../transcript_creation')
    from transcript_creation import helper_fns as helper
except ModuleNotFoundError:
    import helper_fns as helper

# Import Langchain and Ollama
from langchain_ollama import OllamaLLM
from langchain_core.prompts import BasePromptTemplate

# Ollama client setup
model = OllamaLLM(model="llama3.1:8b")

# Define the paths for your prompts
starter_path = Path('prompts/starter.txt')
questions_path = Path('prompts/questionbank_v2.txt')
interview_path = Path('prompts/single_model_prompts/interview_prompt_v2.txt')
tracking_path = Path("./tracking.csv")
out_dir = "transcripts/SM"

def oai_interview_gen(patient: dict, temp=0.5):
    """
    Generate interview using Llama model.

    Parameters
    ----------
    patient (dict): Patient information.
    temp (float): Temperature of the model.

    Returns
    -------
    messages_list (list): List of conversation strings.
    oai_response (str): Model response.
    temp (float): Model temperature.
    total_tokens (int): Total tokens used.
    total_cost (float): Total cost of the API in dollars.
    """
    # Read prompts
    interview_gen = interview_path.read_text()
    questions = questions_path.read_text()
    starter = starter_path.read_text()
    
    print("Interview generation instructions:", interview_gen)
    print("Questions:", questions)
    print("Starter:", starter)

    clinician_name = patient["Clinician Name"]
    appt_date = patient["Appointment Date"]
    
    print("Clinician Name:", clinician_name)
    print("Appt Date:", appt_date)

    if "Edge Case Scenario" in patient:
        edge_case = patient["Edge Case Scenario"]
        interview_gen = interview_gen.replace(r"{edge_case_scenario}", f"\n\n{edge_case}")
        ignore_keys = ["Clinician Name", "Appointment Date", 'Conversational Tone', "Edge Case Scenario", 'Reason for Appointment']
    else:
        edge_case = ""
        interview_gen = interview_gen.replace(r"{edge_case_scenario}", "")
        ignore_keys = ["Clinician Name", "Appointment Date", 'Conversational Tone', 'Reason for Appointment']
        
    patient_str = helper.patient_to_str(patient, ignore_keys)

    # Hydrate prompts
    starter = starter.replace(r"{Clinician Name}", clinician_name)
    starter = starter.replace(r"{Date}", appt_date)

    interview_gen = interview_gen.replace(r"{questions}", questions)
    interview_gen = interview_gen.replace(r"{interview_starter}", starter)
    interview_gen = interview_gen.replace(r"{patient_info}", patient_str)
    
    print()
    print()
    # print("New Interview Gen:", interview_gen)
    list_intgen = [interview_gen]
    
    print("Listgen:", list_intgen)

    # Get response from model
    response = model.generate(list_intgen)
    
    print()
    print()
    print()
    # print(response)

    # Access the text directly from the response object
    oai_response = response.generations[0][0].text  # Adjust as needed
    
    print(oai_response)

    complete_interview = oai_response
    messages_list = complete_interview.split("\n\n")

    messages_list = helper.remove_duplicate_starters(messages_list)

     # Insert messages accordingly
    messages_list.insert(0, f"Assistant: {starter}")
    # messages_list.insert(0, "User: (Patient has entered the chat.)")
    # messages_list.insert(0, f"System: {interview_gen}")
    
    print()
    print()
    print(messages_list)

#     # Token and cost tracking may need to be adapted if Llama provides these details differently
    total_tokens = len(complete_interview.split())  # Basic token count; adjust if needed
#     total_cost = (total_tokens / 1000) * pricing_out  # Example cost calculation; adjust based on your model's pricing

    # return messages_list, oai_response, temp, total_tokens, total_cost
    list = ["yuh", "oit", "three", "four", "five"]
    print(total_tokens)
    return messages_list, oai_response, total_tokens

    

def interview_gen(patient: dict, output_id: str, out_dir=out_dir, tracking_path=tracking_path):
    """
    Create an interview using the Llama model.

    Parameters
    ----------
    patient (dict): Patient information.
    output_id (str): Output identifier.
    out_dir (str): Output directory.
    tracking_path (str): Path for tracking data.
    """
    start = time.time()
    messages_list, oai_response, temp, total_tokens, total_cost = oai_interview_gen(patient=patient)
    end = time.time()
    time_taken = end - start

#     print("Total cost for generating interview:", total_cost)
#     print("Total time taken:", time_taken)

#     # Save transcript
#     Path(out_dir).mkdir(parents=True, exist_ok=True)
#     out_path = f"SM_{output_id}_Interview"

#     try:
#         json_msg_list = helper.create_json_obj(messages_list)
#         helper.write_list_to_json(json_msg_list, Path(out_dir, out_path + ".json"))
#         helper.write_str_to_txt(
#             string=helper.transcript_json_to_str(
#                 Path(out_dir, out_path + ".json"),
#                 msg_separator="\n\n"),
#             filepath=Path(out_dir, out_path + ".txt"))
        
#         patient_string = helper.patient_to_str(patient, ignore_keys=["Clinician Name", "Appointment Date", "Reason for Appointment"])
        
#         patient_edge_case = patient.get("Edge Case Scenario", "")

#     except Exception as e:
#         print(e)
#         with open(str(Path(out_dir, out_path + ".txt")), "w") as text_file:
#             text_file.write(oai_response)

#     # Update general CSV
#     helper.track_patient(
#         interview_path=Path(out_path + ".json"),
#         patient_str=patient_string,
#         extra_info_dict={
#             "total_cost": total_cost,
#             "temp": temp,
#             "time": time_taken,
#             "edge_case": patient_edge_case,
#             "llm_model": "Llama 3.1 8B",  # Update model name
#         },
#         tracking_path=tracking_path)

    print("yuh int gen")

def oai_summary_gen(transcript, temp=0.5, summary_path='prompts/summary_prompt.txt'):
    """
    Generate a summary using the Llama model.

    Parameters
    ----------
    transcript (str): Transcript contents.
    temp (float): Temperature of the model.
    summary_path (str): Path to prompt.

    Returns
    -------
    oai_summary (str): Summary of transcript.
    temp (float): Model temperature.
    s_total_tokens (str): Total tokens used.
    s_total_cost (str): Total cost of the API in dollars.
    """
#     summary_gen = Path(summary_path).read_text()

#     # Hydrate prompt
#     summary_gen = summary_gen.replace(r"{transcript}", transcript)

#     # Call Llama
#     response = model.invoke(summary_gen, temperature=temp)

#     oai_summary = response['text']  # Adjust as needed based on the response structure

#     s_total_tokens = len(oai_summary.split())  # Basic token count; adjust if needed
#     s_total_cost = (s_total_tokens / 1000) * pricing_out  # Example cost calculation

#     return oai_summary, temp, str(s_total_tokens), str(s_total_cost)

    print("yuh sum gen")
