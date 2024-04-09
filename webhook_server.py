import os
from flask import Flask, request, jsonify
from kavenegar import *

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Extract data from the webhook payload
    data = request.json
    issue_user = data['user']['displayName']
    issue_key = data['issue']['key']
    issue_url = "https://pmo.vaslapp.com/browse/{}".format(issue_key)
    issue_priority = data['issue']['fields']['priority']['name']
    issue_assignee = data['issue']['fields']['assignee']['displayName']
    issue_creator= data['issue']['fields']['creator']['displayName']
    issue_reporter= data['issue']['fields']['reporter']['displayName']
    issue_type= data['issue']['fields']['issuetype']['name']
    issue_project_name= data['issue']['fields']['project']['name']
    issue_summary= data['issue']['fields']['summary']

    # Prepare the SMS message
    message = "User: {}\nKey: {}\nPriority: {}\nAssignee: {}\nCreator: {}\nReporter: {}\nType: {}\nProject Name: {}\nSummary: {}".format(issue_user, issue_key,issue_priority, issue_assignee, issue_creator, issue_reporter, issue_type, issue_project_name, issue_summary)

    # Read receptor numbers from a file
    receptor_file_path = os.environ.get(os.environ['RECEPTOR_FILE_PATH'], 'receptors.txt')
    with open(receptor_file_path, 'r') as file:
        receptor_numbers = file.readlines()

    # Send SMS using Kavenegar API
    try:
        api = KavenegarAPI(os.environ['KAVENEGAR_API_KEY'])
        for number in receptor_numbers:
            number = number.strip() # Remove any leading/trailing whitespace
            params = {
                'receptor': number,
                'message': message
            }
            response = api.sms_send(params)
            print(f"SMS sent to {number}: {str(response)}")
        return jsonify({"message": "SMS sent successfully to all receptors"}), 200
    except APIException as e:
        print(str(e))
        return jsonify({"error": "Failed to send SMS", "details": str(e)}), 500
    except HTTPException as e:
        print(str(e))
        return jsonify({"error": "Failed to send SMS", "details": str(e)}), 500
    except FileNotFoundError:
        print(f"Receptor file not found: {receptor_file_path}")
        return jsonify({"error": "Receptor file not found"}), 500

if __name__ == '__main__':
    app.run(port=5000)
