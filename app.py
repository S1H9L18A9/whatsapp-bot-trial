from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import datetime

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

# Define conversation flow with function references
conversation_flow = {
    "greeting": {
        "response": "Welcome! Choose an option:\n1. Get the secret\n2. Get the current time\nReply with the number of your choice.",
        "options": {
            "1": "check_authorization",
            "2": "provide_time"
        },
        "handler": "handle_greeting"
    },
    "check_authorization": {
        "handler": "handle_check_authorization"
    },
    "provide_time": {
        "handler": "handle_provide_time"
    },
    "invalid_option": {
        "handler": "handle_invalid_option"
    }
}

# Handler functions
def handle_greeting(from_number, incoming_message):
    response = MessagingResponse()
    state_data = conversation_flow["greeting"]
    print("in handle_greeting")

    # Initialize user data if not already done
    if from_number not in user_data:
        print("number not in userdata, initializing")
        user_data[from_number] = {}

    # Validate the user's choice
    if incoming_message in state_data["options"]:
        user_states[from_number] = state_data["options"][incoming_message]
        return globals()[conversation_flow[user_states[from_number]]["handler"]](from_number, incoming_message)
    else:
        user_states[from_number] = "invalid_option"
        return globals()[conversation_flow["invalid_option"]["handler"]](from_number, incoming_message)

def handle_check_authorization(from_number, incoming_message):
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
    response = MessagingResponse()
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    response.message(f"The current time is: {current_time}")
    
    # Store last time request timestamp in user_data
    user_data[from_number]["last_requested_time"] = current_time
    user_states[from_number] = "greeting"
    return str(response)

def handle_invalid_option(from_number, incoming_message):
    response = MessagingResponse()
    response.message("Invalid option. Please reply with 1 or 2.")
    user_states[from_number] = "greeting"  # Reset to greeting state
    return str(response)

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    from_number = request.form.get('From')
    incoming_message = request.form.get('Body').strip()

    print('I got a message')
    # Initialize state for new user
    if from_number not in user_states:
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
