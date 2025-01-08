from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import datetime
import pandas as pd
from fuzzywuzzy import process
from difflib import SequenceMatcher
from typing import Tuple
import logging

logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG for verbose output
logger = logging.getLogger(__name__)

logger.debug("This is a debug message")

# global df 
df = None
FILE_NAME = 'Enterprise stock report - India.xlsx'
MAX_MATCHES = 3

app = Flask(__name__)

# Approved phone numbers
APPROVED_NUMBERS = ["+1234567890", "+0987654321"]
# Approved phone numbers
APPROVED_NUMBERS = ["+1234567890", "+919820621850", "+919892402126"]  # Replace with your approved numbers
APPROVED_NUMBERS = [f'whatsapp:{i}' for i in APPROVED_NUMBERS]



# Secret code
CODE_WORD = "YourSecretCode"

# Store user states and data
user_states = {}
user_data = {}
df = None

# Define conversation flow with function references
conversation_flow = {
    "greeting": {
        "options": {
            "1": "check_authorization",
            "2": "provide_time",
            "3": "check_on_quantity"  # New option
        },
        "handler": "handle_greeting"
    },
    "check_authorization": {
        "handler": "handle_check_authorization"
    },
    "provide_time": {
        "handler": "handle_provide_time"
    },
    "check_on_quantity": {
        "handler": "handle_check_on_quantity_greet"
    },
    "check_on_quantity2": {
        "handler": "handle_check_on_quantity"
    },
    "check_on_quantity": {
        "handler": "handle_check_on_quantity_greet"
    },
    "check_on_person": {
        "handler": "handle_check_on_person"
    },
    "invalid_option": {
        "handler": "handle_invalid_option"
    },
}


def handle_check_on_quantity_greet(from_number, incoming_message):
    logger.debug('In check on quantity')
    logger.debug(f'user_data:{user_data}\nuser_states:{user_states}')
    response = MessagingResponse()
    if not user_data.get(from_number):
        user_data[from_number] = {'state':'get_code'}
    
    
    if user_data[from_number]['state'] == 'get_code':
        logger.debug('I realize I need to ask to get code')
        response.message('Reply with the material code you want to check quantity for.')
        user_data[from_number]['state'] = 'check_code'
        return str(response)
    logger.debug('I don need to ask for code now')
    name_result = get_name_match_for(incoming_message)
    if type(name_result) is str:
        logger.debug('I got exact answer')
        response.message(name_result)
        del user_data[from_number]['state']
        user_states[from_number] = "greeting"
        return str(response)
    logger.debug('I need to give options')
    #The name results in various responses. Need to process further
    return handle_check_on_person(from_number, incoming_message, name_result)


def get_name_match_for(input_name:str)->str | list:
    logger.debug('In the pandas part')
    logger.debug(f'df: {df}')
    global df
    if df is None:
        logger.debug('Starting to read df')
        df = pd.read_excel(FILE_NAME)
        logger.debug('Reading ended')
    if (n:=input_name.strip().upper()) in df['MaterialCode'].values:
        return get_quantity_for(n)
    top_matches = process.extract(input_name, df['MaterialCode'].unique(), limit=MAX_MATCHES)
    return top_matches


def visualize_string_differences(original: str, similar: str) -> str:
    """
    Visualizes differences between two strings using markers:
    - Changed characters are wrapped in *
    - Skipped/missing characters are marked with _
    
    Args:
        original: The original string to compare against
        similar: The similar string to compare with
    
    Returns:
        A string showing the differences with markers
    """
    matcher = SequenceMatcher(None, original, similar)
    logger.debug('Emphasizing differences')
    result = []
    i = 0  # Index for the similar string
    
    for tag, orig_start, orig_end, sim_start, sim_end in matcher.get_opcodes():
        if tag == 'equal':
            # Characters match exactly
            result.append(similar[sim_start:sim_end])
        elif tag == 'replace':
            # Characters were changed
            result.append(f" *{similar[sim_start:sim_end]}* ")
        elif tag == 'delete':
            # Characters in original were deleted
            result.extend(['_'] * (orig_end - orig_start))
        elif tag == 'insert':
            # New characters were inserted
            result.append(f" *{similar[sim_start:sim_end]}* ")
    
    return ''.join(result)


def whatsapp_format_for(names, code_wanted)->list:
    logger.debug('Formatting output')
    return [f"{visualize_string_differences(code_wanted,i)} - {v}% match" for i,v in names]


def handle_check_on_person(from_number, incoming_message, matching_names):
    logger.debug('In check on person')
    logger.debug(f'user_data:{user_data}\nuser_states:{user_states}')
    response = MessagingResponse()
    
    if not user_data.get(from_number):
        user_data[from_number] = {'state':'check_code'}

    # If no options stored yet, we're generating dynamic options
    if "dynamic_options" not in user_data[from_number]:
        matching_names = whatsapp_format_for(matching_names, incoming_message)
        if matching_names:
            user_data[from_number]["dynamic_options"] = matching_names
            options_list = "\n".join(f"{i+1}. {name}" for i, name in enumerate(matching_names))
            response.message(f"Found the following matches:\n{options_list}\nReply with the number of your choice.")
        else:
            response.message("No matches found for your query.")
            user_states[from_number] = "greeting"
        return str(response)
        

    # If options already stored, process the user's selection
    try:
        choice_index = int(incoming_message) - 1
        selected_name = user_data[from_number]["dynamic_options"][choice_index]
        response.message(f"You selected: {selected_name}. Checking on them...")
        response.message(get_quantity_for(selected_name))
        # Clear dynamic options after processing
        del user_data[from_number]["dynamic_options"]
        del user_data[from_number]['state']
        user_states[from_number] = "greeting"
    except (ValueError, IndexError):
        response.message("Invalid choice. Please reply with a valid number.")
    return str(response)


def get_quantity_for(selected_name)->str:
    logger.debug('Giving quantity')
    return df[df['MaterialCode']==selected_name][['Branch','TodayStock','BlockedStk']].to_string(index=False)



# Handler functions
def handle_greeting(from_number, incoming_message):
    logger.debug('In greeting')
    response = MessagingResponse()

    if user_states[from_number] == "greeting" and incoming_message.lower() == "hi":
        response.message("Welcome! Choose an option:\n1. Get the secret\n2. Get the current time\n3. Check on a person\nReply with the number of your choice.")
        return str(response)

    state_data = conversation_flow["greeting"]
    if incoming_message in state_data["options"]:
        user_states[from_number] = state_data["options"][incoming_message]
        return globals()[conversation_flow[user_states[from_number]]["handler"]](from_number, incoming_message)
    else:
        user_states[from_number] = "invalid_option"
        return globals()[conversation_flow["invalid_option"]["handler"]](from_number, incoming_message)


def handle_check_authorization(from_number, incoming_message):
    logger.debug('Checking authorization')
    response = MessagingResponse()
    if from_number in APPROVED_NUMBERS:
        # Store secret code access timestamp in user_data
        user_data[from_number]["last_accessed_secret"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response.message(f"Here is your secret code: {CODE_WORD}")
    else:
        response.message("You are not authorized to receive the secret.")
    user_states[from_number] = "greeting"
    return str(response)

def handle_provide_time(from_number, incoming_message):
    logger.debug('In providing time')
    response = MessagingResponse()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response.message(f"The current time is: {current_time}")
    
    # Store last time request timestamp in user_data
    user_data[from_number]["last_requested_time"] = current_time
    user_states[from_number] = "greeting"
    return str(response)

def handle_invalid_option(from_number, incoming_message):
    logger.debug('In invalid option')
    response = MessagingResponse()
    response.message("Invalid option. Please reply with a number in the list")
    user_states[from_number] = "greeting"  # Reset to greeting state
    return str(response)

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    from_number = request.form.get('From')
    incoming_message = request.form.get('Body').strip()

    logger.debug('I got a message')
    # Initialize state for new user
    if (from_number not in user_states) or (incoming_message.strip().lower()=='hi'):
        print('new number, adding to user states')
        user_states[from_number] = "greeting"

    # Get the current state and handler function
    current_state = user_states[from_number]
    handler_function_name = conversation_flow[current_state]["handler"]

    # Call the appropriate handler function
    handler_function = globals()[handler_function_name]
    return handler_function(from_number, incoming_message)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
