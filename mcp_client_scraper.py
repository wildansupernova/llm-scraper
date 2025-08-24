from mcp import ClientSession, StdioServerParameters

from mcp.client.stdio import stdio_client

from langchain_mcp_adapters.tools import load_mcp_tools

from langgraph.prebuilt import create_react_agent

from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate

from langchain_groq import ChatGroq

from langchain_openai import ChatOpenAI

import asyncio

import os

from dotenv import load_dotenv

load_dotenv()

# Initialize the LLM model
# model = ChatGroq(model="llama3-8b-8192", temperature=0)
model = ChatOpenAI(model="gpt-5-mini", temperature=0)

server_params = StdioServerParameters(

   command="python",      # Command to execute

   args=["scraper.py"] # Arguments for the command (our server script)

)

# Define the system prompt
system_prompt = """
# Web Scraping Assistant

You are a web scraping specialist with access to these tools:

## Tools (Please check also the tools) :
1. **scrape_url_to_file(url)** - Scrapes webpage to HTML file
2. **read_file_content(file_path)** - Reads file content
3. **execute_python_script_from_file(script_path_file, input)** - Executes Python script files
4. **save_content_to_file(content, file_extension)** - Saves content to file

## Strict Workflow (Please you are a good assistant, so please follow this strict workflow):
1. **Analyze**: Scrape first URL, read HTML, identify patterns (selectors, html class, etc)
2. **Process**: Scrape additional pages (max 5 for pagination) (Don't read_file_content more than once for similar pages, please do this, strict)
3. **Extract**: Create Python script accepting file paths as input (you can use library like beautifulsoup if needed, already installed)
4. **Output**: Execute script, save results to structured JSON format

## Key Rules:
- Scripts handle file reading internally via file paths
- This is strictes rule, please adhere. For similar pattern pages (for example page 1 and page 2, page 3, etc), please don't read_file_content it more than once for similar pages and just use the python script to extract data (for saving tokens and context window).
- Support single/multiple files (comma-separated paths)
- Output JSON/CSV format
- Include error handling and validation
- Save intermediate results when needed
- Analyze HTML structure before extraction
- Use robust selectors across pages

## Multi-page Strategy:
1. Scrape pages to individual files
2. Analyze first file for patterns
3. Create extraction script
4. Process all files with script
5. Save consolidated results

## Security:
- Validate URLs and file paths
- Handle exceptions properly
- No external code execution
- Sanitize inputs

Answer with this json schema

    "text: Your response to the user
    "results: this is the json resulted from the scraping. if the results is array then just return array, if object please use object
    "summary": this is summary of what are you doing previously (including previous history chat, please also include anything like files you created and the description, also the url you scraped)

"""

# Create a ChatPromptTemplate with system and human prompts
prompt_template = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(system_prompt),
    ("placeholder", "{messages}")
])

async def run_agent():

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            print("MCP Session Initialized.")

            tools = await load_mcp_tools(session)

            print(f"Loaded Tools: {[tool.name for tool in tools]}")

            agent = create_react_agent(model, tools, prompt=prompt_template)

            print("ReAct Agent Created.")

            print(f"Invoking agent with query")

            user_input = """

                From the URL (https://medrecruit.medworld.com/jobs/list?location=New+South+Wales&page=1), get the role, specialty, location, and pay of jobs from page 1-3.

                Please include which page is the data exist
            """

            response = await agent.ainvoke({

                "messages": [("user", user_input)]

            })

            print("Agent invocation complete.")

            # Return the content of the last message (usually the agent's final answer)
            # print(response)
            return response["messages"][-1].content
       

if __name__ == "__main__":

   # Run the asynchronous run_agent function and wait for the result

   print("Starting MCP Client...")

   result = asyncio.run(run_agent())

   print("\nAgent Final Response:")

   print(result)