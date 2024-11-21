import sys, os, csv, ast, random, time
from pathlib import Path
import pandas as pd
import time
from collections import deque  # Queue for questions
import re
import random

random.seed()

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

model1 = OllamaLLM(base_url="localhost:11435", 
                  model="llama3.1:70b-instruct-q4_0", 
                  temperature=0.3, 
                  num_ctx = 6144,
                  top_k = 60,
                  top_p = 0.9)
model2 = OllamaLLM(base_url="localhost:11435", 
                  model="llama3.1:70b-instruct-q4_0", 
                  temperature=0.3, 
                  num_ctx = 6144,
                  top_k = 60,
                  top_p = 0.9)

##### Prompt templates
starter_path = 'prompts/starter.txt'
questions_path = 'prompts/questions_test/Analysis/questionbank_chunked_test.txt'
patient_prompt_path = 'prompts/double_model_prompts/INSTRUCT/patient_prompt_v1.txt'
asst_prompt_path = 'prompts/double_model_prompts/INSTRUCT/assistant_prompt_v2.txt'
tracking_path = "./tracking.csv"

##### directory for interview outputs
out_dir = "transcripts/DM"

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

def extract_and_store_notes(response, notes):
    """
    Extracts 'Notes' from the response and appends them to the notes string.
    """
    if "Note:" in response:
        note_start = response.find("Note:") + len("Note:")
        note_end = response.find("<END_NOTE>", note_start)
        notes += response[note_start:note_end].strip() + "\n"
        # notes.append(note_content)
    return notes

def chunk_message_history(message_list, max_history_size=10):
    """
    Trims the message list to only keep the most recent `max_history_size` messages.
    """
    if len(message_list) > max_history_size:
        message_list = message_list[-max_history_size:]  # Keep only the most recent messages
    return message_list

##############################
# NEW QUESTION PARSING FUNCTIONS
##############################

def parse_questions_with_headers(question_text):
    """
    Parses the questions with headers into a structured list, preserving the hierarchy.
    Returns a list of sections, where each section is a list that includes both the headers and their associated questions.
    """
    lines = question_text.splitlines()
    current_section = []
    current_subsection = []
    sections = []

    for line in lines:
        line = line.strip()  # Clean up any extra spaces
        if line.startswith("##"):  # Section header
            if current_section:
                sections.append(current_section)
            current_section = [line]  # Start new section
        elif line.startswith("#"):  # Subheader
            if current_subsection:
                current_section.append(current_subsection)
            current_subsection = [line]  # Start new subsection
        elif line.startswith("-") or line.startswith("+"):  # Question or continuation
            current_subsection.append(line)  # Add to current subsection

    # Add the final section and subsection
    if current_subsection:
        current_section.append(current_subsection)
    if current_section:
        sections.append(current_section)
    
    return sections

def chunk_questions(sections):
    """
    Chunk the questions into a list of lists, where each sublist contains
    questions from a specific sub-section. Each list starts with the 
    section title and subheader as the first entry, followed by the questions.
    """
    chunked_questions = []

    for section in sections:
        section_title = section[0]  # Get the main section title
        
        for sub_section in section[1:]:
            sub_section_title = sub_section[0]  # Get the sub-header title
            sub_section_chunks = [f"{section_title} {sub_section_title}"]  # Start with combined title
            
            # Add the first question if it exists
            if len(sub_section) > 1:
                first_question = sub_section[1]
                sub_section_chunks = [f"{section_title} {sub_section_title}\n{first_question}"]
            
            # Add the rest of the questions in the sub-section
            for question in sub_section[2:]:
                sub_section_chunks.append(question)
            
            # Append this sub-section's chunk of questions to the overall list
            chunked_questions.append(sub_section_chunks)

    return chunked_questions


def queue_questions(chunks, questions_queue, num_questions_to_add=2):
    """
    Adds a set number of questions from the chunks to the queue, ensuring headers are preserved.
    """
    while len(questions_queue) < num_questions_to_add and chunks:
        chunk = chunks.pop(0)
        questions_queue.extend(chunk)  # Add chunk to queue
    return questions_queue


##############################
# INVOKING MODEL FUNCTIONS
##############################

def invoke_asst_model(message_list, prompt, notes, summarize):
    '''
    Model responds as an interviewer. 
    '''
    
    if summarize:
        notes_prompt = "Here is all the notes taken for this interview. When you've finished asking all the questions: output the notes as given, thank the patient for their time, then you MUST output '<STOP>'"
        system_msg = {"role": "system", "content": prompt}
        # msgs = message_list.copy()
        notes = notes_prompt + notes
        notes_msg = {"role": "system", "content": notes}
        summary_prompt = []
        
        summary_prompt.insert(0, notes_msg)
        summary_prompt.insert(0, system_msg)
    
        response = model1.invoke(notes)
        print("------------------------------------------------------------")
        print("Assistant response: ", response)
        notes = extract_and_store_notes(response, notes)
    
        extracted_response = extract_response_text(response)
        print("Assistant extracted response: ", extracted_response)
    
        return extracted_response, notes
            
    else: 
        system_msg = {"role": "system", "content": prompt}
        msgs = message_list.copy()
        msgs.insert(0, system_msg)
    
        response = model1.invoke(msgs)
        print("------------------------------------------------------------")
        print("Assistant response: ", response)
        notes = extract_and_store_notes(response, notes)
    
        extracted_response = extract_response_text(response)
        print("Assistant extracted response: ", extracted_response)
    
        return extracted_response, notes       

patient_msgs = []

def invoke_pat_model(message_list, prompt):
    '''
    Model responds as a patient. 
    '''
    swapped_list = swap_msg_list(message_list)
    
    system_msg = {"role": "system", "content": prompt}
    msgs = swapped_list.copy()
    msgs.insert(0, system_msg)
    
    response = model2.invoke(msgs)
    print("------------------------------------------------------------")
    print("Patient response: ", response)
    
    extracted_response = extract_response_text(response)
    print("Patient extracted response: ", extracted_response)
    
    # patient_msgs.append(extracted_response)
    # print("Patient Messages: ", patient_msgs)
    
    return extracted_response 

##############################
# CONVERSATION FUNCTION
##############################

def chat_between_models(message_list, asst_prompt, patient_prompt, starter):
    # Conduct the interview between two models until <STOP> condition is reached
    
    questions = Path(questions_path).read_text()  # This should read the content as a string
    sections = parse_questions_with_headers(questions)  # Pass the string directly
    # print("Sections:", sections)  # Print sections for debugging
    chunks = chunk_questions(sections)  # Get the structured chunks of questions
    # print("Chunks:", chunks)  # Print chunks for debugging
    
    # max_history_size = 10  # Define the size of message history chunks
    notes = ""  # Initialize notes storage
    max_turns = 100
    # current_chunk_idx = 0  # Start at the first chunk
    questions_queue = deque()  # Initialize a queue for questions
    transcript = []

        
    for i in chunks:
        print(i)
        questions_queue.append(i)

    stop_condition = False
    turns = 0
    prev_chunk_length = 0
    total_chunk_lengths = 0
    start = time.time()
    
    first_chunk_complete = 0
    summarize = 0
    
    first_chunk = questions_queue.popleft()
    curr_chunk = first_chunk
    questions_list = curr_chunk
    formatted_questions_list = '\n'.join(first_chunk)


    while not stop_condition and turns < max_turns:
        time.sleep(1)
        
        if questions_queue: 
            
            filtered_curr_chunk = [q for q in curr_chunk if not q.startswith('+')]
            curr_chunk_length = len(filtered_curr_chunk)
    
            print("Question amount (filtered): ", curr_chunk_length)
            print("if turns == ", curr_chunk_length, " + ", total_chunk_lengths)
            # curr_chunk_length = len(curr_chunk)
            print("Question amount: ", curr_chunk_length)
        
            print("if turns == ", curr_chunk_length, " + ", total_chunk_lengths)
            if turns == curr_chunk_length + total_chunk_lengths:
            
                print("Next chunk: ", questions_queue[0])
                next_question_chunk = questions_queue.popleft()
            
                if first_chunk_complete:
                    print()
                    print("Dumping first questions.........................................................")
                    i=0
                    while i < prev_chunk_length:
                        print("Dumping ", prev_chunk[i])
                        questions_list.pop(0)
                        # print(questions_list)
                        i += 1
                    
                    print("Saving and dumping previous messages..............................................")
                    i=0
                    print(message_list)
                    while i < prev_chunk_length*2:
                        print("Saving ", message_list[0])
                        transcript.append(message_list[0])
                        message_list.pop(0)
                        print("Message_list length: ", len(message_list))
                        i+=1
            
                prev_chunk_length = curr_chunk_length
                total_chunk_lengths = total_chunk_lengths + curr_chunk_length
                prev_chunk = curr_chunk
                curr_chunk = next_question_chunk
            
            
                questions_list = questions_list + curr_chunk
                formatted_questions_list = '\n'.join(questions_list)
                print("Formatted questions: ", '\n', formatted_questions_list)
                print("Updating assistant prompt...")
            
                first_chunk_complete = 1
            
            asst_prompt_with_questions = asst_prompt.replace(r"{questions}", formatted_questions_list)
            # print("Assistant prompt with questions:", '\n', asst_prompt_with_questions)  # Debug print

            # Patient response
            patient_response = invoke_pat_model(message_list, patient_prompt)
            message_list = update_msg_list(message_list, is_assistant=False, content=patient_response)
            
            # Assistant response
            asst_response, notes = invoke_asst_model(message_list, asst_prompt_with_questions, notes, summarize)
            print("Notes so far: ", notes)
            # notes = extract_and_store_notes(asst_response, notes)  # Store any notes the model gives
            message_list = update_msg_list(message_list, is_assistant=True, content=asst_response)
           
        else:
            
         ## answer final question and summarize conversation
            patient_response = invoke_pat_model(message_list, patient_prompt)
            message_list = update_msg_list(message_list, is_assistant=False, content=patient_response)
        
            summarize = 1
            print("SUMMARIZE NOW ACTIVE")
            asst_response, notes = invoke_asst_model(message_list, asst_prompt_with_questions, notes, summarize)
        
        turns += 1
        print("Turn count:", turns)

        # Check for stop condition
        stop_condition = (
            "Summary:" in asst_response or
            "To summarize:" in asst_response or
            "<STOP>" in asst_response
            )


    end = time.time()
    time_taken = end - start
    print("INTERVIEW HAS ENDED")
    print("SYSTEM: ")
    print("Total time taken:", time_taken)
    print("Final Notes:", notes)  # Print or return final notes
    return message_list, notes

def interview_gen(patient: dict, output_id: str, out_dir=out_dir, tracking_path=tracking_path):
    """
    Creates interviews based on the patients that are passed in.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    ##### Prompt templates
    patient_prompt_str = Path(patient_prompt_path).read_text()
    asst_prompt_str = Path(asst_prompt_path).read_text()
    starter_str = Path(starter_path).read_text()

    ### hydrate starter
    clinician_name = patient["Clinician Name"]
    appt_date = patient["Appointment Date"]
    starter = starter_str.replace(r"{Clinician Name}", clinician_name)
    starter = starter.replace(r"{Date}", appt_date)

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
    conversation, notes = chat_between_models(message_list, asst_prompt_str, patient_prompt, starter)
    for message in conversation:
        print(message["content"])

    # Use the final notes at the end of the conversation
    print("Final notes summary: ", notes)