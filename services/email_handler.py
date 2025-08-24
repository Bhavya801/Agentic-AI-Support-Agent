# import imaplib
# import email
# from email.header import decode_header
# import ssl
# import smtplib
# from email.message import EmailMessage
# from datetime import datetime, timedelta, timezone
# import os
# import json
# import google.generativeai as genai
# from dotenv import load_dotenv

# # Import the services
# from services.trello import create_trello_card
# from services.firebase import FirebaseService

# def send_email(receiver_email, subject, body):
#     """
#     Sends an email using SMTP and environment variables for credentials.
#     """
#     sender_email = os.getenv("SUPPORT_EMAIL_ADDRESS")
#     password = os.getenv("SUPPORT_EMAIL_PASSWORD")
#     smtp_server = "smtp.gmail.com"
#     port = 587

#     try:
#         context = ssl.create_default_context()
#         msg = EmailMessage()
#         msg['Subject'] = subject
#         msg['From'] = sender_email
#         msg['To'] = receiver_email
#         msg.set_content(body)

#         print(f"Connecting to SMTP server at {smtp_server}...")
#         with smtplib.SMTP(smtp_server, port) as server:
#             server.starttls(context=context)
#             server.login(sender_email, password)
#             print(f"Sending email to {receiver_email}...")
#             server.send_message(msg)
#             print("Email sent successfully!")

#     except smtplib.SMTPException as e:
#         print(f"SMTP Error: {e}")
#         print("Make sure the sender's email and app password are correct.")
#     except Exception as e:
#         print(f"An unexpected error occurred while sending email: {e}")


# def fetch_recent_emails():
#     """
#     Fetches recent emails from the inbox and returns them as a list of dicts.
#     """
#     email_address = os.getenv("SUPPORT_EMAIL_ADDRESS")
#     password = os.getenv("SUPPORT_EMAIL_PASSWORD")
#     imap_server = "imap.gmail.com"
#     mail = None
#     emails_data = []

#     try:
#         mail = imaplib.IMAP4_SSL(imap_server)
#         mail.login(email_address, password)
#         mail.select("inbox")

#         five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
        
#         # Search for all emails since a specific date
#         date_string = five_minutes_ago.strftime("%d-%b-%Y")
#         status, messages = mail.search(None, f'(SINCE "{date_string}")')
#         email_ids = messages[0].split()

#         if not email_ids:
#             print("No emails found since the specified date.")
#             return []

#         print(f"Found {len(email_ids)} emails since {date_string}. Checking for recent ones...")

#         for email_id in reversed(email_ids):
#             status, msg_data = mail.fetch(email_id, "(RFC822)")
#             if status != "OK":
#                 continue

#             msg = email.message_from_bytes(msg_data[0][1])
#             email_date = email.utils.parsedate_to_datetime(msg.get("Date"))

#             if email_date > five_minutes_ago:
#                 subject, _ = decode_header(msg["Subject"])[0]
#                 if isinstance(subject, bytes):
#                     subject = subject.decode("utf-8")
                
#                 sender, _ = decode_header(msg.get("From"))[0]
#                 if isinstance(sender, bytes):
#                     sender = sender.decode("utf-8")
#                 sender_address = email.utils.parseaddr(sender)[1]
                
#                 body = ""
#                 if msg.is_multipart():
#                     for part in msg.walk():
#                         if part.get_content_type() == "text/plain":
#                             body = part.get_payload(decode=True).decode()
#                             break
#                 else:
#                     body = msg.get_payload(decode=True).decode()

#                 emails_data.append({
#                     "subject": subject,
#                     "sender_address": sender_address,
#                     "body": body
#                 })
#             else:
#                 # Since we are iterating from the newest, we can stop here
#                 break
        
#         return emails_data

#     except imaplib.IMAP4.error as e:
#         print(f"IMAP Error: {e}")
#         print("Make sure your email address and app password are correct and IMAP is enabled.")
#         return []
#     except Exception as e:
#         print(f"An unexpected error occurred: {e}")
#         return []
#     finally:
#         if mail:
#             mail.close()
#             mail.logout()
#             print("IMAP connection closed.")

# def process_emails_job():
#     """
#     This function contains the core logic for the AI support agent.
#     """
#     # Load environment variables inside the job function
#     load_dotenv()
    
#     # Configure the Gemini API and Firebase
#     try:
#         gemini_api_key = os.getenv("GEMINI_API_KEY")
#         if not gemini_api_key:
#             raise ValueError("GEMINI_API_KEY not found in environment variables.")
#         genai.configure(api_key=gemini_api_key)
#         model = genai.GenerativeModel('gemini-1.5-pro')
        
#         firebase_service = FirebaseService()
#     except Exception as e:
#         print(f"Failed to initialize services: {e}")
#         return

#     # Fetch recent emails
#     recent_emails = fetch_recent_emails()
#     if not recent_emails:
#         print("No new emails found in the last 5 minutes.")
#         return

#     for email_data in recent_emails:
#         subject = email_data["subject"]
#         sender_address = email_data["sender_address"]
#         body = email_data["body"]
        
#         print("-" * 50)
#         print(f"Processing new email from: {sender_address}")
#         print(f"Subject: {subject}")
#         print(f"Body: {body[:200]}...")

#         # --- AI Decision Making ---
#         print("Asking AI for an action...")
        
#         prompt = (
#             "You are an AI customer support agent for Casease.tranzission.com, a legal case management platform for professionals like advocates, "
#             "insolvency professionals, and liquidators. Your goal is to help customers with their queries regarding case filing, document management, "
#             "and workflow issues. You should classify the email, provide a response, and decide if it needs to be escalated to a human."
#             "\n\nPossible classifications: 'Password Reset', 'Billing Issue', 'Technical Error', 'General Question', 'Account Access', 'Other'."
#             "\n\nAnalyze the following email from a legal professional using our platform. Based on the email's content, "
#             "decide if the query can be answered immediately with a short, helpful response, or if it is complex "
#             "(e.g., involving specific client data, technical errors, or legal advice), requires account-specific information, or is a complaint that "
#             "must be escalated to a human support representative. The customer has given you an explicit command to 'create a support ticket'. If the "
#             "email contains this phrase, you must escalate it and not attempt to answer it yourself."
#             "\n\nRespond with a JSON object containing three keys: 'action', 'response_text', and 'classification'."
#             "The 'action' must be either 'reply' or 'escalate'. "
#             "The 'response_text' should contain either your suggested response to the customer "
#             "or a short summary for the human agent, such as 'Customer needs a refund'."
#             "The 'classification' should be one of the pre-defined categories."
#             "\n\nCustomer Email:\n---\n"
#             f"From: {sender_address}\nSubject: {subject}\nBody: {body}"
#             "\n---\n"
#         )

#         response = model.generate_content(prompt, stream=False)
        
#         try:
#             response_text = response.text.strip().replace('```json', '').replace('```', '')
#             ai_response = json.loads(response_text)
#             action = ai_response.get("action")
#             response_text = ai_response.get("response_text")
#             classification = ai_response.get("classification")

#             # Log the email and AI analysis to Firebase
#             db_doc = {
#                 "from": sender_address,
#                 "subject": subject,
#                 "body": body,
#                 "timestamp": datetime.now(timezone.utc),
#                 "ai_action": action,
#                 "ai_classification": classification,
#                 "ai_response_text": response_text
#             }
#             firebase_service.add_ticket(db_doc)

#             if action == "reply":
#                 print("AI decided to REPLY.")
#                 reply_subject = f"Re: {subject}"
#                 send_email(sender_address, reply_subject, response_text)
#             elif action == "escalate":
#                 print("AI decided to ESCALATE.")
#                 # Send a holding email to the customer
#                 holding_subject = f"Re: {subject} - We've received your request"
#                 holding_body = (
#                     "Thank you for reaching out to Casease support. We've received your request and our human support team is now looking into it. "
#                     "We will get back to you as soon as possible with a detailed response. Thank you for your patience."
#                 )
#                 send_email(sender_address, holding_subject, holding_body)

#                 # Create the Trello card for the human agent
#                 card_name = f"Support Ticket ({classification}) from {sender_address}"
#                 card_desc = f"Subject: {subject}\n\nEmail Body:\n---\n{body}\n\nAI Summary: {response_text}"
#                 create_trello_card(card_name, card_desc)
#             else:
#                 print(f"AI returned an unknown action: {action}. Escalating to be safe.")
#                 card_name = f"UNKNOWN AI ACTION from {sender_address}"
#                 card_desc = f"Subject: {subject}\n\nEmail Body:\n---\n{body}\n\nAI Response was:\n---\n{ai_response}"
#                 create_trello_card(card_name, card_desc)

#         except json.JSONDecodeError as e:
#             print(f"AI returned invalid JSON. Escalating to be safe. Error: {e}")
#             card_name = f"AI JSON ERROR from {sender_address}"
#             card_desc = f"Subject: {subject}\n\nEmail Body:\n---\n{body}\n\nRaw AI Response:\n---\n{response.text}"
#             create_trello_card(card_name, card_desc)


import imaplib
import email
from email.header import decode_header
import ssl
import smtplib
from email.message import EmailMessage
from datetime import datetime, timedelta, timezone
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Import the services
from services.trello import create_trello_card
from services.firebase import FirebaseService
from services.typesense_rag import TypesenseRAG


# --- Email Functionality ---

def send_email(receiver_email, subject, body):
    """
    Sends an email using SMTP and environment variables for credentials.
    """
    sender_email = os.getenv("SUPPORT_EMAIL_ADDRESS")
    password = os.getenv("SUPPORT_EMAIL_PASSWORD")
    smtp_server = "smtp.gmail.com"
    port = 587

    try:
        context = ssl.create_default_context()
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = receiver_email
        msg.set_content(body)

        print(f"Connecting to SMTP server at {smtp_server}...")
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls(context=context)
            server.login(sender_email, password)
            server.send_message(msg)
            print("Email sent successfully!")

    except smtplib.SMTPException as e:
        print(f"SMTP Error: {e}")
        print("Make sure the sender's email and app password are correct.")
    except Exception as e:
        print(f"An unexpected error occurred while sending email: {e}")


def fetch_recent_emails():
    """
    Fetches recent emails from the inbox and returns them as a list of dicts.
    """
    email_address = os.getenv("SUPPORT_EMAIL_ADDRESS")
    password = os.getenv("SUPPORT_EMAIL_PASSWORD")
    imap_server = "imap.gmail.com"
    mail = None
    emails_data = []

    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, password)
        mail.select("inbox")

        five_minutes_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
        date_string = five_minutes_ago.strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(SINCE "{date_string}")')
        email_ids = messages[0].split()

        if not email_ids:
            print("No emails found since the specified date.")
            return []

        for email_id in reversed(email_ids):
            status, msg_data = mail.fetch(email_id, "(RFC822)")
            if status != "OK": continue

            msg = email.message_from_bytes(msg_data[0][1])
            email_date = email.utils.parsedate_to_datetime(msg.get("Date"))

            if email_date > five_minutes_ago:
                subject, _ = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes): subject = subject.decode("utf-8")
                
                sender, _ = decode_header(msg.get("From"))[0]
                if isinstance(sender, bytes): sender = sender.decode("utf-8")
                sender_address = email.utils.parseaddr(sender)[1]
                
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                emails_data.append({
                    "subject": subject,
                    "sender_address": sender_address,
                    "body": body
                })
            else:
                break
        
        return emails_data

    except imaplib.IMAP4.error as e:
        print(f"IMAP Error: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []
    finally:
        if mail:
            mail.close()
            mail.logout()
            print("IMAP connection closed.")

def process_emails_job():
    """
    This function contains the core logic for the AI support agent.
    """
    load_dotenv()
    
    try:
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        firebase_service = FirebaseService()
        typesense_rag = TypesenseRAG()
    except Exception as e:
        print(f"Failed to initialize services: {e}")
        return

    recent_emails = fetch_recent_emails()
    if not recent_emails:
        print("No new emails found in the last 5 minutes.")
        return

    for email_data in recent_emails:
        subject = email_data["subject"]
        sender_address = email_data["sender_address"]
        body = email_data["body"]
        
        print("-" * 50)
        print(f"Processing new email from: {sender_address}")
        print(f"Subject: {subject}")
        
        prompt = (
            "You are an AI customer support agent for Casease.tranzission.com, a legal case management platform for professionals like advocates, "
            "insolvency professionals, and liquidators. Your goal is to help customers with their queries regarding case filing, document management, "
            "and workflow issues. You should classify the email, provide a response, and decide if it needs to be escalated to a human."
            "\n\nPossible classifications: 'Password Reset', 'Billing Issue', 'Technical Error', 'General Question', 'Account Access', 'Knowledge Base Query', 'Other'."
            "\n\nAnalyze the following email from a legal professional. Based on the email's content, "
            "decide if the query can be answered immediately with a short, helpful response, or if it is a request for legal information "
            "that could be answered by a RAG model. If the query is about a specific legal case or a point of law, "
            "classify it as **'Knowledge Base Query'** and provide the user's question verbatim in the 'response_text' (e.g., 'What is the ratio of the Shrinathji Spintex case?'). "
            "The customer has given you an explicit command to 'create a support ticket'. If the "
            "email contains this phrase, you must escalate it and not attempt to answer it yourself."
            "\n\nRespond with a JSON object containing three keys: 'action', 'response_text', and 'classification'."
            "The 'action' must be either 'reply' or 'escalate'. "
            "The 'response_text' should contain either your suggested response to the customer "
            "or a short summary for the human agent, or the verbatim query for a knowledge base. "
            "The 'classification' should be one of the pre-defined categories."
            "\n\nCustomer Email:\n---\n"
            f"From: {sender_address}\nSubject: {subject}\nBody: {body}"
            "\n---\n"
        )

        response = model.generate_content(prompt, stream=False)
        
        try:
            response_text = response.text.strip().replace('```json', '').replace('```', '')
            ai_response = json.loads(response_text)
            action = ai_response.get("action")
            response_text = ai_response.get("response_text")
            classification = ai_response.get("classification")

            db_doc = {
                "from": sender_address,
                "subject": subject,
                "body": body,
                "timestamp": datetime.now(timezone.utc),
                "ai_action": action,
                "ai_classification": classification,
                "ai_response_text": response_text
            }
            firebase_service.add_ticket(db_doc)

            if action == "reply":
                if classification == "Knowledge Base Query":
                    print("AI decided to REPLY with a knowledge base query.")
                    rag_response = typesense_rag.get_rag_response(response_text)
                    
                    if rag_response:
                        final_response = rag_response
                        send_email(sender_address, f"Re: {subject}", final_response)
                        print("Sent a detailed RAG-based response.")

                    else:
                        print("Knowledge base search returned no results or failed. Falling back to general reply.")
                        send_email(sender_address, f"Re: {subject}", "Thank you for your query. I could not find a specific case on this topic, but our team will review and get back to you shortly.")

                else:
                    print("AI decided to send a general REPLY.")
                    send_email(sender_address, f"Re: {subject}", response_text)

            elif action == "escalate":
                print("AI decided to ESCALATE.")
                holding_subject = f"Re: {subject} - We've received your request"
                holding_body = (
                    "Thank you for reaching out to Casease support. We've received your request and our human support team is now looking into it. "
                    "We will get back to you as soon as possible with a detailed response. Thank you for your patience."
                )
                send_email(sender_address, holding_subject, holding_body)

                card_name = f"Support Ticket ({classification}) from {sender_address}"
                card_desc = f"Subject: {subject}\n\nEmail Body:\n---\n{body}\n\nAI Summary: {response_text}"
                create_trello_card(card_name, card_desc)
            else:
                print(f"AI returned an unknown action: {action}. Escalating to be safe.")
                card_name = f"UNKNOWN AI ACTION from {sender_address}"
                card_desc = f"Subject: {subject}\n\nEmail Body:\n---\n{body}\n\nAI Response was:\n---\n{ai_response}"
                create_trello_card(card_name, card_desc)

        except json.JSONDecodeError as e:
            print(f"AI returned invalid JSON. Escalating to be safe. Error: {e}")
            card_name = f"AI JSON ERROR from {sender_address}"
            card_desc = f"Subject: {subject}\n\nEmail Body:\n---\n{body}\n\nRaw AI Response:\n---\n{response.text}"
            create_trello_card(card_name, card_desc)
            print("Email sent successfully!")