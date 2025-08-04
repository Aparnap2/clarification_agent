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
    session_id: Optional[str] = Field(None, description="Session identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @field_validator('user_query')
    @classmethod
    def validate_user_query(cls, v):
        """Validate user query is not empty."""
        if not v.strip():
            raise ValueError('User query cannot be empty')
        return v.strip()
    
    def update_timestamp(self):
        """Update the last modified timestamp."""
        self.updated_at = datetime.now()
    
    model_config = {
        "use_enum_values": True,
        "validate_assignment": True
    }