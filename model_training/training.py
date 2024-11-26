from datasets import load_dataset
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, BitsAndBytesConfig
from peft import prepare_model_for_kbit_training, LoraConfig, get_peft_model

# Load the JSONL file
data = load_dataset('json', data_files='instruction_training.jsonl')

# Check the data format by printing the first entry
print("Sample Data Entry:")
print(data['train'][0])  # Example entry

# Define a function to format the dataset
def formatting_func(example):
    if example.get("input", "") != "":
        input_prompt = (
            "Below is an instruction that describes a task, paired with an input that provides further context. "
            "Write a response that appropriately completes the request.\n\n"
            "### Instruction:\n"
            f"{example['instruction']}\n\n"
            "### Input: \n"
            f"{example['input']}\n\n"
            "### Response: \n"
            f"{example['output']}"
        )
    else:
        input_prompt = (
            "Below is an instruction that describes a task. "
            "Write a response that appropriately completes the request.\n\n"
            "### Instruction:\n"
            f"{example['instruction']}\n\n"
            "### Response:\n"
            f"{example['output']}"
        )
    return {"text": input_prompt}

# Apply the formatting function to the dataset
formatted_dataset = data.map(formatting_func)

# Check the formatted output
print("Formatted Sample Data Entry:")
print(formatted_dataset["train"][0]["text"])

# Define model path
modelpath = "meta-llama/Llama-3.1-8B"

# Load 4-bit quantized model
print("Loading the model...")
model = AutoModelForCausalLM.from_pretrained(
    modelpath,
    device_map="auto",
    quantization_config=BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_type="nf4",
    ),
    torch_dtype=torch.bfloat16,
)

print("Model loaded successfully!")
