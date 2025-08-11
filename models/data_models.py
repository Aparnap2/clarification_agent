"""Core Pydantic data models for AI Strategy Assistant."""

from datetime import datetime
from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, field_validator

from .enums import MarketValidationLevel, MVPPriority


class BusinessModel(BaseModel):
    """Business model data structure with validation."""
    value_proposition: str = Field(..., description="Clear value proposition in one sentence")
    target_customer: str = Field(..., description="Target customer description")
    revenue_streams: List[str] = Field(..., min_items=1, description="List of revenue streams")
    cost_structure: List[str] = Field(default_factory=list, description="Cost structure components")
    key_metrics: List[str] = Field(..., min_items=1, description="Key business metrics")
    
    @field_validator('value_proposition')
    @classmethod
    def validate_value_prop_length(cls, v):
        """Validate value proposition is concise (max 20 words)."""
        if len(v.split()) > 20:
            raise ValueError('Value proposition must be concise (max 20 words)')
        return v.strip()
    
    @field_validator('target_customer')
    @classmethod
    def validate_target_customer(cls, v):
        """Validate target customer is not empty."""
        if not v.strip():
            raise ValueError('Target customer cannot be empty')
        return v.strip()


class FeatureSpec(BaseModel):
    """Feature specification with validation."""
    name: str = Field(..., description="Feature name")
    user_story: str = Field(..., description="User story description")
    acceptance_criteria: List[str] = Field(..., min_items=3, description="Acceptance criteria list")
    mvp_priority: MVPPriority = Field(..., description="MVP priority level")
    effort_estimate: Literal["XS", "S", "M", "L", "XL"] = Field(..., description="Effort estimate")
    business_impact: Literal["Low", "Medium", "High", "Critical"] = Field(..., description="Business impact level")
    validation_level: MarketValidationLevel = Field(
        default=MarketValidationLevel.ASSUMPTION, 
        description="Market validation level"
    )
    dependencies: List[str] = Field(default_factory=list, description="Feature dependencies")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate feature name is not empty."""
        if not v.strip():
            raise ValueError('Feature name cannot be empty')
        return v.strip()
    
    @field_validator('user_story')
    @classmethod
    def validate_user_story(cls, v):
        """Validate user story follows proper format."""
        if not v.strip():
            raise ValueError('User story cannot be empty')
        # Check for basic user story format
        story_lower = v.lower()
        if not ('as a' in story_lower or 'as an' in story_lower):
            raise ValueError('User story should follow "As a [role], I want [feature], so that [benefit]" format')
        return v.strip()
    
    @field_validator('acceptance_criteria')
    @classmethod
    def validate_acceptance_criteria_format(cls, v):
        """Validate acceptance criteria follow EARS format."""
        if len(v) < 3:
            raise ValueError('At least 3 acceptance criteria are required')
        
        for criterion in v:
            if not criterion.strip():
                raise ValueError('Acceptance criteria cannot be empty')
            
            criterion_upper = criterion.upper()
            ears_keywords = ['WHEN', 'THEN', 'SHALL', 'IF', 'GIVEN']
            if not any(keyword in criterion_upper for keyword in ears_keywords):
                raise ValueError(
                    f'Acceptance criteria must follow EARS format with keywords: {", ".join(ears_keywords)}'
                )
        
        return [c.strip() for c in v]


class GTMStrategy(BaseModel):
    """Go-to-Market strategy data structure."""
    distribution_channels: List[str] = Field(..., min_items=3, max_items=5, description="Distribution channels")
    pricing_strategy: str = Field(..., description="Pricing strategy description")
    launch_timeline: Dict[str, str] = Field(..., description="Launch timeline with milestones")
    success_metrics: List[str] = Field(..., min_items=1, description="Success metrics")
    competitive_positioning: str = Field(..., description="Competitive positioning statement")
    budget_requirements: Optional[str] = Field(None, description="Budget requirements")
    
    @field_validator('distribution_channels')
    @classmethod
    def validate_channels(cls, v):
        """Validate distribution channels are specific and actionable."""
        if len(v) < 3:
            raise ValueError('At least 3 distribution channels are required')
        if len(v) > 5:
            raise ValueError('Maximum 5 distribution channels allowed')
        
        for channel in v:
            if not channel.strip():
                raise ValueError('Distribution channels cannot be empty')
        
        return [c.strip() for c in v]
    
    @field_validator('pricing_strategy')
    @classmethod
    def validate_pricing_strategy(cls, v):
        """Validate pricing strategy is not empty."""
        if not v.strip():
            raise ValueError('Pricing strategy cannot be empty')
        return v.strip()
    
    @field_validator('launch_timeline')
    @classmethod
    def validate_launch_timeline(cls, v):
        """Validate launch timeline has required milestones."""
        if not v:
            raise ValueError('Launch timeline cannot be empty')
        
        required_phases = ['mvp_launch', 'growth', 'expansion']
        for phase in required_phases:
            if phase not in v:
                raise ValueError(f'Launch timeline must include {phase} phase')
        
        return v


class ClarificationQuestion(BaseModel):
    """Clarification question model for requirements analysis."""
    id: str = Field(..., description="Unique question identifier")
    text: str = Field(..., description="Question text")
    category: Literal["functional", "nfr", "data", "integration", "compliance"] = Field(..., description="Question category")
    priority: int = Field(..., ge=1, le=10, description="Question priority (1-10)")
    rationale: str = Field(..., description="Rationale for asking this question")
    blocking: bool = Field(default=False, description="Whether this question blocks progress")
    
    @field_validator('text')
    @classmethod
    def validate_question_text(cls, v):
        """Validate question text is not empty and ends with question mark."""
        if not v.strip():
            raise ValueError('Question text cannot be empty')
        if not v.strip().endswith('?'):
            raise ValueError('Question text must end with a question mark')
        return v.strip()
    
    @field_validator('rationale')
    @classmethod
    def validate_rationale(cls, v):
        """Validate rationale is not empty."""
        if not v.strip():
            raise ValueError('Question rationale cannot be empty')
        return v.strip()


class GapItem(BaseModel):
    """Gap analysis item for requirements assessment."""
    id: str = Field(..., description="Unique gap identifier")
    type: Literal["functional", "nfr", "data", "integration", "compliance"] = Field(..., description="Gap type")
    description: str = Field(..., description="Gap description")
    impact: Literal["low", "medium", "high", "critical"] = Field(..., description="Impact level")
    suggested_ac: Optional[str] = Field(None, description="Suggested acceptance criteria")
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        """Validate gap description is not empty."""
        if not v.strip():
            raise ValueError('Gap description cannot be empty')
        return v.strip()
    
    @field_validator('suggested_ac')
    @classmethod
    def validate_suggested_ac(cls, v):
        """Validate suggested acceptance criteria format if provided."""
        if v is not None and v.strip():
            # Check for basic EARS format keywords
            ac_upper = v.upper()
            ears_keywords = ['WHEN', 'THEN', 'SHALL', 'IF', 'GIVEN']
            if not any(keyword in ac_upper for keyword in ears_keywords):
                raise ValueError(
                    f'Suggested acceptance criteria should follow EARS format with keywords: {", ".join(ears_keywords)}'
                )
            return v.strip()
        return v


class RiskItem(BaseModel):
    """Risk assessment item for requirements analysis."""
    id: str = Field(..., description="Unique risk identifier")
    description: str = Field(..., description="Risk description")
    impact: Literal["low", "medium", "high", "critical"] = Field(..., description="Risk impact level")
    likelihood: Literal["low", "medium", "high"] = Field(..., description="Risk likelihood")
    mitigation: Optional[str] = Field(None, description="Risk mitigation strategy")
    
    @field_validator('description')
    @classmethod
    def validate_risk_description(cls, v):
        """Validate risk description is not empty."""
        if not v.strip():
            raise ValueError('Risk description cannot be empty')
        return v.strip()


class AcceptanceCriterion(BaseModel):
    """Acceptance criterion model with EARS format validation."""
    id: str = Field(..., description="Unique criterion identifier")
    text: str = Field(..., description="Acceptance criterion text")
    requirement_id: Optional[str] = Field(None, description="Associated requirement ID")
    testable: bool = Field(default=True, description="Whether criterion is testable")
    
    @field_validator('text')
    @classmethod
    def validate_ears_format(cls, v):
        """Validate acceptance criterion follows EARS format."""
        if not v.strip():
            raise ValueError('Acceptance criterion text cannot be empty')
        
        # Check for EARS format keywords
        criterion_upper = v.upper()
        ears_keywords = ['WHEN', 'THEN', 'SHALL', 'IF', 'GIVEN']
        if not any(keyword in criterion_upper for keyword in ears_keywords):
            raise ValueError(
                f'Acceptance criterion must follow EARS format with keywords: {", ".join(ears_keywords)}'
            )
        return v.strip()


class ClarificationReport(BaseModel):
    """Comprehensive clarification report aggregating analysis results."""
    questions: List[ClarificationQuestion] = Field(default_factory=list, description="Generated clarification questions")
    gaps: List[GapItem] = Field(default_factory=list, description="Identified requirement gaps")
    risks: List[RiskItem] = Field(default_factory=list, description="Identified risks")
    acceptance_criteria: List[AcceptanceCriterion] = Field(default_factory=list, description="Generated acceptance criteria")
    sources: List[str] = Field(default_factory=list, description="Source documents or URLs")
    workflow_checkpoint_id: Optional[str] = Field(None, description="Associated checkpoint ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Report creation timestamp")
    
    @field_validator('questions')
    @classmethod
    def validate_questions_limit(cls, v):
        """Validate reasonable number of questions."""
        if len(v) > 50:
            raise ValueError('Maximum 50 clarification questions allowed per report')
        return v
    
    @field_validator('gaps')
    @classmethod
    def validate_gaps_limit(cls, v):
        """Validate reasonable number of gaps."""
        if len(v) > 30:
            raise ValueError('Maximum 30 gap items allowed per report')
        return v


class ProductState(BaseModel):
    """Primary state container for the product development workflow."""
    user_query: str = Field(..., description="Initial user query/project description")
    business_model: Optional[BusinessModel] = Field(None, description="Business model")
    target_personas: List[Dict] = Field(default_factory=list, description="Target customer personas")
    feature_specifications: List[FeatureSpec] = Field(default_factory=list, description="Feature specifications")
    gtm_strategy: Optional[GTMStrategy] = Field(None, description="Go-to-market strategy")
    competitive_analysis: List[Dict] = Field(default_factory=list, description="Competitive analysis data")
    mvp_roadmap: List[Dict] = Field(default_factory=list, description="MVP roadmap")
    technical_architecture: Optional[Dict] = Field(None, description="Technical architecture")
    market_validation: Dict[str, str] = Field(default_factory=dict, description="Market validation results")
    research_data: List[Dict] = Field(default_factory=list, description="Web research data")
    current_phase: Literal["discovery", "validation", "planning", "mvp_design", "gtm_planning"] = Field(
        default="discovery", 
        description="Current workflow phase"
    )
    # New clarification support fields
    clarification_questions: List['ClarificationQuestion'] = Field(default_factory=list, description="Generated clarification questions")
    answered_questions: Dict[str, str] = Field(default_factory=dict, description="User answers to clarification questions")
    gap_analysis: List['GapItem'] = Field(default_factory=list, description="Identified gaps in requirements")
    checkpoint_history: List[str] = Field(default_factory=list, description="History of checkpoint IDs")
    # Checkpoint integration fields
    workflow_checkpoint_id: Optional[str] = Field(None, description="Current checkpoint identifier")
    # Existing fields
    session_id: Optional[str] = Field(None, description="Session identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    version: str = Field(default="2.0", description="Model version for backward compatibility")
    
    @field_validator('user_query')
    @classmethod
    def validate_user_query(cls, v):
        """Validate user query with comprehensive error messages."""
        if not v or not v.strip():
            raise ValueError('User query cannot be empty. Please provide a clear description of your project idea or business concept.')
        
        if len(v.strip()) < 10:
            raise ValueError('User query is too short. Please provide at least 10 characters describing your project idea.')
        
        if len(v.strip()) > 5000:
            raise ValueError('User query is too long. Please limit your description to 5000 characters or less.')
        
        return v.strip()
    
    @field_validator('clarification_questions')
    @classmethod
    def validate_clarification_questions_limit(cls, v):
        """Validate reasonable number of clarification questions."""
        if len(v) > 100:
            raise ValueError('Maximum 100 clarification questions allowed. Consider prioritizing the most critical questions.')
        return v
    
    @field_validator('answered_questions')
    @classmethod
    def validate_answered_questions(cls, v):
        """Validate answered questions format."""
        for question_id, answer in v.items():
            if not question_id.strip():
                raise ValueError('Question ID cannot be empty in answered_questions.')
            if not answer or not answer.strip():
                raise ValueError(f'Answer for question {question_id} cannot be empty.')
        return v
    
    @field_validator('gap_analysis')
    @classmethod
    def validate_gap_analysis_limit(cls, v):
        """Validate reasonable number of gap analysis items."""
        if len(v) > 50:
            raise ValueError('Maximum 50 gap analysis items allowed. Consider consolidating similar gaps.')
        return v
    
    @field_validator('checkpoint_history')
    @classmethod
    def validate_checkpoint_history(cls, v):
        """Validate checkpoint history format."""
        if len(v) > 1000:
            raise ValueError('Checkpoint history is too long. Consider archiving older checkpoints.')
        
        for checkpoint_id in v:
            if not checkpoint_id or not checkpoint_id.strip():
                raise ValueError('Checkpoint ID cannot be empty in checkpoint history.')
        
        return v
    
    def update_timestamp(self):
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()
    
    def create_checkpoint(self) -> str:
        """
        Create a new checkpoint using existing update_timestamp pattern.
        
        Returns:
            Generated checkpoint identifier
        """
        # Generate checkpoint ID using session_id and timestamp pattern
        checkpoint_id = f"{self.session_id or 'unknown'}_{datetime.now().isoformat()}"
        
        # Update timestamp using existing pattern
        self.update_timestamp()
        
        # Set current checkpoint ID
        self.workflow_checkpoint_id = checkpoint_id
        
        # Add to checkpoint history if not already present
        if checkpoint_id not in self.checkpoint_history:
            self.checkpoint_history.append(checkpoint_id)
        
        return checkpoint_id
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True,
        # Checkpoint settings for SQLite integration
        "checkpoint_enabled": True,
        "checkpoint_namespace": "ai_strategy_assistant"
    }