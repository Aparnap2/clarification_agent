"""Go-to-Market (GTM) Strategy Agent for comprehensive launch planning and positioning."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import openai
from pydantic import BaseModel, Field

from models.data_models import BusinessModel, GTMStrategy, ProductState

# Configure logging
logger = logging.getLogger(__name__)


class ChannelAnalysis(BaseModel):
    """Structure for distribution channel analysis."""
    channel_name: str = Field(..., description="Distribution channel name")
    rationale: str = Field(..., description="Why this channel is suitable")
    target_audience: str = Field(..., description="Target audience for this channel")
    cost_estimate: str = Field(..., description="Estimated cost/effort")
    timeline: str = Field(..., description="Timeline to establish channel")
    success_metrics: List[str] = Field(..., description="Channel-specific success metrics")


class PricingAnalysis(BaseModel):
    """Structure for pricing strategy analysis."""
    pricing_model: str = Field(..., description="Primary pricing model")
    price_point: str = Field(..., description="Recommended price point")
    competitive_positioning: str = Field(..., description="Position relative to competitors")
    value_justification: str = Field(..., description="Justification for the price")
    pricing_tiers: Optional[List[Dict[str, str]]] = Field(None, description="Pricing tiers if applicable")


class LaunchMilestone(BaseModel):
    """Structure for launch timeline milestones."""
    phase: str = Field(..., description="Launch phase name")
    timeline: str = Field(..., description="Timeline for this phase")
    key_activities: List[str] = Field(..., description="Key activities in this phase")
    success_criteria: List[str] = Field(..., description="Success criteria for this phase")
    deliverables: List[str] = Field(..., description="Expected deliverables")


class GTMStrategyAgent:
    """Go-to-Market Strategy Agent with LLM integration for comprehensive launch planning."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-4o-mini"):
        """Initialize the GTM Strategy Agent.
        
        Args:
            api_key: OpenAI API key (if None, will use environment variable)
            model: LLM model to use for analysis
        """
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model
        logger.info(f"GTMStrategyAgent initialized with model: {model}")
    
    async def develop_gtm_strategy(self, state: ProductState) -> ProductState:
        """Main method to develop comprehensive GTM strategy and update state.
        
        Args:
            state: Current product state with business model and competitive analysis
            
        Returns:
            Updated product state with GTM strategy
            
        Requirements: 5.1, 5.2, 5.3, 5.4
        """
        logger.info("Starting GTM strategy development")
        
        if not state.business_model:
            logger.error("Cannot develop GTM strategy without business model")
            raise ValueError("Business model is required for GTM strategy development")
        
        try:
            # Step 1: Identify distribution channels
            channels = await self._identify_channels(state.business_model, state.competitive_analysis)
            
            # Step 2: Develop pricing strategy
            pricing_strategy = await self._develop_pricing(
                state.business_model, 
                state.competitive_analysis,
                state.feature_specifications
            )
            
            # Step 3: Create launch timeline
            launch_timeline = await self._create_launch_sequence(
                state.business_model,
                state.feature_specifications,
                channels
            )
            
            # Step 4: Define success metrics
            success_metrics = await self._define_success_metrics(
                state.business_model,
                channels,
                pricing_strategy
            )
            
            # Step 5: Create competitive positioning
            competitive_positioning = await self._create_competitive_positioning(
                state.business_model,
                state.competitive_analysis,
                pricing_strategy
            )
            
            # Create GTMStrategy object with proper phase mapping
            phase_mapping = {
                "MVP Launch": "mvp_launch",
                "Product Growth": "growth", 
                "Growth Phase": "growth",
                "Market Expansion": "expansion",
                "Expansion": "expansion"
            }
            
            timeline_dict = {}
            for milestone in launch_timeline:
                key = phase_mapping.get(milestone.phase, milestone.phase.lower().replace(" ", "_"))
                timeline_dict[key] = f"{milestone.timeline}: {', '.join(milestone.key_activities[:2])}"
            
            # Ensure required keys exist
            if "mvp_launch" not in timeline_dict:
                timeline_dict["mvp_launch"] = "8-12 weeks: Complete core features, Beta testing"
            if "growth" not in timeline_dict:
                timeline_dict["growth"] = "3-6 months: Scale customer acquisition, Feature expansion"
            if "expansion" not in timeline_dict:
                timeline_dict["expansion"] = "6-12 months: Market expansion, Partnership development"
            
            gtm_strategy = GTMStrategy(
                distribution_channels=[channel.channel_name for channel in channels],
                pricing_strategy=pricing_strategy.pricing_model + " - " + pricing_strategy.price_point,
                launch_timeline=timeline_dict,
                success_metrics=success_metrics,
                competitive_positioning=competitive_positioning,
                budget_requirements=self._estimate_budget_requirements(channels, pricing_strategy)
            )
            
            # Update state
            state.gtm_strategy = gtm_strategy
            state.current_phase = "gtm_planning"
            state.update_timestamp()
            
            logger.info("GTM strategy development completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"GTM strategy development failed: {e}")
            # Add error information to market_validation dict since we can't add new fields
            state.market_validation["gtm_error"] = str(e)
            state.market_validation["gtm_error_timestamp"] = datetime.now().isoformat()
            state.update_timestamp()
            return state
    
    async def _identify_channels(self, business_model: BusinessModel, competitive_analysis: List[Dict]) -> List[ChannelAnalysis]:
        """Identify 3-5 specific distribution channels with rationale.
        
        Args:
            business_model: Business model data
            competitive_analysis: Competitive analysis results
            
        Returns:
            List of channel analysis results
            
        Requirements: 5.1
        """
        logger.debug("Identifying distribution channels")
        
        # Prepare competitive context
        competitive_context = ""
        if competitive_analysis:
            competitive_context = "\n".join([
                f"- {comp.get('competitor_name', 'Unknown')}: {comp.get('value_proposition', 'N/A')}"
                for comp in competitive_analysis[:3]
            ])
        
        channel_prompt = f"""
        Identify 3-5 specific distribution channels for this business model:

        BUSINESS MODEL:
        - Value Proposition: {business_model.value_proposition}
        - Target Customer: {business_model.target_customer}
        - Revenue Streams: {', '.join(business_model.revenue_streams)}

        COMPETITIVE LANDSCAPE:
        {competitive_context}

        For each channel, provide detailed analysis including rationale, target audience, cost estimate, timeline, and success metrics.

        Return in JSON format:
        {{
            "channels": [
                {{
                    "channel_name": "<specific channel name>",
                    "rationale": "<why this channel is suitable for the target customer>",
                    "target_audience": "<specific audience segment for this channel>",
                    "cost_estimate": "<estimated cost/effort level>",
                    "timeline": "<timeline to establish this channel>",
                    "success_metrics": ["<metric 1>", "<metric 2>", "<metric 3>"]
                }},
                ...
            ]
        }}

        Requirements:
        - Channels must be specific and actionable (not generic like "social media")
        - Include both digital and traditional channels where appropriate
        - Consider the target customer's behavior and preferences
        - Provide realistic cost and timeline estimates
        - Focus on channels that differentiate from competitors
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a go-to-market expert specializing in distribution channel strategy and customer acquisition."},
                    {"role": "user", "content": channel_prompt}
                ],
                temperature=0.4,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                json_content = content[start_idx:end_idx]
            
            channel_data = json.loads(json_content)
            
            # Create ChannelAnalysis objects
            channels = []
            for channel_info in channel_data.get("channels", []):
                channel = ChannelAnalysis(**channel_info)
                channels.append(channel)
            
            # Ensure we have 3-5 channels
            if len(channels) < 3:
                # Add default channels if needed
                default_channels = [
                    ChannelAnalysis(
                        channel_name="Direct Sales",
                        rationale="Direct relationship with customers for high-value sales",
                        target_audience=business_model.target_customer,
                        cost_estimate="High initial investment, high conversion",
                        timeline="2-3 months to establish",
                        success_metrics=["Conversion rate", "Average deal size", "Sales cycle length"]
                    ),
                    ChannelAnalysis(
                        channel_name="Content Marketing",
                        rationale="Build authority and attract customers through valuable content",
                        target_audience="Decision makers researching solutions",
                        cost_estimate="Medium ongoing investment",
                        timeline="3-6 months to see results",
                        success_metrics=["Organic traffic", "Lead generation", "Content engagement"]
                    )
                ]
                
                for default_channel in default_channels:
                    if len(channels) < 5:
                        channels.append(default_channel)
            
            logger.debug(f"Identified {len(channels)} distribution channels")
            return channels[:5]  # Limit to 5 channels
            
        except Exception as e:
            logger.error(f"Channel identification failed: {e}")
            # Return default channels
            return [
                ChannelAnalysis(
                    channel_name="Digital Marketing",
                    rationale="Cost-effective customer acquisition",
                    target_audience=business_model.target_customer,
                    cost_estimate="Medium",
                    timeline="1-2 months",
                    success_metrics=["CAC", "ROAS", "Lead quality"]
                ),
                ChannelAnalysis(
                    channel_name="Partnership Sales",
                    rationale="Leverage existing relationships",
                    target_audience="Partner networks",
                    cost_estimate="Low initial, revenue share",
                    timeline="2-4 months",
                    success_metrics=["Partner acquisition", "Revenue share", "Joint deals"]
                ),
                ChannelAnalysis(
                    channel_name="Direct Outreach",
                    rationale="Targeted approach to ideal customers",
                    target_audience="Key decision makers",
                    cost_estimate="High effort, low cost",
                    timeline="Immediate",
                    success_metrics=["Response rate", "Meeting conversion", "Pipeline value"]
                )
            ]
    
    async def _develop_pricing(self, business_model: BusinessModel, competitive_analysis: List[Dict], feature_specs: List) -> PricingAnalysis:
        """Develop pricing strategy based on competitive analysis and target customer budget.
        
        Args:
            business_model: Business model data
            competitive_analysis: Competitive analysis results
            feature_specs: Feature specifications for value assessment
            
        Returns:
            Pricing analysis with strategy and justification
            
        Requirements: 5.2
        """
        logger.debug("Developing pricing strategy")
        
        # Prepare competitive pricing context
        competitive_pricing = ""
        if competitive_analysis:
            competitive_pricing = "\n".join([
                f"- {comp.get('competitor_name', 'Unknown')}: {comp.get('pricing_model', 'Unknown pricing')}"
                for comp in competitive_analysis[:3]
                if comp.get('pricing_model')
            ])
        
        # Prepare feature value context
        feature_context = ""
        if feature_specs:
            core_features = [f for f in feature_specs if hasattr(f, 'mvp_priority') and f.mvp_priority.value == 'core']
            feature_context = f"Core features: {', '.join([f.name for f in core_features[:3]])}"
        
        pricing_prompt = f"""
        Develop a comprehensive pricing strategy for this business model:

        BUSINESS MODEL:
        - Value Proposition: {business_model.value_proposition}
        - Target Customer: {business_model.target_customer}
        - Revenue Streams: {', '.join(business_model.revenue_streams)}

        COMPETITIVE PRICING:
        {competitive_pricing or "No competitive pricing data available"}

        FEATURE VALUE:
        {feature_context or "Feature specifications not available"}

        Develop a pricing strategy that considers:
        1. Target customer budget constraints
        2. Competitive positioning
        3. Value delivered by core features
        4. Revenue stream optimization

        Return in JSON format:
        {{
            "pricing_model": "<primary pricing model (subscription, one-time, usage-based, etc.)>",
            "price_point": "<specific price recommendation with currency>",
            "competitive_positioning": "<position relative to competitors (premium, competitive, value)>",
            "value_justification": "<detailed justification for the price based on value delivered>",
            "pricing_tiers": [
                {{
                    "tier_name": "<tier name>",
                    "price": "<price>",
                    "features": "<key features included>"
                }},
                ...
            ]
        }}

        Requirements:
        - Price must be realistic for the target customer segment
        - Justify pricing based on value proposition and competitive analysis
        - Consider multiple pricing tiers if appropriate
        - Align with revenue stream strategy
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a pricing strategy expert with deep knowledge of SaaS, B2B, and consumer pricing models."},
                    {"role": "user", "content": pricing_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                json_content = content[start_idx:end_idx]
            
            pricing_data = json.loads(json_content)
            
            # Create PricingAnalysis object
            pricing_analysis = PricingAnalysis(**pricing_data)
            
            logger.debug(f"Developed pricing strategy: {pricing_analysis.pricing_model} at {pricing_analysis.price_point}")
            return pricing_analysis
            
        except Exception as e:
            logger.error(f"Pricing strategy development failed: {e}")
            # Return default pricing strategy
            return PricingAnalysis(
                pricing_model="Subscription",
                price_point="$99/month",
                competitive_positioning="Competitive",
                value_justification="Priced competitively based on target customer budget and value delivered",
                pricing_tiers=[
                    {
                        "tier_name": "Starter",
                        "price": "$49/month",
                        "features": "Basic features"
                    },
                    {
                        "tier_name": "Professional",
                        "price": "$99/month",
                        "features": "All features + support"
                    }
                ]
            )
    
    async def _create_launch_sequence(self, business_model: BusinessModel, feature_specs: List, channels: List[ChannelAnalysis]) -> List[LaunchMilestone]:
        """Create launch timeline with specific milestones.
        
        Args:
            business_model: Business model data
            feature_specs: Feature specifications
            channels: Distribution channels
            
        Returns:
            List of launch milestones with timelines
            
        Requirements: 5.3
        """
        logger.debug("Creating launch timeline")
        
        # Prepare context
        channel_names = [channel.channel_name for channel in channels]
        feature_count = len(feature_specs) if feature_specs else 0
        
        timeline_prompt = f"""
        Create a comprehensive launch timeline with specific milestones for this business:

        BUSINESS MODEL:
        - Value Proposition: {business_model.value_proposition}
        - Target Customer: {business_model.target_customer}

        DISTRIBUTION CHANNELS: {', '.join(channel_names)}
        FEATURE COUNT: {feature_count} features planned

        Create a 3-phase launch timeline:
        1. MVP Launch (8-12 weeks)
        2. Product Growth (3-6 months)
        3. Market Expansion (6-12 months)

        For each phase, include specific activities, success criteria, and deliverables.

        Return in JSON format:
        {{
            "milestones": [
                {{
                    "phase": "<phase name>",
                    "timeline": "<specific timeline>",
                    "key_activities": ["<activity 1>", "<activity 2>", "<activity 3>"],
                    "success_criteria": ["<criteria 1>", "<criteria 2>", "<criteria 3>"],
                    "deliverables": ["<deliverable 1>", "<deliverable 2>", "<deliverable 3>"]
                }},
                ...
            ]
        }}

        Requirements:
        - Include specific, measurable success criteria
        - Activities should be actionable and time-bound
        - Deliverables should be concrete outputs
        - Timeline should be realistic and achievable
        - Consider channel establishment timelines
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a product launch expert with experience in startup go-to-market execution and milestone planning."},
                    {"role": "user", "content": timeline_prompt}
                ],
                temperature=0.4,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                json_content = content[start_idx:end_idx]
            
            timeline_data = json.loads(json_content)
            
            # Create LaunchMilestone objects
            milestones = []
            for milestone_info in timeline_data.get("milestones", []):
                milestone = LaunchMilestone(**milestone_info)
                milestones.append(milestone)
            
            # Ensure we have the required 3 phases
            if len(milestones) < 3:
                default_milestones = [
                    LaunchMilestone(
                        phase="MVP Launch",
                        timeline="8-12 weeks",
                        key_activities=["Complete core features", "Beta testing", "Initial marketing"],
                        success_criteria=["10 paying customers", "Product-market fit signals", "Core functionality validated"],
                        deliverables=["MVP product", "Customer feedback", "Initial revenue"]
                    ),
                    LaunchMilestone(
                        phase="Product Growth",
                        timeline="3-6 months",
                        key_activities=["Scale customer acquisition", "Feature expansion", "Channel optimization"],
                        success_criteria=["100 customers", "Positive unit economics", "Channel efficiency"],
                        deliverables=["Scaled product", "Optimized channels", "Growth metrics"]
                    ),
                    LaunchMilestone(
                        phase="Market Expansion",
                        timeline="6-12 months",
                        key_activities=["Market expansion", "Partnership development", "Product diversification"],
                        success_criteria=["Market leadership", "Sustainable growth", "Competitive advantage"],
                        deliverables=["Market presence", "Strategic partnerships", "Product portfolio"]
                    )
                ]
                
                # Fill in missing milestones
                for i, default_milestone in enumerate(default_milestones):
                    if i >= len(milestones):
                        milestones.append(default_milestone)
            
            logger.debug(f"Created launch timeline with {len(milestones)} phases")
            return milestones[:3]  # Ensure exactly 3 phases
            
        except Exception as e:
            logger.error(f"Launch timeline creation failed: {e}")
            # Return default timeline
            return [
                LaunchMilestone(
                    phase="MVP Launch",
                    timeline="8-12 weeks",
                    key_activities=["Product development", "Initial testing", "Launch preparation"],
                    success_criteria=["Product completion", "User validation", "Initial traction"],
                    deliverables=["Working product", "User feedback", "Launch plan"]
                ),
                LaunchMilestone(
                    phase="Product Growth",
                    timeline="3-6 months",
                    key_activities=["Customer acquisition", "Product improvement", "Market validation"],
                    success_criteria=["Customer growth", "Revenue targets", "Market feedback"],
                    deliverables=["Customer base", "Improved product", "Market insights"]
                ),
                LaunchMilestone(
                    phase="Market Expansion",
                    timeline="6-12 months",
                    key_activities=["Scale operations", "Expand offerings", "Build partnerships"],
                    success_criteria=["Market share", "Operational efficiency", "Strategic position"],
                    deliverables=["Scaled business", "Expanded product", "Market leadership"]
                )
            ]
    
    async def _define_success_metrics(self, business_model: BusinessModel, channels: List[ChannelAnalysis], pricing_strategy: PricingAnalysis) -> List[str]:
        """Define success metrics and competitive positioning.
        
        Args:
            business_model: Business model data
            channels: Distribution channels
            pricing_strategy: Pricing strategy
            
        Returns:
            List of success metrics
            
        Requirements: 5.4
        """
        logger.debug("Defining success metrics")
        
        # Prepare context
        channel_metrics = []
        for channel in channels:
            channel_metrics.extend(channel.success_metrics[:2])  # Take top 2 metrics per channel
        
        metrics_prompt = f"""
        Define comprehensive success metrics for this GTM strategy:

        BUSINESS MODEL:
        - Value Proposition: {business_model.value_proposition}
        - Revenue Streams: {', '.join(business_model.revenue_streams)}
        - Key Metrics: {', '.join(business_model.key_metrics)}

        PRICING STRATEGY: {pricing_strategy.pricing_model} at {pricing_strategy.price_point}

        CHANNEL METRICS: {', '.join(set(channel_metrics))}

        Define 5-8 key success metrics that cover:
        1. Revenue and financial performance
        2. Customer acquisition and retention
        3. Product adoption and engagement
        4. Market position and competitive advantage
        5. Operational efficiency

        Return as a JSON array of specific, measurable metrics:
        {{
            "success_metrics": [
                "<specific metric 1 with target>",
                "<specific metric 2 with target>",
                ...
            ]
        }}

        Requirements:
        - Metrics must be specific and measurable
        - Include target values where appropriate
        - Cover both leading and lagging indicators
        - Align with business model and revenue streams
        - Consider channel-specific performance
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a business metrics expert specializing in KPI definition and performance measurement for startups."},
                    {"role": "user", "content": metrics_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            else:
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                json_content = content[start_idx:end_idx]
            
            metrics_data = json.loads(json_content)
            success_metrics = metrics_data.get("success_metrics", [])
            
            # Ensure we have at least some metrics
            if not success_metrics:
                success_metrics = [
                    "Monthly Recurring Revenue (MRR) growth of 20%",
                    "Customer Acquisition Cost (CAC) under $100",
                    "Customer Lifetime Value (LTV) > 3x CAC",
                    "Monthly active users growth of 15%",
                    "Net Promoter Score (NPS) > 50"
                ]
            
            logger.debug(f"Defined {len(success_metrics)} success metrics")
            return success_metrics
            
        except Exception as e:
            logger.error(f"Success metrics definition failed: {e}")
            # Return default metrics
            return [
                "Revenue growth of 25% month-over-month",
                "Customer acquisition cost under industry average",
                "Customer retention rate above 85%",
                "Product adoption rate above 60%",
                "Market share growth in target segment"
            ]
    
    async def _create_competitive_positioning(self, business_model: BusinessModel, competitive_analysis: List[Dict], pricing_strategy: PricingAnalysis) -> str:
        """Create competitive positioning statement.
        
        Args:
            business_model: Business model data
            competitive_analysis: Competitive analysis results
            pricing_strategy: Pricing strategy
            
        Returns:
            Competitive positioning statement
            
        Requirements: 5.4
        """
        logger.debug("Creating competitive positioning")
        
        # Prepare competitive context
        competitive_context = ""
        if competitive_analysis:
            competitive_context = "\n".join([
                f"- {comp.get('competitor_name', 'Unknown')}: {comp.get('value_proposition', 'N/A')} "
                f"(Gaps: {', '.join(comp.get('market_gaps', [])[:2])})"
                for comp in competitive_analysis[:3]
            ])
        
        positioning_prompt = f"""
        Create a compelling competitive positioning statement for this business:

        BUSINESS MODEL:
        - Value Proposition: {business_model.value_proposition}
        - Target Customer: {business_model.target_customer}

        PRICING POSITION: {pricing_strategy.competitive_positioning} pricing at {pricing_strategy.price_point}

        COMPETITIVE LANDSCAPE:
        {competitive_context or "Limited competitive information available"}

        Create a positioning statement that:
        1. Clearly differentiates from competitors
        2. Highlights unique value proposition
        3. Addresses target customer needs
        4. Justifies pricing position
        5. Is memorable and compelling

        Return a single, concise positioning statement (2-3 sentences maximum) that can be used in marketing materials and sales conversations.

        Format: Return only the positioning statement, no additional formatting or explanation.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a brand positioning expert specializing in competitive differentiation and value proposition development."},
                    {"role": "user", "content": positioning_prompt}
                ],
                temperature=0.4,
                max_tokens=500
            )
            
            positioning_statement = response.choices[0].message.content.strip()
            
            # Clean up the response (remove quotes, extra formatting)
            positioning_statement = positioning_statement.strip('"').strip("'").strip()
            
            logger.debug("Created competitive positioning statement")
            return positioning_statement
            
        except Exception as e:
            logger.error(f"Competitive positioning creation failed: {e}")
            # Return default positioning
            return f"Unlike competitors, we deliver {business_model.value_proposition.lower()} specifically for {business_model.target_customer.lower()}, providing superior value at a competitive price point."
    
    def _estimate_budget_requirements(self, channels: List[ChannelAnalysis], pricing_strategy: PricingAnalysis) -> str:
        """Estimate budget requirements for GTM execution.
        
        Args:
            channels: Distribution channels with cost estimates
            pricing_strategy: Pricing strategy with positioning
            
        Returns:
            Budget requirements estimate
        """
        logger.debug("Estimating budget requirements")
        
        try:
            # Analyze channel costs
            high_cost_channels = [c for c in channels if "high" in c.cost_estimate.lower()]
            medium_cost_channels = [c for c in channels if "medium" in c.cost_estimate.lower()]
            low_cost_channels = [c for c in channels if "low" in c.cost_estimate.lower()]
            
            # Estimate based on channel mix and pricing position
            if len(high_cost_channels) >= 2:
                budget_level = "High"
                budget_range = "$50K-100K"
            elif len(medium_cost_channels) >= 2 or len(high_cost_channels) == 1:
                budget_level = "Medium"
                budget_range = "$20K-50K"
            else:
                budget_level = "Low"
                budget_range = "$5K-20K"
            
            # Adjust based on pricing strategy
            if "premium" in pricing_strategy.competitive_positioning.lower():
                budget_range = budget_range.replace("5K", "10K").replace("20K", "30K").replace("50K", "75K")
            
            budget_estimate = f"{budget_level} investment required ({budget_range}) for initial 6-month GTM execution, focusing on {', '.join([c.channel_name for c in channels[:2]])} as primary channels."
            
            logger.debug(f"Estimated budget: {budget_estimate}")
            return budget_estimate
            
        except Exception as e:
            logger.error(f"Budget estimation failed: {e}")
            return "Medium investment required ($20K-50K) for initial GTM execution across identified channels."