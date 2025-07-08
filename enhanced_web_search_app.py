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
from agent_activity_logger import AgentActivityLogger, ActivityType, ActivityContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_web_search_app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="🧠 Enhanced Clarification Agent with Activity Logs",
    page_icon="🧠",
    layout="wide"
)

class EnhancedWebSearchTool:
    """Enhanced web search tool with activity logging"""
    
    def __init__(self, activity_logger: AgentActivityLogger):
        self.config = WebSearchConfig()
        self.search_history = []
        self.activity_logger = activity_logger
        
        # Setup environment for crawl4ai
        self.config.setup_environment()
        
    async def search_web(self, query: str, engine: str = "duckduckgo", max_results: int = 5) -> Dict[str, Any]:
        """
        Search the web with detailed activity logging
        """
        with ActivityContext(
            self.activity_logger,
            ActivityType.SEARCH,
            f"🔍 Web Search: {query}",
            f"Initializing search with {engine}"
        ) as activity:
            
            try:
                # Update activity with search preparation
                activity.update(
                    f"Preparing search query for {engine}",
                    {"query": query, "engine": engine, "max_results": max_results}
                )
                
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
                
                activity.update(
                    f"Starting web crawler for search results",
                    {"search_url": full_url}
                )
                
                async with AsyncWebCrawler(config=browser_conf) as crawler:
                    # Crawl search results page
                    logger.info(f"Crawling search results from: {full_url}")
                    
                    # Log crawler activity
                    crawler_id = self.activity_logger.start_activity(
                        ActivityType.TOOL_CALL,
                        "🕷️ Web Crawler",
                        f"Crawling search results page"
                    )
                    
                    search_result = await crawler.arun(url=full_url, config=run_conf)
                    
                    self.activity_logger.complete_activity(
                        crawler_id,
                        f"Search results page crawled successfully",
                        {"content_length": len(search_result.markdown) if search_result.markdown else 0}
                    )
                    
                    if search_result and search_result.markdown:
                        # Extract URLs from markdown content
                        urls = self._extract_urls_from_markdown(search_result.markdown)
                        
                        activity.update(
                            f"Found {len(urls)} potential result URLs",
                            {"urls_found": len(urls)}
                        )
                        
                        # Crawl individual result pages
                        for i, url in enumerate(urls[:max_results]):
                            if self._is_valid_url(url):
                                try:
                                    # Log individual page crawling
                                    page_id = self.activity_logger.start_activity(
                                        ActivityType.TOOL_CALL,
                                        f"📄 Page Crawler #{i+1}",
                                        f"Crawling: {url[:50]}..."
                                    )
                                    
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
                                        
                                        self.activity_logger.complete_activity(
                                            page_id,
                                            f"Page crawled: {result_item['title']}",
                                            {
                                                "title": result_item['title'],
                                                "content_length": len(content_summary),
                                                "url": url
                                            }
                                        )
                                    else:
                                        self.activity_logger.fail_activity(
                                            page_id,
                                            "No content extracted from page"
                                        )
                                        
                                except Exception as e:
                                    logger.error(f"Error crawling {url}: {str(e)}")
                                    self.activity_logger.fail_activity(
                                        page_id,
                                        f"Crawling failed: {str(e)}"
                                    )
                                    continue
                    
                    # Generate summary of all results
                    if results["results"]:
                        summary_id = self.activity_logger.start_activity(
                            ActivityType.ANALYSIS,
                            "📊 Results Analysis",
                            "Generating search results summary"
                        )
                        
                        results["summary"] = self._generate_search_summary(results["results"], query)
                        
                        self.activity_logger.complete_activity(
                            summary_id,
                            f"Summary generated for {len(results['results'])} results"
                        )
                    
                    # Add to search history
                    self.search_history.append(results)
                    logger.info(f"Search completed. Found {len(results['results'])} results")
                    
                    activity.update(
                        f"Search completed successfully",
                        {
                            "results_count": len(results['results']),
                            "citations_count": len(results['citations'])
                        }
                    )
                    
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

class SuperEnhancedConversationAgent(ConversationAgent):
    """Enhanced conversation agent with detailed activity logging"""
    
    def __init__(self, project_name: str, project_data: Optional[Dict[str, Any]] = None):
        super().__init__(project_name, project_data)
        self.activity_logger = AgentActivityLogger()
        self.web_search = EnhancedWebSearchTool(self.activity_logger)
        self.search_context = []
    
    async def process_user_input_with_logging(self, user_input: str, enable_search: bool = True) -> tuple:
        """
        Process user input with comprehensive activity logging
        """
        with ActivityContext(
            self.activity_logger,
            ActivityType.THINKING,
            "🤔 Processing User Input",
            f"Analyzing user message: '{user_input[:50]}...'"
        ) as main_activity:
            
            search_results = None
            
            # Check if user input suggests need for web search
            if enable_search and self._should_search(user_input):
                main_activity.update(
                    "Search trigger detected, preparing web search",
                    {"search_triggers": True}
                )
                
                search_query = self._extract_search_query(user_input)
                if search_query:
                    logger.info(f"Performing web search for: {search_query}")
                    search_results = await self.web_search.search_web(search_query)
                    self.search_context.append(search_results)
            
            # Log LLM processing
            llm_id = self.activity_logger.start_activity(
                ActivityType.GENERATION,
                "🧠 LLM Processing",
                "Generating response using language model"
            )
            
            try:
                # Process with original agent logic
                response, is_complete = self.process_user_input(user_input)
                
                self.activity_logger.complete_activity(
                    llm_id,
                    "Response generated successfully",
                    {
                        "response_length": len(response),
                        "conversation_complete": is_complete
                    }
                )
                
                # Enhance response with search results if available
                if search_results and search_results.get("results"):
                    enhancement_id = self.activity_logger.start_activity(
                        ActivityType.ANALYSIS,
                        "🔗 Response Enhancement",
                        "Integrating search results with agent response"
                    )
                    
                    enhanced_response = self._enhance_response_with_search(response, search_results)
                    
                    self.activity_logger.complete_activity(
                        enhancement_id,
                        f"Response enhanced with {len(search_results['results'])} search results"
                    )
                    
                    main_activity.update(
                        "Processing completed with search enhancement",
                        {
                            "search_results_count": len(search_results['results']),
                            "response_enhanced": True
                        }
                    )
                    
                    return enhanced_response, is_complete, search_results
                
                main_activity.update(
                    "Processing completed successfully",
                    {"search_performed": search_results is not None}
                )
                
                return response, is_complete, search_results
                
            except Exception as e:
                self.activity_logger.fail_activity(
                    llm_id,
                    f"LLM processing failed: {str(e)}"
                )
                raise
    
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
    st.title("🧠 Enhanced Clarification Agent with Beautiful Activity Logs")
    st.write("AI-powered project clarification with real-time activity tracking and web search.")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "agent" not in st.session_state:
        st.session_state.agent = None
        st.session_state.project_name = None
        st.session_state.complete = False
        st.session_state.search_history = []
    
    # Initialize activity logger
    if "activity_logger" not in st.session_state:
        st.session_state.activity_logger = AgentActivityLogger()
    
    # Create layout
    col1, col2, col3 = st.columns([2, 1, 1])
    
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
                st.session_state.agent = SuperEnhancedConversationAgent(project_name=project_name)
                st.session_state.project_name = project_name
                st.session_state.messages = []
                st.session_state.complete = False
                st.session_state.search_history = []
                
                # Clear activity logs for new project
                st.session_state.activity_logger.clear_logs()
                
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
                        st.session_state.agent = SuperEnhancedConversationAgent(
                            project_name=selected_project,
                            project_data=project_data
                        )
                        st.session_state.project_name = selected_project
                        st.session_state.messages = []
                        st.session_state.complete = False
                        st.session_state.search_history = []
                        
                        # Clear activity logs for loaded project
                        st.session_state.activity_logger.clear_logs()
                        
                        # Get initial message from agent
                        initial_message, _ = st.session_state.agent.process_user_input("")
                        st.session_state.messages.append({"role": "assistant", "content": initial_message})
                        st.rerun()
                else:
                    st.info("No existing projects found.")
            else:
                st.info("No existing projects found.")
        
        # Activity controls
        st.divider()
        st.header("🤖 Activity Controls")
        if st.button("Clear Activity Logs"):
            st.session_state.activity_logger.clear_logs()
            st.rerun()
        
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
    
    # Main chat interface
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
                
                # Show activity in real-time
                with st.status("🤖 Agent is working...", expanded=True) as status:
                    try:
                        # Use asyncio to run the async method
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        agent_response, is_complete, search_results = loop.run_until_complete(
                            st.session_state.agent.process_user_input_with_logging(
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
                        status.update(label="✅ Processing complete!", state="complete")
                        
                    except Exception as e:
                        logger.error(f"Error processing user input: {str(e)}")
                        st.error(f"An error occurred: {str(e)}")
                        st.session_state.messages.append({
                            "role": "assistant", 
                            "content": "I'm sorry, I encountered an error. Let's continue with the next step."
                        })
                        status.update(label="❌ Error occurred", state="error")
                
                st.rerun()
        elif not st.session_state.agent:
            st.info("👈 Create or load a project to start the conversation.")
    
    # Activity logs column
    with col2:
        st.subheader("🤖 Agent Activity")
        
        # Create container for activity logs
        activity_container = st.container()
        
        with activity_container:
            if st.session_state.agent:
                st.session_state.agent.activity_logger._render_activities()
            else:
                st.info("Start a conversation to see agent activities.")
    
    # Search results column
    with col3:
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
            
            # Manual search option
            st.divider()
            st.subheader("🔍 Manual Search")
            manual_query = st.text_input("Search Query:")
            
            if st.button("Search") and manual_query and st.session_state.agent:
                with st.spinner("Searching..."):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        search_results = loop.run_until_complete(
                            st.session_state.agent.web_search.search_web(
                                manual_query, 
                                engine=search_engine, 
                                max_results=max_results
                            )
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