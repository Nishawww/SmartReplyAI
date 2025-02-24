from swarm import Swarm, Agent
from openai import OpenAI
import os
from services import gmail_authenticate
from email.message import EmailMessage
import base64
import json
from dotenv import load_dotenv
# # Ensure API Key is set in the environment
load_dotenv()
open_ai= OpenAI(api_key=os.environ["OPEN_API_KEY"])
# # Initialize the Swarm client
client = Swarm(open_ai)
 
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
