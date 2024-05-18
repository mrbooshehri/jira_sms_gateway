# Jira Webhook SMS Notifier

## Overview

This project is designed to automate the sending of SMS notifications to a list of recipients whenever specific events occur in a Jira project. It utilizes Jira's webhook feature to trigger an external Flask application, which then sends SMS messages to the specified recipients using the Kavenegar SMS gateway. The application is containerized using Docker for easy deployment and scalability.

## Prerequisites

- Docker installed on your machine
- A Kavenegar account with an API key
- A list of recipient phone numbers

## Setup

1. **Clone the Repository:**

```bash
git clone https://github.com/mrbooshehri/jira_sms_gateway.git
cd jira_sms_gateway
```

2. **Build the Docker Image:**

```bash
docker build -t jira_sms_gateway .
```


3. **Prepare the Receptor File:**

   Create a text file named `receptors.txt` in the project directory. Each line should contain a phone number.

> Sample receptors.txt:
> ```
> Admin|John Lenon|09101234567
> PMO|David Lenz|09111234567
> Devops|Gary More|09121234567
> Support|Kurt Cobain|09131234567
> ```

4. **Run the Docker Container:**

```
docker run -p 5000:5000 -e KAVENEGAR_API_KEY=your_api_key \
-e SENDER_NUMBER=your_sender_number -e RECEPTOR_FILE_PATH=receptors.txt \
jira_sms_gateway
```

> Replace `your_api_key` and `your_sender_number` with your actual Kavenegar API key and sender number.

## Usage

1. **Configure Jira Webhook:**

   In your Jira project, navigate to the webhook settings and create a new webhook. Set the URL to point to the endpoint your Flask application is listening on (e.g., `http://localhost:5000/webhook`).

2. **Trigger the Webhook:**

   Perform an action in Jira that triggers the webhook (e.g., create, update, or transition an issue). The Flask application will receive the webhook notification and send an SMS to each recipient listed in the `receptors.txt` file.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.


