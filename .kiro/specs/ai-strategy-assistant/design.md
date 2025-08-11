# Design Document: AI Strategy Assistant Evolution

## Overview

The AI Strategy Assistant evolves from a Streamlit-based business validation tool to a comprehensive platform combining business analysis with requirements clarification. The design maintains the current working system while adding FastAPI backend, advanced persistence, and modular agent architecture.

**Architecture Philosophy**: Business-first development with validation gates, structured workflows, and comprehensive state management.

## Architecture

### Current Architecture (Phase 1 - Implemented)
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │────│  LangGraph       │────│  OpenAI API     │
│   - Forms       │    │  Orchestrator    │    │  - GPT-4o-mini  │
│   - Visualizations│   │  - BPA Agent     │    │  - Direct calls │
│   - Session Mgmt│    │  - GTM Agent     │    └─────────────────┘
└─────────────────┘    │  - Memory Saver  │    
                       └──────────────────┘    
                                │              
                       ┌──────────────────┐    
                       │  Pickle Storage  │    
                       │  - Session data  │    
                       │  - State history │    
                       └──────────────────┘    
```

### Target Architecture (Phase 2 - Enhanced)
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit UI  │    │    FastAPI       │    │   PydanticAI    │
│   - Interactive │────│    Backend       │────│   Agents        │
│   - Visualizations│   │  - REST API      │    │  - Typed calls  │
│   - Real-time   │    │  - WebSocket     │    │  - Schema valid │
└─────────────────┘    │  - Auth/Rate     │    └─────────────────┘
                       └──────────────────┘              │
                                │                        │
                       ┌──────────────────┐    ┌─────────────────┐
                       │   LangGraph      │    │  OpenRouter     │
                       │   Workflow       │────│  Multi-model    │
                       │  - SQLite        │    │  - Fallbacks    │
                       │  - Checkpoints   │    │  - Cost tracking│
                       └──────────────────┘    └─────────────────┘
                                │
                       ┌──────────────────┐    ┌─────────────────┐
                       │     Storage      │    │   Crawl4AI      │
                       │  - SQLite (dev)  │────│  Web Research   │
                       │  - PostgreSQL    │    │  - Async crawl  │
                       │  - Neo4j (opt)   │    │  - Content ext  │
                       └──────────────────┘    └─────────────────┘
```

## Components and Interfaces

### 1. Agent Layer

#### BPA Agent (Enhanced)
```python
class BPAAgent:
    """Business Process Analysis with structured validation."""
    
    async def analyze_business_viability(self, state: ProductState) -> ProductState:
        """Core business validation with 1-10 scoring."""
        
    async def validate_problem_space(self, query: str) -> ProblemValidationResult:
        """Problem validation with structured scoring."""
        
    async def generate_business_model(self, query: str) -> BusinessModel:
        """Business model generation with validation."""
        
    async def generate_mvp_features(self, business_model: BusinessModel) -> List[FeatureSpec]:
        """MVP feature generation with EARS acceptance criteria."""
```

#### Clarification Agent (New)
```python
class ClarificationAgent:
    """Requirements clarification with gap analysis."""
    
    async def analyze_requirements(self, document: str) -> ClarificationReport:
        """Generate clarification questions and gap analysis."""
        
    async def extract_entities(self, document: str) -> List[Entity]:
        """Extract actors, systems, and requirements."""
        
    async def detect_ambiguity(self, text: str) -> List[AmbiguityFlag]:
        """Detect vague terms and undefined concepts."""
        
    async def generate_acceptance_criteria(self, requirement: str) -> List[str]:
        """Generate testable acceptance criteria."""
```

#### Web Research Agent (Enhanced)
```python
class WebResearchAgent:
    """Intelligent web research with Crawl4AI integration."""
    
    async def research_competitors(self, business_model: BusinessModel) -> List[CompetitorData]:
        """Automated competitive analysis."""
        
    async def validate_market_size(self, target_customer: str) -> MarketData:
        """Market size validation with web sources."""
        
    async def crawl_urls(self, urls: List[str]) -> List[CrawlResult]:
        """Structured content extraction."""
```

### 2. Data Layer

#### Core Models (Enhanced)
```python
# Current models enhanced with validation
class ProductState(BaseModel):
    """Enhanced with checkpointing and versioning."""
    user_query: str
    business_model: Optional[BusinessModel]
    feature_specifications: List[FeatureSpec]
    gtm_strategy: Optional[GTMStrategy]
    clarification_questions: List[ClarificationQuestion] = []  # New
    gap_analysis: List[GapItem] = []  # New
    checkpoint_id: Optional[str] = None  # New
    version: str = "2.0"  # New

# New clarification models
class ClarificationQuestion(BaseModel):
    id: str
    text: str
    category: Literal["functional", "nfr", "data", "integration", "compliance"]
    priority: int = Field(ge=1, le=10)
    rationale: str
    blocking: bool = False

class GapItem(BaseModel):
    id: str
    type: Literal["functional", "nfr", "data", "integration", "compliance"]
    description: str
    impact: Literal["low", "medium", "high", "critical"]
    suggested_ac: Optional[str] = None

class ClarificationReport(BaseModel):
    questions: List[ClarificationQuestion]
    gaps: List[GapItem]
    risks: List[RiskItem]
    acceptance_criteria: List[AcceptanceCriterion]
    sources: List[str] = []
    checkpoint_id: Optional[str] = None
```

#### Persistence Layer
```python
# Enhanced persistence with multiple backends
class PersistenceManager:
    """Unified persistence with multiple backends."""
    
    def __init__(self, config: PersistenceConfig):
        self.sqlite_checkpointer = SqliteSaver(config.sqlite_path)
        self.graph_memory = GraphMemory(config.memory_path)
        self.neo4j_client = Neo4jClient(config.neo4j_uri) if config.use_neo4j else None
    
    async def save_checkpoint(self, thread_id: str, state: ProductState) -> str:
        """Save with versioned checkpointing."""
        
    async def load_checkpoint(self, thread_id: str, checkpoint_id: str = None) -> ProductState:
        """Load with fallback handling."""
        
    async def upsert_knowledge_graph(self, entities: List[Entity], relations: List[Relation]):
        """Optional knowledge graph storage."""
```

### 3. API Layer (New)

#### FastAPI Backend
```python
# RESTful API with typed responses
@app.post("/threads", response_model=ThreadResponse)
async def create_thread() -> ThreadResponse:
    """Create new analysis thread."""

@app.post("/analyze", response_model=ClarificationReport)
async def analyze_document(request: AnalyzeRequest) -> ClarificationReport:
    """Analyze document with business validation and clarification."""

@app.post("/threads/{thread_id}/answers", response_model=ClarificationReport)
async def answer_questions(thread_id: str, answers: AnswerRequest) -> ClarificationReport:
    """Process clarification answers and update analysis."""

@app.get("/threads/{thread_id}/history", response_model=List[CheckpointInfo])
async def get_thread_history(thread_id: str) -> List[CheckpointInfo]:
    """Get thread checkpoint history."""

@app.post("/crawl", response_model=List[CrawlResult])
async def crawl_urls(request: CrawlRequest) -> List[CrawlResult]:
    """Crawl URLs for context."""
```

### 4. Workflow Layer

#### Enhanced LangGraph Workflow
```python
def build_enhanced_workflow() -> StateGraph:
    """Enhanced workflow with clarification integration."""
    
    workflow = StateGraph(ProductState)
    
    # Business validation path (current)
    workflow.add_node("problem_validation", problem_validation_node)
    workflow.add_node("business_analysis", business_analysis_node)
    workflow.add_node("market_research", market_research_node)
    workflow.add_node("mvp_planning", mvp_planning_node)
    workflow.add_node("gtm_strategy", gtm_strategy_node)
    
    # Clarification path (new)
    workflow.add_node("requirements_analysis", requirements_analysis_node)
    workflow.add_node("gap_detection", gap_detection_node)
    workflow.add_node("clarification_generation", clarification_generation_node)
    workflow.add_node("acceptance_criteria_generation", ac_generation_node)
    
    # Optional enhancement nodes
    workflow.add_node("web_research", web_research_node)
    workflow.add_node("knowledge_graph_upsert", kg_upsert_node)
    
    # Conditional routing with validation gates
    workflow.add_conditional_edges(
        "problem_validation",
        should_continue_business_validation,
        {"continue": "business_analysis", "clarify": "requirements_analysis", "stop": "rejection_report"}
    )
    
    return workflow.compile(checkpointer=SqliteSaver())
```

## Data Models

### Enhanced State Management
```python
class EnhancedProductState(ProductState):
    """Extended state with clarification capabilities."""
    
    # Clarification fields
    clarification_questions: List[ClarificationQuestion] = []
    answered_questions: Dict[str, str] = {}
    gap_analysis: List[GapItem] = []
    risk_analysis: List[RiskItem] = []
    
    # Workflow tracking
    workflow_path: Literal["business_first", "requirements_first", "hybrid"] = "business_first"
    checkpoint_history: List[str] = []
    
    # Knowledge graph integration
    extracted_entities: List[Entity] = []
    entity_relations: List[Relation] = []
    
    def create_checkpoint(self) -> str:
        """Create versioned checkpoint."""
        checkpoint_id = f"{self.session_id}_{datetime.now().isoformat()}"
        self.checkpoint_history.append(checkpoint_id)
        return checkpoint_id
```

### Integration Models
```python
class AnalyzeRequest(BaseModel):
    """Unified analysis request."""
    thread_id: Optional[str] = None
    document_text: str
    urls: List[str] = []
    analysis_type: Literal["business_validation", "requirements_clarification", "hybrid"] = "hybrid"
    options: AnalysisOptions = AnalysisOptions()

class AnalysisOptions(BaseModel):
    """Analysis configuration options."""
    top_n_questions: int = 10
    enable_web_crawl: bool = True
    use_knowledge_graph: bool = False
    model_preference: str = "openai/gpt-4o-mini"
    validation_threshold: float = 7.0
```

## Error Handling

### Comprehensive Error Strategy
```python
class ErrorHandler:
    """Centralized error handling with recovery."""
    
    async def handle_llm_error(self, error: Exception, context: Dict) -> ErrorResponse:
        """Handle LLM API failures with fallbacks."""
        
    async def handle_persistence_error(self, error: Exception, state: ProductState) -> bool:
        """Handle storage failures with recovery."""
        
    async def handle_workflow_error(self, error: Exception, thread_id: str) -> ProductState:
        """Handle workflow failures with state recovery."""

# Error response models
class ErrorResponse(BaseModel):
    error_type: str
    message: str
    request_id: str
    timestamp: datetime
    recovery_suggestions: List[str] = []
    debug_info: Optional[Dict] = None
```

### Graceful Degradation
- **LLM Failures**: Fallback to simpler models or cached responses
- **Storage Failures**: In-memory fallback with periodic retry
- **Network Failures**: Offline mode with limited functionality
- **Validation Failures**: Partial results with error annotations

## Testing Strategy

### Unit Testing
```python
# Agent testing with mocked LLM responses
class TestBPAAgent:
    async def test_business_validation_scoring(self):
        """Test scoring algorithm with known inputs."""
        
    async def test_validation_gate_threshold(self):
        """Test 7.0 threshold enforcement."""

# API testing with FastAPI test client
class TestAPI:
    async def test_analyze_endpoint_validation(self):
        """Test request validation and error handling."""
        
    async def test_thread_state_persistence(self):
        """Test checkpoint save/load functionality."""
```

### Integration Testing
```python
# End-to-end workflow testing
class TestWorkflowIntegration:
    async def test_business_validation_workflow(self):
        """Test complete business validation path."""
        
    async def test_requirements_clarification_workflow(self):
        """Test complete clarification path."""
        
    async def test_hybrid_workflow(self):
        """Test combined business + clarification workflow."""
```

### Performance Testing
- **Load Testing**: Concurrent analysis requests
- **Memory Testing**: Large document processing
- **Latency Testing**: Response time requirements (≤15s p50)
- **Scalability Testing**: Multi-user session management

## Deployment Architecture

### Development Environment
```yaml
# docker-compose.dev.yml
services:
  api:
    build: .
    environment:
      - DATABASE_URL=sqlite:///./dev.db
      - REDIS_URL=redis://redis:6379
    volumes:
      - ./data:/app/data
  
  ui:
    build: ./ui
    ports:
      - "8501:8501"
    depends_on:
      - api
  
  redis:
    image: redis:alpine
    
  neo4j:
    image: neo4j:latest
    environment:
      - NEO4J_AUTH=neo4j/password
    ports:
      - "7474:7474"
      - "7687:7687"
```

### Production Environment
```yaml
# docker-compose.prod.yml
services:
  api:
    image: ai-strategy-assistant:latest
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/aiassistant
      - NEO4J_URI=bolt://neo4j:7687
      - REDIS_URL=redis://redis:6379
    deploy:
      replicas: 3
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=aiassistant
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  neo4j:
    image: neo4j:enterprise
    environment:
      - NEO4J_AUTH=neo4j/production_password
    volumes:
      - neo4j_data:/data
```

This design bridges the current working implementation with the comprehensive technical vision, providing a clear evolution path while maintaining the core business-first philosophy.