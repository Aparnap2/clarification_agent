# Enhanced Clarification Agent with Web Search

This enhanced version of the Clarification Agent includes powerful web search capabilities using `crawl4ai` and `httpx` to provide real-time information during project planning conversations.

## 🌟 New Features

### 1. **Web Search Integration**
- **Real-time web crawling** using `crawl4ai` with `AsyncWebCrawler`
- **Multiple search engines** support (DuckDuckGo, Bing, Google)
- **No API keys required** - uses direct web scraping
- **Automatic search triggering** based on user input patterns

### 2. **Smart Search Detection**
The agent automatically detects when to perform web searches based on keywords like:
- "latest", "current", "recent", "new", "trends"
- "best practices", "what is", "how to", "examples"
- "tutorials", "documentation", "compare", "vs"
- "alternatives", "reviews", "benchmarks"

### 3. **Citation System**
- **Automatic citation generation** for all search results
- **Source tracking** with URLs and timestamps
- **Content summarization** from crawled pages
- **Search history** maintained throughout the session

### 4. **Enhanced UI Components**

#### Sidebar Features:
- **Web Search Settings**: Enable/disable search, select search engine, configure max results
- **Search History**: View recent searches with expandable details
- **Manual Search**: Perform custom searches independent of conversation

#### Main Interface:
- **Two-column layout**: Conversation on left, search results on right
- **Real-time search results** displayed during conversation
- **Source links** with content previews
- **Search status indicators** and loading states

### 5. **Logging System**
- **Comprehensive logging** to both file and console
- **Search activity tracking** with timestamps
- **Error handling** with detailed logging
- **Performance monitoring** for search operations

## 🚀 Usage

### Running the Enhanced App

```bash
# Make the run script executable
chmod +x run_web_search_app.sh

# Run the enhanced app
./run_web_search_app.sh
```

Or manually:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run web_search_app.py
```

### Testing the Features

```bash
# Run the test suite
python test_web_search.py
```

## 🔧 Technical Implementation

### Web Search Tool (`WebSearchTool`)

```python
class WebSearchTool:
    async def search_web(self, query: str, engine: str = "duckduckgo", max_results: int = 5):
        # Configure browser for crawling
        browser_conf = BrowserConfig(headless=True)
        run_conf = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)
        
        async with AsyncWebCrawler(config=browser_conf) as crawler:
            # Crawl search results and individual pages
            # Extract content and generate citations
```

### Enhanced Conversation Agent

```python
class EnhancedConversationAgent(ConversationAgent):
    async def process_user_input_with_search(self, user_input: str, enable_search: bool = True):
        # Detect if search is needed
        if self._should_search(user_input):
            search_results = await self.web_search.search_web(query)
            # Enhance response with search results
```

## 📊 Search Result Structure

```json
{
  "query": "Python web frameworks 2024",
  "engine": "duckduckgo",
  "timestamp": "2024-01-15T10:30:00",
  "results": [
    {
      "title": "Best Python Web Frameworks 2024",
      "url": "https://example.com/article",
      "content": "Summary of the article content...",
      "timestamp": "2024-01-15T10:30:15"
    }
  ],
  "citations": [
    "[1] Best Python Web Frameworks 2024 - https://example.com/article"
  ],
  "summary": "Found 3 relevant results for 'Python web frameworks 2024'..."
}
```

## 🎯 Use Cases

### 1. **Technology Research**
- User: "What are the latest React alternatives?"
- Agent performs web search and provides current information about Vue.js, Svelte, Angular, etc.

### 2. **Best Practices Discovery**
- User: "I need Docker best practices for production"
- Agent searches for recent Docker deployment guides and security practices

### 3. **Framework Comparison**
- User: "Compare FastAPI vs Django for my API project"
- Agent finds recent comparisons and benchmarks

### 4. **Tutorial Discovery**
- User: "How to implement authentication in Next.js?"
- Agent searches for current tutorials and documentation

## 🔍 Search Engines Supported

1. **DuckDuckGo** (Default)
   - Privacy-focused
   - No tracking
   - Good for general searches

2. **Bing**
   - Microsoft's search engine
   - Good for technical content
   - Rich results

3. **Google**
   - Comprehensive results
   - May have rate limiting
   - Extensive coverage

## 📝 Configuration Options

### Environment Variables
```bash
export CRAWL4AI_HEADLESS=true
export CRAWL4AI_CACHE_MODE=bypass
```

### Streamlit Configuration
- **Search Engine**: Choose from dropdown
- **Max Results**: Slider from 1-10
- **Enable Search**: Toggle on/off
- **Manual Search**: Custom query input

## 🛠️ Dependencies

### New Dependencies Added:
- `crawl4ai>=0.3.0` - Web crawling and content extraction
- `httpx>=0.24.0` - HTTP client for web requests

### Core Features:
- **Async/await support** for non-blocking operations
- **Browser automation** with headless Chrome
- **Content extraction** with CSS selectors
- **Markdown generation** from HTML content
- **Cache management** for performance

## 🔒 Privacy & Security

- **No API keys required** - all searches use direct web access
- **Headless browsing** - no GUI components loaded
- **Cache bypass** - ensures fresh content
- **Local processing** - all data stays on your machine
- **Configurable engines** - choose your preferred search provider

## 🚨 Error Handling

- **Graceful degradation** - continues without search if errors occur
- **Retry mechanisms** - handles temporary network issues
- **Logging** - detailed error tracking for debugging
- **Fallback responses** - agent continues conversation even if search fails

## 📈 Performance Considerations

- **Async operations** - non-blocking search execution
- **Result limiting** - configurable max results to control load
- **Content summarization** - reduces memory usage
- **Search history management** - limits stored results

## 🔮 Future Enhancements

1. **LLM-powered search query optimization**
2. **Content relevance scoring**
3. **Multi-language search support**
4. **Custom search result filtering**
5. **Integration with specialized technical databases**
6. **Caching layer for frequently searched topics**
7. **Export search results to project documentation**

---

This enhanced version transforms the Clarification Agent into a powerful research assistant that can provide up-to-date information while helping you plan your projects!