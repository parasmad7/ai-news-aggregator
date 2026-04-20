import requests
from bs4 import BeautifulSoup
from typing import List, Dict

def search_the_web(query: str) -> str:
    """
    Searches DuckDuckGo for a query and returns the top results.
    Use this to find context about news items or recent AI developments.
    """
    print(f"\n[Tool: Search] Querying DuckDuckGo: {query}...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # DuckDuckGo HTML version is easier to scrape than the JS version
    url = f"https://duckduckgo.com/html/?q={query}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return f"Error: Search failed with status code {response.status_code}"
            
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        # Search for results in the 'result' class
        for result in soup.find_all('div', class_='result', limit=5):
            title_tag = result.find('a', class_='result__a')
            snippet_tag = result.find('a', class_='result__snippet')
            
            if title_tag and snippet_tag:
                results.append(f"Title: {title_tag.text}\nSource: {title_tag['href']}\nSnippet: {snippet_tag.text}\n")
        
        if not results:
            return "No search results found."
            
        return "\n---\n".join(results)
        
    except Exception as e:
        return f"Error during search: {e}"

if __name__ == "__main__":
    # Test
    print(search_the_web("latest AI news today"))
