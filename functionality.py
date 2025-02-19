import datetime
import json
import openai
from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
openai_client = OpenAI(api_key=os.environ["OPEN_API_KEY"])

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

with open('electron_list.json', 'r') as file:
    schemas = json.load(file)

def parse_warranty_period(warranty_str):
    """Convert warranty period (e.g., '2 years') to days."""
    if "year" in warranty_str:
        return int(warranty_str.split()[0]) * 365  # Convert years to days
    return 0  # Default fallback

def extract_product_name(query):
    """Extracts product name from the user's query."""
    for product in EXTENSION_RULES.keys():
        if product.lower() in query.lower():
            return product
    return None


def retrieve_for_model(query:str):
    try:
        # Open and load the JSON database
        with open("electron_list.json", "r") as file:
            data = json.load(file)  # data is a list, not a dictionary
        
        # Search for a product matching the query
        for product in data:  # Iterate directly over the list
            if product.get("Model Number", "").lower() in query.lower():

                
                return [{"metadata": product}]  # Wrap in a list to match expected format

        return None  # No product found

    except Exception as e:
        # print(f"Error in retrieve function: {e}")  # Debugging log
        return None

def retrieve(query: str):
    """Retrieve product details from the JSON database."""
    # print(f"Searching for: {query}")  # Debugging log

    try:
        # Open and load the JSON database
        with open("electron_list.json", "r") as file:
            data = json.load(file)  # data is a list, not a dictionary
        
        # Search for a product matching the query
        for product in data:  # Iterate directly over the list
            if product.get("Serial Number", "").lower() in query.lower():

                
                return [{"metadata": product}]  # Wrap in a list to match expected format

        return None  # No product found

    except Exception as e:
        # print(f"Error in retrieve function: {e}")  # Debugging log
        return None

def extract_model_number(user_query):
    prompttt=f"""
                You are a helpful assistant, where you will try to extract and return the model number of a product in a user query.
                here is your user query {user_query}.
                after extraction just return the Model number or "No Model Number" other than that i don't want any thing"""
    reponse=openai_client.chat.completions.create(model="gpt-4o-mini",messages=[{"role":"user","content":prompttt}])
    resp=reponse.choices[0].message.content
    # print("rep from user query Modellll====================)

    return resp


def extract_serial_number(user_query):

    prompttt=f"""
                You are a helpful assistant, where you will try to extract and return the serial number of a product in a user query.
                here is your user query {user_query}.
                after extraction just return the serial number or "No Serial Number" other than that i don't want any thing"""
    reponse=openai_client.chat.completions.create(model="gpt-4o-mini",messages=[{"role":"user","content":prompttt}])
    resp=reponse.choices[0].message.content
    # print("rep from user query serialllllll==========================",resp)

    return resp


def check_warranty_extension_eligibility(user_query,context_variables:dict):


    """
    Determines if the product is eligible for a warranty extension.
    """


    # print("context avra from check_warranty funct=======================:",context_variables)
    # print(user_query)
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
    # print(product_name)
    # if not product_name:
    #     return {"eligible": False, "reason": "Product not found in query."}

    # product_data = retrieve(serial_num)
    # print(product_data)
    metadata = product_data[0]['metadata']

    warranty_cover_details=metadata.get("warranty_coverage_covered")
    warranty_notcover_details=metadata.get("warranty_coverage_not_covered")
    warranty_period=metadata.get("Warranty Period")
    # combined_warranty_details = {**warranty_cover_details, **warranty_period}
    combined_warranty_details = {
    "warranty_coverage": warranty_cover_details,
    "warranty_not_covered":warranty_notcover_details,
    "warranty_period": warranty_period
}

    # warranty_cover_details
    user_content = json.dumps(combined_warranty_details, indent=2)

    messages = [
    {"role": "system", "content": "You are a helpful Assistant where you have given an dictionary, you have to convert it to meaningful and context related sentences without loosing Information"},
    {"role": "user", "content": user_content}
]
    response=openai_client.chat.completions.create(model="gpt-4o-mini",
                                          messages=messages,)
    process=response.choices[0].message.content
    context_variables["to_know_the_process"]=process
    # print("response from llm to create context============",process)


    # print("Meta data of the product===================",metadata)


    product_details = f"""
    1. Provide the serial number which is {metadata['Serial Number']} or model number {metadata['Model Number']} for verification.
    2. Check the warranty period of the {metadata['Product Name']}; it must be within the {metadata['Warranty Period']} period.
    3. Covered issues: {(metadata['warranty_coverage_covered'])}.
    4. Not covered: {(metadata['warranty_coverage_not_covered'])}.
    5. If all conditions are met, the product is eligible for repair/replacement.
    """
    # print(product_details)

    context_variables["product_details"]=product_details
    
    
    
    # if not product_data or "date_of_purchase" not in product_data[0]["metadata"]:
    #     return {"eligible": False, "reason": f"Could not fetch details for {product_name}."}
    if metadata["Purchase Date"] != "No Date Found":
        try:
            purchase_date = datetime.datetime.strptime(metadata["Purchase Date"], "%Y-%m-%d").date()
            warranty_days = parse_warranty_period(metadata.get("Warranty Period", "0 years"))
        except ValueError:
            return {"eligible": False, "reason": "Invalid warranty data format."}

        warranty_end_date = purchase_date + datetime.timedelta(days=warranty_days)
        today = datetime.date.today()
        remaining_days = (warranty_end_date-today).days


        # print("remainingggggggggggggggggggggggggg daysssssssssssssssss=======================",remaining_days)
        # check heree whether days are positive or not
        # print(warranty_end_date)

        reason = f"{metadata["Product Name"]} was purchased on {purchase_date.strftime('%Y-%m-%d')} and has {remaining_days} days of warranty remaining."

        context_variables["warranty_day_remaining"]=reason
        if remaining_days>0:

            context_variables["product_details"] =product_details +"6. "+(reason)
            
            extension_info = EXTENSION_RULES.get(metadata["Product Name"])
            # print("Extension info ==============",extension_info)   
            if remaining_days<=90:
                extension_details=f"""
                    {reason},so would you like to extend the warranty period, it is just {extension_info["cost"]}, which extends your warranty period for upto {(extension_info["duration"])}"""
                # return {
                #     "eligible": True,
                #     "reason": reason,
                #     "extension_cost": extension_info["cost"],
                #     "extension_duration": extension_info["duration"]
                # }

                context_variables["additional_offers"]=extension_details

                print("Extension if eligible============================",context_variables.get("additional_offers"))
                return context_variables
            
        if remaining_days<=0:        
            
            reason_for_reject= f"Warranty claim for this {metadata["Product Name"]} is allowed till {warranty_end_date.strftime('%Y-%m-%d')} which is expired already, so we can't claim your warranty."
            context_variables["product_details"]=reason_for_reject
            context_variables["additional_offers"]="Not Eligible"
            print("Extension not eligible=================================",context_variables.get("additional_offers"))
            return context_variables
    return context_variables

# # Mock product data for testing
# mock_product_data = {
#     "metadata": {
#         "date_of_purchase": "2023-08-01",  # Change this to test different cases
#         "warranty_period": "1 year"
#     }
# }

# # Mock retrieval function to return the test data
# def retrieve(query: str):
#     return [mock_product_data]  # Simulates a successful retrieval

# # Test the function with a user query
# user_query = "I bought a Smartphone. Can I extend my warranty?"
# result = check_warranty_extension_eligibility(user_query)

# # Print the result
# print(result)
