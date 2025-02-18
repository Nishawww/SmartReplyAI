import json
import datetime
from database import retrieve

import openai
from openai import OpenAI

from functionality import extract_model_number,retrieve_for_model

openai.api_key = "sk-svcacct-f-w8Kl1PbYP-xfJ0mJA5tJ9iMGLfZNBlJWfPNrpzLak9H-MO2orHBdyIa7a5tWT3BlbkFJGUdItJUijerYpfDpR29p_RjNJpfTflOgFdugRlWXm21PB3Rfn5kqZ4FkmmzD8A"
openai_client = OpenAI(api_key=openai.api_key)



def extract_serial_number(user_query):

    prompttt=f"""
                You are a helpful assistant, where you will try to extract and return the serial number of a product in a user query.
                here is your user query {user_query}.
                after extraction just return the serial number or "No Serial Number" other than that i don't want any thing"""
    reponse=openai_client.chat.completions.create(model="gpt-4o-mini",messages=[{"role":"user","content":prompttt}])
    resp=reponse.choices[0].message.content
    print("rep from user query serialllllll==========================",resp)

    return resp
# def extract_product_name(product_data, identifier):
#     """
#     Extracts the product name based on the given model number or serial number.
    
#     param product_data: List of product dictionaries.
#     param identifier: Model number or serial number of the product.
#     return: Product name if found, else None.
#     """
#     for product in product_data:
#         if product.get("model_number") == identifier or product.get("serial_number") == identifier:
#             return product.get("product_name")
#     return None


def check_return_eligibility(user_query,context_variables:dict):
    """Check if a product is eligible for return based on return policy."""
    # product_name = extract_product_name(user_query)
    
    # if not product_name:
    #     return {"eligible": False, "reason": "Product not found in query."}

    serial_num=extract_serial_number(user_query=user_query)
    model_num=extract_model_number(user_query=user_query)

    if serial_num == "No Serial Number" and model_num=="No Model Number":
        context_variables["product_details"]="Provide the serial number for further Verification."
        context_variables["additional_offers"]="Not Eligible"
        return context_variables
    
    if serial_num != "No Serial Number":
        product_data = retrieve(serial_num)

    if model_num !="No Model Number":
        product_data=retrieve_for_model(model_num)
    
    print("Data from return==========================================",product_data)
    
    if not product_data:
        return {"eligible": False, "reason": "Product details not found in database."}
    
    metadata = product_data[0]['metadata']

    refund_cover_details=metadata.get("return_policy_not_eligible")
    refund_not_cover_details=metadata.get("return_policy_eligible")

    refund_period=metadata.get("Return Period")
    # combined_warranty_details = {**warranty_cover_details, **warranty_period}
    combined_warranty_details = {
    "Return_details": refund_cover_details,
    "Return_not_cover":refund_not_cover_details,
    "Return_period": refund_period
}

    # warranty_cover_details
    user_content = json.dumps(combined_warranty_details, indent=2)

    messages = [
    {"role": "system", "content": "You are a helpful where you have given an dictionary, you have to convert it to meaningful and context related sentences without loosing Information"},
    {"role": "user", "content": user_content}
]
    response=openai_client.chat.completions.create(model="gpt-4o-mini",
                                          messages=messages,)
    
    to_know_process=response.choices[0].message.content
    print("response from llm to create context============",response.choices[0].message.content)

    context_variables["to_know_the_process"]=to_know_process

    print("Meta data of the product===================",metadata)


    
    # return_policy = (metadata["return_policy"]) 
    product_details = f"""
    1. Provide the serial number which is {metadata['Serial Number']} or model number {metadata["Model Number"]} for verification.
    2. Check the return period of the {metadata['Product Name']}; it must be within the {metadata['Return Period']} period.
    3. Eligible: {metadata["return_policy_eligible"]}.
    4. Not Eligible: {(metadata["return_policy_not_eligible"])}.
    5. If all conditions are met, the product is eligible for repair/replacement.
    """

    context_variables["product_details"]=product_details
    
    if metadata["Purchase Date"] != "No Date Found":
        try:
            purchase_date = datetime.datetime.strptime(metadata["Purchase Date"], "%Y-%m-%d").date()
            return_window = int(metadata.get("Return Period").split()[0])  # Assuming return_period is like "30 days"
            print("The return peroiddddddddddddddddddd=============",return_window)
        except ValueError:
            return {"eligible": False, "reason": "Invalid return data format."}
        
        return_deadline = purchase_date + datetime.timedelta(days=return_window)
        today = datetime.date.today()

        if today <= return_deadline:
            reason= f"Return allowed until {return_deadline.strftime('%Y-%m-%d')}."
            context_variables["additional_offers"]=reason
            return context_variables
        reason= f"1. Return Eligibility period expired on {return_deadline.strftime('%Y-%m-%d')}.so you can't claim for return of your product."
        context_variables["product_details"]= reason
        context_variables["additional_offers"]="Not Eligible"
        return context_variables
    return context_variables





def check_refund_eligibility(user_query,context_variables:dict):
    """Check if a product is eligible for return based on return policy."""
    # product_name = extract_product_name(user_query)
    
    # if not product_name:
    #     return {"eligible": False, "reason": "Product not found in query."}
    serial_num=extract_serial_number(user_query=user_query)
    model_num=extract_model_number(user_query=user_query)

    if serial_num == "No Serial Number" and model_num=="No Model Number":
        context_variables["product_details"]="Provide the serial number for further Verification."
        context_variables["additional_offers"]="Not Eligible"
        return context_variables
    
    if serial_num != "No Serial Number":
        product_data = retrieve(serial_num)

    if model_num !="No Model Number":
        product_data=retrieve_for_model(model_num)
    # product_data = retrieve(user_query)
    
    if not product_data:
        return {"eligible": False, "reason": "Product details not found in database."}
    
    metadata = product_data[0]['metadata']
    refund_cover_details=metadata.get("refund_policy_eligible")
    refund_not_cover_details=metadata.get("refund_policy_not_eligible")

    refund_period=metadata.get("Refund Period")
    # combined_warranty_details = {**warranty_cover_details, **warranty_period}
    combined_warranty_details = {
    "Refund_details": refund_cover_details,
    "Refund_period": refund_period,
    "refund_not_details":refund_not_cover_details
}

    # warranty_cover_details
    user_content = json.dumps(combined_warranty_details, indent=2)

    messages = [
    {"role": "system", "content": "You are a helpful where you have given an dictionary, you have to convert it to meaningful and context related sentences without loosing Information"},
    {"role": "user", "content": user_content}
]
    response=openai_client.chat.completions.create(model="gpt-4o-mini",
                                          messages=messages,)
    
    to_know_process=response.choices[0].message.content
    print("response from llm to create context============",to_know_process)

    context_variables["to_know_the_process"]=to_know_process


    # refund_policy = json.loads(metadata["refund_policy"]) 
    product_details = f"""
    1. Provide the serial number which is {metadata['Serial Number']} or  model number {metadata["Model Number"]} for verification.
    2. Check the refund period of the {metadata['Product Name']}; it must be within the {metadata['Refund Period']} period.
    3. Eligible: {(metadata['refund_policy_eligible'])}.
    4. Not Eligible: {(metadata['refund_policy_not_eligible'])}.
    5. If all conditions are met, the product is eligible for repair/replacement.
    """
    context_variables["product_details"]=product_details

    if metadata["Purchase Date"] != "No Date Found":
        
        try:
            purchase_date = datetime.datetime.strptime(metadata["Purchase Date"], "%Y-%m-%d").date()
            return_window = int(metadata.get("Refund Period").split()[0])
            print("The Refund Eligibility period=========================",return_window)  # Assuming return_period is like "30 days"
        except ValueError:
            return {"eligible": False, "reason": "Invalid return data format."}
        
        refund_deadline = purchase_date + datetime.timedelta(days=return_window)
        today = datetime.date.today()

        if today <= refund_deadline:
            reason=f"Return allowed until {refund_deadline.strftime('%Y-%m-%d')} days, and also if you add you allow us to credit amount in the wallet, then you will have 100 wallet points for every thousand rupees, so that you can use it in your Next Purchases or orders." 
            context_variables["additional_offers"]=reason
            return context_variables
        
        reason= f"1. Refund Eligibility period expired on {refund_deadline.strftime('%Y-%m-%d')}.so you can't claim for refund."
        context_variables["product_details"]= reason
        context_variables["additional_offers"]="Not Eligible"
        return context_variables

    return context_variables


def check_exchange_eligibility(user_query,context_variables:dict):
    """Check if a product is eligible for an exchange."""
    # product_name = extract_product_name(user_query)
    
    # if not product_name:
    #     return {"eligible": False, "reason": "Product not found in query."}
    serial_num=extract_serial_number(user_query=user_query)
    model_num=extract_model_number(user_query=user_query)

    if serial_num == "No Serial Number" and model_num=="No Model Number":
        context_variables["product_details"]="Provide the serial number for further Verification."
        context_variables["additional_offers"]="Not Eligible"
        return context_variables
    
    if serial_num != "No Serial Number":
        product_data = retrieve(serial_num)

    if model_num !="No Model Number":
        product_data=retrieve_for_model(model_num)
    
    print("product data from check exchange eligibility==================",product_data)
    
    if not product_data:
        return {"eligible": False, "reason": "Product details not found in database."}
    
    metadata = product_data[0]['metadata']

    exchne_cvr=metadata.get("exchange_policy_eligible")
    exchne_not_cvr=metadata.get("exchange_policy_not_eligible")

    refund_period=metadata.get("Exchange Period")
    # combined_warranty_details = {**warranty_cover_details, **warranty_period}
    combined_warranty_details = {
    "Exchange_details": exchne_cvr,
    "exchange_not_cover_details":exchne_not_cvr,
    "Exchange_period": refund_period
}

    # warranty_cover_details
    user_content = json.dumps(combined_warranty_details, indent=2)

    messages = [
    {"role": "system", "content": "You are a helpful where you have given an dictionary, you have to convert it to meaningful and context related sentences without loosing Information"},
    {"role": "user", "content": user_content}
]
    response=openai_client.chat.completions.create(model="gpt-4o-mini",
                                          messages=messages,)
    
    to_know_process=response.choices[0].message.content
    print("response from llm to create context============",to_know_process)

    context_variables["to_know_the_process"]=to_know_process

    
    # exchange_policy = json.loads(metadata["exchange_policy"]) 
    product_details = f"""
    1. Provide the serial number which is {metadata['Serial Number']} or  model number {metadata["Model Number"]} for verification.
    2. Check the exchange period of the {metadata['Product Name']}; it must be within the {metadata['Exchange Period']} period.
    3. Eligible: {(metadata["exchange_policy_eligible"])}.
    4. Not Eligible: {(metadata["exchange_policy_not_eligible"])}.
    5. If all conditions are met, the product is eligible for repair/replacement.
    """
    context_variables["product_details"]=product_details


    if metadata["Purchase Date"] != "No Date Found":
        try:
            purchase_date = datetime.datetime.strptime(metadata["Purchase Date"], "%Y-%m-%d").date()
            exchange_window = int(metadata.get("Exchange Period").split()[0])  # Assuming exchange_period is like "30 days"
            print("Exchangeeeeeeeeeeeeeeeeeeeeee window==================",exchange_window)
        except ValueError:
            return {"eligible": False, "reason": "Invalid exchange data format."}
        
        exchange_deadline = purchase_date + datetime.timedelta(days=exchange_window)

        
        today = datetime.date.today()
        print("exchangeeeee deadlineeeeeeeeeeeeeeeeeeeeeeeeee================", exchange_deadline,"=================",today)
        
        if today <= exchange_deadline:
            reason= f"Exchange  allowed until {exchange_deadline.strftime('%Y-%m-%d')} days.So do you want to go for any exchange process."
            context_variables["additional_offers"]=reason
            return context_variables
        reason=f"1. Exchange  allowed until {exchange_deadline.strftime('%Y-%m-%d')} days. so now Exchange claim is not able to approve. sorry for your convenience"
        context_variables["product_details"]= reason
        context_variables["additional_offers"]="Not Eligible"
        return context_variables
    return context_variables
