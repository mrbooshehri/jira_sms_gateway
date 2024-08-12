import os, json, requests
from flask import Flask, request, jsonify
from requests.exceptions import RequestException, Timeout, ConnectionError

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
receptors = []

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_webhook():

    # Print raw data
    data = request.json
    print ("Jira Json Data:\n", data)

    # Extract data from the webhook payload
    issue_user = data.get('user', {}).get('displayName', 'Unknown User')
    issue_key = data.get('issue', {}).get('key', 'Unknown Issue Key')

    # Constructing URLs and other strings
    if issue_key != 'Unknown Issue Key':
        issue_url = "https://pmo.vaslapp.com/browse/{}".format(issue_key)

    # Accessing nested fields safely
    issue_priority = data.get('issue', {}).get('fields', {}).get('priority', {}).get('name', 'Unknown Priority')
    issue_assignee = data.get('issue', {}).get('fields', {}).get('assignee', {}).get('displayName', 'No Assignee')
    issue_creator = data.get('issue', {}).get('fields', {}).get('creator', {}).get('displayName', 'No Creator')
    issue_reporter = data.get('issue', {}).get('fields', {}).get('reporter', {}).get('displayName', 'No Reporter')
    issue_type = data.get('issue', {}).get('fields', {}).get('issuetype', {}).get('name', 'Unknown Type')
    issue_project_name = data.get('issue', {}).get('fields', {}).get(f"customfield_{os.environ['ISSUE_PROJECT_NAME_FIELD_ID']}", {}).get('value', 'Unknown Project Name')
    issue_status = data.get('issue', {}).get('fields', {}).get('status', {}).get('name', 'Unknown Status')
    issue_summary = data.get('issue', {}).get('fields', {}).get('summary', 'No Summary')
    issue_description = data.get('issue', {}).get('fields', {}).get('description', 'No Description')
    issue_department = data.get('issue', {}).get('fields', {}).get(f"customfield_{os.environ['ISSUE_DEPARTMENT_FIELD_ID']}", {}).get('value', 'Error')

    # Change log extraction
    try:
        change_log_from = data.get('changelog', {}).get('items', [{}])[0].get('fromString', 'Change Log Not Available')
        change_log_to = data.get('changelog', {}).get('items', [{}])[-1].get('toString', 'Change Log Not Available')
    except IndexError:
        change_log_from = 'Change Log Not Available'
        change_log_to = 'Change Log Not Available'

    # Prepare the SMS message
#    message = (
#    f"Project Name: {issue_project_name}%0A"
#    f"Department: {issue_department}%0A"
#    f"Issue Key: {issue_key}%0A"
#    f"Assignee: {issue_assignee}%0A"
#    f"Reporter: {issue_reporter}%0A"
#    f"Task moved from [{change_log_from}] to [{change_log_to}]%0A"
#    f"Status: {issue_status}%0A"
#    f"Summary: {issue_summary}%0A"
#    f"Description: {issue_description}"
#)

    # Prepare the SMS message
    message = (
    f"Project Name: {issue_project_name}%0A"
    f"Department: {issue_department}%0A"
    f"Issue Key: {issue_key}%0A"
    f"Assignee: {issue_assignee}%0A"
    f"Reporter: {issue_reporter}%0A"
    f"Status: {issue_status}%0A"
    f"Summary: {issue_summary}"
)

    #print ("Message Format:\n",message)
    tmp_receptors = receptors.copy()
    tmp_receptors.append(issue_department)
    #print("receptor list is: ",tmp_receptors)
    filtered_records = filter_records_by_receptors(records, tmp_receptors)

    # Variables
    url = os.environ['SMS_ONLINE_URL']
    username = os.environ['SMS_ONLINE_USERNAME']
    password = os.environ['SMS_ONLINE_PASSWORD']
    from_number = os.environ['SMS_ONLINE_NUMBER']

    for record in filtered_records:

        number = record['phone_number']
        params = {
            "from": from_number,
            "to": number,
            "text": message,
            "password": password,
            "username": username
        }
        print(f"params: {params}")
        response = requests.get(url, params=params, timeout=5)
        print(f"SMS sent to {number}: {str(response)}")
        # Raise an exception if the request was unsuccessful
        #response.raise_for_status()
        response.raise_for_status()  # Raises an HTTPError for bad responses
    return jsonify({"message": "SMS sent successfully to all filtered receptors"}), 200


if __name__ == '__main__':
    app.run(port=5000)


