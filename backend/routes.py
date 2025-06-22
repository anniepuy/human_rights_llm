"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-21-2025
File: routes.py
Description: Flask routes for the Human Rights LLM.
"""

from flask import Flask, request, jsonify
from agent.notion_react_agent import run_agent

app = Flask(__name__)

@app.route('/api/generate_report', methods=['POST'])
def generate_report():
    data = request.get_json()
    query = data.get("query", "")

    if not query:
        return jsonify({"error": "Query is required"}), 400
    
    try:
        result = run_agent(query)
        return jsonify({"result": result["output"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(debug=True)