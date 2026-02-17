"""
WebSearchTool - Searches the web using DuckDuckGo

LEARNING POINTS:
- Uses DuckDuckGo (no API key required!)
- HTML parsing with BeautifulSoup
- Async HTTP requests with aiohttp
- Error handling for network issues
- Returns top N results with title, snippet, and URL

NOTE: For production, consider paid APIs (Google, Bing) for better results.
      DuckDuckGo is great for learning since it's free and needs no setup!
"""

import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import quote_plus
from src.core.base_tool import BaseTool


class WebSearchTool(BaseTool):
    """
    A tool that searches the web using DuckDuckGo.
    
    Why DuckDuckGo?
    - No API key required (perfect for learning!)
    - No rate limits for reasonable use
    - Privacy-focused
    - Good enough results for agent tasks
    
    How it works:
    1. Constructs DuckDuckGo search URL
    2. Fetches HTML results page
    3. Parses results with BeautifulSoup
    4. Returns structured data
    """
    
    def __init__(self, max_results: int = 5):
        """
        Initialize the web search tool.
        
        Args:
            max_results: Maximum number of search results to return
        """
        self.max_results = max_results
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return f"Searches the web using DuckDuckGo and returns up to {self.max_results} results"
    
    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": f"Maximum number of results (default: {self.max_results})"
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, params: dict) -> List[Dict[str, str]]:
        """
        Perform a web search and return results.
        
        Args:
            params: Dict with "query" and optional "max_results"
            
        Returns:
            List of dicts, each containing:
            - title: Page title
            - snippet: Brief description
            - url: Link to the page
        """
        query = params.get("query")
        max_results = params.get("max_results", self.max_results)
        
        if not query:
            raise ValueError("query parameter is required")
        
        try:
            # URL encode the query (spaces become %20, etc.)
            encoded_query = quote_plus(query)
            
            # Construct DuckDuckGo search URL
            # html version is easier to parse than lite version
            url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
            
            # Make async HTTP request
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    # Check if request was successful
                    if response.status != 200:
                        raise Exception(f"Search failed with status {response.status}")
                    
                    # Get HTML content
                    html = await response.text()
            
            # Parse results
            results = self._parse_results(html, max_results)
            
            return results
            
        except aiohttp.ClientError as e:
            raise Exception(f"Network error during search: {str(e)}")
        except Exception as e:
            raise Exception(f"Error searching web: {str(e)}")
    
    def _parse_results(self, html: str, max_results: int) -> List[Dict[str, str]]:
        """
        Parse DuckDuckGo HTML to extract search results.
        
        This is a helper method that uses BeautifulSoup to:
        1. Find result divs
        2. Extract title, snippet, and URL
        3. Return structured data
        
        Args:
            html: Raw HTML from DuckDuckGo
            max_results: How many results to return
            
        Returns:
            List of result dicts
        """
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find all result divs (DuckDuckGo's HTML structure)
        # Class names may change - this is a simple implementation
        result_divs = soup.find_all('div', class_='result', limit=max_results)
        
        for div in result_divs:
            try:
                # Extract title (in <a> tag with class 'result__a')
                title_tag = div.find('a', class_='result__a')
                title = title_tag.get_text(strip=True) if title_tag else "No title"
                url = title_tag.get('href', '') if title_tag else ''
                
                # Extract snippet (in <a> tag with class 'result__snippet')
                snippet_tag = div.find('a', class_='result__snippet')
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else "No description"
                
                # Only add if we got a URL
                if url:
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": url
                    })
                    
            except Exception:
                # Skip malformed results
                continue
        
        return results


# LEARNING QUESTIONS:
# Q1: Why use aiohttp instead of requests library?
# A1: requests is synchronous - blocks the event loop while waiting for response
#     aiohttp is async - allows other operations while waiting
#     Essential for responsive multi-agent systems

# Q2: What does quote_plus() do?
# A2: URL encodes the query string:
#     "python async" → "python+async"
#     "café" → "caf%C3%A9"
#     Ensures special characters work in URLs

# Q3: Why use BeautifulSoup instead of regex?
# A3: HTML is complex and irregular - regex is fragile
#     BeautifulSoup handles malformed HTML gracefully
#     Much easier to maintain and understand

# Q4: Why limit results in find_all()?
# A4: Performance - don't parse more than needed
#     Memory efficiency - large pages have many results
#     User experience - agents don't need 100 results

# Q5: Why is _parse_results not async?
# A5: It's pure computation (parsing text), no I/O
#     No benefit from async since it doesn't wait for anything
#     Simpler as a regular function
