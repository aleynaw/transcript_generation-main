import csv
import json
from pathlib import Path
from datetime import datetime
from deepeval import evaluate
from deepeval.metrics import HallucinationMetric, RoleAdherenceMetric
from deepeval.test_case import LLMTestCase, ConversationalTestCase

filepath = Path(r"C:\Users\aleynaw\Desktop\transcript_generation-main\transcript_generation\transcripts\llama3.1\Test")
out_dir = r"C:\Users\aleynaw\Desktop\transcript_generation-main\transcript_generation\transcripts\llama3.1\Metrics"

# Generate a unique filename with the current date
output_csv = Path(out_dir, f"role_adherence_results_{date_str}.csv")

# Initialize the role adherence metric
metric = RoleAdherenceMetric(threshold=0.5, include_reason=True, verbose_mode=True)

# Prepare the CSV file with headers
with open(output_csv, mode="w", newline="") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Filename", "Role", "Score", "Reason"])

# Function to evaluate and save results
def evaluate_role_adherence(json_file, role, role_key):
    # Load the conversation data
    with open(json_file, "r") as f:
        conversation = json.load(f)

    # Build turns for the ConversationalTestCase based on role
    turns = [LLMTestCase(input=msg["content"], actual_output=msg["content"]) 
             for msg in conversation if msg.get("role") == role_key]

    # Create ConversationalTestCase for role adherence
    convo_test_case = ConversationalTestCase(
        chatbot_role=role,
        turns=turns
    )

    # Measure role adherence
    metric.measure(convo_test_case)

    # Write results to the CSV
    with open(output_csv, mode="a", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow([json_file.name, role, metric.score, metric.reason])
        print(f"Processed {json_file.name} for {role} with score {metric.score} and reason: {metric.reason}")

# Loop through each JSON file and evaluate for both roles
for json_file in filepath.glob("*.json"):
    evaluate_role_adherence(json_file, "interviewer", "assistant")
    evaluate_role_adherence(json_file, "patient", "user")

print(f"Role adherence results saved to {output_csv}")
