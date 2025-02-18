import openai
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
import json
import os
from dotenv import load_dotenv
from swarm import Swarm, Agent

# Initialize OpenAI and Pinecone
openai.api_key = "sk-proj-NfwNBItyMTe0vMeRY9LqT3BlbkFJpTRyfMxAiJ3wN4TRBLtE"
api_key = "pcsk_6unayn_7NDiyFLZmevgcuGCz1cp5xm39AHDrm7zoWNREmtVJHPr4Nb9CBzczeXQBpqjohG"
pc = Pinecone(api_key=api_key)   

# Connect to existing index
index_name = "email-rag"
index = pc.Index(index_name)

# Initialize OpenAI client and Swarm
openai_client = OpenAI(api_key=openai.api_key)
swarm = Swarm(client=openai_client)

def retrieve_for_policies(query: str):
    """Retrieve relevant documents from Pinecone."""
    # Create embedding for the query
    response = openai_client.embeddings.create(
        input=query,
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding
    
    # Search Pinecone
    results = index.query(
        vector=embedding,
        top_k=1,
        include_metadata=True
    )
    return results['matches']

def generate(query: str,context_variables:dict):
    """Generate response using RAG technique."""
    # Step 1: Retrieve relevant information
    retrieved_docs = retrieve_for_policies(query)
    
    # Step 2: Format the context from retrieved documents
    contexts = []
    for doc in retrieved_docs:
        metadata = doc['metadata']
        context = f"""
Product: {metadata['Product Name']}
Model: {metadata['Model Number']}
Purchase Date: {metadata['Purchase Date']}

Return Policy (Period: {metadata['Return Period']}):
Return policy Eligiblites": {(metadata["return_policy_eligible"])}
Return Policies Not eligible: {(metadata["return_policy_not_eligible"])}

Refund Policy (Period: {metadata['Refund Period']})

Refund policy Eligiblites": {(metadata["refund_policy_eligible"])}
Refund Policies Not eligible: {(metadata["refund_policy_not_eligible"])}


Exchange Policy (Period: {metadata['Exchange Period']}):
Exchange policy Eligiblites": {(metadata["exchange_policy_eligible"])}
Exchange Policies Not eligible: {(metadata["exchange_policy_not_eligible"])}


Warranty Period: {metadata['Warranty Period']})
Warranty covers": {(metadata["warranty_coverage_covered"])}
Warranty not covers: {(metadata["warranty_coverage_not_covered"])}


"""
        contexts.append(context)
    
    combined_context = "\n\n---\n\n".join(contexts)
    print("combined_context------------",combined_context)
    # Step 3: Create prompt and generate response
    prompt = f"""Based on the following product policies and information, please answer the user's query.
Provide a clear, step-by-step response when applicable.
Give the response based on the user's query, like if he is asking about only return,refund categories then give the info about that categories only.
Don't mention about remaining categories.

PRODUCT INFORMATION:
{combined_context}

USER QUERY: {query}

Please provide a specific, accurate response based only on the information provided above."""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides accurate information about product policies and procedures."},
            {"role": "user", "content": prompt}
        ],
    )
    
    res_from_generate=response.choices[0].message.content


    print("Responseeeeeeeeeeeeeeeee from Generateeeeeeeeeeeeeeee==================",res_from_generate)
    context_variables["product_details"]=res_from_generate
    

    return context_variables

def coordinate(query: str,context_variables:dict):
    """Coordinate the RAG process using agents."""
    # Create agents
    # retriever_agent = Agent(
    #     name="retriever",
    #     functions=[retrieve_for_policies]
    # )
    
    generator = Agent(
        name="generator",
        functions=[generate]
    )
    
    # Use the generator agent to get the final response
    response = swarm.run(
        generator,
        messages=[
            {"role": "system", "content": "You generate appropriate responses based on retrieved information."},
            {"role": "user", "content": query}
        ],context_variables=context_variables
    )
    
    
    
    product_det_from_cordinate=response.context_variables["product_details"]

    print("response from cordinate==================================",product_det_from_cordinate)


    context_variables["product_details"]=product_det_from_cordinate

    return context_variables

coordinator_agent = Agent(
    name="coordinator",
    functions=[coordinate]
)
# Example usage
# if __name__ == "__main__":
#     query = "What is the return policy for the smart tv?"
#     response = coordinate(query)
#     print(f"Query: {query}")
#     print(f"Response: {response}")
