"""
Application: Human Rights LLM
Author: Ann Hagan - ann.marie783@gmail.com
Date: 06-21-2025
File: routes.py
Description: Flask routes for the Human Rights LLM.
"""

import os
import sys
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import subprocess
import logging
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

# Import the agent, Notion publishing, and chat history
from backend.agent.notion_react_agent import run_agent, publish_to_notion
from backend.memory import sql_chat_memory as chat_history

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.route('/api/agent', methods=['POST'])
def agent_endpoint():
    """
    Handle agent queries from the frontend.
    Expects JSON with 'query' field.
    Returns JSON with 'result' (agent response) and 'notion_success' (publishing status).
    """
    logger.info("Received request to /api/agent")
    try:
        data = request.get_json()
        
        if not data or 'query' not in data:
            logger.error("Missing query parameter")
            return jsonify({'error': 'Missing query parameter'}), 400
        
        user_query = data['query']
        logger.info(f"API query: {user_query}")
        
        # Run the agent
        result = run_agent(user_query)
        logger.info(f"Agent result: {result['output'][:100]}...")
        
        # Extract the output
        if isinstance(result, dict) and 'output' in result:
            response_text = result['output']
        else:
            logger.warning("Unexpected result structure")
            response_text = str(result)
        
        # Prepare for Notion publishing
        title = f"Human Rights Report: {user_query.title()}" if "report" in user_query.lower() else f"Summary: {user_query.title()}"
        logger.info(f"Attempting to publish to Notion with title: {title}")
        
        # Publish to Notion
        notion_success = publish_to_notion(
            title=title,
            content=response_text,
            date=datetime.now().strftime("%Y-%m-%d"),
            source="Human Rights LLM Agent"
        )
        if notion_success:
            logger.info("Successfully published to Notion")
        else:
            logger.error("Failed to publish to Notion")
        
        return jsonify({
            'result': response_text,
            'notion_success': notion_success,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Agent error: {str(e)}")
        return jsonify({
            'error': f'Agent error: {str(e)}',
            'status': 'error'
        }), 500

@app.route('/api/ingest', methods=['POST'])
def trigger_ingest():
    """
    Trigger the ingest pipeline from the frontend.
    Returns status of the ingest process.
    """
    logger.info("Starting ingest pipeline")
    try:
        result = subprocess.run(
            ["python", "backend/ingest/run_ingest_pipeline.py"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=300
        )
        
        if result.returncode == 0:
            logger.info("Ingest pipeline completed successfully")
            return jsonify({
                'status': 'success',
                'message': 'Ingest pipeline completed successfully!',
                'output': result.stdout
            })
        else:
            logger.error(f"Ingest pipeline failed: {result.stderr}")
            return jsonify({
                'status': 'error',
                'message': 'Ingest pipeline failed',
                'error': result.stderr,
                'output': result.stdout
            }), 500
            
    except subprocess.TimeoutExpired:
        logger.error("Ingest pipeline timed out")
        return jsonify({
            'status': 'error',
            'message': 'Ingest pipeline timed out (5 minutes)'
        }), 500
    except Exception as e:
        logger.error(f"Failed to run ingest pipeline: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to run ingest pipeline: {str(e)}'
        }), 500

@app.route('/api/chat_history', methods=['GET'])
def get_chat_history():
    """
    Retrieve chat history from sql_chat_memory.
    Returns a list of chat sessions with session ID and preview.
    """
    logger.info("Received request to /api/chat_history")
    try:
        chat_sessions = chat_history.get_chat_sessions()
        history = [
            {
                "session_id": session_id,
                "preview": session_info[:50] + "..." if len(session_info) > 50 else session_info,
                "timestamp": chat_history.get_session_timestamp(session_id)
            }
            for session_id, session_info in chat_sessions
        ]
        return jsonify({
            'status': 'success',
            'history': history
        })
    except Exception as e:
        logger.error(f"Chat history error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to retrieve chat history: {str(e)}'
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting Human Rights LLM API on port {port}")
    logger.info(f"API will be available at: http://localhost:{port}")
    logger.info(f"Frontend can connect to: http://localhost:{port}/api/agent")
    
    app.run(host='0.0.0.0', port=port, debug=debug)