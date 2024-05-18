import os, json
from flask import Flask, request, jsonify
from kavenegar import *

def read_file_and_store_contents(file_path):
    try:
        with open(file_path, 'r') as file:
            records = []
            for line in file:
                line = line.strip()  # Remove newline character
                parts = line.split('|')
                record = {
                    'department': parts[0],
                    'name': parts[1],
                    'phone_number': parts[2]
                }
                records.append(record)
            return records
    except FileNotFoundError:
        print(f"The file {file_path} was not found.")
        return []

def filter_records_by_receptors(records, receptors):
    filtered_records = [record for record in records if record['department'] in receptors]
    return filtered_records


records = read_file_and_store_contents(os.environ.get(os.environ['RECEPTOR_FILE_PATH'], 'receptors.txt'))
receptors = ["PMO", "Admin"]

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():

    # Print raw data
    data = request.json
    print ("Jira Json Data:\n", data)
    #print ("Jira Json Data:\n",json.dumps(data, indent=4))

    # Extract data from the webhook payload
    issue_user = data['user']['displayName']
    issue_key = data['issue']['key']
    issue_url = "https://pmo.vaslapp.com/browse/{}".format(issue_key)
    issue_priority = data['issue']['fields']['priority']['name']
    issue_assignee = data['issue']['fields']['assignee']['displayName']
    issue_creator = data['issue']['fields']['creator']['displayName']
    issue_reporter = data['issue']['fields']['reporter']['displayName']
    issue_type = data['issue']['fields']['issuetype']['name']
    issue_project_name = data['issue']['fields']['customfield_10503']['value']
    issue_status = data['issue']['fields']['status']['name']
    issue_summary = data['issue']['fields']['summary']
    issue_description = data['issue']['fields']['description']
    issue_department = data['issue']['fields']['customfield_10902']['value']
    change_log_from = data['changelog']['items'][-1]['fromString']
    change_log_to= data['changelog']['items'][-1]['toString']

    # Prepare the SMS message
    message = (
    f"Assignee: {issue_assignee}\n"
    f"Reporter: {issue_reporter}\n"
    f"Department: {issue_department}\n"
    f"Project Name: {issue_project_name}\n"
    f"Summary: {issue_summary}\n"
    f"Task moved from [{change_log_from}] to [{change_log_to}]\n"
    f"Issue Type: {issue_type}\n"
    f"Issue Key: {issue_key}\n"
    f"Priority: {issue_priority}\n"
    f"Created By: {issue_creator}\n"
    f"Status: {issue_status}\n"
    f"Description: {issue_description}\n"
)

    #print ("Message Format:\n",message)
    tmp_receptors = receptors.copy()
    tmp_receptors.append(issue_department)
    #print("receptor list is: ",tmp_receptors)
    filtered_records = filter_records_by_receptors(records, tmp_receptors)

   # Send SMS using Kavenegar API
    try:
        api = KavenegarAPI(os.environ['KAVENEGAR_API_KEY'])
        for record in filtered_records:
            number = record['phone_number']
            #message_1 = message + "\nGroup: {}".format(record['department'])
            params = {
                'receptor': number,
                'message': message
            }
            response = api.sms_send(params)
            print(f"SMS sent to {number}: {str(response)}")
        return jsonify({"message": "SMS sent successfully to all filtered receptors"}), 200
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
