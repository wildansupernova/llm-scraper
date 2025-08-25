# LLM Scraper

# Technology Used
- Langgraph
- Python 3
- Model Used: gpt-5-mini (please change this to gpt-5 if you have budget for better crawling)
- Crawl4AI as the browser.
- MCP
- Flask

## How to Install

1. **Clone the repository:**
   ```sh
   git clone https://github.com/wildansupernova/llm-scraper.git
   cd llm-scraper
   ```

2. **(Recommended) Create and activate a Python virtual environment:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Copy `.env.example` to `.env` (if provided), or create a `.env` file with any required API keys or settings.
   - Change the OPENAI_API_KEY to yours

5. **Start the HTTP server:**
   ```sh
   python http_server.py
   ```

## API Usage

### Endpoint

POST `/chats`

### Request Example

```
curl --request POST \
  --url http://127.0.0.1:5000/chats \
  --header 'Content-Type: application/json' \
  --data '{
    "text_input": "https://medrecruit.medworld.com/jobs/list?location=New+South+Wales&page=1 From the URL, get the role, specialty, location, and pay of jobs from page 1 until 3.",
    "session_id": "session-id-1"
}'
```

### Response
Returns a JSON object:
- `results`: the scraped data
- `session_id`: session id used
- `text`: the response from the LLM

### Continuing a Session
To continue a session, use the same `session_id`:

```
curl --request POST \
  --url http://127.0.0.1:5000/chats \
  --header 'Content-Type: application/json' \
  --data '{
    "text_input": "Filter data that have pay higher than $2,000 per day only.",
    "session_id": "session-id-1"
}'
```

### Starting a New Session
To start a new session, use a different `session_id` value.




