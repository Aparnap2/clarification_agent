# 🧠 Enhanced Clarification Agent with Web Search

An AI-powered project clarification tool enhanced with real-time web search capabilities using `crawl4ai` and `httpx`. This tool helps you define, scope, and plan your software projects while providing up-to-date information from the web.

## 🌟 Features

### Core Clarification Agent
- **Conversational project planning** through natural language
- **Multi-perspective analysis** (Product Manager, Tech Lead, Business Analyst, UX Designer, QA Engineer)
- **Automatic file generation** (README.md, .plan.yml, architecture.md)
- **Project state persistence** with .clarity folder

### 🔍 Web Search Integration
- **Real-time web crawling** with crawl4ai AsyncWebCrawler
- **Multiple search engines** (DuckDuckGo, Bing, Google)
- **No API keys required** - direct web scraping
- **Smart search detection** based on user input patterns
- **Automatic citation generation** with source tracking
- **Content summarization** from crawled pages

### 🎯 Smart Features
- **Automatic search triggering** when users ask about:
  - Latest technologies and trends
  - Best practices and tutorials
  - Framework comparisons
  - Current documentation
- **Search history tracking** throughout the session
- **Manual search capability** for custom queries
- **Comprehensive logging** for debugging and monitoring

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd clarification-agent

# Install dependencies
pip install -r requirements.txt
```

### Running the Enhanced Web Search App

```bash
# Make the run script executable
chmod +x run_web_search_app.sh

# Run the enhanced app
./run_web_search_app.sh
```

Or manually:

```bash
# Set environment variables
export CRAWL4AI_HEADLESS=true
export CRAWL4AI_CACHE_MODE=bypass

# Run the app
streamlit run web_search_app.py
```

### Testing

```bash
# Run the test suite
python test_web_search.py
```

## 📋 Usage Examples

### Example 1: Technology Research
```
User: "What are the latest Python web frameworks for 2024?"
Agent: [Performs web search] "Based on recent research, here are the top Python web frameworks..."
```

### Example 2: Best Practices Discovery
```
User: "I need Docker best practices for production deployment"
Agent: [Searches for current Docker guides] "Here are the current best practices for Docker in production..."
```

### Example 3: Framework Comparison
```
User: "Compare React vs Vue.js for my new project"
Agent: [Finds recent comparisons] "Based on current benchmarks and reviews..."
```

## 🔧 Configuration

### Web Search Settings (via UI)
- **Search Engine**: Choose from DuckDuckGo, Bing, or Google
- **Max Results**: Configure number of results (1-10)
- **Enable/Disable Search**: Toggle web search functionality
- **Manual Search**: Perform custom searches

### Environment Variables
```bash
export CRAWL4AI_HEADLESS=true          # Run browser in headless mode
export CRAWL4AI_CACHE_MODE=bypass      # Always fetch fresh content
export CRAWL4AI_TIMEOUT=30             # Request timeout in seconds
export CRAWL4AI_MAX_RETRIES=3          # Maximum retry attempts
```

### Configuration File
Customize settings in `web_search_config.py`:

```python
class WebSearchConfig:
    DEFAULT_SEARCH_ENGINE = "duckduckgo"
    MAX_SEARCH_RESULTS = 5
    SEARCH_TIMEOUT = 30
    
    SEARCH_TRIGGER_KEYWORDS = [
        "latest", "current", "recent", "best practices",
        "what is", "how to", "compare", "vs", "tutorials"
    ]
```

## 📁 File Structure

```
clarification-agent/
├── web_search_app.py           # Enhanced Streamlit app with web search
├── web_search_config.py        # Configuration settings
├── test_web_search.py          # Test suite for web search features
├── run_web_search_app.sh       # Run script for the enhanced app
├── WEB_SEARCH_FEATURES.md      # Detailed feature documentation
├── requirements.txt            # Updated dependencies
├── clarification_agent/        # Core agent modules
│   ├── core/
│   ├── models/
│   ├── nodes/
│   └── utils/
├── .clarity/                   # Project data storage
└── logs/                       # Application logs
```

## 🔍 Search Result Structure

Each search returns structured data:

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

## 🎨 UI Components

### Main Interface
- **Two-column layout**: Conversation on left, search results on right
- **Real-time search indicators**: Shows when searches are being performed
- **Citation display**: Automatic source attribution
- **Search history**: Expandable history of recent searches

### Sidebar Features
- **Project management**: Create/load projects
- **Search configuration**: Engine selection, result limits
- **Search history**: Quick access to previous searches
- **Manual search**: Custom query input

## 📊 Dependencies

### New Dependencies
```
crawl4ai>=0.3.0     # Web crawling and content extraction
httpx>=0.24.0       # HTTP client for web requests
```

### Core Dependencies
```
streamlit>=1.24.0   # Web UI framework
langchain>=0.0.267  # LLM integration
langgraph>=0.1.72   # Graph-based workflows
pydantic>=2.0.0     # Data validation
openai>=1.0.0       # OpenAI API client
```

## 🔒 Privacy & Security

- **No API keys required** for web search functionality
- **Local processing** - all data stays on your machine
- **Headless browsing** - no GUI components loaded
- **Configurable search engines** - choose your preferred provider
- **Cache bypass** - ensures fresh content on every search

## 🚨 Error Handling

- **Graceful degradation** - continues without search if errors occur
- **Comprehensive logging** - detailed error tracking
- **Retry mechanisms** - handles temporary network issues
- **Fallback responses** - agent continues conversation even if search fails

## 📈 Performance Features

- **Async operations** - non-blocking search execution
- **Configurable timeouts** - prevents hanging requests
- **Result limiting** - controls resource usage
- **Content summarization** - reduces memory footprint
- **Search history management** - limits stored results

## 🔮 Future Enhancements

1. **LLM-powered search query optimization**
2. **Content relevance scoring and ranking**
3. **Multi-language search support**
4. **Custom search result filtering**
5. **Integration with specialized technical databases**
6. **Advanced caching layer for performance**
7. **Export search results to project documentation**
8. **Real-time collaboration features**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: See `WEB_SEARCH_FEATURES.md` for detailed feature docs
- **Issues**: Report bugs and feature requests via GitHub issues
- **Testing**: Run `python test_web_search.py` to verify functionality
- **Logs**: Check `web_search_app.log` for debugging information

---

Transform your project planning with AI-powered clarification and real-time web research! 🚀