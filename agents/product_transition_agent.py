"""Product Transition Agent for 3-phase roadmap generation and execution planning."""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import openai
from pydantic import BaseModel, Field

from models.data_models import BusinessModel, FeatureSpec, GTMStrategy, ProductState

# Configure logging
logger = logging.getLogger(__name__)


class RoadmapPhase(BaseModel):
    """Structure for roadmap phase definition."""
    phase_name: str = Field(..., description="Phase name")
    timeline: str = Field(..., description="Phase timeline")
    description: str = Field(..., description="Phase description")
    key_features: List[str] = Field(..., description="Key features for this phase")
    success_criteria: List[str] = Field(..., description="Success criteria for phase completion")
    key_learnings: List[str] = Field(..., description="Expected key learnings from this phase")
    deliverables: List[str] = Field(..., description="Expected deliverables")
    risks_and_mitigation: List[str] = Field(default_factory=list, description="Risks and mitigation strategies")


class ExecutionChecklist(BaseModel):
    """Structure for execution checklist with validation items."""
    category: str = Field(..., description="Checklist category")
    validation_items: List[str] = Field(..., description="Validation items for this category")
    priority: str = Field(..., description="Priority level (High, Medium, Low)")
    responsible_role: str = Field(..., description="Role responsible for validation")


class ProductTransitionAgent:
    """Product Transition Agent for creating 3-phase roadmaps and execution planning."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-4o-mini"):
        """Initialize the Product Transition Agent.
        
        Args:
            api_key: OpenAI API key (if None, will use environment variable)
            model: LLM model to use for analysis
        """
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        self.model = model
        logger.info(f"ProductTransitionAgent initialized with model: {model}")
    
    async def generate_product_roadmap(self, state: ProductState) -> ProductState:
        """Main method to generate 3-phase product roadmap and update state.
        
        Args:
            state: Current product state with business model, features, and GTM strategy
            
        Returns:
            Updated product state with roadmap
            
        Requirements: 7.1, 7.2, 7.3, 7.4
        """
        logger.info("Starting 3-phase product roadmap generation")
        
        if not state.business_model:
            logger.error("Cannot generate roadmap without business model")
            raise ValueError("Business model is required for roadmap generation")
        
        try:
            # Step 1: Generate 3-phase roadmap
            roadmap_phases = await self._generate_roadmap_phases(
                state.business_model,
                state.feature_specifications,
                state.gtm_strategy
            )
            
            # Step 2: Generate execution checklist
            execution_checklist = await self._generate_execution_checklist(
                roadmap_phases,
                state.business_model,
                state.feature_specifications
            )
            
            # Update state with roadmap data
            roadmap_data = []
            for phase in roadmap_phases:
                roadmap_data.append({
                    "phase_name": phase.phase_name,
                    "timeline": phase.timeline,
                    "description": phase.description,
                    "key_features": phase.key_features,
                    "success_criteria": phase.success_criteria,
                    "key_learnings": phase.key_learnings,
                    "deliverables": phase.deliverables,
                    "risks_and_mitigation": phase.risks_and_mitigation
                })
            
            # Add execution checklist to roadmap data
            checklist_data = []
            for checklist in execution_checklist:
                checklist_data.append({
                    "category": checklist.category,
                    "validation_items": checklist.validation_items,
                    "priority": checklist.priority,
                    "responsible_role": checklist.responsible_role
                })
            
            # Store in mvp_roadmap field
            state.mvp_roadmap = roadmap_data
            
            # Store execution checklist in market_validation (since we can't add new fields)
            state.market_validation["execution_checklist"] = json.dumps(checklist_data)
            state.market_validation["roadmap_generated"] = datetime.now().isoformat()
            
            # Update phase and timestamp
            state.current_phase = "mvp_design"
            state.update_timestamp()
            
            logger.info("Product roadmap generation completed successfully")
            return state
            
        except Exception as e:
            logger.error(f"Product roadmap generation failed: {e}")
            # Add error information to state
            state.market_validation["roadmap_error"] = str(e)
            state.market_validation["roadmap_error_timestamp"] = datetime.now().isoformat()
            state.update_timestamp()
            return state
    
    async def _generate_roadmap_phases(
        self, 
        business_model: BusinessModel, 
        feature_specs: List[FeatureSpec], 
        gtm_strategy: Optional[GTMStrategy]
    ) -> List[RoadmapPhase]:
        """Generate 3-phase roadmap with specific timelines and success criteria.
        
        Args:
            business_model: Business model data
            feature_specs: Feature specifications
            gtm_strategy: Go-to-market strategy (optional)
            
        Returns:
            List of roadmap phases
            
        Requirements: 7.1, 7.2, 7.3
        """
        logger.debug("Generating 3-phase roadmap")
        
        # Prepare feature context
        core_features = [f.name for f in feature_specs if f.mvp_priority.value == 'core']
        important_features = [f.name for f in feature_specs if f.mvp_priority.value == 'important']
        future_features = [f.name for f in feature_specs if f.mvp_priority.value == 'future']
        
        # Prepare GTM context
        gtm_context = ""
        if gtm_strategy:
            gtm_context = f"""
            GTM STRATEGY:
            - Distribution Channels: {', '.join(gtm_strategy.distribution_channels)}
            - Pricing Strategy: {gtm_strategy.pricing_strategy}
            - Success Metrics: {', '.join(gtm_strategy.success_metrics[:3])}
            """
        
        roadmap_prompt = f"""
        Generate a comprehensive 3-phase product roadmap for transitioning from project to product mindset:

        BUSINESS MODEL:
        - Value Proposition: {business_model.value_proposition}
        - Target Customer: {business_model.target_customer}
        - Revenue Streams: {', '.join(business_model.revenue_streams)}
        - Key Metrics: {', '.join(business_model.key_metrics)}

        FEATURE SPECIFICATIONS:
        - Core Features ({len(core_features)}): {', '.join(core_features[:5])}
        - Important Features ({len(important_features)}): {', '.join(important_features[:3])}
        - Future Features ({len(future_features)}): {', '.join(future_features[:3])}

        {gtm_context}

        Create exactly 3 phases with the following structure:

        Phase 1: MVP Launch (8-12 weeks)
        - Focus on core features and initial market validation
        - Success criteria MUST include "10 paying customers" and "Product-market fit signals"
        - Key learnings about customer behavior and product-market fit

        Phase 2: Product Growth (3-6 months)
        - Scale customer acquisition and expand feature set
        - Focus on growth metrics and operational efficiency
        - Key learnings about scalability and market dynamics

        Phase 3: Market Expansion (6-12 months)
        - Market leadership and competitive advantage
        - Product diversification and strategic partnerships
        - Key learnings about market positioning and long-term strategy

        Return in JSON format:
        {{
            "phases": [
                {{
                    "phase_name": "<phase name>",
                    "timeline": "<specific timeline>",
                    "description": "<detailed phase description>",
                    "key_features": ["<feature 1>", "<feature 2>", "<feature 3>"],
                    "success_criteria": ["<criteria 1>", "<criteria 2>", "<criteria 3>"],
                    "key_learnings": ["<learning 1>", "<learning 2>", "<learning 3>"],
                    "deliverables": ["<deliverable 1>", "<deliverable 2>", "<deliverable 3>"],
                    "risks_and_mitigation": ["<risk 1: mitigation>", "<risk 2: mitigation>"]
                }},
                ...
            ]
        }}

        Requirements:
        - Phase 1 success criteria MUST include "10 paying customers" and "Product-market fit signals"
        - Each phase must have specific, measurable success criteria
        - Key learnings should focus on transitioning from project to product mindset
        - Features should align with the provided feature specifications
        - Timelines must be realistic and achievable
        - Include risk mitigation strategies for each phase
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a product roadmap expert specializing in startup product development and project-to-product transitions."},
                    {"role": "user", "content": roadmap_prompt}
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
            
            roadmap_data = json.loads(json_content)
            
            # Create RoadmapPhase objects
            phases = []
            for phase_info in roadmap_data.get("phases", []):
                phase = RoadmapPhase(**phase_info)
                phases.append(phase)
            
            # Ensure we have exactly 3 phases with required content
            if len(phases) < 3:
                # Add default phases if needed
                default_phases = [
                    RoadmapPhase(
                        phase_name="MVP Launch",
                        timeline="8-12 weeks",
                        description="Launch minimum viable product with core features and validate product-market fit",
                        key_features=core_features[:3] if core_features else ["User authentication", "Core functionality", "Basic UI"],
                        success_criteria=["10 paying customers", "Product-market fit signals", "Core functionality validated"],
                        key_learnings=["Customer behavior patterns", "Product-market fit indicators", "Core value proposition validation"],
                        deliverables=["Working MVP", "Customer feedback", "Initial revenue"],
                        risks_and_mitigation=["Low adoption: Improve onboarding", "Technical issues: Robust testing"]
                    ),
                    RoadmapPhase(
                        phase_name="Product Growth",
                        timeline="3-6 months",
                        description="Scale customer acquisition and expand feature set based on market feedback",
                        key_features=important_features[:3] if important_features else ["Advanced features", "Integrations", "Analytics"],
                        success_criteria=["100 active customers", "Positive unit economics", "Feature adoption > 60%"],
                        key_learnings=["Scalability challenges", "Customer acquisition channels", "Feature prioritization"],
                        deliverables=["Scaled product", "Optimized channels", "Growth metrics"],
                        risks_and_mitigation=["Scaling issues: Infrastructure planning", "Competition: Differentiation strategy"]
                    ),
                    RoadmapPhase(
                        phase_name="Market Expansion",
                        timeline="6-12 months",
                        description="Achieve market leadership and expand into adjacent markets or customer segments",
                        key_features=future_features[:3] if future_features else ["Enterprise features", "API platform", "Mobile app"],
                        success_criteria=["Market leadership position", "Strategic partnerships", "Sustainable competitive advantage"],
                        key_learnings=["Market dynamics", "Partnership strategies", "Long-term positioning"],
                        deliverables=["Market presence", "Strategic partnerships", "Product portfolio"],
                        risks_and_mitigation=["Market saturation: New segments", "Resource constraints: Strategic focus"]
                    )
                ]
                
                # Fill in missing phases
                for i, default_phase in enumerate(default_phases):
                    if i >= len(phases):
                        phases.append(default_phase)
            
            # Ensure Phase 1 has required success criteria
            if phases and phases[0]:
                phase1_criteria = phases[0].success_criteria
                required_criteria = ["10 paying customers", "Product-market fit signals"]
                
                for required in required_criteria:
                    if not any(required.lower() in criterion.lower() for criterion in phase1_criteria):
                        phase1_criteria.append(required)
                
                phases[0].success_criteria = phase1_criteria
            
            logger.debug(f"Generated {len(phases)} roadmap phases")
            return phases[:3]  # Ensure exactly 3 phases
            
        except Exception as e:
            logger.error(f"Roadmap phase generation failed: {e}")
            # Return default 3-phase roadmap
            return [
                RoadmapPhase(
                    phase_name="MVP Launch",
                    timeline="8-12 weeks",
                    description="Launch minimum viable product and validate market fit",
                    key_features=["Core functionality", "User authentication", "Basic UI"],
                    success_criteria=["10 paying customers", "Product-market fit signals", "Core features validated"],
                    key_learnings=["Customer needs validation", "Product-market fit", "Initial user behavior"],
                    deliverables=["Working MVP", "Customer feedback", "Market validation"],
                    risks_and_mitigation=["Low adoption: Improve UX", "Technical debt: Code reviews"]
                ),
                RoadmapPhase(
                    phase_name="Product Growth",
                    timeline="3-6 months",
                    description="Scale customer base and expand feature set",
                    key_features=["Advanced features", "Integrations", "Analytics dashboard"],
                    success_criteria=["100 active users", "Positive unit economics", "Feature adoption > 50%"],
                    key_learnings=["Scaling challenges", "Customer acquisition", "Feature prioritization"],
                    deliverables=["Scaled product", "Growth metrics", "Optimized processes"],
                    risks_and_mitigation=["Scaling issues: Infrastructure", "Competition: Differentiation"]
                ),
                RoadmapPhase(
                    phase_name="Market Expansion",
                    timeline="6-12 months",
                    description="Achieve market leadership and expand reach",
                    key_features=["Enterprise features", "API platform", "Mobile support"],
                    success_criteria=["Market leadership", "Strategic partnerships", "Sustainable growth"],
                    key_learnings=["Market dynamics", "Partnership value", "Long-term strategy"],
                    deliverables=["Market presence", "Partnerships", "Product ecosystem"],
                    risks_and_mitigation=["Market saturation: New segments", "Resources: Focus strategy"]
                )
            ]   
 
    async def _generate_execution_checklist(
        self, 
        roadmap_phases: List[RoadmapPhase], 
        business_model: BusinessModel,
        feature_specs: List[FeatureSpec]
    ) -> List[ExecutionChecklist]:
        """Generate execution checklist with 10+ validation items.
        
        Args:
            roadmap_phases: Generated roadmap phases
            business_model: Business model data
            feature_specs: Feature specifications
            
        Returns:
            List of execution checklists by category
            
        Requirements: 7.4
        """
        logger.debug("Generating execution checklist")
        
        # Prepare context from roadmap phases
        phase_context = "\n".join([
            f"- {phase.phase_name} ({phase.timeline}): {', '.join(phase.success_criteria[:2])}"
            for phase in roadmap_phases
        ])
        
        # Prepare feature context
        total_features = len(feature_specs)
        core_features_count = len([f for f in feature_specs if f.mvp_priority.value == 'core'])
        
        checklist_prompt = f"""
        Generate a comprehensive execution checklist with 10+ validation items for this product roadmap:

        BUSINESS MODEL:
        - Value Proposition: {business_model.value_proposition}
        - Target Customer: {business_model.target_customer}
        - Key Metrics: {', '.join(business_model.key_metrics)}

        ROADMAP PHASES:
        {phase_context}

        FEATURE CONTEXT:
        - Total Features: {total_features}
        - Core Features: {core_features_count}

        Create validation checklists across these categories:
        1. Product Development & Technical
        2. Market Validation & Customer
        3. Business Operations & Finance
        4. Go-to-Market & Sales
        5. Risk Management & Quality

        Each category should have 2-4 specific validation items that ensure successful execution.

        Return in JSON format:
        {{
            "checklists": [
                {{
                    "category": "<category name>",
                    "validation_items": [
                        "<specific validation item 1>",
                        "<specific validation item 2>",
                        "<specific validation item 3>"
                    ],
                    "priority": "<High/Medium/Low>",
                    "responsible_role": "<role responsible for validation>"
                }},
                ...
            ]
        }}

        Requirements:
        - Must have at least 10 total validation items across all categories
        - Each item must be specific, measurable, and actionable
        - Items should align with the roadmap phases and success criteria
        - Include both technical and business validation items
        - Specify responsible roles for accountability
        - Prioritize items based on impact and urgency
        """
        
        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an execution planning expert specializing in product development checklists and validation frameworks."},
                    {"role": "user", "content": checklist_prompt}
                ],
                temperature=0.3,
                max_tokens=2500
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
            
            checklist_data = json.loads(json_content)
            
            # Create ExecutionChecklist objects
            checklists = []
            total_items = 0
            
            for checklist_info in checklist_data.get("checklists", []):
                checklist = ExecutionChecklist(**checklist_info)
                checklists.append(checklist)
                total_items += len(checklist.validation_items)
            
            # Ensure we have at least 10 validation items
            if total_items < 10:
                # Add default checklists to reach 10+ items
                default_checklists = [
                    ExecutionChecklist(
                        category="Product Development",
                        validation_items=[
                            "Core features implemented and tested",
                            "User acceptance testing completed",
                            "Performance benchmarks met",
                            "Security audit passed"
                        ],
                        priority="High",
                        responsible_role="Development Team"
                    ),
                    ExecutionChecklist(
                        category="Market Validation",
                        validation_items=[
                            "Customer interviews conducted (min 20)",
                            "Product-market fit metrics established",
                            "Pricing strategy validated with customers",
                            "Competitive analysis updated"
                        ],
                        priority="High",
                        responsible_role="Product Manager"
                    ),
                    ExecutionChecklist(
                        category="Business Operations",
                        validation_items=[
                            "Revenue model validated",
                            "Unit economics positive",
                            "Customer support processes established",
                            "Legal and compliance requirements met"
                        ],
                        priority="Medium",
                        responsible_role="Business Operations"
                    )
                ]
                
                # Add missing items to reach 10+
                for default_checklist in default_checklists:
                    if total_items >= 10:
                        break
                    
                    # Check if category already exists
                    existing_categories = [c.category for c in checklists]
                    if default_checklist.category not in existing_categories:
                        checklists.append(default_checklist)
                        total_items += len(default_checklist.validation_items)
            
            logger.debug(f"Generated execution checklist with {total_items} validation items across {len(checklists)} categories")
            return checklists
            
        except Exception as e:
            logger.error(f"Execution checklist generation failed: {e}")
            # Return default comprehensive checklist with 10+ items
            return [
                ExecutionChecklist(
                    category="Product Development & Technical",
                    validation_items=[
                        "All core features implemented and tested",
                        "User acceptance testing completed with 90%+ satisfaction",
                        "Performance benchmarks met (load time < 3s)",
                        "Security audit passed with no critical issues"
                    ],
                    priority="High",
                    responsible_role="Development Team"
                ),
                ExecutionChecklist(
                    category="Market Validation & Customer",
                    validation_items=[
                        "Customer interviews conducted (minimum 20)",
                        "Product-market fit signals validated",
                        "Customer acquisition cost (CAC) calculated",
                        "Customer lifetime value (LTV) established"
                    ],
                    priority="High",
                    responsible_role="Product Manager"
                ),
                ExecutionChecklist(
                    category="Business Operations & Finance",
                    validation_items=[
                        "Revenue model validated with paying customers",
                        "Unit economics are positive (LTV > 3x CAC)",
                        "Financial projections updated and realistic",
                        "Legal and compliance requirements met"
                    ],
                    priority="Medium",
                    responsible_role="Business Operations"
                ),
                ExecutionChecklist(
                    category="Go-to-Market & Sales",
                    validation_items=[
                        "Sales process documented and tested",
                        "Marketing channels identified and validated",
                        "Customer onboarding process optimized",
                        "Success metrics and KPIs defined"
                    ],
                    priority="Medium",
                    responsible_role="Marketing/Sales Team"
                ),
                ExecutionChecklist(
                    category="Risk Management & Quality",
                    validation_items=[
                        "Risk assessment completed for all phases",
                        "Quality assurance processes established",
                        "Backup and disaster recovery plans tested",
                        "Team capacity and resource allocation validated"
                    ],
                    priority="Low",
                    responsible_role="Project Manager"
                )
            ]
    
    def get_roadmap_summary(self, state: ProductState) -> Dict[str, Any]:
        """Get a summary of the generated roadmap for display purposes.
        
        Args:
            state: Product state with roadmap data
            
        Returns:
            Dictionary with roadmap summary
        """
        if not state.mvp_roadmap:
            return {"error": "No roadmap generated"}
        
        summary = {
            "total_phases": len(state.mvp_roadmap),
            "phases": []
        }
        
        for phase_data in state.mvp_roadmap:
            phase_summary = {
                "name": phase_data.get("phase_name", "Unknown"),
                "timeline": phase_data.get("timeline", "Unknown"),
                "key_features_count": len(phase_data.get("key_features", [])),
                "success_criteria_count": len(phase_data.get("success_criteria", [])),
                "deliverables_count": len(phase_data.get("deliverables", []))
            }
            summary["phases"].append(phase_summary)
        
        # Add execution checklist summary if available
        if "execution_checklist" in state.market_validation:
            try:
                checklist_data = json.loads(state.market_validation["execution_checklist"])
                total_validation_items = sum(len(item.get("validation_items", [])) for item in checklist_data)
                summary["execution_checklist"] = {
                    "categories": len(checklist_data),
                    "total_validation_items": total_validation_items
                }
            except (json.JSONDecodeError, KeyError):
                summary["execution_checklist"] = {"error": "Invalid checklist data"}
        
        return summary