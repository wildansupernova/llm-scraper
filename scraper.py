from mcp.server.fastmcp import FastMCP
import os
import uuid
from dotenv import load_dotenv
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode
import logging

load_dotenv()

mcp = FastMCP("webcrawl")

mcp.settings.port = 8002
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Keep console output as well
    ]
)
logger = logging.getLogger(__name__)


browser_config = BrowserConfig(
            headless=True,  
            java_script_enabled=True,
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/116.0.0.0 Safari/537.36"
        )  
run_config = CrawlerRunConfig(
    delay_before_return_html=5,
    wait_until="networkidle",  # Wait until network is idle
    page_timeout=30000,  # 30 second timeout for page load
    js_code=["window.scrollTo(0, document.body.scrollHeight);"]  # Scroll to bottom to trigger lazy loading
) 


@mcp.tool()
async def scrape_url_to_file(url: str) -> str:
    """
    Scrape a webpage and save its cleaned HTML content to a file.
    
    Args:
        url: The URL of the webpage to scrape
        
    Returns:
        The absolute file path where the HTML content was saved
    """
    logger.info(f"Starting scrape_url_to_file with URL: {url}")
    try:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, run_config=run_config)
            if not result.success:
                logger.error(f"Error scraping URL {url}: {result.error_message}")
                return f"Error scraping URL {url} with status code {result.status_code}`: {result.error_message}"
            # Generate a unique filename using UUID
            filename = f"{uuid.uuid4().hex}.html"
            file_path = os.path.abspath("temp/"+filename)
            
            # Save the HTML content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result.cleaned_html)
            
            logger.info(f"Successfully saved HTML content to {file_path}")
            return file_path
            
    except Exception as e:
        logger.error(f"Error in scrape_url_to_file: {str(e)}")
        return f"Error scraping URL and saving to file: {str(e)}"

@mcp.tool()
async def save_content_to_file(content: str, file_extension: str = "txt") -> str:
    """
    Save string content to a file with a specified extension.
    
    Args:
        content: The string content to save to file
        file_extension: The file extension (default: "txt")
        
    Returns:
        The absolute file path where the content was saved
    """
    logger.info(f"Starting save_content_to_file with file_extension: {file_extension}")
    try:
        # Generate a unique filename using UUID
        filename = f"{uuid.uuid4().hex}.{file_extension.lstrip('.')}"
        file_path = os.path.abspath("temp/"+filename)

        # Save the content to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Successfully saved content to {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error in save_content_to_file: {str(e)}")
        return f"Error saving content to file: {str(e)}"

@mcp.tool()
async def read_file_content(file_path: str) -> str:
    """
    Read and return the content of a file.
    
    Args:
        file_path: The absolute path to the file to read
        
    Returns:
        The content of the file as a string
    """
    logger.info(f"Starting read_file_content with file_path: {file_path}")
    try:
        if not os.path.exists(file_path):
            error_message = f"Error: File '{file_path}' does not exist"
            logger.error(error_message)
            return error_message
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"Successfully read content from {file_path}")
        return content
        
    except Exception as e:
        logger.error(f"Error in read_file_content: {str(e)}")
        return f"Error reading file: {str(e)}"

@mcp.tool()
async def execute_python_script_from_file(script_path_file: str, input: str = None, output_extension: str = "txt") -> str:
    """
    Execute a Python script file with optional stdin input and save stdout to a file.
    
    Args:
        script_path_file: The absolute path to the Python script file to execute
        input: Optional string input to pass to the script via stdin
        output_extension: File extension for the stdout output file (default: "txt")
        
    Returns:
        Information about the execution including output file path and any errors
    """
    logger.info(f"Starting execute_python_script with input: {input} and script_path_file: {script_path_file}")
    import subprocess
    import sys
    
    try:
        logger.info(f"Executing script stored at {script_path_file}")
        # Execute the script using subprocess
        result = subprocess.run(
            [sys.executable, script_path_file],
            input=input,
            capture_output=True,
            text=True,
            timeout=60  # 60 second timeout for safety
        )
        
        logger.info("Script executed successfully")
        
        # Save stdout to file if there's output
        stdout_file_path = None
        if result.stdout:
            # Generate a unique filename for stdout output with specified extension
            stdout_filename = f"{uuid.uuid4().hex}.{output_extension.lstrip('.')}"
            stdout_file_path = os.path.abspath("temp/" + stdout_filename)
            
            with open(stdout_file_path, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            
            logger.info(f"Stdout saved to {stdout_file_path}")
        
        # Prepare response
        response = f"Script executed successfully.\n"
        if stdout_file_path:
            response += f"Stdout saved to: {stdout_file_path}\n"
        else:
            response += "No stdout output to save.\n"
            
        if result.stderr:
            response += f"STDERR:\n{result.stderr}\n"
        if result.returncode != 0:
            response += f"Exit code: {result.returncode}\n"
            
        return response
        
    except subprocess.TimeoutExpired:
        logger.error("Error: Script execution timed out (60 seconds)")
        return "Error: Script execution timed out (60 seconds)"
    except Exception as e:
        logger.error(f"Error in execute_python_file: {str(e)}")
        return f"Error executing script file: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")