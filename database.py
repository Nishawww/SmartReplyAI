import openai
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import json
import os
from dotenv import load_dotenv
from swarm import Swarm, Agent
load_dotenv()
# Initialize OpenAI API


pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])   

# Create or connect to pc index
index_name = "email-rag"
if index_name not in pc.list_indexes().names():
    pc.create_index(
            name=index_name, 
            dimension=1536, 
            metric='cosine',
            spec=ServerlessSpec(
                cloud='aws',
                region='us-east-1'
            )
    )
index = pc.Index(index_name)

with open('database.json', 'r') as file:
    schemas = json.load(file)

openai_client = OpenAI(api_key=os.environ["OPEN_API_KEY"])
# Initialize the Swarm
swarm = Swarm(client=openai_client)

# # Define the retrieve function
# def retrieve(query: str):
#     # Embed the query using OpenAI embeddings
#     response = openai_client.embeddings.create(
#         input=query, 
#         model="text-embedding-ada-002"
#     )
#     embedding = response.data[0].embedding
#     # Retrieve relevant schemas from Pinecone
#     results = index.query(
#         vector=embedding, 
#         top_k=1, 
#         include_metadata=True
#     )
#     print("The retrieved results from retrieve function============",results)
#     return results["matches"]


# # Define the generate function
# def generate(data: dict):
#     schemas = data.get("schemas", [])
#     query = data.get("query", "")
    
#     # Combine schemas into a single context
#     context = "\n\n".join([
#         f"Item: {item['metadata']['item_name']}\n{item['metadata']['content']}" 
#         for item in schemas
#     ])
    
#     prompt = f"""Role: You are an AI assistant specialized in processing e-commerce policies and procedural guidelines. Your task is to structure unformatted JSON data into clear, step-by-step procedural instructions for return, refund, exchange, and warranty claims. Ensure the instructions are precise, follow a logical sequence, and maintain their original meaning without adding extra information.

# context:
# {context}

# query:
# {query}

# Format the final response as a sequence of well-formed procedural steps."""
    
#     # Generate response using chat completions
#     response = openai_client.completions.create(
#         model="gpt-4o-mini",
#         messages=[{"role": "user", "content": prompt}],
#         max_tokens=500
#     )
#     return response.choices[0].message.content

def retrieve(query: str):
    """Retrieve product details from the JSON database."""
    print(f"Searching for: {query}")  # Debugging log

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
        print(f"Error in retrieve function: {e}")  # Debugging log
        return None

def coordinate(query: str):
    # Retrieve refund-related information
    refund_info = retrieve(query)
    
    print("Using coordinate function ==============",refund_info)
    return refund_info
    
#    ` # Step 1: Retrieve relevant schemas using the retriever agent
#     context = swarm.run(agent=retriever_agent, messages=[
#         {"role": "system", "content": "You retrieve relevant data from the Pinecone database."},
#         {"role": "user", "content": query}
#     ])  
    
#     # Step 2: Generate a response using the generator agent
#     response = swarm.run(
#         generator_agent, 
#         messages=[
#             {"role": "system", "content": "You generate appropriate responses."},
#             {"role": "user", "content": query},
#             {"role": "assistant", "content": context},
#             {"role": "assistant", "content": str(refund_info)}
#         ]
#     )
    
#     return response

# Create agents using OpenAI's Agent class
retriever_agent = Agent(
    name="retriever",
    functions=[retrieve]
)

# generator_agent = Agent(
#     name="generator",
#     functions=[generate]
# )

coordinator_agent = Agent(
    name="coordinator",
    functions=[coordinate]
)
