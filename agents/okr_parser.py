import os
from dotenv import load_dotenv

from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from prompts.okr_parser_prompt import OKR_PARSER_TEMPLATE

from tools.linkedin_scraper_tool import scrape_linkedin_article

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

prompt =PromptTemplate(template=OKR_PARSER_TEMPLATE, input_variables=["article_text"])
 

# Gemini LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0)

# Output parser
parser = JsonOutputParser()

# Define LLM chain
chain = LLMChain(llm=llm, prompt=prompt, output_parser=parser)

# Agent function
async def run_parser_agent(state):
    url = state["input_url"]
    scraped = await scrape_linkedin_article(url)

    if "error" in scraped:
        return {"error": scraped["error"]}

    article_text = scraped["text"]
    result = chain.run(article_text=article_text)

    return {
        "parsed_okr": result,
        "metadata": scraped["metadata"],
        "title": scraped["metadata"].get("title")  
    }
