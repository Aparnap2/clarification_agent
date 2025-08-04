"""Business Process Analysis (BPA) Agent for structured business validation and planning."""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import openai
from pydantic import BaseModel, Field

from models.data_models import BusinessModel, FeatureSpec, ProductState
from models.enums import MarketValidationLevel, MVPPriority

# Configure logging
logger = logging.getLogger(__name__)


class ProblemValidationResult(BaseModel):
    """Structure for problem validation results."""
    problem_score: int = Field(..., ge=1, le=10, description="Problem severity score (1-10)")
    market_size_score: int = Field(..., ge=1, le=10, description="Market size score (1-10)")
    solution_fit_score: int = Field(..., ge=1, le=10, description="Solution fit score (1-10)")
    overall_score: float = Field(..., ge=1.0, le=10.0, description="Overall viability score")
    reasoning: str = Field(..., description="Detailed reasoning for the scores")
    recommendations: List[str] = Field(..., description="Recommendations based on analysis")
    should_continue: bool = Field(..., description="Whether development should continue")
    validation_questions: List[str] = Field(default_factory=list, description="Additional validation questions")


class CompetitorAnalysis(BaseModel):
    """Structure for competitor analysis results."""
    competitor_name: str = Field(..., description="Competitor name")
    value_proposition: str = Field(..., description="Competitor's value proposition")
    target_market: str = Field(..., description="Competitor's target market")
    pricing_model: Optional[str] = Field(None, description="Pricing model")
    key_strengths: List[str] = Field(default_factory=list, description="Key competitive strengths")
    market_gaps: List[str] = Field(default_factory=list, description="Identified market gaps")
    differentiation_opportunities: List[str] = Field(default_factory=list, description="Opportunities for differentiation")


class BPAAgent:
    """Business Process Analysis Agent with LLM integration for business validation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-4o-mini"):
        """Initialize the BPA Agent.
        
        Args:
            api_key: OpenAI API key (if None, will use environment variable)
            model: LLM model to use for analysis
        """
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model
        logger.info(f"BPAAgent initialized with model: {model}")
    
    async def analyze_business_viability(self, state: ProductState) -> ProductState:
        """Main method to analyze business viability and update state.
        
        Args:
            state: Current product state
            
        Returns:
            Updated product state with business analysis
            
        Requirements: 1.1, 1.2, 1.3
        """
        logger.info(f"Starting business viability analysis for: {state.user_query}")
        
        try:
            # Step 1: Validate problem space
            problem_validation = await self._validate_problem_space(state.user_query)
            
            # Update market validation in state
            state.market_validation.update({
                "problem_score": str(problem_validation.problem_score),
                "market_size_score": str(problem_validation.market_size_score),
                "solution_fit_score": str(problem_validation.solution_fit_score),
                "overall_score": str(problem_validation.overall_score),
                "reasoning": problem_validation.reasoning,
                "should_continue": str(problem_validation.should_continue),
                "validation_timestamp": datetime.now().isoformat()
            })
            
            # Validation gate: Stop if score is below 7
            if problem_validation.overall_score < 7.0:
                logger.warning(f"Business validation failed with score {problem_validation.overall_score}")
                state.current_phase = "validation"
                state.update_timestamp()
                return state
            
            # Step 2: Generate business model
            business_model = await self._generate_business_model(state.user_query, problem_validation)
            state.business_model = business_model
            
            # Step 3: Analyze competitors
            competitive_analysis = await self._analyze_competitors(business_model.target_customer, state.user_query)
            state.competitive_analysis = [comp.dict() for comp in competitive_analysis]
            
            # Step 4: Generate MVP features
            mvp_features = await self._generate_mvp_features(business_model, competitive_analysis)
            state.feature_specifications = mvp_features
            
            # Update phase and timestamp
            state.current_phase = "planning"
            state.update_timestamp()
            
            logger.info("Business viability analysis completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Business viability analysis failed: {e}")
            # Add error information to state but don't fail completely
            state.market_validation["error"] = str(e)
            state.market_validation["error_timestamp"] = datetime.now().isoformat()
            state.update_timestamp()
            return state
    
    async def _validate_problem_space(self, user_query: str) -> ProblemValidationResult:
        """Validate the problem space with 1-10 scoring system.
        
        Args:
            user_query: User's project description
            
        Returns:
            Problem validation result with scores and recommendations
            
        Requirements: 1.1, 1.3 (validation gates)
        """
        logger.debug("Validating problem space")
        
        validation_prompt = f"""
        Analyze the following project idea for business viability. Provide scores from 1-10 for each criterion:

        PROJECT IDEA: {user_query}

        Evaluate on these criteria:
        1. PROBLEM SEVERITY (1-10): How severe/painful is the problem being solved?
        2. MARKET SIZE (1-10): How large is the potential market?
        3. SOLUTION FIT (1-10): How well does the proposed solution fit the problem?

        Provide your analysis in the following JSON format:
        {{
            "problem_score": <1-10 integer>,
            "market_size_score": <1-10 integer>,
            "solution_fit_score": <1-10 integer>,
            "overall_score": <calculated average as float>,
            "reasoning": "<detailed explanation of scores>",
            "recommendations": ["<recommendation 1>", "<recommendation 2>", ...],
            "should_continue": <true if overall_score >= 7, false otherwise>,
            "validation_questions": ["<question 1>", "<question 2>", ...]
        }}

        Be critical but fair. A score below 7 means the project should not proceed without significant changes.
        Include 3-5 specific validation questions that would help clarify the business opportunity.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a business analyst expert in startup validation and market analysis."},
                    {"role": "user", "content": validation_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response (handle potential markdown formatting)
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                json_content = content[json_start:json_end].strip()
            elif content.startswith("{") and content.endswith("}"):
                json_content = content
            else:
                # Try to find JSON-like content
                start_idx = content.find("{")
                end_idx = content.rfind("}") + 1
                json_content = content[start_idx:end_idx]
            
            validation_data = json.loads(json_content)
            
            # Calculate overall score if not provided
            if "overall_score" not in validation_data:
                validation_data["overall_score"] = (
                    validation_data["problem_score"] + 
                    validation_data["market_size_score"] + 
                    validation_data["solution_fit_score"]
                ) / 3.0
            
            # Ensure should_continue is set correctly
            validation_data["should_continue"] = validation_data["overall_score"] >= 7.0
            
            result = ProblemValidationResult(**validation_data)
            logger.debug(f"Problem validation completed with overall score: {result.overall_score}")
            
            return result
            
        except Exception as e:
            logger.error(f"Problem validation failed: {e}")
            # Return a default low-score result to prevent progression
            return ProblemValidationResult(
                problem_score=3,
                market_size_score=3,
                solution_fit_score=3,
                overall_score=3.0,
                reasoning=f"Validation failed due to error: {str(e)}",
                recommendations=["Fix validation process", "Provide clearer project description"],
                should_continue=False,
                validation_questions=["What specific problem are you solving?", "Who is your target customer?"]
            )
    
    async def _generate_business_model(self, user_query: str, problem_validation: ProblemValidationResult) -> BusinessModel:
        """Generate business model with competitive analysis.
        
        Args:
            user_query: User's project description
            problem_validation: Results from problem validation
            
        Returns:
            BusinessModel object with validated data
            
        Requirements: 1.2, 2.1, 2.2
        """
        logger.debug("Generating business model")
        
        business_model_prompt = f"""
        Based on the validated project idea and analysis, create a comprehensive business model.

        PROJECT IDEA: {user_query}
        
        VALIDATION RESULTS:
        - Problem Score: {problem_validation.problem_score}/10
        - Market Size Score: {problem_validation.market_size_score}/10
        - Solution Fit Score: {problem_validation.solution_fit_score}/10
        - Reasoning: {problem_validation.reasoning}

        Create a business model in the following JSON format:
        {{
            "value_proposition": "<clear value proposition in max 20 words>",
            "target_customer": "<detailed target customer description>",
            "revenue_streams": ["<revenue stream 1>", "<revenue stream 2>", ...],
            "cost_structure": ["<cost item 1>", "<cost item 2>", ...],
            "key_metrics": ["<metric 1>", "<metric 2>", ...]
        }}

        Requirements:
        - Value proposition MUST be 20 words or less
        - Include at least 1 revenue stream
        - Include at least 3 key metrics
        - Target customer should be specific (industry, company size, role, pain points)
        - Revenue streams should be realistic and specific
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a business model expert specializing in startup business models and value propositions."},
                    {"role": "user", "content": business_model_prompt}
                ],
                temperature=0.4,
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
            
            business_data = json.loads(json_content)
            
            # Create and validate BusinessModel
            business_model = BusinessModel(**business_data)
            logger.debug(f"Business model generated for target: {business_model.target_customer}")
            
            return business_model
            
        except Exception as e:
            logger.error(f"Business model generation failed: {e}")
            # Return a minimal valid business model
            return BusinessModel(
                value_proposition="Solve customer problems efficiently",
                target_customer="Small to medium businesses needing efficiency solutions",
                revenue_streams=["Subscription fees"],
                cost_structure=["Development costs", "Marketing costs"],
                key_metrics=["Monthly Recurring Revenue", "Customer Acquisition Cost", "Customer Lifetime Value"]
            )
    
    async def _analyze_competitors(self, target_customer: str, user_query: str) -> List[CompetitorAnalysis]:
        """Analyze competitors with market gap identification.
        
        Args:
            target_customer: Target customer description
            user_query: Original project description
            
        Returns:
            List of competitor analysis results
            
        Requirements: 1.2 (competitive analysis)
        """
        logger.debug("Analyzing competitors")
        
        competitor_prompt = f"""
        Analyze the competitive landscape for this project:

        PROJECT: {user_query}
        TARGET CUSTOMER: {target_customer}

        Identify 3-5 main competitors and analyze them. For each competitor, provide:

        Return analysis in the following JSON format:
        {{
            "competitors": [
                {{
                    "competitor_name": "<competitor name>",
                    "value_proposition": "<their value proposition>",
                    "target_market": "<their target market>",
                    "pricing_model": "<their pricing model if known>",
                    "key_strengths": ["<strength 1>", "<strength 2>", ...],
                    "market_gaps": ["<gap 1>", "<gap 2>", ...],
                    "differentiation_opportunities": ["<opportunity 1>", "<opportunity 2>", ...]
                }},
                ...
            ]
        }}

        Focus on identifying market gaps and differentiation opportunities that the new project could exploit.
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a competitive analysis expert with deep knowledge of market positioning and differentiation strategies."},
                    {"role": "user", "content": competitor_prompt}
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
            
            competitor_data = json.loads(json_content)
            
            # Create CompetitorAnalysis objects
            competitors = []
            for comp_data in competitor_data.get("competitors", []):
                competitor = CompetitorAnalysis(**comp_data)
                competitors.append(competitor)
            
            logger.debug(f"Analyzed {len(competitors)} competitors")
            return competitors
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            # Return a minimal competitor analysis
            return [
                CompetitorAnalysis(
                    competitor_name="Generic Competitor",
                    value_proposition="Similar solution in the market",
                    target_market=target_customer,
                    pricing_model="Unknown",
                    key_strengths=["Established presence"],
                    market_gaps=["Limited customization", "Poor user experience"],
                    differentiation_opportunities=["Better UX", "More features", "Lower cost"]
                )
            ]
    
    async def _generate_mvp_features(self, business_model: BusinessModel, competitive_analysis: List[CompetitorAnalysis]) -> List[FeatureSpec]:
        """Generate MVP feature specifications following user story format.
        
        Args:
            business_model: Business model data
            competitive_analysis: Competitor analysis results
            
        Returns:
            List of FeatureSpec objects for MVP
            
        Requirements: 4.1, 4.2, 4.3, 4.4
        """
        logger.debug("Generating MVP features")
        
        # Prepare competitive context
        competitive_context = "\n".join([
            f"- {comp.competitor_name}: {comp.value_proposition} (Gaps: {', '.join(comp.market_gaps[:2])})"
            for comp in competitive_analysis[:3]
        ])
        
        mvp_prompt = f"""
        Generate 5-8 MVP feature specifications based on the business model and competitive analysis.

        BUSINESS MODEL:
        - Value Proposition: {business_model.value_proposition}
        - Target Customer: {business_model.target_customer}
        - Revenue Streams: {', '.join(business_model.revenue_streams)}

        COMPETITIVE LANDSCAPE:
        {competitive_context}

        For each feature, provide:
        1. Name: Clear, descriptive feature name
        2. User Story: "As a [role], I want [feature], so that [benefit]" format
        3. Acceptance Criteria: At least 3 criteria using EARS format (WHEN/THEN/SHALL/IF/GIVEN)
        4. MVP Priority: CORE (max 2-3), IMPORTANT, or FUTURE
        5. Effort Estimate: XS, S, M, L, or XL
        6. Business Impact: Low, Medium, High, or Critical

        Return in JSON format:
        {{
            "features": [
                {{
                    "name": "<feature name>",
                    "user_story": "<user story>",
                    "acceptance_criteria": ["<criteria 1>", "<criteria 2>", "<criteria 3>"],
                    "mvp_priority": "<CORE/IMPORTANT/FUTURE>",
                    "effort_estimate": "<XS/S/M/L/XL>",
                    "business_impact": "<Low/Medium/High/Critical>",
                    "validation_level": "assumption",
                    "dependencies": ["<dependency 1>", ...]
                }},
                ...
            ]
        }}

        Requirements:
        - Only 2-3 features should be marked as CORE priority
        - Each feature must have at least 3 acceptance criteria
        - User stories must follow the specified format
        - Focus on features that differentiate from competitors
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a product manager expert in MVP planning and feature specification using agile methodologies."},
                    {"role": "user", "content": mvp_prompt}
                ],
                temperature=0.4,
                max_tokens=3000
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
            
            feature_data = json.loads(json_content)
            
            # Create FeatureSpec objects
            features = []
            core_count = 0
            
            for feat_data in feature_data.get("features", []):
                # Ensure validation_level is set
                if "validation_level" not in feat_data:
                    feat_data["validation_level"] = "assumption"
                
                # Convert string enums to proper enum values
                if feat_data.get("mvp_priority") == "CORE":
                    feat_data["mvp_priority"] = MVPPriority.CORE
                    core_count += 1
                elif feat_data.get("mvp_priority") == "IMPORTANT":
                    feat_data["mvp_priority"] = MVPPriority.IMPORTANT
                else:
                    feat_data["mvp_priority"] = MVPPriority.FUTURE
                
                # Limit core features to 3
                if feat_data["mvp_priority"] == MVPPriority.CORE and core_count > 3:
                    feat_data["mvp_priority"] = MVPPriority.IMPORTANT
                
                # Set validation level enum
                feat_data["validation_level"] = MarketValidationLevel.ASSUMPTION
                
                try:
                    feature = FeatureSpec(**feat_data)
                    features.append(feature)
                except Exception as validation_error:
                    logger.warning(f"Feature validation failed: {validation_error}")
                    # Skip invalid features rather than failing completely
                    continue
            
            logger.debug(f"Generated {len(features)} MVP features ({core_count} core)")
            
            # Ensure we have at least some features
            if not features:
                # Create a minimal feature set
                features = [
                    FeatureSpec(
                        name="User Registration",
                        user_story=f"As a {business_model.target_customer.split()[0].lower()}, I want to create an account, so that I can access the platform",
                        acceptance_criteria=[
                            "WHEN a user provides valid email and password THEN the system SHALL create a new account",
                            "WHEN account creation is successful THEN the system SHALL send a confirmation email",
                            "GIVEN an existing email WHEN user tries to register THEN the system SHALL show an error message"
                        ],
                        mvp_priority=MVPPriority.CORE,
                        effort_estimate="S",
                        business_impact="High",
                        validation_level=MarketValidationLevel.ASSUMPTION,
                        dependencies=[]
                    )
                ]
            
            return features
            
        except Exception as e:
            logger.error(f"MVP feature generation failed: {e}")
            # Return minimal feature set
            return [
                FeatureSpec(
                    name="Core Functionality",
                    user_story="As a user, I want basic functionality, so that I can solve my problem",
                    acceptance_criteria=[
                        "WHEN user accesses the system THEN it SHALL provide core functionality",
                        "WHEN user performs main action THEN the system SHALL respond appropriately",
                        "GIVEN valid input WHEN user submits THEN the system SHALL process successfully"
                    ],
                    mvp_priority=MVPPriority.CORE,
                    effort_estimate="M",
                    business_impact="Critical",
                    validation_level=MarketValidationLevel.ASSUMPTION,
                    dependencies=[]
                )
            ]