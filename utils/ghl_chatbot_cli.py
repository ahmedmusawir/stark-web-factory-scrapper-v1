#!/usr/bin/env python3
"""
Interactive GHL API Chatbot - CLI Mode
Ask questions about your GHL API documentation in real-time
Now with production-grade system prompt for optimal responses
"""
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

# KILLER SYSTEM PROMPT - STREAMLIT OPTIMIZED WITH SMART RETRIEVAL
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

1. Lists:
   - ALWAYS numbered (1., 2., 3.)
   - ALWAYS alphabetically sorted unless specified otherwise
   - ALWAYS complete (no "and X more" unless list is huge)
   - Include counts: "Categories (38 total)"

2. Code Blocks:
   - ALWAYS use ```python or ```javascript or ```bash
   - Include authentication examples
   - Keep it minimal and focused

3. Tables:
   - Use for parameter lists
   - Columns: Parameter | Type | Required | Description
   - Keep descriptions brief (one line max)

4. Structure:
   - Use ## headers for major sections
   - Use ### for subsections
   - Keep paragraphs short (2-3 sentences max)

5. Conciseness:
   - Don't include every optional parameter unless asked
   - Focus on what the user needs
   - Highlight required items clearly

🎯 INTELLIGENCE RULES:

- If initial search fails, try synonyms automatically
- Combine information from multiple sources when needed
- State clearly if information is incomplete
- Never return "None" without explaining why
- Always provide next steps or alternatives

Remember: Users expect intelligent, concise, well-formatted responses ready for Streamlit display."""

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

with open("ghl_store_name.txt", "r") as f:
    store_name = f.read().strip()

print("="*70)
print("  🤖 GHL API KNOWLEDGE BASE - INTERACTIVE CLI")
print("  (Enhanced with Production System Prompt)")
print("="*70)
print(f"\n📁 Store: {store_name}")
print(f"🤖 Model: gemini-2.5-flash")
print(f"✨ Features: Streamlit-optimized markdown output")

print("\n" + "="*70)
print("💡 COMMANDS:")
print("   • Type your question and hit Enter")
print("   • 'help' - Show example questions")
print("   • 'exit' or 'quit' - Exit chatbot")
print("\n🎯 EXAMPLE QUESTIONS:")
print("   • List all API categories")
print("   • Show me all contact endpoints")
print("   • How do I create a contact? (with Python code)")
print("   • What parameters does delete contact need?")
print("   • Give me a comparison of authentication methods")
print("="*70 + "\n")

while True:
    question = input("❓ You: ").strip()
    
    if question.lower() in ['exit', 'quit', 'q']:
        print("\n👋 Goodbye! Your knowledge base is always here.")
        break
    
    if not question:
        continue
    
    if question.lower() == 'help':
        print("\n🎯 EXAMPLE QUESTIONS:")
        print("   • List all API categories (alphabetically)")
        print("   • Show me all contact endpoints")
        print("   • How do I create a contact with Python?")
        print("   • What are all the authentication methods?")
        print("   • Compare GET vs POST endpoints")
        print("   • Show me webhook documentation")
        print("   • What parameters are required for create task?\n")
        continue
    
    print("\n🤔 Thinking...\n")
    
    # Add system prompt to query
    full_query = f"{SYSTEM_PROMPT}\n\nUser Question: {question}"
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=full_query,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[store_name]
                    )
                )
            ]
        )
    )
    
    print(f"✅ Answer:\n{response.text}\n")
    print("─"*70 + "\n")