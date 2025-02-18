from swarm import Swarm, Agent
from openai import OpenAI
from dotenv import load_dotenv
import os
import json
# from database import retrieve, coordinate, coordinator_agent
from database_for_coordinate import retrieve_for_policies,generate,coordinate,coordinator_agent
import email
import json
from email import policy
from email.parser import BytesParser, Parser
from functionality import check_warranty_extension_eligibility
from check_eligibility import check_exchange_eligibility, check_refund_eligibility, check_return_eligibility
from send_mail import generate_answer
from dotenv import load_dotenv

load_dotenv()
import os
openai_client= OpenAI(api_key= os.environ["OPEN_API_KEY"])
client = Swarm(openai_client)
EXTENSION_RULES = {
    "Smartphone": {"cost": "$49", "duration": "1 year"},
    "Laptop": {"cost": "$99", "duration": "2 year"},
    "Smartwatch": {"cost": "$39", "duration": "1 year"},
    "Wireless Earbuds": {"cost": "$29", "duration": "1 year"},
    "Smart TV": {"cost": "$79", "duration": "2 year"},
    "Gaming Console": {"cost": "$59", "duration": "1 year"},
    "Bluetooth Speaker": {"cost": "$25", "duration": "1 year"},
    "Digital Camera": {"cost": "$89", "duration": "2 year"},
    "Microwave Oven": {"cost": "$35", "duration": "2 year"},
    "Vacuum Cleaner": {"cost": "$45", "duration": "1 year"},
    "Router":{"cost": "$39", "duration": "1 year"},
    "Monitor":{"cost":"$45", "duration":"1 year"},
    "External Hard Drive": {"cost": "$55", "duration": "2 year"},
    "Projector": {"cost": "$95", "duration": "2 year"},
    "VR Headset": {"cost": "$69", "duration": "1 year"},
    "Camera":{"cost":"$20", "duration":"1 year"}
   
}


def extract_email_content(raw_mail):
    # Check if input is string or bytes
    context_variables={}
    # if isinstance(raw_mail, str):
    #     msg = Parser(policy=policy.default).parsestr(raw_mail)  # Use parsestr for string input
    # else:
    #     msg = BytesParser(policy=policy.default).parsebytes(raw_mail)  # Use parsebytes for bytes input

    # subject = msg["Subject"] if msg["Subject"] else "No Subject"
    # body = ""

    # if msg.is_multipart():
    #     for part in msg.walk():
    #         content_type = part.get_content_type()
    #         content_disposition = str(part.get("Content-Disposition"))

    #         if content_type == "text/plain" and "attachment" not in content_disposition:
    #             charset = part.get_content_charset() or "utf-8"  # Ensure a default charset
    #             body = part.get_payload(decode=True).decode(charset, errors="replace")
    #             break  # Extracts only the first text/plain part
    # else:
    #     charset = msg.get_content_charset() or "utf-8"  # Ensure a default charset
    #     body_bytes = msg.get_payload(decode=True)  # Decode payload
    #     body = body_bytes.decode(charset, errors="replace") if body_bytes else "No Content"

    # context_variables["subject"]=subject
    context_variables["Body_of_the_mail"]=raw_mail

    return context_variables

def intent_analys(context_variables: dict):
    body_of_the_mail = context_variables.get('Body_of_the_mail')
    # sub_mail = context_variables.get('Subject')
    # analysis_prompt = f"""
    #             You are a Content Analysis Expert and Query Creator, Where you will Analyze the Content and Tells it comes under the E-commerce Domain.
    #             So based on the Email Subject and Body provided, you need to analyze the whole content and say Whether it comes under the E-commerce Domain or not.
    #             If it Comes under the E-commerce Domain then you have to Categorize it under these categories ["Warranty","Exchange","Return","Refund"].
    #             other than this i don't want you to categorize or describe about them.
    #             And also you just have to turn the whole content as the Query or kind of a Summarized Format, where don't Exclude any important details and mention it in the query. Include all the details such as serial numbers, model numbers, warranty period, warranty coverage, exchange eligibility period, exchange policy, refund eligibility period etc., and whatever details mentioned in it.
    #             Example: The customer wants to claim a warranty on Smart TV, which is purchased on 20-10-2024 and details of TV is serial number 1234343.
    #             Like this in the above mentioned Query Format I want.

    #             IMPORTANT  : ***If the content is not aligning with the E-commerce domain then Return it as query as "Not Relatable". other than that i don't want any Thing

    #             ***

    #             Note: Make sure you are returning the Both Query and Category in a Dictionary format.

    #             So these are the Email Intents, Email subject :{sub_mail} and Email body : {body_of_the_mail}. """
    analysis_prompt = f"""
    You are a Content Analysis Expert and Query Creator. Your task is to analyze the given email subject and body to determine whether the content falls under the E-commerce domain. 

    ### **Instructions:**
    1. **Domain Identification:**  
       - If the email is related to E-commerce, proceed with categorization.  
       - If not, return **"Query": "Not Relatable"** and **"Category": "Not Relatable"**.

    2. **Categorization:**  
       - If the email is related to E-commerce, classify it under one of the following categories:  
         **["Warranty", "Exchange", "Return", "Refund"]**.  
       - If it does not fit any of these, return **"Category": "Not Relatable"**.

    3. **Query Generation:**  
       - Summarize the email content in a structured query format.  
       - Retain all key details, including:
         - **Product name**
         - **Serial number**
         - **Model number**
         - **Purchase date**
         - **Warranty period and coverage**
         - **Exchange/refund eligibility period and policy**
       - If any detail is missing in the email, exclude it from the summary.

       Example: The customer wants to claim a warranty on Smart TV, which is purchased on 20-10-2024 and details of TV is serial number 1234343 and model number TN-23342.

       Important : Just make sure you are extracting all the details regarding to the product and return the Summarized Query and this query should be in sentence format and which is used to query the vector db  and Category as a dictionary.
       4. **Expected Output Format (Dictionary):**
          ```json
          
              "Query": "<Summarized query or 'Not Relatable'>",
              "Category": "<Warranty | Exchange | Return | Refund | Not Relatable>"
          
       
        
       
       email_body:{body_of_the_mail}

    """
    # print(analysis_prompt)
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        # stream=True,
        messages=[{
            "role": "user",
            "content": analysis_prompt
        }])

    # print(response.choices[0].message.content)

    summarized_intent_json = response.choices[0].message.content

    # Convert the JSON string response to a dictionary
    # try:
    print(type(summarized_intent_json))
    if summarized_intent_json.startswith("```json"):
        final_response_dict = json.loads(summarized_intent_json[7:-3].strip())
    else:
        final_response_dict = json.loads(summarized_intent_json)
    print("-----" * 10)
    print(final_response_dict)
    print("-----" * 10)

    # except json.JSONDecodeError as e:
    #     print("Error parsing JSON:", e)
    #     final_response_dict = {
    #         # "error": "Response not in expected JSON format",
    #         "response": summarized_intent_json
    #     }

    context_variables.update(final_response_dict)


    # print("The Context Variables from Intent Analysis ----------------", context_variables)

    return context_variables

def transfer_to_warranty_agent():
    """transfer the queries related to warranty claims immediately."""
    return warranty_agent

def transfer_to_refund_agent():
    """transfer the queries related to refund policies immediately."""
    return refund_agent

def transfer_to_return_agent():
    """transfer the queries related to return policies immediately."""
    return return_agent

def transfer_to_exchange_agent():
    """transfer the queries related to exchange policies immediately."""
    return exchange_agent

def transfer_to_technical_agent():
    """transfer the queries which are unsolved."""
    return technical_agent

def transfer_back_to_control_agent():
    """Call this function if a user is asking about a topic that is not handled by the current agent."""
    return control_agent

def transfer_to_coordinator_agent():
    """Call this function if user is asking about any of the concerns including warranty, return, refund and exchange."""
    return coordinator_agent
# def refund_agent_handler(user_query):
#     """
#     Handles refund queries by classifying intent and calling the appropriate function.
#     """
    
#     intent = classify_refund_intent(user_query)

#     if intent == "refund_process":
#         return transfer_to_coordinator_agent()  # Fetch refund info

#     elif intent == "refund_claim":
#         return process_refund(user_query)  # Start refund process

#     else:
#         return "I'm sorry, I didn't understand your request. Can you clarify?"
# def refund_agent_handler(user_query):
#     intent = classify_refund_intent(user_query)
    
#     if intent == "refund_process":
#         return retrieve(user_query)  # Fetch refund info
#     elif intent == "refund_claim":
#         refund_info = retrieve(user_query)  # Get refund details
#         print(refund_info)
#         if refund_info:
#             return process_refund(refund_info)  # Start refund process
#         else:
#             return "Refund details not found. Please check eligibility."
#     else:
#         return "I'm sorry, I didn't understand your request. Can you clarify?"
def extract_product_from_messages(messages):
    """
    Extract product name from the messages list in main.py.
    Specifically looks for product mentions in user messages.
    """
    for message in messages:
        if message["role"] == "user":
            content = message["content"].lower()
            # Look for product names from EXTENSION_RULES in the message
            for product in EXTENSION_RULES.keys():
                if product.lower() in content:
                    return product
    return None

# def auto_check_warranty_from_messages(messages):
#     """
#     Automatically checks warranty extension eligibility based on product mentioned in messages.
#     Takes the messages list directly from main.py.
#     """
#     # Extract product from messages
#     product = extract_product_from_messages(messages)
#     if not product:
#         return {"eligible": False, "reason": "No supported product found in messages."}
    
#     # Create a query using the extracted product
#     query = f"I bought a {product}"
    
#     # Use existing check_warranty_extension_eligibility with constructed query
#     return check_warranty_extension_eligibility(query)

warranty_agent = Agent(
    name="warranty_agent",
    model = "gpt-4o-mini",
    instructions= """Call this function for warranty related queries.
                    1. Fetch warranty coverage related information from check_warranty_extension_eligibility.
                    2. Check warranty extension eligibility by calling check_warranty_extension_eligibility function with the user's query.

                    """,
    functions= [transfer_back_to_control_agent, transfer_to_technical_agent, check_warranty_extension_eligibility],
)
refund_agent= Agent(
    name="refund_agent",
    model= "gpt-4o-mini",
    instructions="""1.Call this function to fetch refund related informations or to claim refund from check_refund_eligibility ,
                     2. check eligblity if a query claims refund.""",
    functions= [transfer_back_to_control_agent, transfer_to_technical_agent, transfer_to_coordinator_agent, check_refund_eligibility],
)
# refund_agent = Agent(
#     name="refund_agent",
#     model="gpt-4o-mini",
#     instructions="""This agent determines whether a customer is asking about the refund process or initiating a refund claim.
#                     1. If user is asking about refund process, fetch refund details.
#                     2. If user wants to claim a refund, check refund eligibility and process it.
#                     3. If unclear, ask for more details.""",
#     functions=[
#         # classify_refund_intent,  # Add classification step first
#         # refund_agent_handler,    # Handles actual processing
#         transfer_back_to_control_agent,
#         transfer_to_technical_agent,
#         transfer_to_coordinator_agent,
#         # process_refund,
#         check_refund_eligibility,
#     ],
# )

return_agent= Agent(
    name= "return_agent",
    model= "gpt-4o-mini",
    instructions= """1.Call this function to fetch return related informations from check_return_eligibility function.,
                     2. check eligblity if a query claims return.""",
    functions= [transfer_back_to_control_agent, transfer_to_technical_agent, transfer_to_coordinator_agent, check_return_eligibility],
)
exchange_agent= Agent(
    name="exchange_agent",
    model= "gpt-4o-mini",
    instructions= """1.Call this function to fetch exchange related informations from check_exchange_eligibility function.,
                     2. check eligblity if a query claims exchange.""",
    functions= [transfer_to_technical_agent, transfer_back_to_control_agent, transfer_to_coordinator_agent, check_exchange_eligibility],
)
technical_agent= Agent(
    name="technical_agent",
    model= "o1-mini",
    instructions= "you take care of the unsolved queries.",
    functions= [transfer_back_to_control_agent],
)
control_agent= Agent(
    name="control_agent",
    model= "gpt-3.5-turbo",
    instructions= "1.you supervise the agents accordingly and Based on the query you will choose appropriate agent."
                    "2.If the Query is regarding about Multiple policies, then call transfer_to_coordinator_agent",
    functions= [transfer_to_warranty_agent,
                 transfer_to_exchange_agent,
                 transfer_to_refund_agent,
                 transfer_to_return_agent,  
                 transfer_to_technical_agent,
                 transfer_to_coordinator_agent],
)


def extract_dop_from_query(context_variables:dict):

    Query_from_body=context_variables.get("Query")
    dop_prompt=f"""
                You are a Helpful Assistant.Here You are going to get some Query, 
                you have to analyze that and check whethere that Query has any kind of information regarding date of purchase of a product.
                If it has then just return that Date or else return "No Date Found". Other than that I don't want any other things to return.
                This is your query :{Query_from_body}

"""
    response=openai_client.chat.completions.create(model="gpt-4o-mini",messages=[{"role":"user","content":dop_prompt}])
    purchase_date=response.choices[0].message.content
    context_variables.update({"date_of_purchase":purchase_date})
    return context_variables
    # return


# email_body="""
# Subject: Warranty Information Request
#     Dear Support,
#     I bought a camera which has the serial number SN100035 on 2023-08-15.
#     camera lens is broken. I want to claim the warranty regarding this issue.
#     Regards,
#     David
# """

# context_variables.update({"From":"harsha10102001@gmail.com",
#                         #   "Subject":"Request regarding Return process",
#                      "Body_of_the_mail":email_body},
#                      )

# query=intent_analys(context_variables)

# # print("Query from intent analysis : =================",query)

# date_of_buying=extract_dop_from_query(context_variables)

# messages= [{"role":"user", "content":context_variables.get("Query")}]
# response = client.run(agent= control_agent, messages=messages,context_variables=context_variables)
# # print(response)
# # response_content_to_know_process=response.context_variables["to_know_the_process"]

# response_for_product_details=response.context_variables["product_details"]
# # print("to know the processs=============================",response_content)

# # print("Aditional ofers==========================",response.context_variables["additional_offers"])
# import copy
# context_variables=copy.deepcopy(response.context_variables)


# # print("latest context variables-----------------------------------------",context_variables)
# # # ext_to_process_frm_convar=response.context_variables["to_know_the_process"]

# # ext_to_process_frm_convar=context_variables["product_details"]





# # print("The process knowing==================",ext_to_process_frm_convar)

# import re
# steps = re.findall(r"(?:\d+\.\s|\-\s)(.+)", response_for_product_details)
# # Clean up extracted steps
# procedure_steps = [step.strip() for step in steps]
# # Store in context_variables
# # context_variables["product_details"] = procedure_steps
# # print("The product details---------------",procedure_steps)

# # Print result to verify
# print("The Context Variablesssssssssssssssssssssss",context_variables)


# res=generate_answer(context_variables)


# # print("output from generate answer ========",res)
