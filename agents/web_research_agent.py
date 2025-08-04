"""Web Research Agent with Crawl4AI integration for market research and competitive analysis."""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from crawl4ai import AsyncWebCrawler
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class ResearchResult(BaseModel):
    """Structure for research results."""
    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Page title")
    content: str = Field(..., description="Extracted content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Extraction timestamp")
    success: bool = Field(default=True, description="Whether extraction was successful")
    error_message: Optional[str] = Field(None, description="Error message if extraction failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class CompetitorData(BaseModel):
    """Structure for competitor analysis data."""
    company_name: str = Field(..., description="Competitor company name")
    url: str = Field(..., description="Competitor website URL")
    value_proposition: Optional[str] = Field(None, description="Competitor's value proposition")
    pricing_info: Optional[str] = Field(None, description="Pricing information")
    target_market: Optional[str] = Field(None, description="Target market description")
    key_features: List[str] = Field(default_factory=list, description="Key product features")
    strengths: List[str] = Field(default_factory=list, description="Competitive strengths")
    weaknesses: List[str] = Field(default_factory=list, description="Potential weaknesses")
    market_position: Optional[str] = Field(None, description="Market positioning")


class MarketTrendData(BaseModel):
    """Structure for market trend analysis data."""
    industry: str = Field(..., description="Industry or market segment")
    trend_title: str = Field(..., description="Trend title or description")
    trend_description: str = Field(..., description="Detailed trend description")
    impact_level: str = Field(..., description="Impact level (High/Medium/Low)")
    time_horizon: str = Field(..., description="Time horizon for the trend")
    sources: List[str] = Field(default_factory=list, description="Source URLs")
    key_insights: List[str] = Field(default_factory=list, description="Key insights from the trend")


class WebResearchAgent:
    """Web Research Agent for automated market research using Crawl4AI."""
    
    def __init__(self, max_concurrent_crawls: int = 5, timeout: int = 30):
        """Initialize the WebResearchAgent.
        
        Args:
            max_concurrent_crawls: Maximum number of concurrent crawl operations
            timeout: Timeout in seconds for each crawl operation
        """
        self.max_concurrent_crawls = max_concurrent_crawls
        self.timeout = timeout
        self.crawler: Optional[AsyncWebCrawler] = None
        self._semaphore = asyncio.Semaphore(max_concurrent_crawls)
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.crawler = AsyncWebCrawler(
            verbose=False,
            headless=True,
            browser_type="chromium"
        )
        await self.crawler.__aenter__()
        logger.info("WebResearchAgent initialized with Crawl4AI")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.crawler:
            await self.crawler.__aexit__(exc_type, exc_val, exc_tb)
            self.crawler = None
        logger.info("WebResearchAgent closed")
        
    async def research_topic(self, query: str, urls: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Research a topic by crawling relevant URLs.
        
        Args:
            query: Research query or topic
            urls: Optional list of specific URLs to crawl. If None, will generate URLs based on query
            
        Returns:
            List of research results with extracted data
            
        Requirements: 3.1, 3.2, 3.3
        """
        if not self.crawler:
            raise RuntimeError("WebResearchAgent must be used as async context manager")
            
        logger.info(f"Starting research for topic: {query}")
        
        # Generate URLs if not provided
        if urls is None:
            urls = self._generate_research_urls(query)
            
        # Crawl URLs concurrently with error handling
        research_results = []
        crawl_tasks = [self._crawl_url_with_semaphore(url, query) for url in urls]
        
        try:
            results = await asyncio.gather(*crawl_tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Crawl task failed: {result}")
                    # Create error result but continue processing
                    error_result = {
                        "url": "unknown",
                        "title": "Error",
                        "content": f"Crawl failed: {str(result)}",
                        "timestamp": datetime.now().isoformat(),
                        "success": False,
                        "error_message": str(result),
                        "metadata": {"query": query}
                    }
                    research_results.append(error_result)
                elif result:
                    research_results.append(result)
                    
        except Exception as e:
            logger.error(f"Research failed for query '{query}': {e}")
            # Return partial results with error information
            error_result = {
                "url": "batch_error",
                "title": "Batch Processing Error",
                "content": f"Research batch failed: {str(e)}",
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error_message": str(e),
                "metadata": {"query": query, "urls": urls}
            }
            research_results.append(error_result)
            
        successful_results = [r for r in research_results if r.get("success", False)]
        failed_results = [r for r in research_results if not r.get("success", False)]
        
        logger.info(f"Research completed: {len(successful_results)} successful, {len(failed_results)} failed")
        
        return research_results
        
    async def _crawl_url_with_semaphore(self, url: str, query: str) -> Optional[Dict[str, Any]]:
        """Crawl a single URL with semaphore for concurrency control.
        
        Args:
            url: URL to crawl
            query: Research query for context
            
        Returns:
            Research result dictionary or None if failed
            
        Requirements: 3.4 (error handling with graceful continuation)
        """
        async with self._semaphore:
            try:
                logger.debug(f"Crawling URL: {url}")
                
                # Perform the crawl with timeout (without LLM extraction for now)
                result = await asyncio.wait_for(
                    self.crawler.arun(
                        url=url,
                        bypass_cache=True,
                        include_raw_html=False
                    ),
                    timeout=self.timeout
                )
                
                if result.success:
                    return {
                        "url": url,
                        "title": result.metadata.get("title", "No title"),
                        "content": result.extracted_content or result.cleaned_html[:2000],  # Limit content size
                        "timestamp": datetime.now().isoformat(),
                        "success": True,
                        "error_message": None,
                        "metadata": {
                            "query": query,
                            "word_count": len(result.cleaned_html.split()) if result.cleaned_html else 0,
                            "extraction_used": bool(result.extracted_content),
                            **result.metadata
                        }
                    }
                else:
                    logger.warning(f"Crawl unsuccessful for {url}: {result.error_message}")
                    return {
                        "url": url,
                        "title": "Crawl Failed",
                        "content": f"Failed to crawl: {result.error_message}",
                        "timestamp": datetime.now().isoformat(),
                        "success": False,
                        "error_message": result.error_message,
                        "metadata": {"query": query}
                    }
                    
            except asyncio.TimeoutError:
                logger.warning(f"Timeout crawling {url}")
                return {
                    "url": url,
                    "title": "Timeout",
                    "content": f"Crawl timed out after {self.timeout} seconds",
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "error_message": f"Timeout after {self.timeout} seconds",
                    "metadata": {"query": query}
                }
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                return {
                    "url": url,
                    "title": "Error",
                    "content": f"Crawl error: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "success": False,
                    "error_message": str(e),
                    "metadata": {"query": query}
                }
                
    def _generate_research_urls(self, query: str) -> List[str]:
        """Generate relevant URLs for research based on query.
        
        Args:
            query: Research query
            
        Returns:
            List of URLs to crawl
        """
        # Extract key terms from query for URL generation
        query_terms = query.lower().replace(" ", "+")
        
        # Generate search URLs and industry-specific sites
        urls = [
            f"https://www.google.com/search?q={query_terms}+market+analysis",
            f"https://www.google.com/search?q={query_terms}+competitors",
            f"https://www.google.com/search?q={query_terms}+industry+trends",
            "https://www.crunchbase.com",
            "https://www.gartner.com",
            "https://www.forrester.com",
            "https://techcrunch.com",
            "https://www.mckinsey.com/insights",
        ]
        
        return urls[:8]  # Limit to 8 URLs to avoid overwhelming the system
        
    async def extract_competitor_data(self, competitor_urls: List[str]) -> List[CompetitorData]:
        """Extract structured competitor data from URLs.
        
        Args:
            competitor_urls: List of competitor website URLs
            
        Returns:
            List of CompetitorData objects
            
        Requirements: 3.2, 3.3
        """
        if not self.crawler:
            raise RuntimeError("WebResearchAgent must be used as async context manager")
            
        logger.info(f"Extracting competitor data from {len(competitor_urls)} URLs")
        
        competitor_data = []
        
        for url in competitor_urls:
            try:
                # Research this specific competitor
                research_results = await self.research_topic(
                    query=f"competitor analysis {urlparse(url).netloc}",
                    urls=[url]
                )
                
                if research_results and research_results[0].get("success"):
                    result = research_results[0]
                    
                    # Extract competitor information from the crawled content
                    competitor = CompetitorData(
                        company_name=self._extract_company_name(result["content"], url),
                        url=url,
                        value_proposition=self._extract_value_proposition(result["content"]),
                        pricing_info=self._extract_pricing_info(result["content"]),
                        target_market=self._extract_target_market(result["content"]),
                        key_features=self._extract_key_features(result["content"]),
                        strengths=self._extract_strengths(result["content"]),
                        weaknesses=self._extract_weaknesses(result["content"]),
                        market_position=self._extract_market_position(result["content"])
                    )
                    
                    competitor_data.append(competitor)
                    logger.debug(f"Successfully extracted data for {competitor.company_name}")
                    
                else:
                    logger.warning(f"Failed to extract competitor data from {url}")
                    
            except Exception as e:
                logger.error(f"Error extracting competitor data from {url}: {e}")
                # Continue with other competitors even if one fails
                continue
                
        logger.info(f"Extracted data for {len(competitor_data)} competitors")
        return competitor_data
        
    async def analyze_market_trends(self, industry: str, trend_urls: Optional[List[str]] = None) -> List[MarketTrendData]:
        """Analyze market trends for a specific industry.
        
        Args:
            industry: Industry or market segment to analyze
            trend_urls: Optional specific URLs for trend analysis
            
        Returns:
            List of MarketTrendData objects
            
        Requirements: 3.2, 3.3
        """
        if not self.crawler:
            raise RuntimeError("WebResearchAgent must be used as async context manager")
            
        logger.info(f"Analyzing market trends for industry: {industry}")
        
        # Generate trend-specific URLs if not provided
        if trend_urls is None:
            trend_urls = self._generate_trend_urls(industry)
            
        # Research market trends
        research_results = await self.research_topic(
            query=f"{industry} market trends 2024 analysis",
            urls=trend_urls
        )
        
        trend_data = []
        
        for result in research_results:
            if result.get("success"):
                try:
                    # Extract trend information from the content
                    trends = self._extract_trends_from_content(result["content"], industry)
                    
                    for trend in trends:
                        trend_obj = MarketTrendData(
                            industry=industry,
                            trend_title=trend.get("title", "Market Trend"),
                            trend_description=trend.get("description", ""),
                            impact_level=trend.get("impact", "Medium"),
                            time_horizon=trend.get("timeline", "1-2 years"),
                            sources=[result["url"]],
                            key_insights=trend.get("insights", [])
                        )
                        trend_data.append(trend_obj)
                        
                except Exception as e:
                    logger.error(f"Error extracting trends from {result['url']}: {e}")
                    continue
                    
        logger.info(f"Analyzed {len(trend_data)} market trends for {industry}")
        return trend_data
        
    def _generate_trend_urls(self, industry: str) -> List[str]:
        """Generate URLs for market trend research."""
        industry_terms = industry.lower().replace(" ", "+")
        
        return [
            f"https://www.google.com/search?q={industry_terms}+market+trends+2024",
            f"https://www.google.com/search?q={industry_terms}+industry+report",
            "https://www.statista.com",
            "https://www.ibisworld.com",
            "https://www.grandviewresearch.com",
            "https://www.marketsandmarkets.com"
        ]
        
    # Helper methods for data extraction
    def _extract_company_name(self, content: str, url: str) -> str:
        """Extract company name from content or URL."""
        # Simple extraction - in a real implementation, this would use NLP
        domain = urlparse(url).netloc.replace("www.", "").split(".")[0]
        return domain.title()
        
    def _extract_value_proposition(self, content: str) -> Optional[str]:
        """Extract value proposition from content."""
        # Simplified extraction - look for common value prop indicators
        content_lower = content.lower()
        value_indicators = ["we help", "we provide", "our mission", "value proposition"]
        
        for indicator in value_indicators:
            if indicator in content_lower:
                # Extract sentence containing the indicator
                sentences = content.split(".")
                for sentence in sentences:
                    if indicator in sentence.lower():
                        return sentence.strip()[:200]  # Limit length
        return None
        
    def _extract_pricing_info(self, content: str) -> Optional[str]:
        """Extract pricing information from content."""
        content_lower = content.lower()
        pricing_indicators = ["$", "price", "pricing", "cost", "subscription", "plan"]
        
        for indicator in pricing_indicators:
            if indicator in content_lower:
                sentences = content.split(".")
                for sentence in sentences:
                    if indicator in sentence.lower():
                        return sentence.strip()[:200]
        return None
        
    def _extract_target_market(self, content: str) -> Optional[str]:
        """Extract target market information from content."""
        content_lower = content.lower()
        market_indicators = ["target", "customers", "market", "audience", "users"]
        
        for indicator in market_indicators:
            if indicator in content_lower:
                sentences = content.split(".")
                for sentence in sentences:
                    if indicator in sentence.lower():
                        return sentence.strip()[:200]
        return None
        
    def _extract_key_features(self, content: str) -> List[str]:
        """Extract key features from content."""
        # Simplified feature extraction
        feature_indicators = ["feature", "capability", "function", "service", "solution"]
        features = []
        
        sentences = content.split(".")
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in feature_indicators):
                features.append(sentence.strip()[:100])
                if len(features) >= 5:  # Limit to 5 features
                    break
                    
        return features
        
    def _extract_strengths(self, content: str) -> List[str]:
        """Extract competitive strengths from content."""
        strength_indicators = ["advantage", "strength", "leader", "best", "unique", "innovative"]
        strengths = []
        
        sentences = content.split(".")
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in strength_indicators):
                strengths.append(sentence.strip()[:100])
                if len(strengths) >= 3:
                    break
                    
        return strengths
        
    def _extract_weaknesses(self, content: str) -> List[str]:
        """Extract potential weaknesses from content."""
        # This is challenging to extract automatically - would need more sophisticated analysis
        # For now, return empty list as weaknesses are rarely self-reported
        return []
        
    def _extract_market_position(self, content: str) -> Optional[str]:
        """Extract market positioning from content."""
        position_indicators = ["position", "leader", "pioneer", "innovator", "market share"]
        
        sentences = content.split(".")
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in position_indicators):
                return sentence.strip()[:200]
        return None
        
    def _extract_trends_from_content(self, content: str, industry: str) -> List[Dict[str, Any]]:
        """Extract trend information from content."""
        # Simplified trend extraction
        trend_indicators = ["trend", "growth", "increase", "decrease", "emerging", "future"]
        trends = []
        
        sentences = content.split(".")
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(indicator in sentence_lower for indicator in trend_indicators):
                trend = {
                    "title": f"{industry} Trend",
                    "description": sentence.strip()[:300],
                    "impact": "Medium",  # Default impact
                    "timeline": "1-2 years",  # Default timeline
                    "insights": [sentence.strip()[:200]]
                }
                trends.append(trend)
                if len(trends) >= 3:  # Limit to 3 trends per source
                    break
                    
        return trends