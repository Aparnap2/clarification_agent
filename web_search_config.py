"""
Configuration settings for the Enhanced Clarification Agent with Web Search
"""

import os
from typing import Dict, List

class WebSearchConfig:
    """Configuration class for web search functionality"""
    
    # Search Engine Settings
    DEFAULT_SEARCH_ENGINE = "duckduckgo"
    MAX_SEARCH_RESULTS = 5
    SEARCH_TIMEOUT = 30  # seconds
    
    # Search Engines Configuration
    SEARCH_ENGINES = {
        "duckduckgo": {
            "url": "https://duckduckgo.com/html/?q=",
            "name": "DuckDuckGo",
            "description": "Privacy-focused search engine"
        },
        "bing": {
            "url": "https://www.bing.com/search?q=",
            "name": "Bing",
            "description": "Microsoft's search engine"
        },
        "google": {
            "url": "https://www.google.com/search?q=",
            "name": "Google",
            "description": "Google search engine"
        }
    }
    
    # Crawl4AI Settings
    CRAWL4AI_CONFIG = {
        "headless": True,
        "cache_mode": "bypass",
        "timeout": 30,
        "max_retries": 3,
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Search Trigger Keywords
    SEARCH_TRIGGER_KEYWORDS = [
        "latest", "current", "recent", "new", "trends", "trending",
        "best practices", "what is", "how to", "examples", "tutorial",
        "tutorials", "documentation", "docs", "guide", "guides",
        "compare", "vs", "versus", "comparison", "alternatives",
        "reviews", "benchmarks", "performance", "speed", "fast",
        "modern", "2024", "2025", "updated", "state of the art"
    ]
    
    # Content Extraction Settings
    CONTENT_EXTRACTION = {
        "max_content_length": 500,
        "max_title_length": 100,
        "summary_paragraphs": 3,
        "exclude_domains": [
            "facebook.com", "twitter.com", "instagram.com",
            "linkedin.com", "youtube.com", "tiktok.com"
        ]
    }
    
    # Logging Configuration
    LOGGING_CONFIG = {
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        "file": "web_search_app.log",
        "max_file_size": 10 * 1024 * 1024,  # 10MB
        "backup_count": 5
    }
    
    # UI Configuration
    UI_CONFIG = {
        "page_title": "🧠 Enhanced Clarification Agent with Web Search",
        "page_icon": "🧠",
        "layout": "wide",
        "sidebar_width": 300,
        "max_search_history": 10
    }
    
    # Performance Settings
    PERFORMANCE = {
        "max_concurrent_searches": 3,
        "search_result_cache_size": 100,
        "content_cache_ttl": 3600,  # 1 hour
        "async_timeout": 60
    }
    
    @classmethod
    def get_search_engine_url(cls, engine: str) -> str:
        """Get search engine URL by name"""
        return cls.SEARCH_ENGINES.get(engine, cls.SEARCH_ENGINES[cls.DEFAULT_SEARCH_ENGINE])["url"]
    
    @classmethod
    def get_search_engine_name(cls, engine: str) -> str:
        """Get search engine display name"""
        return cls.SEARCH_ENGINES.get(engine, cls.SEARCH_ENGINES[cls.DEFAULT_SEARCH_ENGINE])["name"]
    
    @classmethod
    def should_trigger_search(cls, text: str) -> bool:
        """Check if text contains search trigger keywords"""
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in cls.SEARCH_TRIGGER_KEYWORDS)
    
    @classmethod
    def get_environment_config(cls) -> Dict[str, str]:
        """Get environment configuration for crawl4ai"""
        return {
            "CRAWL4AI_HEADLESS": str(cls.CRAWL4AI_CONFIG["headless"]).lower(),
            "CRAWL4AI_CACHE_MODE": cls.CRAWL4AI_CONFIG["cache_mode"],
            "CRAWL4AI_TIMEOUT": str(cls.CRAWL4AI_CONFIG["timeout"]),
            "CRAWL4AI_MAX_RETRIES": str(cls.CRAWL4AI_CONFIG["max_retries"])
        }
    
    @classmethod
    def setup_environment(cls):
        """Setup environment variables for crawl4ai"""
        env_config = cls.get_environment_config()
        for key, value in env_config.items():
            os.environ[key] = value

# Example usage and validation
if __name__ == "__main__":
    # Test configuration
    config = WebSearchConfig()
    
    print("🔧 Web Search Configuration")
    print("=" * 40)
    
    print(f"Default Search Engine: {config.DEFAULT_SEARCH_ENGINE}")
    print(f"Max Search Results: {config.MAX_SEARCH_RESULTS}")
    print(f"Search Timeout: {config.SEARCH_TIMEOUT}s")
    
    print("\nAvailable Search Engines:")
    for engine, details in config.SEARCH_ENGINES.items():
        print(f"  - {details['name']} ({engine}): {details['description']}")
    
    print(f"\nSearch Trigger Keywords ({len(config.SEARCH_TRIGGER_KEYWORDS)}):")
    for keyword in config.SEARCH_TRIGGER_KEYWORDS[:10]:  # Show first 10
        print(f"  - {keyword}")
    print("  ...")
    
    print("\nTesting search trigger detection:")
    test_phrases = [
        "What are the latest Python frameworks?",
        "I need help with my project",
        "How to implement authentication?",
        "Compare React vs Vue.js performance"
    ]
    
    for phrase in test_phrases:
        should_search = config.should_trigger_search(phrase)
        print(f"  '{phrase}' -> Search: {should_search}")
    
    print("\n✅ Configuration validated successfully!")