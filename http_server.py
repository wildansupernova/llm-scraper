from flask import Flask, request, jsonify

import asyncio
from mcp_client_scraper import MCPClient
import os
import json

app = Flask(__name__)

client = MCPClient(model_type="openai", temperature=0)

async def process_request(text_input, session_id=None) -> str:
    response = await client.invoke_query(text_input, session_id=session_id)
    return response

def read_file_content(file_path: str) -> str:
    """
    Read and return the content of a file.
    
    Args:
        file_path: The absolute path to the file to read
        
    Returns:
        The content of the file as a string
    """
    try:
        if not os.path.exists(file_path):
            error_message = f"Error: File '{file_path}' does not exist"
            return error_message
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return content
        
    except Exception as e:
        return f"Error reading file: {str(e)}"

@app.route('/chats', methods=['POST'])
def chats():
    data = request.get_json()
    text_input = data.get('text_input')
    session_id = data.get('session_id') if data.get('session_id') else None

    response = asyncio.run(process_request(text_input, session_id=session_id))
    print(response.get("results_json_file_path", "[]"))
    return jsonify({
        "text": response.get("text", text_input),
        "results": json.loads(read_file_content(response.get("results_json_file_path", "[]"))),
        "session_id": session_id
    })

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
