import csv
import json
from pathlib import Path
from deepeval import evaluate
from deepeval.metrics import HallucinationMetric
from deepeval.test_case import LLMTestCase

filepath = r"C:\Users\aleynaw\Desktop\transcript_generation-main\transcript_generation\transcripts\llama3.1\Test\"

# Initialize the hallucination metric
metric = HallucinationMetric(verbose_mode=True, threshold=0.5)

# Define a function to load messages by role from JSON
def load_filtered_messages(filepath, role):
    with open(filepath, "r") as f:
        conversation = json.load(f)
    return [msg["content"] for msg in conversation if msg.get("role") == role]

# Define output CSV file path
csv_file_path = Path(out_dir, "evaluation_results.csv")

# Write headers for the CSV file
with open(csv_file_path, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Filename", "Test Case", "Input Prompt", "Patient Response", "Score", "Reason"])

# Loop over each JSON file in the folder
for json_file in Path(out_dir).glob("*.json"):
    # Load messages from the JSON file
    input_prompts = load_filtered_messages(json_file, "assistant")
    patient_responses = load_filtered_messages(json_file, "user")

    # List to hold test cases
    test_cases = []

    # Create test cases for each prompt-response pair
    for input_prompt, output in zip(input_prompts, patient_responses):
        test_case = LLMTestCase(
            input=input_prompt,
            actual_output=output,
            context=patient_info
        )
        test_cases.append(test_case)

    # Evaluate the test cases
    evaluate(test_cases, [metric])

    # Write results to the CSV file
    with open(csv_file_path, mode="a", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        for i, test_case in enumerate(test_cases):
            csv_writer.writerow([
                json_file.name,
                f"Test Case {i+1}",
                test_case.input,
                test_case.actual_output,
                metric.score,
                metric.reason
            ])
