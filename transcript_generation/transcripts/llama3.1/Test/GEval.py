import sys, os, csv, ast, random, time, re, json
import pandas as pd
from statistics import mean
from pathlib import Path
from datetime import datetime
from deepeval import evaluate
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

filepath = r"C:\Users\aleynaw\Desktop\transcript_generation-main\transcript_generation\transcripts\llama3.1\Single_File"
out_dir = r"C:\Users\aleynaw\Desktop\transcript_generation-main\transcript_generation\transcripts\llama3.1\Metrics"

patients_path = Path(r"C:\Users\aleynaw\Desktop\transcript_generation-main\patient_creation\llm_patients.csv")
patients_df = pd.read_csv(patients_path, delimiter="|")

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
    if "Edge Case Scenario" in patient:
        edge_case = patient["Edge Case Scenario"]
        ignore_keys = ["Clinician Name", "Appointment Date", 'Conversational Tone', 'Reason for Appointment']
    else:
        edge_case = ""
        ignore_keys = ["Clinician Name", "Appointment Date", 'Conversational Tone', "Edge Case Scenario", 'Reason for Appointment']

    patient_dict = patient.dropna().to_dict()
    patient = patient_dict
    patient_string = helper.patient_to_str(patient, ignore_keys)
    patients_info.append(patient_string)

# Debugging: Print loaded patient data
print(f"Reading patient data from CSV...")
print(f"Loaded {len(patients_info)} patient rows from CSV.")

# Define the correctness metric using GEval
correctness_metric = GEval(
    name="Hallucination",
    criteria="The ONLY thing you should penalize is factually incorrect information in a response as compared to the context.",
    evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT, LLMTestCaseParams.CONTEXT],
    evaluation_steps = [
    """1. Initial Check for Factual Accuracy:
       - Examine the response to identify any factual inaccuracies based on the provided context.
       - Verify that any specific details (e.g., names, conditions, frequencies) directly match the patient’s context and are not contradictory or incorrect.
       - Penalize only if the response includes inaccurate details or conflicting information.""",

    """2. Relevance and Detail Consistency:
       - The response should match the level of detail provided in the context. Minimal detail is acceptable, and additional information is not required unless specified.
       - Do not penalize responses that give a general answer or indicate uncertainty, especially if the context does not include specifics.
       - Avoid penalties if the response does not go into exhaustive detail, as long as it sufficiently addresses the question.""",

    """3. Checking for Required Information:
       - If the prompt explicitly asks for a detail (e.g., a specific date or event), confirm whether it is addressed in the response.
       - However, do not penalize if the response indicates the model is uncertain or doesn’t know the information.
       - Ensure that omissions are penalized only if the context provides specific information that was directly asked for and omitted in the response.
       - If any information requested is not present in the context, do not penalize for omission.""",

    """4. Edge Case Handling:
       - Review any edge case instructions that may require omitting specific information (e.g., omitting dosage or timing).
       - Ensure that no penalty is applied if the response adheres to the edge case requirements, even if the prompt requested the omitted information.""",

    """5. Handling Responses with Uncertainty or General Statements:
       - Accept responses that convey uncertainty (e.g., "I don’t recall exactly") if the question is addressed generally.
       - Do not penalize if the patient implies they lack precise information or memory for the details requested, as long as they address the question.""",

    """6. Allowance for Additional Information:
       - Extra information is permissible as long as it does not contradict the context.
       - Do not penalize for additional or related details if they do not introduce any inaccuracies.""",

    """7. Treatment of Redundancies and Repetition:
       - Avoid penalizing for redundancy if it does not contradict or change the intended meaning.
       - Repetition of correct information should not be penalized, as long as it aligns with the context.""",],
    threshold=0.5,
    strict_mode=False,
    verbose_mode=False,
)

# evaluation_steps=[
#     "Check if the actual output contains any factual inaccuracies based on the context.",
#     "Ensure the output reflects the patient's response to the question, including implicit information. Do not penalize for the lack of explicit detail if the patient's response provides clear context.",
#     "Do not penalize for omissions of specific details if the context or patient response clearly implies the information, even if it’s not explicitly stated.",
#     "Accept indirect or ambiguous language if it adequately addresses the question, as long as it aligns with the overall context.",
#     "Allow minimal or general responses when they sufficiently address the question without requiring detailed or specific information.",
#     "Differing opinions are acceptable as long as they do not alter factual accuracy or contradict the context."
# ]

# Define a function to load messages by role from JSON
def load_filtered_messages(filepath, role):
    with open(filepath, "r") as f:
        conversation = json.load(f)
    
    # Debugging: Print structure of conversation
    print(f"Loaded conversation from {filepath}:")
    
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
total_score_csv_path = Path(out_dir, "hallucination_total_score.csv")

# Write headers for the CSV file
with open(csv_file_path, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Filename", "Test Case", "Score", "Reason", "Question", "Response"])
    print(f"Headers written successfully to {csv_file_path}.")
    
with open(total_score_csv_path, mode="w", newline="") as total_score_csv:
    total_score_writer = csv.writer(total_score_csv)
    total_score_writer.writerow(["Filename", "Overall Score Percentage"])
    print(f"Headers written successfully to {total_score_csv_path}.")

# Processing JSON files and corresponding patient data
print(f"Processing JSON files...")
for index, json_file in enumerate(json_files):
    start_time = time.time()  # Start timing the evaluation for this file
    try:
        # Load messages from the JSON file
        input_prompts = load_filtered_messages(json_file, "assistant")
        patient_responses = load_filtered_messages(json_file, "user")
        
        # Get the corresponding patient context from the CSV by index
        if index < len(patients_info):
            patient_data = patients_info[index]
            print("Patient Data: ", patient_data)
            context = [patient_data]  # Ensure context is a list
            print(f"Found matching patient data for index {index}. Using context: {context}")
        else:
            context = []
            print(f"No matching patient data for index {index}. Using empty context.")

        # Create test cases for each prompt-response pair
        test_cases = []
        for input_prompt, patient_response in zip(input_prompts, patient_responses):
            test_case = LLMTestCase(
                input=input_prompt,
                actual_output=patient_response,
                context=context
            )
            test_cases.append(test_case)
        
        # List to store individual scores for this JSON file
        individual_scores = []
        
        # Evaluate the test cases with the correctness metric and write individual results to CSV
        with open(csv_file_path, mode="a", newline="") as csv_file:
            csv_writer = csv.writer(csv_file)
            for i, test_case in enumerate(test_cases):
                correctness_metric.measure(test_case)
                individual_scores.append(float(correctness_metric.score))  # Store each score in the list
                csv_writer.writerow([json_file.name, f"Test Case {i+1}", float(correctness_metric.score), str(correctness_metric.reason), test_case.input, test_case.actual_output])
            print(f"Results for {json_file.name} written to CSV.")
        
        # Calculate the overall score percentage for this JSON file
        if individual_scores:
            overall_score_percentage = mean(individual_scores) * 100
        else:
            overall_score_percentage = 0  # If no scores are present, default to 0%

        end_time = time.time()  # End timing
        elapsed_time = end_time - start_time  # Time taken for this file
        
        # Write the overall score percentage to the total score CSV
        with open(total_score_csv_path, mode="a", newline="") as total_score_csv:
            total_score_writer = csv.writer(total_score_csv)
            total_score_writer.writerow([json_file.name, overall_score_percentage])
            print(f"Summary for {json_file.name}: Average Score = {overall_score_percentage}, Total Time = {elapsed_time:.2f} seconds")
            
        

    except Exception as e:
        print(f"Error processing {json_file.name}: {e}")

print(f"Correctness results saved to {csv_file_path}")
print(f"Overall score percentages saved to {total_score_csv_path}")


