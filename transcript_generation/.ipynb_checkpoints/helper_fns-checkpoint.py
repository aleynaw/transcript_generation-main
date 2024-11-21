'''Functions for modifying message list, saving to/reading from files'''
import time, os, json, csv
import pandas as pd
from pathlib import Path

#################################
## MESSAGE_LIST MODIFICATION HELPERS
#################################

def remove_last_line_from_string(s):
    return s[:s.rfind('\n\n')]

def remove_duplicate_starters(msg_list:list) -> list:
    '''
    Returns a messages list with only one instance of the starter message.
    '''
    clean_msg_list = msg_list
    try:
        assert len(msg_list)>0, "message list is empty"
        if msg_list[0].split(":",1)[0] == msg_list[1].split(":",1)[0]:
            clean_msg_list = msg_list[1:]
    except AssertionError as e:
        print(e, "message list is empty")
    except Exception as e:
        print(e, f"first two messages: {msg_list[0:2]}")
        pass
    return clean_msg_list

# def insert_user_start(msg_list:list) -> list:
#     '''
#     Returns the messages list beginning with the user's entry into the chatting interface.
#     '''

# def modify_role_tag(transcript:list, user_tag, assistant_tag) -> list:
#     '''
#     Returns a list with the role tags changed to the new user_tag and assistant_tag.
#     '''
#     pass

def create_json_obj(msg_list:list, user_str=["User", "Patient", "P"], asst_str=["Assistant", "A"])->list:
    '''
    returns a list of messages in the format of a json object. 
    
    Parameters
    ----------
    msg_list (list):
        list of strings containing messages with the roles separated by a colon.
    user_str (str):
        string which represents the user in the synthetic interview.
    asst_str (str):
        string which represents the assistant in the synthetic interview.

    Output
    ------
    json_msgs (list):
        list of dictionaries with the keys "role" and "content"; each dictionary corresponds to a message. user and assistant tags are defaulted to "user" and "assistant".
    '''
    json_msgs = []
    for line in msg_list:
        msg_dict = dict.fromkeys(["role", "content"])
        
        if ":" in line:
            try:
                split_line = line.split(":")
                role = split_line[0]
                content = ":".join(split_line[1:]) #if ":" is used in the content itself

                if "System" in role:
                    msg_dict["role"] = "system"
                    msg_dict["content"] = content.strip()
                elif any([match in role for match in user_str]):
                    msg_dict["role"] = "user"
                    msg_dict["content"] = content.strip()
                elif any([match in role for match in asst_str]):
                    msg_dict["role"] = "assistant"
                    msg_dict["content"] = content.strip()
                else:
                    pass
            except Exception as e:
                print(e, f"while processing line {line}")
                raise e
        else:
            raise IndexError(f"':' not found in line {line}")
            pass
        
        json_msgs.append(msg_dict)
    return json_msgs

#################################
## FILE EXPORT HELPERS
#################################

def write_str_to_txt(string:str, filepath:Path):
    '''
    creates a txt file at filepath from a string.

    Parameters
    ----------
    string (str):
        string to be written to txt file
    filepath (str):
        filepath to where the file should be saved as. (e.g. "./examples/csvs/Interview_Summary.txt")
    '''
    if filepath.suffix != ".txt":
        raise ValueError("filepath suffix is not '.txt', will result in ill-formatted output")
    
    parent_dir = filepath.parent.resolve()
    if not parent_dir.exists():
        os.makedirs(parent_dir, exist_ok=True)

    with open(filepath, 'w') as f:
        f.write(string)

def write_list_to_txt(lst:list, filepath:Path, sep="\n\n"):
    '''
    creates a txt file at filepath from a string.

    Parameters
    ----------
    lst (list):
        string to be written to txt file
    filepath (str or Path):
        filepath to where the file should be saved as. (e.g. "./examples/csvs/Interview_Summary.txt")
    sep (str):
        string used for separation between messages
    '''
    filepath = Path(filepath)
    if filepath.suffix != ".txt":
        raise ValueError("filepath suffix is not '.txt', will result in ill-formatted output")
    
    parent_dir = filepath.parent.resolve()
    if not parent_dir.exists():
        os.makedirs(parent_dir, exist_ok=True)

    with open(filepath, 'w') as f:
        for item in lst: 
            f.write(item+sep)

def write_list_to_json(json_obj:list, filepath:Path):
    '''
    creates a json file in at filepath from a list of dictionaries with role/content tags.

    Parameters
    ----------
    json_obj (NxM list):
        json-like formatted list containing dictionaries of key:value pairings
    filepath (str):
        filepath to where the file should be saved as. (e.g. "./examples/csvs/Interview.json")
    '''
    if filepath.suffix != ".json":
        raise ValueError("filepath suffix is not '.json', will result in ill-formatted output")
    
    parent_dir = filepath.parent.resolve()
    if not parent_dir.exists():
        os.makedirs(parent_dir, exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(json_obj, f, indent=4)

#################################
## FILE IMPORT HELPERS
#################################

def patient_to_str(patient, ignore_keys=["Clinician Name", "Appointment Date"]):
    '''
    returns a string of the patient's information/characteristics in a printable format. does not print keys with empty values or the keys listed in ignore_keys.

    Parameters
    ----------
    patient: dict, Series, NamedTuple
        single patient's information
    ignore_keys: list 
        list containing variable keys that should not be displayed in the output

    Output
    ------
    patient_str: str
        patient's information in the format
        "key: value
        key: value
        ..."
    '''
    patient_str = ""
    for key in patient.keys():
        if key in ignore_keys:
            continue
        elif (not pd.isna(patient[key])) or len(str(patient[key]))==0:
            patient_str += f"{key}: {patient[key]}\n"
    return patient_str.strip()

def transcript_json_to_str(transcript, assistant_tag = "Assistant", user_tag = "User", msg_separator = "\n"):
    '''
    turn transcript json file into a string that can be used to hydrate prompts
    
    Parameters
    ----------
    transcript (str or list):
        path to json file or list containing the format [{"role": "user", "content": "..."},\n{"role": "assistant", "content": "..."}]. start with the user's entrance message and end with a assistant's response.
    
    Output
    ------
        string that looks like "assistant: ...\nuser:..." for all conversation pairs
    '''
    if isinstance(transcript, list):
        transcript_list = transcript
    else:
        file = open(transcript, "r")
        transcript_list = json.load(file)

    transcript_str = ""

    for message_dict in transcript_list:
        if message_dict["role"] == "user":
            transcript_str = transcript_str + rf"{user_tag}: {message_dict['content']}" + msg_separator
        if message_dict["role"] == "assistant":
            transcript_str = transcript_str + rf"{assistant_tag}: {message_dict['content']}"  + msg_separator
    
    return transcript_str.strip()

#################################
## FILE MODIFICATION HELPERS
#################################

def track_patient(interview_path, 
                  patient_str, 
                  extra_info_dict = {},
                  tracking_path="patients_tracking.csv"
                  ):
    '''
    updates the relevant information for patients in a csv file to track and compare the synthetic interview filename, patient information used to construct the interview, and the generated summary from the interview. creates a file in the current directory.
    '''
    #load existing tracking file
    try:
        tracking_filename = Path(interview_path).stem
        tracking_df = pd.read_csv(tracking_path, sep="|")
        tracking_dict = tracking_df.to_dict("list")
        existing_len = tracking_df.shape[0] #how many empty rows to add for a new column

        #get info of row to append
        append_dict = {
            "interview_path":interview_path,
            "patient_str":patient_str,
            }
        append_dict.update(extra_info_dict)
        missing_cols = list(set(list(tracking_dict.keys())) - set(list(append_dict.keys()))) #columns to be added to the incoming row
        for missing_col in missing_cols:
            append_dict[missing_col] = ""

        #add everything from patient dict to to the current dict
        for col in append_dict.keys():
            if col in tracking_dict:
                tracking_dict[col].append(append_dict[col])
            else:
                #create a new column for variable in patient dict not in current dict
                buffer = [""]*existing_len
                buffer.append(append_dict[col])
                tracking_dict[col] = buffer
        pd.DataFrame(tracking_dict).to_csv(tracking_path, sep="|",index=False)
    except Exception as e:
        print(e)
        append_dict = {
            "interview_path":interview_path,
            "patient_str":patient_str,
            }
        append_dict.update(extra_info_dict)
        pd.DataFrame(append_dict, index=[0]).to_csv(tracking_path, sep="|",index=False)