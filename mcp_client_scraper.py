from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
import asyncio
import os
import json
import uuid
from dotenv import load_dotenv

load_dotenv()


class MCPClient:
    def __init__(self, model_type="openai", temperature=0):
        """
        Initialize the MCP Client with specified model configuration.
        
        Args:
            model_type (str): Type of model to use ("openai" or "groq")
            temperature (float): Temperature setting for the model
        """
        # Initialize the LLM model
        if model_type == "groq":
            self.model = ChatGroq(model="llama3-8b-8192", temperature=temperature)
        else:
            self.model = ChatOpenAI(model="gpt-5-mini", temperature=temperature)
        
        self.server_params = StdioServerParameters(
            command="python",
            args=["scraper.py"]
        )
        
        # Define the base system prompt
        self.base_system_prompt = """
                # Web Scraping Assistant

                You are a web scraping specialist with access to these tools:

                ## Tools (Please check also the tools) :
                1. **scrape_url_to_file(url)** - Scrapes webpage to HTML file
                2. **read_file_content(file_path)** - Reads file content
                3. **execute_python_script_from_file(script_path_file, input, output_extension)** - Executes Python script files with optional stdin input and saves stdout to a file with specified extension (default: "txt"). Returns information about execution including output file path and any errors.
                4. **save_content_to_file(content, file_extension)** - Saves content to file

                ## Strict Workflow (Please you are a smart and rigid assistant, so please follow this strict workflow):
                1. **Analyze**: Scrape first URL, read HTML, identify patterns (selectors, html class, etc)
                2. **Process**: Scrape additional pages (max 5 for pagination) (Don't read_file_content more than once for similar pages, please do this, strict)
                3. **Extract**: Create Python script accepting file paths as input (you can use library like beautifulsoup if needed, already installed)
                4. **Output**: Execute script with appropriate output extension (json for JSON data, csv for CSV data), which automatically saves stdout results to a file and returns the file path
                    - If you think this is final output, please don't reveal any system file names but if it is only for intermediate processing then it is fine (if it is not final result)
                ## Key Rules:
                - Scripts handle file reading internally via file paths
                - This is strictes rule, please adhere. For similar pattern pages (for example page 1 and page 2, page 3, etc), please don't read_file_content it more than once for similar pages and just use the python script to extract data (for saving tokens and context window).
                - Support single/multiple files (comma-separated paths)
                - Python script stdout is automatically saved to file with UUID naming and custom extension support
                - Use appropriate file extensions (json, csv, txt) based on output format
                - Output JSON/CSV format
                - Include error handling and validation
                - Save intermediate results when needed
                - Analyze HTML structure before extraction
                - Use robust selectors across pages

                ## Multi-page Strategy:
                1. Scrape pages to individual files
                2. Analyze first file for patterns
                3. Create extraction script
                4. Process all files with script (stdout automatically saved with appropriate extension)
                5. Access consolidated results from saved output file (JSON/CSV format based on extension used)

                ## Security:
                - Validate URLs and file paths
                - Handle exceptions properly
                - No external code execution
                - Sanitize inputs

                {context_section}

                Answer with this json schema

                    "text": Your response to the user
                    "results_json_file_path": Path to the JSON file containing the results
                    "summary": this is summary of what are you doing previously (including previous history chat summary, please also include anything like files you created and the description such as script, html and so on and also the url you scraped and json file result if exist)

        """

        self.session_summary = dict()

    def _create_prompt_template(self, previous_summary=None):
        """
        Create a prompt template with optional session context.
        
        Args:
            previous_summary (dict): Previous session summary to include in context
            
        Returns:
            ChatPromptTemplate: Configured prompt template
        """
        if previous_summary:
            context_section = f"""
                ## Session Context:
                Previous session summary: {previous_summary}
                
                Please consider this previous context when processing the current request. You can reference previous files, URLs scraped, and any patterns or scripts that were created in the previous session.
                """
        else:
            context_section = "## Session Context:\nThis is a new session with no previous context."
        
        system_prompt = self.base_system_prompt.format(context_section=context_section)
        
        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            ("placeholder", "{messages}")
        ])

    async def invoke_query(self, user_input: str, session_id=None) -> str:
        """
        Invoke a query using the MCP client and return the agent's response.
        
        Args:
            user_input (str): The query/instruction to send to the agent
            session_id (str, optional): Session ID for maintaining context
            
        Returns:
            dict: The agent's response content as JSON
        """
        if session_id == None:
            session_id = str(uuid.uuid4().hex)
        
        previous_summary = None
        if session_id in self.session_summary:
            previous_summary = self.session_summary[session_id]
        
        # Create prompt template with session context
        prompt_template = self._create_prompt_template(previous_summary)

        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("MCP Session Initialized.")
                
                tools = await load_mcp_tools(session)
                print(f"Loaded Tools: {[tool.name for tool in tools]}")
                
                agent = create_react_agent(self.model, tools, prompt=prompt_template)
                print("ReAct Agent Created.")
                
                if previous_summary:
                    print(f"Using previous session context for session: {session_id}")
                else:
                    print(f"Starting new session: {session_id}")
                
                print(f"Invoking agent with query")
                
                response = await agent.ainvoke({
                    "messages": [("user", user_input)]
                })
                content = response["messages"][-1].content
                print("Agent invocation complete.")
                
                # Parse JSON content
                try:
                    json_content = json.loads(content)
                except json.JSONDecodeError:
                    print("Failed to parse JSON content.")
                    return {"error": "Failed to parse JSON content.", "session_id": session_id}
                
                # Update session summary
                self.session_summary[session_id] = json_content.get("summary", {})
                json_content["session_id"] = session_id
                return json_content

    async def run_agent(self):
        """
        Legacy method for backward compatibility.
        Runs the agent with a predefined query.
        """
        user_input = """
        From the URL (https://medrecruit.medworld.com/jobs/list?location=New+South+Wales&page=1), get the role, specialty, location, and pay of jobs from page 1-3.

        Please include which page is the data exist
        """
        
        return await self.invoke_query(user_input)


def main():
    """Main function to run the MCP client with default configuration."""
    client = MCPClient()
    
    print("Starting MCP Client...")
    
    # Default query for demonstration
    default_query = """
    From the URL (https://medrecruit.medworld.com/jobs/list?location=New+South+Wales&page=1), get the role, specialty, location, and pay of jobs from page 1-3.

    Please include which page is the data exist
    """
    
    result = asyncio.run(client.invoke_query(default_query))
    
    print("\nAgent Final Response:")
    print(result)


if __name__ == "__main__":
    main()