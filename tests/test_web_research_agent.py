"""Tests for WebResearchAgent."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agents.web_research_agent import WebResearchAgent, ResearchResult, CompetitorData, MarketTrendData


class TestWebResearchAgent:
    """Test cases for WebResearchAgent."""
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test that WebResearchAgent works as async context manager."""
        with patch('agents.web_research_agent.AsyncWebCrawler') as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler_class.return_value = mock_crawler
            
            async with WebResearchAgent() as agent:
                assert agent.crawler is not None
                mock_crawler.__aenter__.assert_called_once()
            
            mock_crawler.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_research_topic_success(self):
        """Test successful research topic execution."""
        with patch('agents.web_research_agent.AsyncWebCrawler') as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler_class.return_value = mock_crawler
            
            # Mock successful crawl result
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.extracted_content = "Test extracted content"
            mock_result.cleaned_html = "Test cleaned HTML content"
            mock_result.metadata = {"title": "Test Title"}
            mock_result.error_message = None
            
            mock_crawler.arun.return_value = mock_result
            
            async with WebResearchAgent() as agent:
                results = await agent.research_topic("test query", ["https://example.com"])
                
                assert len(results) == 1
                assert results[0]["success"] is True
                assert results[0]["url"] == "https://example.com"
                assert results[0]["title"] == "Test Title"
                assert "Test extracted content" in results[0]["content"]
    
    @pytest.mark.asyncio
    async def test_research_topic_with_error_handling(self):
        """Test research topic with error handling."""
        with patch('agents.web_research_agent.AsyncWebCrawler') as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler_class.return_value = mock_crawler
            
            # Mock failed crawl result
            mock_result = MagicMock()
            mock_result.success = False
            mock_result.error_message = "Connection failed"
            
            mock_crawler.arun.return_value = mock_result
            
            async with WebResearchAgent() as agent:
                results = await agent.research_topic("test query", ["https://example.com"])
                
                assert len(results) == 1
                assert results[0]["success"] is False
                assert results[0]["error_message"] == "Connection failed"
    
    @pytest.mark.asyncio
    async def test_research_topic_timeout_handling(self):
        """Test research topic with timeout handling."""
        with patch('agents.web_research_agent.AsyncWebCrawler') as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler_class.return_value = mock_crawler
            
            # Mock timeout
            mock_crawler.arun.side_effect = asyncio.TimeoutError()
            
            async with WebResearchAgent(timeout=1) as agent:
                results = await agent.research_topic("test query", ["https://example.com"])
                
                assert len(results) == 1
                assert results[0]["success"] is False
                assert "Timeout" in results[0]["error_message"]
    
    @pytest.mark.asyncio
    async def test_extract_competitor_data(self):
        """Test competitor data extraction."""
        with patch('agents.web_research_agent.AsyncWebCrawler') as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler_class.return_value = mock_crawler
            
            # Mock successful crawl result with competitor content
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.extracted_content = "We help businesses grow with our innovative solutions. Our pricing starts at $99/month."
            mock_result.cleaned_html = "We help businesses grow with our innovative solutions. Our pricing starts at $99/month."
            mock_result.metadata = {"title": "Example Corp"}
            mock_result.error_message = None
            
            mock_crawler.arun.return_value = mock_result
            
            async with WebResearchAgent() as agent:
                competitors = await agent.extract_competitor_data(["https://example.com"])
                
                assert len(competitors) == 1
                assert competitors[0].company_name == "Example"
                assert competitors[0].url == "https://example.com"
                assert competitors[0].value_proposition is not None
                assert competitors[0].pricing_info is not None
    
    @pytest.mark.asyncio
    async def test_analyze_market_trends(self):
        """Test market trend analysis."""
        with patch('agents.web_research_agent.AsyncWebCrawler') as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler_class.return_value = mock_crawler
            
            # Mock successful crawl result with trend content
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.extracted_content = "The AI market is experiencing rapid growth with emerging trends in automation."
            mock_result.cleaned_html = "The AI market is experiencing rapid growth with emerging trends in automation."
            mock_result.metadata = {"title": "AI Market Trends"}
            mock_result.error_message = None
            
            mock_crawler.arun.return_value = mock_result
            
            async with WebResearchAgent() as agent:
                trends = await agent.analyze_market_trends("AI technology")
                
                assert len(trends) > 0
                assert trends[0].industry == "AI technology"
                assert trends[0].trend_title is not None
                assert trends[0].trend_description is not None
    
    def test_generate_research_urls(self):
        """Test URL generation for research."""
        agent = WebResearchAgent()
        urls = agent._generate_research_urls("e-commerce platform")
        
        assert len(urls) > 0
        assert all(isinstance(url, str) for url in urls)
        assert any("e-commerce+platform" in url for url in urls)
    
    def test_extract_company_name(self):
        """Test company name extraction."""
        agent = WebResearchAgent()
        name = agent._extract_company_name("", "https://www.example.com")
        assert name == "Example"
    
    def test_extract_value_proposition(self):
        """Test value proposition extraction."""
        agent = WebResearchAgent()
        content = "We help businesses grow faster with our innovative solutions."
        value_prop = agent._extract_value_proposition(content)
        assert value_prop is not None
        assert "We help businesses grow faster" in value_prop
    
    def test_extract_pricing_info(self):
        """Test pricing information extraction."""
        agent = WebResearchAgent()
        content = "Our pricing starts at $99 per month for the basic plan."
        pricing = agent._extract_pricing_info(content)
        assert pricing is not None
        assert "$99" in pricing
    
    def test_extract_key_features(self):
        """Test key features extraction."""
        agent = WebResearchAgent()
        content = "Our key features include automated reporting, real-time analytics, and custom dashboards."
        features = agent._extract_key_features(content)
        assert len(features) > 0
        assert any("feature" in feature.lower() for feature in features)


class TestDataModels:
    """Test cases for data models."""
    
    def test_research_result_model(self):
        """Test ResearchResult model validation."""
        result = ResearchResult(
            url="https://example.com",
            title="Test Title",
            content="Test content"
        )
        assert result.url == "https://example.com"
        assert result.title == "Test Title"
        assert result.success is True
        assert result.timestamp is not None
    
    def test_competitor_data_model(self):
        """Test CompetitorData model validation."""
        competitor = CompetitorData(
            company_name="Test Corp",
            url="https://testcorp.com"
        )
        assert competitor.company_name == "Test Corp"
        assert competitor.url == "https://testcorp.com"
        assert competitor.key_features == []
        assert competitor.strengths == []
    
    def test_market_trend_data_model(self):
        """Test MarketTrendData model validation."""
        trend = MarketTrendData(
            industry="Technology",
            trend_title="AI Growth",
            trend_description="AI is growing rapidly",
            impact_level="High",
            time_horizon="2-3 years"
        )
        assert trend.industry == "Technology"
        assert trend.trend_title == "AI Growth"
        assert trend.impact_level == "High"
        assert trend.sources == []
        assert trend.key_insights == []


if __name__ == "__main__":
    pytest.main([__file__])