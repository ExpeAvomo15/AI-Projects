# backend.py
#Author: Expe Avomo - AI & ML Engineer
import os
import asyncio
import aiohttp
import requests
import numpy as np
from openai import AsyncOpenAI
from agents import Agent, Runner, function_tool, trace, input_guardrail, GuardrailFunctionOutput
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Global cache
embedding_cache = {}
CACHE_EXPIRY_SECONDS = 3600

# Security guardrail
@input_guardrail
async def security_guardrail(ctx, agent, message):
    if not message or len(message.strip()) == 0:
        return GuardrailFunctionOutput(output_info={"reason": "Empty message"}, tripwire_triggered=True)
    
    if len(message) > 500:
        return GuardrailFunctionOutput(output_info={"reason": "Message too long"}, tripwire_triggered=True)
    
    injection_patterns = [r'(?i)ignore.*previous', r'(?i)system.*prompt', r'(?i)role.*play']
    for pattern in injection_patterns:
        if re.search(pattern, message):
            return GuardrailFunctionOutput(output_info={"reason": "Prompt injection"}, tripwire_triggered=True)
    
    return GuardrailFunctionOutput(output_info={"reason": "Valid input"}, tripwire_triggered=False)

# Formatting functions
def format_market_cap(market_cap):
    if not market_cap or market_cap == "None": return "N/A"
    try:
        market_cap_float = float(market_cap)
        if market_cap_float >= 1e12: return f"${market_cap_float/1e12:.2f}T"
        if market_cap_float >= 1e9: return f"${market_cap_float/1e9:.2f}B"
        if market_cap_float >= 1e6: return f"${market_cap_float/1e6:.2f}M"
        return f"${market_cap_float}"
    except:
        return market_cap

def format_percentage(value):
    if not value or value == "None": return "N/A"
    try:
        return f"{float(value)*100:.1f}%"
    except:
        return value

def format_revenue(revenue):
    if not revenue or revenue == "None": return "N/A"
    try:
        revenue_float = float(revenue)
        if revenue_float >= 1e9: return f"${revenue_float/1e9:.1f}B"
        return f"${revenue_float/1e6:.1f}M"
    except:
        return revenue

# Alpha Vantage data function
async def get_alpha_vantage_data(symbol: str):
    try:
        # Get company overview
        overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        overview_response = requests.get(overview_url)
        overview_data = overview_response.json()
        
        # Get current price
        quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        quote_response = requests.get(quote_url)
        quote_data = quote_response.json().get("Global Quote", {})
        
        return {
            "name": overview_data.get("Name", symbol),
            "symbol": overview_data.get("Symbol", symbol),
            "sector": overview_data.get("Sector", "N/A"),
            "industry": overview_data.get("Industry", "N/A"),
            "market_cap": format_market_cap(overview_data.get("MarketCapitalization")),
            "current_price": quote_data.get("05. price", "N/A"),
            "change": quote_data.get("09. change", "N/A"),
            "change_percent": quote_data.get("10. change percent", "N/A"),
            "pe_ratio": overview_data.get("PERatio", "N/A"),
            "profit_margin": format_percentage(overview_data.get("ProfitMargin")),
            "revenue": format_revenue(overview_data.get("RevenueTTM")),
            "employees": overview_data.get("FullTimeEmployees", "N/A"),
            "description": overview_data.get("Description", "No description available"),
            "real_data": True,
            "source": "Alpha Vantage"
        }
    except Exception as e:
        return {"error": str(e), "real_data": False}

async def get_real_time_company_data(symbol: str):
    try:
        alpha_data = await get_alpha_vantage_data(symbol)
        if alpha_data.get("real_data"):
            return alpha_data
            
        return {"error": "No data available from Alpha Vantage", "real_data": False}
    except Exception as e:
        return {"error": str(e), "real_data": False}

# Main Analysis Tool with Markdown formatting
@function_tool
async def analyze_company_tool(symbol: str, analysis_type: str):
    try:
        company_data = await get_real_time_company_data(symbol)
        
        if not company_data.get("real_data"):
            return f"## ❌ Analysis Failed\n\nNo data available for **{symbol}**. \n\n**Error:** {company_data.get('error', 'Unknown')}"
        
        prompt = f"""
        Analyze {company_data['name']} ({symbol}) based on REAL market data from Alpha Vantage.

        ## 📊 Real-time Data
        - **Company**: {company_data['name']}
        - **Current Price**: {company_data.get('current_price', 'N/A')}
        - **Change**: {company_data.get('change', 'N/A')} ({company_data.get('change_percent', 'N/A')})
        - **Market Cap**: {company_data.get('market_cap', 'N/A')}
        - **Sector**: {company_data.get('sector', 'N/A')}
        - **Industry**: {company_data.get('industry', 'N/A')}
        - **P/E Ratio**: {company_data.get('pe_ratio', 'N/A')}
        - **Profit Margin**: {company_data.get('profit_margin', 'N/A')}
        - **Revenue**: {company_data.get('revenue', 'N/A')}
        - **Employees**: {company_data.get('employees', 'N/A')}

        ## 🎯 Analysis Type: {analysis_type.replace('_', ' ').title()}

        Provide a professional analysis in MARKDOWN format with these sections:

        ### ✅ Key Strengths
        - List main competitive advantages
        - Highlight financial strengths
        - Market position and brand value

        ### ⚠️ Potential Risks  
        - Identify key challenges
        - Market and competitive risks
        - Financial vulnerabilities

        ### 📈 Growth Outlook
        - Growth potential and opportunities
        - Industry trends and position
        - Innovation and expansion

        ### 💡 Investment Recommendation
        - Clear buy/hold/sell advice
        - Risk level assessment
        - Time horizon suggestion

        Use **bold** for key metrics and *italic* for emphasis.
        Keep the analysis comprehensive but focused on actionable insights.
        """
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600
        )
        
        analysis = response.choices[0].message.content
        
        return analysis
        
    except Exception as e:
        return f"## ❌ Analysis Error\n\nError during analysis: **{str(e)}**"

# Financial Analyst Agent
financial_analyst_agent = Agent(
    name="FinancialAnalystAI",
    instructions="""
    You are an expert AI financial analyst. Use ONLY the analyze_company_tool.
    Always format responses in MARKDOWN for better readability.
    Use **bold** for important metrics and *italic* for emphasis.
    Include sections with headers using ### and ##.
    Provide comprehensive financial analysis based on real market data.
    Focus on actionable insights and clear recommendations.
    """,
    tools=[analyze_company_tool],
    model="gpt-4o-mini",
    input_guardrails=[security_guardrail]
)

# Main function
async def analyze_company_data(symbol: str, analysis_type: str):
    try:
        with trace("MarketIntelAnalysis"):
            contextual_input = f"Symbol: {symbol}, Analysis Type: {analysis_type}"
            result = await Runner.run(financial_analyst_agent, contextual_input)
            
            real_data = await get_real_time_company_data(symbol)
            
            return {
                "analysis": result.final_output,
                "metrics": {
                    "Current Price": real_data.get('current_price', 'N/A'),
                    "Change": f"{real_data.get('change', 'N/A')} ({real_data.get('change_percent', 'N/A')})",
                    "Market Cap": real_data.get('market_cap', 'N/A'),
                    "P/E Ratio": real_data.get('pe_ratio', 'N/A'),
                    "Profit Margin": real_data.get('profit_margin', 'N/A'),
                    "Sector": real_data.get('sector', 'N/A'),
                    "Employees": real_data.get('employees', 'N/A')
                },
                "recommendation": "Based on Alpha Vantage real-time data",
                "success": True
            }
    except Exception as e:
        return {
            "analysis": f"## ❌ Error\n\nAnalysis failed: **{str(e)}**",
            "metrics": {},
            "recommendation": "Analysis failed",
            "success": False
        }

def get_available_companies():
    return ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NFLX", "NVDA", "JPM", "JNJ"]

if __name__ == "__main__":
    print("✅ MarketIntel AI Backend loaded successfully")
    print("📊 Using Alpha Vantage for real-time financial data")
    print("📝 Markdown formatting enabled")