from mcp.server.fastmcp import FastMCP
import os
import uuid
from dotenv import load_dotenv
from crawl4ai import AsyncWebCrawler
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
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url)
            
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
async def execute_python_script_from_file(script_path_file: str, input: str = None) -> str:
    """
    Execute a Python script file with optional stdin input.
    
    Args:
        script_path_file: The absolute path to the Python script file to execute
        input: Optional string input to pass to the script via stdin
        
    Returns:
        The output from executing the script (stdout and stderr)
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
        
        # Combine stdout and stderr
        output = ""
        if result.stdout:
            output += f"\n{result.stdout}\n"
        if result.stderr:
            output += f"STDERR:\n{result.stderr}\n"
        if result.returncode != 0:
            output += f"Exit code: {result.returncode}\n"
        return output if output else "Script executed successfully with no output."
        
    except subprocess.TimeoutExpired:
        logger.error("Error: Script execution timed out (60 seconds)")
        return "Error: Script execution timed out (60 seconds)"
    except Exception as e:
        logger.error(f"Error in execute_python_file: {str(e)}")
        return f"Error executing script file: {str(e)}"

# @mcp.tool()
# async def execute_python_script(script: str, input: str = None) -> str:
#     logger.info(f"Starting execute_python_script with input: {input}")
#     import subprocess
#     import sys
#     import tempfile
    
#     try:
#         # Create a temporary file to store the script
#         with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
#             temp_file.write(script)
#             temp_file_path = temp_file.name
        
#         logger.info(f"Executing script stored at {temp_file_path}")
#         # Execute the script using subprocess
#         result = subprocess.run(
#             [sys.executable, temp_file_path],
#             input=input,
#             capture_output=True,
#             text=True,
#             timeout=60  # 60 second timeout for safety
#         )
        
#         # Clean up the temporary file
#         os.unlink(temp_file_path)
#         logger.info("Script executed successfully")
        
#         # Combine stdout and stderr
#         output = ""
#         if result.stdout:
#             output += f"\n{result.stdout}\n"
#         if result.stderr:
#             output += f"STDERR:\n{result.stderr}\n"
#         if result.returncode != 0:
#             output += f"Exit code: {result.returncode}\n"
#         return output if output else "Script executed successfully with no output."
        
#     except subprocess.TimeoutExpired:
#         # Clean up the temporary file if timeout occurs
#         try:
#             os.unlink(temp_file_path)
#         except:
#             pass
#         logger.error("Error: Script execution timed out (60 seconds)")
#         return "Error: Script execution timed out (60 seconds)"
#     except Exception as e:
#         # Clean up the temporary file if error occurs
#         try:
#             os.unlink(temp_file_path)
#         except:
#             pass
#         logger.error(f"Error in execute_python_script: {str(e)}")
#         return f"Error executing script: {str(e)}"

    
# @mcp.tool()
# async def execute_python_script_with_file_input(script: str, file_path: str) -> str:
#     """
#     Execute a Python script using the content of a file as stdin input.
    
#     Args:
#         script: The Python script code to execute
#         file_path: Path to the file whose content will be used as stdin input
        
#     Returns:
#         The output from executing the script (stdout and stderr)
#     """
#     import subprocess
#     import sys
#     import tempfile
    
#     try:
#         # Read the input file content
#         if not os.path.exists(file_path):
#             return f"Error: Input file '{file_path}' does not exist"
        
#         with open(file_path, 'r', encoding='utf-8') as f:
#             file_content = f.read()
        
#         # Create a temporary file to store the script
#         with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
#             temp_file.write(script)
#             temp_file_path = temp_file.name
        
#         # Execute the script using subprocess with file content as stdin
#         result = subprocess.run(
#             [sys.executable, temp_file_path],
#             input=file_content,
#             capture_output=True,
#             text=True,
#             timeout=30  # 30 second timeout for safety
#         )
        
#         # Clean up the temporary file
#         os.unlink(temp_file_path)
        
#         # Combine stdout and stderr
#         output = ""
#         if result.stdout:
#             output += f"Success STDOUT:\n{result.stdout}\n"
#         if result.stderr:
#             output += f"STDERR:\n{result.stderr}\n"
#         if result.returncode != 0:
#             output += f"Exit code: {result.returncode}\n"
#         return output if output else "Script executed successfully with no output."
        
#     except subprocess.TimeoutExpired:
#         # Clean up the temporary file if timeout occurs
#         try:
#             os.unlink(temp_file_path)
#         except:
#             pass
#         return "Error: Script execution timed out (30 seconds)"
#     except Exception as e:
#         # Clean up the temporary file if error occurs
#         try:
#             os.unlink(temp_file_path)
#         except:
#             pass
#         return f"Error executing script: {str(e)}"


# @mcp.tool()
# async def scrape_url(url: str) -> str:
#     """
#     Scrape a webpage and return its content.
    
#     Args:
#         url: The URL of the webpage to scrape
        
#     Returns:
#         The webpage content in cleaned html format
#     """
#     try:
#         async with AsyncWebCrawler() as crawler:
#             result = await crawler.arun(url=url)
#             return result.cleaned_html
#     except Exception as e:
#         return f"Error scraping URL: {str(e)}"

# @mcp.prompt()
# def greet_user_prompt(name: str) -> str:
#     """Generates a message asking for a greeting"""
#     return f"""
#     Return a greeting message for a user called '{name}'. 
#     if the user is called 'Laurent', use a formal style, else use a street style.
#     """


if __name__ == "__main__":
    mcp.run(transport="stdio")