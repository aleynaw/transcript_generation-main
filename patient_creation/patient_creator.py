from faker import Faker
import pandas as pd
import random
import os,sys
from datetime import datetime
from dateutil.relativedelta import relativedelta
import csv

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from patient_generation.variables import HEALTH_CONDITIONS, COMMON_RECREATIONAL_DRUGS, COMMON_HEALTH_SUPPLEMENTS, COMMON_ALLERGIES, DR_APPOINTMENT_REASONS, TYPING_STYLES, CONVERSATIONAL_TONE, EDGE_CASE_SCENARIOS

CSV_DIRECTORY = "../"
def generate_health_conditions(n):
    '''gets a list of n random health conditions along with a list of a randomly selected associated medication for that condition'''
    health_condition = random.sample(list(HEALTH_CONDITIONS.keys()), n)
    meds = []
    for i in health_condition:
        if len(HEALTH_CONDITIONS[i]) > 0:
            #chance that meds may not be taken for that health condition
            if random.random() <= 0.8:
                med_name = random.choice(HEALTH_CONDITIONS[i])
                meds.append(med_name)
        else:
            pass
    return health_condition, meds

def create_clinician_name()->str:
    '''returns string of random name of a clinician'''
    fake = Faker()
    dr = fake.first_name() + " " + fake.last_name()
    return dr

def create_appt_date()->str:
    '''returns string with random month and date (e.g. February 14)'''
    fake = Faker()
    appt_date = fake.date_between("today", "+5y").strftime("%B %-d")
    return appt_date

def get_random_names(fake, num_people, age_low, age_high)->list:
    '''returns a list of strings with num_people number of people with first name, random age ages between age_low and age_high (e.g. "Lary (12)")'''
    output = []
    for i in range(num_people):
        output.append(f"{fake.first_name()} ({random.randint(age_low, age_high)})")
    return output

def create_patient_dict(preset_attributes = {}) -> dict:
    '''create a patient dictionary with random information
    Parameters
    ----------
    preset_attributes (dict):
        dictionary of keys and values for a patient that are initially defined.
    '''
    random.seed()
    fake = Faker()
    patient = dict()
    #doctor data
    patient["Clinician Name"] = create_clinician_name()
    patient["Appointment Date"] = create_appt_date()

    #basic information
    sex = random.randint(0,1)
    middle_name = random.randint(0,1)
    
    if sex == 0:
        patient['Sex'] = "Female"
        patient['Name'] = fake.name_female() 
        if middle_name == 1:
            patient['Name'] = f"{fake.first_name_female()} " + patient['Name']
    else:
        patient['Sex'] = "Male"
        patient['Name'] = fake.name_male()
        if middle_name == 1:
            patient['Name'] = f"{fake.first_name_male()} " + patient['Name']

    if "Age" not in patient.keys():
        dob = fake.date_of_birth(minimum_age = 20, maximum_age=80)
        patient['Age'] = relativedelta(datetime.now(), dob).years

        if random.random() <= 0.8: 
            job = fake.job()
        else:
            job = "unemployed"
        if patient['Age'] <= 22:
            job = "student " + job
        if patient['Age'] >= 75:
            job = "retired " + job

    if "Date of Birth" not in patient.keys():
        patient['Date of Birth'] =dob.strftime("%B %-d %Y") #windows: replace %-d with %#d

    #personal history
    if "Occupation" not in patient.keys():
        patient['Occupation'] = job

    if "Medical Conditions" not in patient.keys() and "Medications" not in patient.keys():
        conditions, meds = generate_health_conditions(random.randint(1,3))
        patient['Medical Conditions'] = ", ".join(conditions)
        patient['Medications'] = ", ".join(meds)
    
    if "Address" not in patient.keys():
        patient['Address'] = f"{fake.street_address()}, {fake.city()}, British Columbia, Canada"
    
    if "Allergies" not in patient.keys():
        patient['Allergies'] = f"{', '.join(random.sample(COMMON_ALLERGIES, random.randint(0,3)))}"

    #medical history
    if "Reason for Appointment" not in patient.keys():
        reasons = random.sample(DR_APPOINTMENT_REASONS, random.randint(1,3))
        patient["Reason for Appointment"] = ", ".join(reasons)
    
    if 'Recreational Drug Usage' not in patient.keys():
        if random.random() <= 0.3:
            patient['Recreational Drug Usage'] = f'{", ".join(random.sample(["beer", "wine", "cannabis", "cigarettes", "shrooms", "psychedelics"], random.randint(1,4)))}'
    
    if 'Relationship Status' not in patient.keys():
        patient['Relationship Status'] = random.choice(["married", "long term relationship", "casual relationship", "divorced", "windowed", "single"])

    #social history
    if "Elementary School Performance" not in patient.keys():
        patient["Elementary School Performance"] = random.choice(["poor", "average", "good", "excellent"])
    if "High School Performance" not in patient.keys():
        patient["High School Performance"] = random.choice(["dropped out", "poor", "average", "good", "excellent"])

    # attributes to create binary responses
    attributes = [
        "Canadian Citizenship", 
        "Children", 
        "Siblings", 
        "Seizures", 
        "Developmental Difficulties", 
        "Family History of Health Conditions", 
        "Previous Hospitalization", 
        "Disability Assistance", 
        ]

    for attribute in attributes:
        if attribute not in patient.keys():
            cond = random.random() #returns [0,1)
            if cond <= 0.5: patient[attribute] = "yes"
            else: patient[attribute] = ""

    # attributes with possible do not disclose options
    dnd_attributes = [
        "Past Trauma", 
        "Substance Abuse", 
    ]

    for attribute in dnd_attributes:
        if attribute not in patient.keys():
            cond = random.random() #returns [0,1)
            if cond <= 0.5: patient[attribute] = "yes"
            else: patient[attribute] = ""
    
    # create variation in conversations and tones
    if "Typing Style" not in patient.keys():
        patient["Typing Style"] = random.choice(TYPING_STYLES)
    if "Conversational Tone" not in patient.keys():
        patient["Conversational Tone"] = random.choice(CONVERSATIONAL_TONE)
    if "Edge Case Scenario" not in patient.keys():
        cond = random.random() #returns [0,1)
        if cond <= 0.5: patient["Edge Case Scenario"] = random.choice(EDGE_CASE_SCENARIOS)
        else: patient[attribute] = ""
    return patient

def patient_to_csv(patient:dict, filepath:str="./patients.csv"):
    '''
    Outputs the patient dictionary to the csv file at filepath.

    Parameters
    ----------
    patient: dict 
        randomized patient dictionary
    filepath: str
        filepath associated with the csv of patients; defaults to patients.csv"
    '''
    try:
        current_df = pd.read_csv(filepath, sep="|")
        current_dict = current_df.to_dict("list")
        existing_len = current_df.shape[0]
        
        #add variables in current dict not in patient dict
        missing_cols = list(set(list(current_dict.keys())) - set(list(patient.keys())))
        for missing_col in missing_cols:
            patient[missing_col] = ""
        
        #add everything from patient dict to to the current dict
        for col in patient.keys():
            if col in current_dict:
                current_dict[col].append(patient[col])
            else:
                #create a new column for variable in patient dict not in current dict
                buffer = [""]*existing_len
                buffer.append(patient[col])
                current_dict[col] = buffer

        updated_df = pd.DataFrame(current_dict)

    except FileNotFoundError:
        print(f"creating file at {filepath}")
        updated_dict = {}
        #save dictionary as csv with keys
        for col in patient.keys():
            updated_dict[col] = [f"{patient[col]}"]
        updated_df = pd.DataFrame(updated_dict)

    updated_df.to_csv(filepath, sep="|",index=False)

def patient_creator(preset_attributes = {}, filepath = "./patients.csv"):
    """
    creates a randomized patient with optional preset attributes and adds it to the patients csv at the filepath
    """
    patient = create_patient_dict(preset_attributes)
    patient_to_csv(patient, filepath)
    return patient

if __name__ == '__main__':
    patient_creator({}, filepath="../patients.csv")
