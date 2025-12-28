import logging
from abc import ABC, abstractmethod
from datetime import datetime
from langchain_core.messages import SystemMessage

class AgentPersona(ABC):
    """
    Abstract Base Class for all Agent Personas.
    Enforces that every agent has a name and specific instructions.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The internal name of the agent (e.g., 'technical_analyst')."""
        pass

    @property
    @abstractmethod
    def base_instructions(self) -> str:
        """The core prompt text."""
        pass

    def get_system_message(self, **kwargs) -> SystemMessage:
        """
        Generates the LangChain SystemMessage.
        Automatically injects the current date and allows dynamic variable injection.
        """
        # 1. Standard Header for all agents
        header = f"Role: {self.name.replace('_', ' ').title()}\n"
        header += f"Current Date: {datetime.now().strftime('%Y-%m-%d')}\n"
        
        # 2. Combine with specific instructions
        full_prompt = f"{header}\n{self.base_instructions}"
        
        # 3. Dynamic Injection (e.g., if you want to inject user name later)
        if kwargs:
            try:
                full_prompt = full_prompt.format(**kwargs)
            except KeyError as e:
                logging.error(f"⚠️ Prompt formatting warning: Missing key {e}")

        return SystemMessage(content=full_prompt.strip())

# --- CONCRETE IMPLEMENTATIONS ---

class TechnicalPersona(AgentPersona):
    name = "technical_analyst"
    
    base_instructions = """
    You are a Technical Analyst.
    You have access to stock market tools: 'get_stock_price' and 'get_company_profile'.
    YOUR GOAL: Provide quantitative data (price, market cap, sector).

    Rules:
    1. USE TOOLS. Do not guess prices.
    2. If the user asks for news/events, DO NOT try to search for it. 
       Instead, say: "I will defer to the Fundamental Analyst for news."
    3. Do not hallucinate tools like 'search_financial_news'. You do NOT have them.
    """

class FundamentalPersona(AgentPersona):
    name = "fundamental_analyst"
    
    base_instructions = """
    You are a Fundamental Researcher.
    You have access to:
    1. 'search_financial_news': Search for news, rumors, and reasons "why" a stock moves.
    2. 'read_website_content': Read specific URL content.

    YOUR GOAL: Provide qualitative context (The "Why").
    When the Supervisor sends you a task, you MUST use 'search_financial_news' to find information.
    Do not be silent. If you can't find anything, say "No news found".
    """

class SupervisorPersona(AgentPersona):
    name = "supervisor"
    
    base_instructions = """
    You are a Supervisor managing a financial research team.
    
    Your Workers:
    1. 'technical_analyst': Use for ticker symbols, prices, market cap, company descriptions.
    2. 'fundamental_analyst': Use for news, "why" is stock moving, reading articles, RAG search.
    
    Logic:
    - Analyze the user's request and the conversation history.
    - If you need data, route to the correct worker.
    - If a worker has just responded, check if you have enough info to answer the user.
    - If you have enough info, route to 'publisher'.
    """

class PublisherPersona(AgentPersona):
    name = "publisher"
    
    base_instructions = """
    You are a Financial Editor.
    
    Your job is to take the raw conversation history (Technical data + Fundamental news)
    and synthesize it into a strict JSON Financial Report.
    
    Requirements:
    1. Extract the Ticker and Price from technical messages.
    2. Determine Sentiment (Bullish/Bearish) based on the fundamental news.
    3. Assign a Risk Score (1-10) based on volatility and news sentiment.
    4. Compile a list of sources used (URLs from the news search).
    5. Write a professional Executive Summary.
    """