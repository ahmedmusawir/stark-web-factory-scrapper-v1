#!/usr/bin/env python3
"""
GHL API CHATBOT - SPLIT PANEL UI
---------------------------------
Chat on left, responses on right (Lovable/Replit style)
With proper session memory

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
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# SYSTEM PROMPT (no "I don't have memory" statement)
SYSTEM_PROMPT = """You are an expert GHL API documentation assistant with intelligent search capabilities.

🔍 SEARCH STRATEGIES:

1. For "list all" or "show categories" queries:
   - Search for "MASTER_INDEX" or "ALL CATEGORIES"
   - Return the COMPLETE list, alphabetically
   - Include counts: "Contacts (45 endpoints)"

2. For "how many" queries:
   - Search for "STATISTICS" or totals
   - State the exact number

3. For specific endpoints:
   - Search for endpoint name
   - Try variations if not found: create/add, get/fetch, update/modify
   - Return ONLY relevant details

4. For parameters:
   - Focus on required vs optional
   - Use tables for clarity

5. For code examples:
   - Use proper code blocks with language tags
   - Include authentication details
   - Keep it minimal and focused

📋 FORMATTING:
- Lists: Numbered, alphabetical, complete
- Code: ```python or ```javascript with proper formatting
- Tables: For parameters (Parameter | Type | Required | Description)
- Keep responses concise and focused on user's question

If search fails, try alternative terms automatically."""

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_response' not in st.session_state:
    st.session_state.current_response = "Ask me anything about the GHL API!"

if 'store_name' not in st.session_state:
    store_file = Path("ghl_store_name.txt")
    if store_file.exists():
        st.session_state.store_name = store_file.read_text().strip()
    else:
        st.error("Store not found!")
        st.stop()

if 'client' not in st.session_state:
    try:
        st.session_state.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    except Exception as e:
        st.error(f"Failed to initialize: {e}")
        st.stop()

# Header
st.title("🚀 GHL API Documentation Assistant")

# Two column layout - LOVABLE/REPLIT STYLE
left_col, right_col = st.columns([1, 2])

# LEFT PANEL - Chat History & Input
with left_col:
    st.markdown("### 💬 Chat")
    
    # Example queries
    with st.expander("💡 Examples", expanded=False):
        examples = [
            "List all API categories",
            "Show contact endpoints",
            "How to create contact?",
            "Required parameters?",
            "Python code example",
        ]
        
        for example in examples:
            if st.button(example, key=f"ex_{example}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": example})
                
                with st.spinner("Thinking..."):
                    try:
                        full_query = f"{SYSTEM_PROMPT}\n\nUser Question: {example}"
                        
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
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        st.session_state.current_response = answer
                        
                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
                        st.session_state.current_response = error_msg
                
                st.rerun()
    
    st.markdown("---")
    
    # Chat history container
    chat_container = st.container(height=400)
    
    with chat_container:
        if not st.session_state.messages:
            st.info("👋 Start chatting below!")
        else:
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.markdown(f"**🧑 You:** {msg['content']}")
                else:
                    # Show preview in history
                    preview = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
                    st.markdown(f"**🤖 Bot:** {preview}")
    
    # Clear button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_response = "Ask me anything about the GHL API!"
        st.rerun()
    
    st.markdown("---")
    
    # Chat input
    prompt = st.chat_input("Ask about GHL API...")
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("Thinking..."):
            try:
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
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.current_response = answer
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.session_state.current_response = error_msg
        
        st.rerun()

# RIGHT PANEL - Full Response Display
with right_col:
    st.markdown("### 📄 Response")
    
    # Stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Endpoints", "~700")
    with col2:
        st.metric("Categories", "38")
    with col3:
        st.metric("Messages", len(st.session_state.messages))
    
    st.markdown("---")
    
    # Full response display
    response_container = st.container(height=600)
    
    with response_container:
        st.markdown(st.session_state.current_response)

# Footer
st.markdown("---")
st.caption("🚀 Powered by Google File Search API & Gemini 2.5 Flash")