from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Approved phone numbers
APPROVED_NUMBERS = ["+1234567890", "+919820621850", "+919892402126"]  # Replace with your approved numbers
APPROVED_NUMBERS = [f'whatsapp:{i}' for i in APPROVED_NUMBERS]

# Code word to send back
CODE_WORD = "YourSecretCode"

@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    # Get the sender's phone number
    from_number = request.form.get('From')
    # Get the incoming message
    incoming_message = request.form.get('Body')

    response = MessagingResponse()

    if from_number in APPROVED_NUMBERS:
        # Send the code word back
        response.message(CODE_WORD)
    else:
        # Send a generic rejection message
        response.message(f"Number:{from_number}\nSorry, you are not authorized to access this service.")

    return str(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
