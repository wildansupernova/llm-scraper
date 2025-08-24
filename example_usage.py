#!/usr/bin/env python3
"""
Example usage of the MCPClient class with session management.
This demonstrates how to use the client for multi-turn conversations
while maintaining context between queries.
"""

import asyncio
from mcp_client_scraper import MCPClient


async def example_with_session():
    """Example of using MCPClient with session management."""
    
    # Create the MCP client
    client = MCPClient(model_type="openai", temperature=0)
    
    print("=== Starting Multi-turn Session Example ===\n")
    
    # First query - scrape some data
    first_query = """
    From the URL (https://medrecruit.medworld.com/jobs/list?location=New+South+Wales&page=1), 
    scrape the first page and identify the structure of job listings.
    """
    
    print("First Query:")
    print(first_query)
    print("\n" + "="*50 + "\n")
    
    result1 = await client.invoke_query(first_query)
    session_id = result1.get("session_id")
    
    print("First Response:")
    print(f"Session ID: {session_id}")
    print(f"Text: {result1.get('text', 'No text')}")
    print(f"Summary: {result1.get('summary', 'No summary')}")
    print("\n" + "="*50 + "\n")
    
    # Second query - use the same session to continue
    # second_query = """
    # Now scrape pages 2 and 3 using the same structure you identified earlier.
    # Extract role, specialty, location, and pay information from all three pages.
    # """
    
    # print("Second Query (same session):")
    # print(second_query)
    # print("\n" + "="*50 + "\n")
    
    # result2 = await client.invoke_query(second_query, session_id=session_id)
    
    # print("Second Response:")
    # print(f"Session ID: {result2.get('session_id')}")
    # print(f"Text: {result2.get('text', 'No text')}")
    # print(f"Results: {result2.get('results', 'No results')}")
    # print(f"Summary: {result2.get('summary', 'No summary')}")


async def example_multiple_sessions():
    """Example of managing multiple independent sessions."""
    
    client = MCPClient()
    
    print("=== Multiple Sessions Example ===\n")
    
    # Session 1 - Job scraping
    result1 = await client.invoke_query(
        "Scrape job listings from https://example-jobs.com",
        session_id="job_session"
    )
    
    # Session 2 - Product scraping 
    result2 = await client.invoke_query(
        "Scrape product information from https://example-products.com",
        session_id="product_session"
    )
    
    print("Active sessions:")
    for session_id, summary in client.get_all_sessions().items():
        print(f"- {session_id}: {summary}")


def main():
    """Main function to run examples."""
    print("MCPClient Session Management Examples")
    print("="*40)
    
    # Run the session example
    asyncio.run(example_with_session())
    
    # Uncomment to run multiple sessions example
    # asyncio.run(example_multiple_sessions())


if __name__ == "__main__":
    main()
