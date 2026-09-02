#!/usr/bin/env python3
"""
GHL API CHATBOT - STREAMLIT UI
-------------------------------
Beautiful interface with session memory and code formatting

Run: streamlit run ghl_chatbot_streamlit.py
"""

import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()

# Page config
st.set_page_config(
    page_title="GHL API Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# KILLER SYSTEM PROMPT
SYSTEM_PROMPT = """You are an expert GHL API documentation assistant with intelligent search capabilities.

🔍 CRITICAL SEARCH STRATEGIES (FOLLOW THESE RULES):

1. For "list all" or "show me the list" queries:
   - ALWAYS search for "MASTER_INDEX" or "ALL CATEGORIES" FIRST
   - Extract the COMPLETE list from the master index
   - Format as numbered list, alphabetically
   - Include endpoint counts: "Contacts (45 endpoints)"

2. For "how many" queries:
   - Search for "STATISTICS" or "MASTER_INDEX"
   - Look for total counts
   - State the EXACT number clearly

3. For specific endpoint queries (e.g., "create contact"):
   - Search for the endpoint name
   - If not found, try variations: create/add, get/fetch, update/modify, delete/remove
   - Return ONLY the relevant endpoint details, not the entire category

4. For parameter/details queries:
   - Focus on required vs optional parameters
   - Use tables for parameter lists
   - Keep descriptions concise

5. For code examples:
   - Extract ONLY the code block needed
   - Include minimal context (authentication, required params)
   - Use proper language tags

6. If query is unclear:
   - Ask for clarification
   - Suggest alternative phrasings
   - Don't return "None" without trying alternatives

📋 RESPONSE FORMATTING RULES (MANDATORY):
- Lists: ALWAYS numbered, alphabetically sorted, complete
- Code: ALWAYS use ```python or ```javascript with proper formatting
- Tables: Use for parameter lists (Parameter | Type | Required | Description)
- Headers: Use ## and ### for organization
- Conciseness: Focus on what user needs, not everything

Remember: Users expect intelligent, concise, well-formatted responses."""

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'store_name' not in st.session_state:
    # Load store name
    store_file = Path("ghl_store_name.txt")
    if store_file.exists():
        st.session_state.store_name = store_file.read_text().strip()
    else:
        st.error("Store not found! Please run setup first.")
        st.stop()

if 'client' not in st.session_state:
    try:
        st.session_state.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    except Exception as e:
        st.error(f"Failed to initialize Gemini client: {e}")
        st.stop()

# Sidebar
with st.sidebar:
    st.title("🚀 GHL API Assistant")
    st.markdown("---")
    
    st.markdown("### 📊 Quick Stats")
    st.info(f"""
    **Store:** GHL API v2 Docs  
    **Endpoints:** ~700  
    **Categories:** 38  
    **Model:** Gemini 2.5 Flash
    """)
    
    st.markdown("---")
    
    st.markdown("### 💡 Example Queries")
    
    examples = [
        "List all API categories",
        "Show me all contact endpoints",
        "How do I create a contact?",
        "What parameters are required for create contact?",
        "Give me Python code for creating a contact",
        "Show me all calendar endpoints",
        "How many email endpoints are there?",
    ]
    
    for example in examples:
        if st.button(example, key=example, use_container_width=True):
            st.session_state.messages.append({"role": "user", "content": example})
            st.rerun()
    
    st.markdown("---")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.title("🤖 GHL API Documentation Assistant")
st.markdown("Ask me anything about the GoHighLevel API!")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about GHL API endpoints, parameters, code examples..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Add system prompt to query
                full_query = f"{SYSTEM_PROMPT}\n\nUser Question: {prompt}"
                
                response = st.session_state.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=full_query,
                    config=types.GenerateContentConfig(
                        tools=[
                            types.Tool(
                                file_search=types.FileSearch(
                                    file_search_store_names=[st.session_state.store_name]
                                )
                            )
                        ]
                    )
                )
                
                answer = response.text
                
                # Display answer
                st.markdown(answer)
                
                # Add to chat history
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.8em;'>
    Powered by Google File Search API & Gemini 2.5 Flash | Session memory enabled
</div>
""", unsafe_allow_html=True)