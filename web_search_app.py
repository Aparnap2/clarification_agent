import streamlit as st
import asyncio
import json
import yaml
import logging
import httpx
from datetime import datetime
from typing import List, Dict, Any, Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from clarification_agent.core.conversation_agent import ConversationAgent
from web_search_config import WebSearchConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('web_search_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="🧠 Enhanced Clarification Agent with Web Search",
    page_icon="🧠",
    layout="wide"
)

class WebSearchTool:
    """Web search tool using httpx and crawl4ai"""
    
    def __init__(self):
        self.config = WebSearchConfig()
        self.search_history = []
        
        # Setup environment for crawl4ai
        self.config.setup_environment()
        
    async def search_web(self, query: str, engine: str = "duckduckgo", max_results: int = 5) -> Dict[str, Any]:
        """
        Search the web using specified search engine and crawl results
        
        Args:
            query: Search query
            engine: Search engine to use
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary containing search results and citations
        """
        logger.info(f"Starting web search for query: '{query}' using {engine}")
        
        try:
            # Prepare search URL
            search_url = self.config.get_search_engine_url(engine)
            full_url = search_url + query.replace(" ", "+")
            
            # Configure browser for crawling
            browser_conf = BrowserConfig(headless=True)
            run_conf = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
            
            # Search results container
            results = {
                "query": query,
                "engine": engine,
                "timestamp": datetime.now().isoformat(),
                "results": [],
                "citations": [],
                "summary": ""
            }
            
            async with AsyncWebCrawler(config=browser_conf) as crawler:
                # Crawl search results page
                logger.info(f"Crawling search results from: {full_url}")
                search_result = await crawler.arun(url=full_url, config=run_conf)
                
                if search_result and search_result.markdown:
                    # Extract search result links using CSS extraction
                    schema = {
                        "name": "Search Results",
                        "baseSelector": "a[href*='http']",
                        "fields": [
                            {"name": "title", "selector": "", "type": "text"},
                            {"name": "url", "selector": "", "type": "attribute", "attribute": "href"},
                            {"name": "snippet", "selector": "", "type": "text"}
                        ]
                    }
                    
                    # Extract URLs from markdown content
                    urls = self._extract_urls_from_markdown(search_result.markdown)
                    
                    # Crawl individual result pages
                    for i, url in enumerate(urls[:max_results]):
                        if self._is_valid_url(url):
                            try:
                                logger.info(f"Crawling result {i+1}: {url}")
                                page_result = await crawler.arun(url=url, config=run_conf)
                                
                                if page_result and page_result.markdown:
                                    # Extract relevant content
                                    content_summary = self._extract_content_summary(page_result.markdown)
                                    
                                    result_item = {
                                        "title": self._extract_title(page_result.markdown),
                                        "url": url,
                                        "content": content_summary,
                                        "timestamp": datetime.now().isoformat()
                                    }
                                    
                                    results["results"].append(result_item)
                                    
                                    # Add citation
                                    citation = f"[{i+1}] {result_item['title']} - {url}"
                                    results["citations"].append(citation)
                                    
                            except Exception as e:
                                logger.error(f"Error crawling {url}: {str(e)}")
                                continue
                
                # Generate summary of all results
                if results["results"]:
                    results["summary"] = self._generate_search_summary(results["results"], query)
                
                # Add to search history
                self.search_history.append(results)
                logger.info(f"Search completed. Found {len(results['results'])} results")
                
                return results
                
        except Exception as e:
            logger.error(f"Error in web search: {str(e)}")
            return {
                "query": query,
                "engine": engine,
                "error": str(e),
                "results": [],
                "citations": [],
                "summary": f"Error occurred during search: {str(e)}"
            }
    
    def _extract_urls_from_markdown(self, markdown_content: str) -> List[str]:
        """Extract URLs from markdown content"""
        import re
        
        # Pattern to match URLs in markdown
        url_pattern = r'https?://[^\s\)]+(?:\([^\)]*\))?[^\s\.,;!?]*'
        urls = re.findall(url_pattern, markdown_content)
        
        # Filter out search engine URLs and common non-content URLs
        filtered_urls = []
        exclude_domains = ['google.com', 'bing.com', 'duckduckgo.com', 'facebook.com', 'twitter.com', 'youtube.com']
        
        for url in urls:
            if not any(domain in url for domain in exclude_domains):
                filtered_urls.append(url)
        
        return list(set(filtered_urls))  # Remove duplicates
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and accessible"""
        try:
            return url.startswith(('http://', 'https://')) and len(url) > 10
        except:
            return False
    
    def _extract_title(self, markdown_content: str) -> str:
        """Extract title from markdown content"""
        lines = markdown_content.split('\n')
        for line in lines:
            if line.strip().startswith('# '):
                return line.strip()[2:]
        return "Untitled"
    
    def _extract_content_summary(self, markdown_content: str, max_length: int = 500) -> str:
        """Extract a summary of the content"""
        # Remove markdown formatting
        import re
        clean_content = re.sub(r'[#*`\[\]()]', '', markdown_content)
        
        # Get first few paragraphs
        paragraphs = [p.strip() for p in clean_content.split('\n\n') if p.strip()]
        
        summary = ""
        for paragraph in paragraphs[:3]:  # Take first 3 paragraphs
            if len(summary + paragraph) < max_length:
                summary += paragraph + " "
            else:
                break
        
        return summary.strip()[:max_length] + "..." if len(summary) > max_length else summary.strip()
    
    def _generate_search_summary(self, results: List[Dict], query: str) -> str:
        """Generate a summary of search results"""
        if not results:
            return "No results found."
        
        summary = f"Found {len(results)} relevant results for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            summary += f"{i}. **{result['title']}**\n"
            summary += f"   {result['content'][:200]}...\n\n"
        
        return summary

class EnhancedConversationAgent(ConversationAgent):
    """Enhanced conversation agent with web search capabilities"""
    
    def __init__(self, project_name: str, project_data: Optional[Dict[str, Any]] = None):
        super().__init__(project_name, project_data)
        self.web_search = WebSearchTool()
        self.search_context = []
    
    async def process_user_input_with_search(self, user_input: str, enable_search: bool = True) -> tuple:
        """
        Process user input with optional web search enhancement
        
        Args:
            user_input: User's input text
            enable_search: Whether to enable web search
            
        Returns:
            Tuple of (agent response, is_complete, search_results)
        """
        search_results = None
        
        # Check if user input suggests need for web search
        if enable_search and self._should_search(user_input):
            search_query = self._extract_search_query(user_input)
            if search_query:
                logger.info(f"Performing web search for: {search_query}")
                search_results = await self.web_search.search_web(search_query)
                self.search_context.append(search_results)
        
        # Process with original agent logic
        response, is_complete = self.process_user_input(user_input)
        
        # Enhance response with search results if available
        if search_results and search_results.get("results"):
            enhanced_response = self._enhance_response_with_search(response, search_results)
            return enhanced_response, is_complete, search_results
        
        return response, is_complete, search_results
    
    def _should_search(self, user_input: str) -> bool:
        """Determine if web search should be performed"""
        return WebSearchConfig.should_trigger_search(user_input)
    
    def _extract_search_query(self, user_input: str) -> str:
        """Extract search query from user input"""
        # Simple extraction - could be enhanced with NLP
        query = user_input.strip()
        
        # Remove common conversational words
        remove_words = ["can you", "please", "help me", "i want to", "i need"]
        for word in remove_words:
            query = query.replace(word, "").strip()
        
        return query
    
    def _enhance_response_with_search(self, original_response: str, search_results: Dict) -> str:
        """Enhance agent response with search results"""
        if not search_results.get("results"):
            return original_response
        
        enhanced = original_response + "\n\n"
        enhanced += "🔍 **Web Search Results:**\n\n"
        enhanced += search_results.get("summary", "")
        enhanced += "\n\n**Sources:**\n"
        
        for citation in search_results.get("citations", []):
            enhanced += f"- {citation}\n"
        
        return enhanced

def load_project_data(project_name):
    """Load project data from .clarity folder if it exists"""
    import os
    clarity_path = os.path.join(".clarity", f"{project_name}.json")
    if os.path.exists(clarity_path):
        with open(clarity_path, "r") as f:
            return json.load(f)
    return None

async def main():
    st.title("🧠 Enhanced Clarification Agent with Web Search")
    st.write("AI-powered project clarification with real-time web search capabilities.")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent" not in st.session_state:
        st.session_state.agent = None
        st.session_state.project_name = None
        st.session_state.complete = False
        st.session_state.search_history = []
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # Web search settings
        st.subheader("Web Search Settings")
        enable_search = st.checkbox("Enable Web Search", value=True)
        search_engine = st.selectbox("Search Engine", ["duckduckgo", "bing", "google"])
        max_results = st.slider("Max Search Results", 1, 10, 5)
        
        st.divider()
        
        # Project settings
        st.header("📁 Project")
        project_action = st.radio("Choose an action:", ["Create New Project", "Load Existing Project"])
        
        if project_action == "Create New Project":
            project_name = st.text_input("Project Name:")
            if st.button("Start New Project") and project_name:
                # Initialize new enhanced conversation agent
                st.session_state.agent = EnhancedConversationAgent(project_name=project_name)
                st.session_state.project_name = project_name
                st.session_state.messages = []
                st.session_state.complete = False
                st.session_state.search_history = []
                
                # Get initial message from agent
                initial_message, _ = st.session_state.agent.process_user_input("")
                st.session_state.messages.append({"role": "assistant", "content": initial_message})
                st.rerun()
        else:
            # List existing projects from .clarity folder
            import os
            if os.path.exists(".clarity"):
                projects = [f.replace(".json", "") for f in os.listdir(".clarity") if f.endswith(".json")]
                if projects:
                    selected_project = st.selectbox("Select a project:", projects)
                    if st.button("Load Project"):
                        project_data = load_project_data(selected_project)
                        st.session_state.agent = EnhancedConversationAgent(
                            project_name=selected_project,
                            project_data=project_data
                        )
                        st.session_state.project_name = selected_project
                        st.session_state.messages = []
                        st.session_state.complete = False
                        st.session_state.search_history = []
                        
                        # Get initial message from agent
                        initial_message, _ = st.session_state.agent.process_user_input("")
                        st.session_state.messages.append({"role": "assistant", "content": initial_message})
                        st.rerun()
                else:
                    st.info("No existing projects found.")
            else:
                st.info("No existing projects found.")
        
        # Display current project info
        if st.session_state.project_name:
            st.divider()
            st.subheader(f"📊 Project: {st.session_state.project_name}")
            
            if st.session_state.complete:
                st.success("✅ Project planning complete!")
                if st.button("📄 View Generated Files"):
                    st.markdown("### Generated Files")
                    st.markdown("- README.md")
                    st.markdown("- .plan.yml")
                    st.markdown("- architecture.md")
                    st.markdown("- .clarity/*.json")
            
            # Search history
            if st.session_state.search_history:
                st.divider()
                st.subheader("🔍 Search History")
                for i, search in enumerate(reversed(st.session_state.search_history[-5:])):  # Show last 5 searches
                    with st.expander(f"Search {len(st.session_state.search_history) - i}: {search.get('query', 'Unknown')}"):
                        st.write(f"**Engine:** {search.get('engine', 'Unknown')}")
                        st.write(f"**Results:** {len(search.get('results', []))}")
                        st.write(f"**Time:** {search.get('timestamp', 'Unknown')}")
    
    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💬 Conversation")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if st.session_state.agent and not st.session_state.complete:
            user_input = st.chat_input("Type your response here...")
            if user_input:
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # Get agent response with search
                with st.spinner("🤔 Thinking and searching..."):
                    try:
                        # Use asyncio to run the async method
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        agent_response, is_complete, search_results = loop.run_until_complete(
                            st.session_state.agent.process_user_input_with_search(
                                user_input, 
                                enable_search=enable_search
                            )
                        )
                        
                        st.session_state.messages.append({"role": "assistant", "content": agent_response})
                        st.session_state.complete = is_complete
                        
                        # Add search results to history
                        if search_results:
                            st.session_state.search_history.append(search_results)
                        
                        loop.close()
                        
                    except Exception as e:
                        logger.error(f"Error processing user input: {str(e)}")
                        st.error(f"An error occurred: {str(e)}")
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "I'm sorry, I encountered an error. Let's continue with the next step."
                        })
                
                st.rerun()
        elif not st.session_state.agent:
            st.info("👈 Create or load a project to start the conversation.")
    
    with col2:
        st.subheader("🔍 Search Results")
        
        if st.session_state.search_history:
            latest_search = st.session_state.search_history[-1]
            
            st.write(f"**Latest Query:** {latest_search.get('query', 'N/A')}")
            st.write(f"**Engine:** {latest_search.get('engine', 'N/A')}")
            st.write(f"**Results Found:** {len(latest_search.get('results', []))}")
            
            if latest_search.get("results"):
                st.divider()
                st.subheader("📄 Sources")
                
                for i, result in enumerate(latest_search["results"], 1):
                    with st.expander(f"{i}. {result.get('title', 'Untitled')}"):
                        st.write(f"**URL:** {result.get('url', 'N/A')}")
                        st.write(f"**Content:** {result.get('content', 'No content available')}")
                        
                        if st.button(f"🔗 Visit Source {i}", key=f"visit_{i}"):
                            st.write(f"Opening: {result.get('url', 'N/A')}")
            
            # Manual search option
            st.divider()
            st.subheader("🔍 Manual Search")
            manual_query = st.text_input("Search Query:")
            
            if st.button("Search") and manual_query:
                with st.spinner("Searching..."):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        search_tool = WebSearchTool()
                        search_results = loop.run_until_complete(
                            search_tool.search_web(manual_query, engine=search_engine, max_results=max_results)
                        )
                        
                        st.session_state.search_history.append(search_results)
                        loop.close()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Search error: {str(e)}")
        else:
            st.info("No search results yet. Start a conversation to see web search results here.")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())