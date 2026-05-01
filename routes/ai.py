import os
import json
from flask import Blueprint, request, jsonify
import google.generativeai as genai
from utils import sanitize_input
from datetime import datetime

ai_bp = Blueprint('ai', __name__)

# Configure Gemini
api_key = os.environ.get("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@ai_bp.route('/chat', methods=['POST'])
def chat():
    if not api_key:
        return jsonify({"response": "AI temporarily unavailable (Missing API Key)", "timestamp": datetime.now().strftime("%H:%M")})

    data = request.json
    raw_message = data.get('message', '')
    country = data.get('country', 'IN')
    
    message = sanitize_input(raw_message)
    if message == "I can only answer election-related questions.":
        return jsonify({"response": message, "timestamp": datetime.now().strftime("%H:%M")})
        
    system_prompt = f"You are ElectIQ, a friendly civic education assistant specializing in {country}'s election process. Answer questions clearly and simply. Always stay factual. End every response with: 'For official info, visit the official election body website'. Never give legal advice. Keep responses under 150 words."
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)
        # Mocking history for simplicity, in a real app you'd pass it in
        chat = model.start_chat(history=[])
        response = chat.send_message(message)
        return jsonify({"response": response.text, "timestamp": datetime.now().strftime("%H:%M")})
    except Exception as e:
        print(f"Gemini Error: {e}")
        return jsonify({"response": "AI temporarily unavailable due to an error.", "timestamp": datetime.now().strftime("%H:%M")}), 500

@ai_bp.route('/bust-myth', methods=['POST'])
def bust_myth():
    if not api_key:
        # Mock response if no key
        return jsonify({
            "verdict": "PARTIAL",
            "explanation": "AI temporarily unavailable. Please check official sources.",
            "source": None
        })

    data = request.json
    raw_myth = data.get('myth', '')
    country = data.get('country', 'IN')
    
    myth = sanitize_input(raw_myth)
    
    prompt = f"You are an election fact-checker for {country}. Analyze this statement: '{myth}'. Respond ONLY in JSON with the exact following structure: {{\"verdict\": \"TRUE\"|\"FALSE\"|\"PARTIAL\", \"explanation\": \"2-3 sentences explaining why\", \"source\": \"official URL or null\"}}"
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        text = response.text.strip()
        # Clean up markdown JSON formatting if present
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        
        result = json.loads(text.strip())
        return jsonify(result)
    except Exception as e:
        print(f"Gemini Error: {e}")
        return jsonify({
            "verdict": "PARTIAL",
            "explanation": "AI temporarily unavailable to verify this myth.",
            "source": None
        }), 500
