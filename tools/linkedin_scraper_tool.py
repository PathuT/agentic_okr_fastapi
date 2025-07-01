import httpx
from bs4 import BeautifulSoup

async def scrape_linkedin_article(url: str) -> dict:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=10)
            response.raise_for_status()
    except Exception as e:
        return {"error": f"Failed to fetch the URL: {str(e)}"}

    soup = BeautifulSoup(response.text, "html.parser")
    article_text = " ".join([p.text for p in soup.find_all("p")])[:4000]

    metadata = {
        "title": soup.title.string if soup.title else "Unknown",
        "meta_description": soup.find("meta", attrs={"name": "description"})["content"]
        if soup.find("meta", attrs={"name": "description"}) else "None"
    }

    return {"text": article_text, "metadata": metadata}
