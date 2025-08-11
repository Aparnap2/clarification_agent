"""
AI Strategy Assistant - Main Streamlit Application

A business-first development tool that enforces proper business validation
before coding begins. Combines multi-agent orchestration, web research,
and interactive planning tools.

Requirements: 6.1, 6.4, 8.1, 8.3
"""

import streamlit as st
import asyncio
import logging
import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import application components
from orchestrator import ProductDevelopmentOrchestrator
from ui.product_strategy_ui import ProductStrategyUI
from models.data_models import ProductState

# Page configuration
st.set_page_config(
    page_title="AI Strategy Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .status-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    
    .error-card {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #dc3545;
        margin: 1rem 0;
    }
    
    .success-card {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    
    .workflow-step {
        background-color: #e9ecef;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        display: inline-block;
        margin: 0.25rem;
        font-size: 0.9rem;
    }
    
    .workflow-step.active {
        background-color: #28a745;
        color: white;
    }
    
    .workflow-step.completed {
        background-color: #6c757d;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


class AIStrategyAssistantApp:
    """
    Main Streamlit application for AI Strategy Assistant.
    
    Provides configuration sidebar, user query input, workflow execution,
    progress tracking, results display, and session management integration.
    """
    
    def __init__(self):
        """Initialize the application with orchestrator and UI components."""
        self.orchestrator = None
        self.ui = None
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """
        Initialize Streamlit session state variables.
        
        Requirements: 8.1 (session ID and ProductState initialization)
        """
        # Core session state
        if 'current_state' not in st.session_state:
            st.session_state.current_state = None
        
        if 'session_id' not in st.session_state:
            st.session_state.session_id = None
        
        if 'workflow_running' not in st.session_state:
            st.session_state.workflow_running = False
        
        if 'workflow_completed' not in st.session_state:
            st.session_state.workflow_completed = False
        
        if 'error_message' not in st.session_state:
            st.session_state.error_message = None
        
        # Configuration state
        if 'api_key_configured' not in st.session_state:
            st.session_state.api_key_configured = False
        
        if 'model_selection' not in st.session_state:
            st.session_state.model_selection = "moonshotai/kimi-k2:free"
    
    def render_configuration_sidebar(self):
        """
        Render configuration sidebar with API key and model selection.
        
        Requirements: 6.1 (configuration sidebar)
        """
        st.sidebar.title("⚙️ Configuration")
        
        # API Key configuration
        st.sidebar.subheader("🔑 API Configuration")
        
        api_key = st.sidebar.text_input(
            "OpenAI API Key:",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Enter your OpenAI API key or set OPENAI_API_KEY environment variable"
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.session_state.api_key_configured = True
            st.sidebar.success("✅ API Key configured")
        else:
            st.session_state.api_key_configured = False
            st.sidebar.warning("⚠️ API Key required")
        
        # Model selection
        st.sidebar.subheader("🤖 Model Configuration")
        
        model_options = [
            "moonshotai/kimi-k2:free",
            "openai/gpt-oss-20b:free",
            "mistralai/mistral-small-3.2-24b-instruct:free",
            "qwen/qwen2.5-vl-72b-instruct:free",
            "tencent/hunyuan-a13b-instruct:free"
        ]
        
        selected_model = st.sidebar.selectbox(
            "Select LLM Model:",
            model_options,
            index=model_options.index(st.session_state.model_selection),
            help="Choose the language model for business analysis"
        )
        
        st.session_state.model_selection = selected_model
        
        # Initialize orchestrator if configuration is ready
        if st.session_state.api_key_configured and not self.orchestrator:
            try:
                self.orchestrator = ProductDevelopmentOrchestrator(
                    api_key=api_key,
                    model=selected_model
                )
                self.ui = ProductStrategyUI(self.orchestrator)
                st.sidebar.success("🚀 System initialized")
            except Exception as e:
                st.sidebar.error(f"❌ Initialization failed: {str(e)}")
                logger.error(f"Failed to initialize orchestrator: {e}")
        
        # System status
        st.sidebar.subheader("📊 System Status")
        
        if self.orchestrator:
            st.sidebar.success("✅ Orchestrator Ready")
            st.sidebar.success("✅ UI Components Ready")
            
            # Memory statistics
            try:
                memory_stats = self.orchestrator.memory.get_memory_stats()
                st.sidebar.info(f"💾 Sessions: {memory_stats.get('total_sessions', 0)}")
            except Exception as e:
                logger.error(f"Failed to get memory stats: {e}")
        else:
            st.sidebar.warning("⚠️ System not initialized")
        
        # Session management
        if self.orchestrator and self.ui:
            self.ui.render_session_management()
    
    def render_main_header(self):
        """Render the main application header."""
        st.markdown("""
        <div class="main-header">
            <h1>🎯 AI Strategy Assistant</h1>
            <p>Business-first development tool that validates your idea before you write a single line of code</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_workflow_status(self):
        """
        Render current workflow status and progress tracking.
        
        Requirements: 6.1 (progress tracking)
        """
        if not st.session_state.current_state:
            return
        
        state = st.session_state.current_state
        
        # Progress tracking
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.subheader("🔄 Workflow Progress")
            
            # Workflow phases with status
            phases = [
                ("discovery", "🔍 Discovery", "Analyzing business opportunity"),
                ("validation", "✅ Validation", "Validating market viability"),
                ("planning", "📋 Planning", "Conducting market research"),
                ("mvp_design", "🛠️ MVP Design", "Designing minimum viable product"),
                ("gtm_planning", "🚀 GTM Planning", "Developing go-to-market strategy")
            ]
            
            current_phase_idx = next(
                (i for i, (phase, _, _) in enumerate(phases) if phase == state.current_phase),
                0
            )
            
            # Render phase indicators
            phase_html = ""
            for i, (phase, label, description) in enumerate(phases):
                if i < current_phase_idx:
                    status_class = "completed"
                elif i == current_phase_idx:
                    status_class = "active"
                else:
                    status_class = ""
                
                phase_html += f'<span class="workflow-step {status_class}" title="{description}">{label}</span>'
            
            st.markdown(phase_html, unsafe_allow_html=True)
            
            # Progress bar
            progress = (current_phase_idx + 1) / len(phases)
            st.progress(progress)
            st.caption(f"Progress: {int(progress * 100)}% complete")
        
        with col2:
            st.metric(
                "Current Phase",
                phases[current_phase_idx][1]
            )
        
        with col3:
            if state.session_id:
                st.metric(
                    "Session",
                    state.session_id[:8] + "..."
                )
                if state.created_at:
                    st.caption(f"Started {state.created_at.strftime('%H:%M')}")
                else:
                    st.caption("Active")
    
    def render_user_input_section(self):
        """
        Render user query input and workflow execution controls.
        
        Requirements: 6.1 (user query input and workflow execution)
        """
        if not self.orchestrator or not self.ui:
            st.warning("⚠️ Please configure API key in the sidebar to begin.")
            return
        
        # Check if we already have a completed workflow
        if st.session_state.current_state and st.session_state.workflow_completed:
            st.success("✅ Workflow completed! Review your results below.")
            
            if st.button("🔄 Start New Analysis", type="primary"):
                # Reset session state for new analysis
                st.session_state.current_state = None
                st.session_state.session_id = None
                st.session_state.workflow_running = False
                st.session_state.workflow_completed = False
                st.session_state.error_message = None
                st.rerun()
            return
        
        # Check if workflow is currently running
        if st.session_state.workflow_running:
            st.info("🔄 Workflow is running... Please wait for completion.")
            
            # Add cancel button
            if st.button("❌ Cancel Workflow"):
                st.session_state.workflow_running = False
                st.session_state.error_message = "Workflow cancelled by user"
                st.rerun()
            return
        
        # Render business validation form
        user_query = self.ui.render_business_validation_form()
        
        if user_query:
            # Start workflow execution
            st.session_state.workflow_running = True
            st.session_state.error_message = None
            
            # Execute workflow asynchronously
            self._execute_workflow_async(user_query)
    
    def _execute_workflow_async(self, user_query: str):
        """
        Execute the workflow asynchronously with progress tracking.
        
        Args:
            user_query: User's project description
            
        Requirements: 8.1 (create unique session ID and initialize ProductState)
        """
        try:
            # Create progress placeholder
            progress_placeholder = st.empty()
            status_placeholder = st.empty()
            
            with progress_placeholder.container():
                st.info("🚀 Starting business analysis workflow...")
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            # Execute workflow
            async def run_workflow():
                try:
                    # Generate session ID if not exists
                    if not st.session_state.session_id:
                        st.session_state.session_id = self.orchestrator.memory.generate_session_id()
                    
                    # Update progress
                    progress_bar.progress(10)
                    status_text.text("Initializing workflow...")
                    
                    # Execute the workflow
                    final_state = await self.orchestrator.execute_workflow(
                        user_query=user_query,
                        session_id=st.session_state.session_id
                    )
                    
                    # Update progress
                    progress_bar.progress(100)
                    status_text.text("Workflow completed!")
                    
                    # Store final state
                    st.session_state.current_state = final_state
                    st.session_state.workflow_running = False
                    st.session_state.workflow_completed = True
                    
                    # Clear progress indicators
                    progress_placeholder.empty()
                    
                    # Show success message
                    st.success("✅ Business analysis completed successfully!")
                    st.rerun()
                    
                except Exception as e:
                    logger.error(f"Workflow execution failed: {e}")
                    st.session_state.workflow_running = False
                    st.session_state.error_message = str(e)
                    
                    # Clear progress indicators
                    progress_placeholder.empty()
                    
                    # Show error
                    st.error(f"❌ Workflow failed: {str(e)}")
                    st.rerun()
            
            # Run the async workflow
            asyncio.run(run_workflow())
            
        except Exception as e:
            logger.error(f"Failed to execute workflow: {e}")
            st.session_state.workflow_running = False
            st.session_state.error_message = str(e)
            st.error(f"❌ Failed to start workflow: {str(e)}")
    
    def render_results_display(self):
        """
        Render workflow results and analysis display.
        
        Requirements: 6.4 (GTM strategy display), 8.3 (restore complete state)
        """
        if not st.session_state.current_state or not self.ui:
            return
        
        state = st.session_state.current_state
        
        # Error handling
        if st.session_state.error_message:
            st.markdown(f"""
            <div class="error-card">
                <h4>❌ Workflow Error</h4>
                <p>{st.session_state.error_message}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Validation results
        if state.market_validation:
            self.ui.render_validation_results(state)
            
            # Check if workflow was rejected
            if state.market_validation.get("workflow_status") == "rejected":
                st.warning("⚠️ Development not recommended based on business validation.")
                return
        
        # Business model and features
        if state.business_model:
            st.subheader("💼 Business Model")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Value Proposition:**")
                st.info(state.business_model.value_proposition)
                
                st.markdown("**Target Customer:**")
                st.info(state.business_model.target_customer)
            
            with col2:
                st.markdown("**Revenue Streams:**")
                for stream in state.business_model.revenue_streams:
                    st.markdown(f"• {stream}")
                
                st.markdown("**Key Metrics:**")
                for metric in state.business_model.key_metrics:
                    st.markdown(f"• {metric}")
        
        # Feature specifications with impact/effort matrix
        if state.feature_specifications:
            st.markdown("---")
            
            # Impact vs Effort Matrix
            self.ui.render_impact_effort_matrix(state.feature_specifications)
            
            # Feature specifications
            self.ui.render_feature_specifications(state.feature_specifications)
        
        # GTM Strategy display
        if state.gtm_strategy:
            st.markdown("---")
            self.ui.render_gtm_strategy_display(state.gtm_strategy)
        
        # Product roadmap
        if state.mvp_roadmap:
            st.markdown("---")
            st.subheader("🗺️ Product Roadmap")
            
            for i, phase in enumerate(state.mvp_roadmap, 1):
                with st.expander(f"Phase {i}: {phase.get('phase_name', f'Phase {i}')}", expanded=i==1):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Timeline:**")
                        st.info(phase.get('timeline', 'Not specified'))
                        
                        st.markdown("**Key Features:**")
                        features = phase.get('key_features', [])
                        for feature in features:
                            st.markdown(f"• {feature}")
                    
                    with col2:
                        st.markdown("**Success Criteria:**")
                        criteria = phase.get('success_criteria', [])
                        for criterion in criteria:
                            st.markdown(f"✅ {criterion}")
                        
                        st.markdown("**Key Learnings:**")
                        learnings = phase.get('key_learnings', [])
                        for learning in learnings:
                            st.markdown(f"📚 {learning}")
        
        # Research data summary
        if state.research_data:
            st.markdown("---")
            st.subheader("🔍 Market Research Summary")
            
            successful_research = [r for r in state.research_data if r.get('success', True) and r.get('title') != 'Research Unavailable']
            
            if successful_research:
                st.success(f"✅ Analyzed {len(successful_research)} market sources")
                
                with st.expander("📊 Research Sources"):
                    for i, research in enumerate(successful_research[:5], 1):  # Show first 5
                        title = research.get('title', 'Unknown Source')
                        url = research.get('url', '')
                        
                        # Clean up title - remove HTML and long URLs
                        if title.startswith('<html>'):
                            title = f"Market Research Source {i}"
                        elif len(title) > 100:
                            title = title[:100] + "..."
                        
                        # Display source info
                        st.markdown(f"**Source {i}: {title}**")
                        
                        # Show URL if it's not a search URL
                        if url and not url.startswith('https://www.google.com/search'):
                            st.caption(f"🔗 {url}")
                        
                        # Show content preview if available and not HTML
                        content = research.get('content', '')
                        if content and not content.startswith('<html>'):
                            # Clean content preview
                            clean_content = content.replace('\n', ' ').strip()
                            if len(clean_content) > 150:
                                clean_content = clean_content[:150] + "..."
                            if clean_content:
                                st.markdown(f"*{clean_content}*")
                        
                        if i < len(successful_research[:5]):
                            st.markdown("---")
            else:
                st.warning("⚠️ Market research data limited or unavailable")
    
    def run(self):
        """
        Main application entry point.
        
        Orchestrates the complete Streamlit application flow including
        configuration, user input, workflow execution, and results display.
        """
        try:
            # Render main components
            self.render_main_header()
            self.render_configuration_sidebar()
            
            # Main content area
            if st.session_state.api_key_configured:
                # Workflow status
                self.render_workflow_status()
                
                # User input section
                self.render_user_input_section()
                
                # Results display
                self.render_results_display()
            else:
                # Welcome message when not configured
                st.markdown("""
                ## 👋 Welcome to AI Strategy Assistant
                
                This tool helps you validate your business idea before writing code by:
                
                1. **🎯 Business Validation** - Analyze market viability and problem severity
                2. **🔍 Market Research** - Automated competitive analysis and trend research  
                3. **🛠️ MVP Planning** - Feature prioritization with impact/effort analysis
                4. **🚀 GTM Strategy** - Go-to-market planning with channels and pricing
                5. **🗺️ Product Roadmap** - 3-phase development roadmap with success criteria
                
                **Get Started:**
                1. Configure your OpenAI API key in the sidebar
                2. Select your preferred language model
                3. Describe your project idea to begin analysis
                
                ---
                
                ### 🔒 Privacy & Security
                - Your API key is stored locally in your browser session
                - All analysis data is saved locally using session management
                - No data is sent to external servers except OpenAI for analysis
                """)
        
        except Exception as e:
            logger.error(f"Application error: {e}")
            st.error(f"❌ Application error: {str(e)}")
            
            # Show debug information in development
            if os.getenv("DEBUG", "false").lower() == "true":
                st.exception(e)


def main():
    """Application entry point."""
    try:
        app = AIStrategyAssistantApp()
        app.run()
    except Exception as e:
        st.error(f"❌ Failed to start application: {str(e)}")
        logger.error(f"Failed to start application: {e}")


if __name__ == "__main__":
    main()