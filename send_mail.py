# from swarm import Swarm, Agent
# import os
# from services import gmail_authenticate
# from email.message import EmailMessage
# import base64
# # from main import context_variables
# # # Ensure API Key is set in the environment
# os.environ[
#     "OPENAI_API_KEY"] = "sk-svcacct-f-w8Kl1PbYP-xfJ0mJA5tJ9iMGLfZNBlJWfPNrpzLak9H-MO2orHBdyIa7a5tWT3BlbkFJGUdItJUijerYpfDpR29p_RjNJpfTflOgFdugRlWXm21PB3Rfn5kqZ4FkmmzD8A"

# # # Initialize the Swarm client
# client = Swarm()
 
# gmail_service = gmail_authenticate()
 
 
# # %%
# def send_email(service, context_variables: dict):
#     """
#     Sends an email via the Gmail API.
#     """
#     try:
#         message = EmailMessage()
#         message["To"] = context_variables.get('From')
#         message["From"] = "harshavardhanbudda@gmail.com"

#         if context_variables.get('Generated_status') != "Approved":
#             message["Subject"] = f"Required Additional Information for the {context_variables.get('Subject')}"
            
#             structured_Message = f"""
# Dear {context_variables.get('customer_name', 'Valued Customer')},

# Thank you for submitting your claim request. We have reviewed your submission and require some additional information to process your claim further.

# Required Information:
# {context_variables.get('Generated_status')}

# Please reply to this email with the requested information. Once received, we will promptly continue processing your claim.

# If you have any questions, please don't hesitate to contact our support team.

# Best regards,
# Customer Service Team
# """
#         else:
#             message["Subject"] = f"Claim Approval Confirmation - {context_variables.get('Subject')}"
            
#             structured_Message = f"""
# Dear {context_variables.get('customer_name', 'Valued Customer')},

# We are pleased to inform you that your claim request has been approved.

# Claim Details:
# - Reference Number: {context_variables.get('reference_number', '645218235424')}
# - Product: {context_variables.get('product_name', 'Your Product')}
# - Claim Type: {context_variables.get('claim_type', 'Warranty Claim')}

# Next Steps:
# 1. Our processing team will contact you within 2-3 business days with further instructions.
# 2. Please keep this email for your records.
# 3. If you need to check your claim status, use your reference number in all communications.

# Important Information:
# - Processing Time: 5-7 business days
# - Support Contact: support@company.com
# - Customer Service: 1-800-XXX-XXXX

# If you have any questions or concerns, please don't hesitate to reach out to our customer service team.

# Thank you for choosing our services. We appreciate your business.

# Best regards,
# Customer Service Team
# """

#         message.set_content(structured_Message)

#         # Encode the email in Base64
#         encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
#         raw_message = {"raw": encoded_message}

#         # Send the email using the Gmail API
#         send_message = service.users().messages().send(
#             userId="harshavardhanbudda@gmail.com", body=raw_message).execute()

#         print(f"Email sent successfully! Message ID: {send_message['id']}")
#         return send_message

#     except Exception as error:
#         print(f"An error occurred: {error}")
#         return None
 
 
# # %%
 
 
# # # send_email(gmail_service, context_variables)
# # def send_email_wrapper(context_variables):
# #     return send_email(gmail_service, context_variables)
 
 
# # response_agent = Agent(
# #     name="Response_Agent",
# #     instructions="You will send emails regarding the status you receive.",
# #     functions=[{
# #         "name": "send_email",
# #         "description": "Sends an email with status updates.",
# #         "parameters": {
# #             "type": "object",
# #             "properties": {
# #                 "context_variables": {
# #                     "type": "object",
# #                     "description": "The dictionary containing email details."
# #                 }
# #             },
# #             "required": ["context_variables"]
# #         }
# #     }])
 
# # response_agent = Agent(
# #     name="Response_Agent",
# #     instructions="You will send emails regarding the status you receive.",
# #     functions=[send_email_wrapper]  # Pass the function reference, not a dict
# # )
 
# # def send_response_mail(context_variables: dict):
 
# #     if context_variables['Generated_status']:
# #         notification_message = [{
# #             "role": "system",
# #             "content": "Warranty claim status received."
# #         }, {
# #             "role":
# #             "user",
# #             "content":
# #             "You will call the send_mail function and give the proper status message and context variables to it."
# #         }]
 
# #         # Run the Response Agent to send the email automatically
# #         notification_response = client.run(agent=response_agent,
# #                                            messages=notification_message,
# #                                            context_variables=context_variables)
# #         print(notification_response)
# #         return notification_response
 
 
 
# def generate_answer(context_variables: dict):
#     print("----" * 10)
#     print(context_variables)
#     print("----" * 10)

#     prompt = f"""
#     You are a claim validation expert. Your task is to analyze the customer's email content against specific validation criteria.

#     VALIDATION CRITERIA FROM KNOWLEDGE BASE:
#     {context_variables.get('product_details')}

#     CUSTOMER EMAIL:
#     {context_variables.get('Body_of_the_mail')}

#     Please perform a strict validation by:
#     1. Carefully comparing each validation requirement from the knowledge base against the information provided in the customer's email
#     2. For each validation step:
#        - Mark as PASS if the requirement is met
#        - Mark as FAIL if the requirement is not met, and specify exactly what information is missing
#     3. Make your final decision based on these outcomes:
#        - If all requirements PASS → Return "Approved"
#        - If any critical information is missing → Return exactly what information is missing, prefixed with "More Information Needed:"
#        - If the claim violates policy → Return "Rejected" with the specific reason

#     IMPORTANT: 
#     - Analyze only the current email content - do not make assumptions
#     - Do not request information that was already provided
#     - Provide only ONE of these responses: "Approved", "More Information Needed: [specific details]", or "Rejected: [specific reason]"
#     """

#     agent = Agent(
#         name="Validator_Agent",
#         model="gpt-4o-mini",
#         instructions="You are a strict claim validator. Compare email content against validation criteria and return only the claim status."
#     )

#     messages = [{"role": "user", "content": prompt}]
    
#     # Execute validation only once
#     response = client.run(agent=agent, messages=messages, context_variables= context_variables)
#     status_message = response.messages[0]['content']
    
#     print(status_message)
#     context_variables.update({'Generated_status': status_message})
    
#     if status_message:
#         res= send_email(gmail_service, context_variables)
#         return res
#     return None
    

from swarm import Swarm, Agent
from openai import OpenAI
import os
from services import gmail_authenticate
from email.message import EmailMessage
import base64
import json
# # Ensure API Key is set in the environment
os.environ[
    "OPENAI_API_KEY"] = "sk-svcacct-f-w8Kl1PbYP-xfJ0mJA5tJ9iMGLfZNBlJWfPNrpzLak9H-MO2orHBdyIa7a5tWT3BlbkFJGUdItJUijerYpfDpR29p_RjNJpfTflOgFdugRlWXm21PB3Rfn5kqZ4FkmmzD8A"
 
open_ai= OpenAI(api_key=os.environ["OPENAI_API_KEY"])
# # Initialize the Swarm client
client = Swarm()
 
# swarm_openai=Swarm(open_ai)

 
gmail_service = gmail_authenticate()
 
 
# %%
def send_email(service, context_variables: dict):
    """
    Sends an email via the Gmail API.
    """
 
    prompt = f"""
    You are an automated service agent responsible for sending emails regarding customer requests.
 
    For the context alignment iam giving you the following context variables:The subject of the customer email is {context_variables.get("Subject")}. The email body is {context_variables.get("Body_of_the_mail")}.
 
    Based on the status message below,and given context given by the customer with subject and body of the mail. Generate a suitable subject line and email body:
    In that Generated subject and email Body, add some relavant context regarding their request and I want concise and very detailed response to be Generated to send the response mail.
    **Status Message:** {context_variables.get('Generated_status')}
    
    Note : If status message is "Approved" then add this "Additional offers" in the middle of the context: {context_variables.get("additional_offers")} and Highlight that.
 
 
    Provide the output in JSON format without any markdown:
    {{
        "subject": "Generated email subject",
        "body": "Generated email body"
    }}
    """
 
    # Call OpenAI Swarm
    response = open_ai.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are an expert email assistant."},
                  {"role": "user", "content": prompt}],
    )
 
    # result_from_llm=response.json()
 
    # print("The Result from LLM ----------------",type(response))
    result_from_llm = response.choices[0].message.content
    print("The Result from LLM 2222222----------------",result_from_llm)
    try:
        # Create an email message
 
        output_response=json.loads(result_from_llm)
        message = EmailMessage()
    
        message["To"] = "harsha10102001@gmail.com"
        message["From"] = "harshavardhanbudda@gmail.com"  # Replace with your email
        # if context_variables.get('Generated_status') != "Approved":
        message["Subject"] = output_response["subject"]
    
        
        message.set_content(output_response["body"])
    
            # Encode the email in Base64
        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()).decode()
    
        # Create the API request body
        raw_message = {"raw": encoded_message}
    
        # Send the email using the Gmail API
        send_message = service.users().messages().send(
            userId="me", body=raw_message).execute()
    
        print(f"Email sent successfully! Message ID: {send_message['id']}")

        context_variables["message_id"]=send_message['id']
        context_variables["To"]="harsha10102001@gmail.com"
        context_variables["res_subject"]=output_response["subject"]
        context_variables["body"]=output_response["body"]

        return context_variables
    
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Error sending email: {str(e)}"
        }
    

    

 
def generate_answer(context_variables: dict):
 
    print("----" * 10)
    print(context_variables)
    print("----" * 10)

    if context_variables.get("date_of_purchase") != "No Date Found":

        if context_variables.get("additional_offers") != "Not Eligible":
            prod_det=context_variables.get("product_details",[])
            # print("producrjfd      detaisl==============================",prod_det)
            add_offer=context_variables.get("additional_offers")

            prod_det.append(add_offer)
            context_variables["product_details"]=prod_det
            # print("ressssssssssssssssssssssssssssssssssssssssss===============",res)
 
    prompt = f"""
    Role:
You are a service agent responsible for processing customer requests related to warranty claims, returns, exchanges, and refunds. Your task is to validate email content against the provided knowledge base and determine the appropriate status.
 
Instructions:
Compare the Email Body with the Provided Product Details:
 
The email body may contain some or all of the product details (e.g., serial number, purchase date, model number, issue description).
Validate the details with product details which are available, but do not reject a request just because some details are missing.

Date Validation rule:
Don't ask for purchase date or don't validate dates.

Validation Criteria:
 
Validate the details against email body with product details from knowledge base.
Check if the issue mentioned is covered under warranty/return/exchange/refund policies.
If any required information is missing for validation, state the missing details clearly and request additional information.
If the request meets all eligibility criteria, approve it.
If it fails even one key validation, reject it.

Return One of the Following Statuses:
 
"Approved" → If all required validations are met.
"More Information Needed" → If some details are missing that prevent validation. Clearly state what is missing.
"Rejected" → If the request does not qualify based on the policies. State the reason.
Additional Information (if applicable):

Note : If the email body is sounding like it is enquiring about the policies then return product_details in a more contextual manner to make the customer understand.

Generate the precise Context for the response to customer.

Input Data:
Product Details (from knowledge base): {context_variables.get('product_details')}
Email Body (from the customer): {context_variables.get('Body_of_the_mail')}


    """


    agent = Agent(
        name="Validator_Agent",
        instructions=
        "You validate warranty claims based on provided information. Only return the claim status."
    )
 
    messages = [{"role": "user", "content": prompt}]
 
    response = client.run(agent=agent, messages=messages,context_variables=context_variables)

    print("response from validator agent ===================================",response)
 
    status_message = response.messages[0]['content']
 
    print(status_message)  # Print only the status message
    context_variables.update({'Generated_status': status_message})
 
    if status_message:
        res = send_email(gmail_service,context_variables)
        return res
# %%
