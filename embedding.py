import openai
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import json
import os
from dotenv import load_dotenv
from swarm import Swarm, Agent
load_dotenv()
# Initialize OpenAI API
openai.api_key =os.environ["OPEN_API_KEY"]

pc = Pinecone(api_key= os.environ["PINECONE_API_KEY"])   

# Create or connect to pc index
index_name = "email-rag"
if index_name not in pc.list_indexes().names():
    pc.create_index(
            name='index_name', 
            dimension=1536, 
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
    )
index = pc.Index(index_name)
# Load schemas
 
with open('electron_list.json', 'r') as file:
    schemas = json.load(file)

# Helper function to create a single text block for embedding
def create_text_block(schema):
    text = f"Product Name: {schema['Product Name']}\n"
    text += f"Model Number: {schema['Model Number']}\n"
    text += f"Serial Number: {schema['Serial Number']}\n"
    text += f"Date of Purchase: {schema['Purchase Date']}\n"
    
    # Return Policy
    text += f"Return Policy (Eligibility Period: {schema['Return Period']}):\n"
    text += "Eligible for Return:\n" + "\n".join(schema['return_policy_eligible']) + "\n"
    text += "Not Eligible for Return:\n" + "\n".join(schema["return_policy_not_eligible"]) + "\n"
    
    # Refund Policy
    text += f"Refund Policy (Eligibility Period: {schema['Refund Period']}):\n"
    text += "Eligible for Refund:\n" + "\n".join(schema['refund_policy_eligible']) + "\n"
    text += "Not Eligible for Refund:\n" + "\n".join(schema['refund_policy_not_eligible']) + "\n"
    
    # Warranty Coverage
    text += f"Warranty Coverage (Period: {schema['Warranty Period']}):\n"
    text += "Covered under Warranty:\n" + "\n".join(schema['warranty_coverage_covered']) + "\n"
    text += "Not Covered under Warranty:\n" + "\n".join(schema['warranty_coverage_not_covered']) + "\n"
    
    # Exchange Policy
    text += f"Exchange Policy (Eligibility Period: {schema['Exchange Period']}):\n"
    text += "Eligible for Exchange:\n" + "\n".join(schema['exchange_policy_eligible']) + "\n"
    text += "Not Eligible for Exchange:\n" + "\n".join(schema['exchange_policy_not_eligible']) + "\n"
    
    return text

# Generate embeddings and store in pc
for schema in schemas:
    # Combine schema sections into a single text block
    text_block = create_text_block(schema)
    
    # Generate embedding using OpenAI API
    response = openai.embeddings.create(
        input=text_block,
        model="text-embedding-ada-002"  # Use OpenAI's embedding model
    )
    #print(response)
    embedding = response.data[0].embedding
    
    
    index.upsert([
        {
            "id": schema["Product Name"],  # Use the product name as the unique identifier
            "values": embedding,
            "metadata": {
                "Product Name": schema["Product Name"],
                "Model Number": schema["Model Number"],
                "Serial Number": schema["Serial Number"],
                "Purchase Date": schema["Purchase Date"],
                "Return Period": schema["Return Period"],
                "return_policy_eligible": (schema["return_policy_eligible"]),
                "return_policy_not_eligible": (schema["return_policy_not_eligible"]),  # Store the return policy as JSON
                "Refund Period": schema["Refund Period"],
                "refund_policy_eligible": (schema["refund_policy_eligible"]),  # Store the refund policy as JSON
                "refund_policy_not_eligible": (schema["refund_policy_not_eligible"]),  # Store the refund policy as JSON

                "Warranty Period": schema["Warranty Period"],
                "warranty_coverage_covered": (schema["warranty_coverage_covered"]),  # Store the warranty coverage as JSON
                "warranty_coverage_not_covered": (schema["warranty_coverage_not_covered"]),  # Store the warranty coverage as JSON

                "Exchange Period": schema["Exchange Period"],
                "exchange_policy_eligible": (schema["exchange_policy_eligible"]),  # Store the exchange policy as JSON
                "exchange_policy_not_eligible": (schema["exchange_policy_not_eligible"]),  # Store the exchange policy as JSON

            }
        }
    ])

print(response)
print("Embeddings successfully stored in pinecone!")
