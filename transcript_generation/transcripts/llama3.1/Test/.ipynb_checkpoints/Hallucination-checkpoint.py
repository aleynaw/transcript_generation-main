import sys, os, csv, ast, random, time, re, json
import pandas as pd
from pathlib import Path
from datetime import datetime
from deepeval import evaluate
from deepeval.metrics import HallucinationMetric
from deepeval.test_case import LLMTestCase

filepath = r"C:\Users\aleynaw\Desktop\transcript_generation-main\transcript_generation\transcripts\llama3.1\Single_File"
out_dir = r"C:\Users\aleynaw\Desktop\transcript_generation-main\transcript_generation\transcripts\llama3.1\Metrics"
# patients_csv_path = r"C:\Users\aleynaw\Desktop\transcript_generation-main\patient_creation\llm_patients.csv"

patients_path = Path(r"C:\Users\aleynaw\Desktop\transcript_generation-main\patient_creation\llm_patients.csv")
patients_df = pd.read_csv(patients_path,delimiter="|")

# Go up two levels to reach the 'transcript_generation' directory
parent_directory = Path(__file__).resolve().parent.parent.parent.parent
print(f"Parent Directory: {parent_directory}")

sys.path.append(str(parent_directory))

try:
    from transcript_generation import helper_fns as helper
except ModuleNotFoundError:
    import helper_fns as helper
    

# Read the patient information from the CSV into a list
patients_info = []
        
for i, patient in patients_df.iterrows():
    
    if "Edge Case Scenario" in patient:  # if there is an edge case
        edge_case = patient["Edge Case Scenario"]
        ignore_keys = ["Clinician Name", "Appointment Date", 'Conversational Tone', 'Reason for Appointment']
    else:  # if there is no edge case
        edge_case = ""
        ignore_keys = ["Clinician Name", "Appointment Date", 'Conversational Tone', "Edge Case Scenario", 'Reason for Appointment']

    # print(patient)
    patient_dict = patient.dropna().to_dict()
    patient=patient_dict
    patient_string = helper.patient_to_str(patient, ignore_keys)
    
    patients_info.append(patient_string)

# Debugging: Print loaded patient data
print(f"Reading patient data from CSV...")
print(f"Loaded {len(patients_info)} patient rows from CSV.")

# Initialize the hallucination metric
metric = HallucinationMetric(verbose_mode=True, threshold=0.5)

# Define a function to load messages by role from JSON
def load_filtered_messages(filepath, role):
    with open(filepath, "r") as f:
        conversation = json.load(f)
    
    # Debugging: Print structure of conversation
    print(f"Loaded conversation from {filepath}:")
    # print(conversation)  # Print the raw content of the JSON file
    
    # Check if the conversation is a list of dictionaries as expected
    if isinstance(conversation, list) and all(isinstance(msg, dict) for msg in conversation):
        return [msg["content"] for msg in conversation if msg.get("role") == role]
    else:
        raise ValueError(f"Unexpected format in {filepath}: conversation should be a list of dictionaries.")

# Check the files in the `filepath` directory
print(f"Checking files in {filepath}...")
json_files = list(Path(filepath).glob("*.json"))
print(f"Found {len(json_files)} JSON files.")

# Check if there are any files at all
if not json_files:
    print(f"No JSON files found in the specified directory: {filepath}. Please verify the directory.")
        
        
# Define output CSV file path
date_str = datetime.now().strftime("%Y-%m-%d")
csv_file_path = Path(out_dir, f"hallucination_results_{date_str}.csv")

# Write headers for the CSV file
with open(csv_file_path, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Filename", "Test Case", "Score", "Reason"])
    print(f"Headers written successfully to {csv_file_path}.")

# Processing JSON files and corresponding patient data
print(f"Processing JSON files...")
for index, json_file in enumerate(json_files):
    try:
        # Load messages from the JSON file
        input_prompts = load_filtered_messages(json_file, "assistant")
        patient_responses = load_filtered_messages(json_file, "user")
        
        # Get the corresponding patient context from the CSV by index
        if index < len(patients_info):  # Ensure there's a corresponding patient row
            patient_data = patients_info[index]
            print("Patient Data: ", patient_data)
            context = patient_data  # Adjust the field name as necessary
            print(f"Found matching patient data for index {index}. Using context: {context}")
        else:
            context = []  # Default to empty list if no corresponding patient data
            print(f"No matching patient data for index {index}. Using empty context.")

        # Ensure that context is a list (even if it's a single string)
        if isinstance(context, str):
            context = [context]  # Wrap the context in a list if it's a string
        
        # Create test cases for each prompt-response pair
        test_cases = []
        for input_prompt, patient_response in zip(input_prompts, patient_responses):
            test_case = LLMTestCase(
                input=input_prompt,
                actual_output=patient_response,
                context=context  # Use the extracted context from CSV
            )
            test_cases.append(test_case)
        
        # Evaluate the test cases
        evaluate(test_cases, [metric])

        # Write results to the CSV file
        with open(csv_file_path, mode="a", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            for i, test_case in enumerate(test_cases):
                csv_writer.writerow([json_file.name, f"Test Case {i+1}", metric.score, metric.reason])
            print(f"Results for {json_file.name} written to CSV.")
    
    except Exception as e:
        print(f"Error processing {json_file.name}: {e}")
        

print(f"Hallucination results saved to {csv_file_path}")
