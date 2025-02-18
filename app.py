import streamlit as st
from main import client, control_agent,intent_analys,extract_email_content,extract_dop_from_query
from send_mail import generate_answer, send_email, gmail_service
import re
from openai import OpenAI
import os
import json
from dotenv import load_dotenv

load_dotenv()
 
open_ai= OpenAI(api_key=os.environ["OPEN_API_KEY"])
 
 
 
def generate_response(email_text):
    """Run the agent and fetch its response."""

    context_variables={}
    try:
        # Step 1: Extract subject and body from email_text
        context_variables = extract_email_content(email_text)
        
        # Step 2: Update context_variables with initial data
        # context_variables.update({
        #     "Subject": email_content['subject'],
        #     "Body_of_the_mail": email_content['body']
        # })
        print(context_variables)
        # Step 3: Use intent_analys to analyze and get query
        query_from_analysis = intent_analys(context_variables)
        print("intent_result",query_from_analysis)
        ate_of_buying=extract_dop_from_query(context_variables)
        
        # Step 4: Generate response using control agent
        messages = [{"role": "user", "content": query_from_analysis["Query"]}]
        response = client.run(agent=control_agent, messages=messages,context_variables=ate_of_buying)
        
        print("The rspomse from the agent=======================",response)
        
        # Get the response content
        response_content = response.context_variables["product_details"]
        
        # Extract steps from response
        steps = re.findall(r"(?:\d+\.\s|\-\s)(.+)", response_content)
        procedure_steps = [step.strip() for step in steps]
        print("procedure stepssssssss==============================================",procedure_steps)
        import copy
        response.context_variables["product_details"]=procedure_steps
        response.context_variables["status"]="Success"
        response.context_variables["validation_steps"]=response_content
        if not procedure_steps:
            response.context_variables["product_details"]=response_content


        context_variables=copy.deepcopy(response.context_variables)

        print("the cdsbdjsd fjshdfjhsfjdsbfmsbfd ===============================",context_variables)

        return context_variables
    
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Error generating response: {str(e)}"
        }
       
 
 
def send_response(context_variables):
    """Send email using the send_email function."""
    try:
        result = send_email(gmail_service, context_variables)
        if result:
            return {
                'status': 'success',
                'message_id': result.get('message_id', 'N/A')
            }
        return {
            'status': 'error',
            'message': 'Failed to send email'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f"Error sending email: {str(e)}"
        }
 
def main():
    st.set_page_config(page_title="AI Email Assistant", layout="wide")
   
    # Initialize session state
    if 'response_generated' not in st.session_state:
        st.session_state.response_generated = False
    if 'context_variables' not in st.session_state:
        st.session_state.context_variables = {}
   
    # Custom Header with Styling
    st.markdown(
        """
        <style>
            .title {
                text-align: center;
                font-size: 36px;
                font-weight: bold;
                color: #4A90E2;
            }
            .subtitle {
                text-align: center;
                font-size: 18px;
                color: #6c757d;
            }
            .stTextArea label { font-size: 18px; font-weight: bold; }
            .email-response {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                margin: 10px 0;
            }
        </style>
        <div class="title">📧 AI-Powered Email Response Generator</div>
        <div class="subtitle">Automate email replies efficiently using AI</div>
        """,
        unsafe_allow_html=True,
    )
   
    # Input fields
    st.write("### 💬 Email Details")
    email_text = st.text_area("Email Body", height=250)
    
   
    # Buttons and Response
    col1, col2 = st.columns([1, 1])
   
    with col1:
        if st.button("🚀 Generate Response", use_container_width=True):
             if email_text:
                with st.spinner("🤖 Generating response..."):
                    response = generate_response(email_text)
                    # st.write(response)
                    if response['status'] == 'Success':
                        st.session_state.response_generated = True
                        st.session_state.context_variables = response


                        
                        # # Display the generated response
                        st.write("### 👤 Customer Request")
                        st.info(response["Query"])
                        st.write("### 🔍 Generated Response")
                        st.info(response['validation_steps'])
                        if response.get("additional_offers") is not None:
                            st.write("### 🤑 Additional Offers")
                            st.info(response["additional_offers"])
                        
                        
                        # # Display category if available
                        # if 'Category' in response['context']:
                        #     st.write("### 📋 Category")
                        #     st.success(response['context']['Category'])
                    else:
                        st.error(f"❌ {response['message']}")
             else:
                st.warning("⚠️ Please provide email content.")
    with col2:
        if st.button("📤 Send Response", use_container_width=True):
            if st.session_state.response_generated:
                with st.spinner("📨 Sending email..."):

                    send_result=generate_answer(st.session_state.context_variables)

                    # send_result = send_response(st.session_state.context_variables)
               
                if send_result['status'] == 'Success':
                    st.success(f"✅ Email sent successfully! Message ID: {send_result['message_id']}")

                # st.write(f"The con-var from the send res {send_result}")

                print("The senddddddddddddddddddddd result===========",send_result)
                    
                   # Create the same prompt as in send_mail.py to show the sent content
                    # prompt = f"""
                    # Generate a brief, professional email response for a customer service request.
                    # Strictly maintained the email format.

                    # Context:
                    # - Customer Request: {st.session_state.context_variables.get("Body_of_the_mail")}
                    # - Status: {st.session_state.context_variables.get('Generated_status')}

                    # Requirements:
                    # 1. Keep the response clear and concise (max 3-4 sentences)
                    # 2. Be direct about the status/decision
                    # 3. Include only essential details
                    # 4. Maintain a professional tone

                    # Provide output in JSON format:
                    # {{
                    #     "subject": "Brief, clear subject line",
                    #     "body": "Concise response"
                    # }}
                    # """
                    
                    # # Get the formatted email content
                    # response = open_ai.chat.completions.create(
                    #     model="gpt-4-turbo",
                    #     messages=[
                    #         {"role": "system", "content": "You are an expert email assistant."},
                    #         {"role": "user", "content": prompt}
                    #     ]
                    # )
                    # llm_result=response.choices[0].message.content
                    # email_content = json.loads(llm_result)
                    
                # Display the actual sent email
                st.write("### 📨 Sent Email Details")
                with st.expander("View Sent Email", expanded=True):
                    st.write("**To:**", send_result.get('To', 'N/A'))
                    st.write("**From:** harshavardhanbudda@gmail.com")
                    # st.write("**Subject:**", st.session_state.send_result['subject'])
                    st.write("**Email Body:**")
                    st.info(send_result["res_subject"])
                    st.info(send_result['body'])
            else:
                st.error(f"❌ {send_result['message']}")
        else:
            st.warning("⚠️ Please generate a response first.")
   
    # # Display Response Details
    # if st.session_state.response_generated:
    #     st.write("### 🔍 Generated Response")
    #     st.info(response['validation_steps'])
    #     st.write("### 🔍 Response Email")
    #     st.info(st.session_state.context_variables.get('validation_steps', ''))
       
    #     if 'Generated_status' in st.session_state.context_variables:
    #         st.write("### 📝 Status")
    #         st.info(st.session_state.context_variables['Generated_status'])
 
if __name__ == "__main__":
    main()
