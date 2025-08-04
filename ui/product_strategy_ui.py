"""Streamlit UI components for AI Strategy Assistant."""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime

from models.data_models import ProductState, BusinessModel, FeatureSpec, GTMStrategy
from models.enums import MVPPriority
from orchestrator import ProductDevelopmentOrchestrator


class ProductStrategyUI:
    """
    Streamlit UI components for the AI Strategy Assistant.
    
    Provides interactive forms, visualizations, and displays for the
    business validation and product strategy workflow.
    
    Requirements: 6.1, 6.2, 6.3, 6.4
    """
    
    def __init__(self, orchestrator: ProductDevelopmentOrchestrator):
        """
        Initialize the UI with orchestrator integration.
        
        Args:
            orchestrator: ProductDevelopmentOrchestrator instance for backend integration
        """
        self.orchestrator = orchestrator
        
        # Initialize session state
        if 'current_state' not in st.session_state:
            st.session_state.current_state = None
        if 'session_id' not in st.session_state:
            st.session_state.session_id = None
        if 'workflow_running' not in st.session_state:
            st.session_state.workflow_running = False
    
    def render_business_validation_form(self) -> Optional[str]:
        """
        Render the business validation form for user input.
        
        Returns:
            User query string if form is submitted, None otherwise
            
        Requirements: 6.1 (business validation section with problem statement input)
        """
        st.header("🎯 Business Validation")
        st.markdown("Start by describing your project idea. We'll help validate the business opportunity before you write any code.")
        
        with st.form("business_validation_form"):
            # Problem statement input
            user_query = st.text_area(
                "Describe your project idea:",
                placeholder="Example: I want to build a task management app for remote teams that integrates with Slack and helps track productivity metrics...",
                height=120,
                help="Describe the problem you're solving, who your target users are, and what solution you have in mind."
            )
            
            # Target customer input
            target_customer = st.text_input(
                "Who is your target customer?",
                placeholder="Example: Remote team managers at tech startups with 10-50 employees",
                help="Be specific about your target customer segment."
            )
            
            # Additional context
            with st.expander("Additional Context (Optional)"):
                market_size = st.text_input(
                    "Estimated market size or opportunity:",
                    placeholder="Example: $2B remote work software market growing 20% annually"
                )
                
                existing_solutions = st.text_area(
                    "What existing solutions are you aware of?",
                    placeholder="Example: Asana, Trello, Monday.com - but they lack real-time Slack integration",
                    height=80
                )
                
                unique_advantage = st.text_area(
                    "What makes your approach unique?",
                    placeholder="Example: AI-powered productivity insights with seamless Slack workflow integration",
                    height=80
                )
            
            # Submit button
            submitted = st.form_submit_button(
                "🚀 Validate Business Opportunity",
                type="primary",
                use_container_width=True
            )
            
            if submitted:
                if not user_query.strip():
                    st.error("Please describe your project idea.")
                    return None
                
                if not target_customer.strip():
                    st.error("Please specify your target customer.")
                    return None
                
                # Enhance query with additional context
                enhanced_query = user_query
                if target_customer:
                    enhanced_query += f"\n\nTarget Customer: {target_customer}"
                if market_size:
                    enhanced_query += f"\n\nMarket Opportunity: {market_size}"
                if existing_solutions:
                    enhanced_query += f"\n\nExisting Solutions: {existing_solutions}"
                if unique_advantage:
                    enhanced_query += f"\n\nUnique Advantage: {unique_advantage}"
                
                return enhanced_query
        
        return None
    
    def render_impact_effort_matrix(self, features: List[FeatureSpec]) -> None:
        """
        Render impact vs effort matrix visualization using Plotly.
        
        Args:
            features: List of feature specifications to visualize
            
        Requirements: 6.2 (impact vs effort matrix visualization using Plotly)
        """
        if not features:
            st.info("No features available for visualization.")
            return
        
        st.subheader("📊 Impact vs Effort Matrix")
        st.markdown("Visual representation of feature prioritization based on business impact and development effort.")
        
        # Prepare data for visualization
        feature_data = []
        
        # Map effort estimates to numeric values
        effort_mapping = {"XS": 1, "S": 2, "M": 3, "L": 4, "XL": 5}
        impact_mapping = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
        priority_colors = {
            MVPPriority.CORE: "#FF6B6B",      # Red for Core
            MVPPriority.IMPORTANT: "#4ECDC4", # Teal for Important  
            MVPPriority.FUTURE: "#95E1D3"     # Light green for Future
        }
        
        for feature in features:
            feature_data.append({
                'name': feature.name,
                'effort': effort_mapping.get(feature.effort_estimate, 3),
                'impact': impact_mapping.get(feature.business_impact, 2),
                'priority': feature.mvp_priority.value,
                'color': priority_colors.get(feature.mvp_priority, "#95E1D3"),
                'user_story': feature.user_story[:100] + "..." if len(feature.user_story) > 100 else feature.user_story
            })
        
        # Create DataFrame
        df = pd.DataFrame(feature_data)
        
        # Create scatter plot
        fig = px.scatter(
            df,
            x='effort',
            y='impact',
            color='priority',
            size=[20] * len(df),  # Fixed size for all points
            hover_data=['name', 'user_story'],
            title="Feature Prioritization Matrix",
            labels={
                'effort': 'Development Effort →',
                'impact': 'Business Impact →'
            },
            color_discrete_map={
                'Core': '#FF6B6B',
                'Important': '#4ECDC4', 
                'Future': '#95E1D3'
            }
        )
        
        # Customize layout
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=[1, 2, 3, 4, 5],
                ticktext=['XS', 'S', 'M', 'L', 'XL'],
                range=[0.5, 5.5]
            ),
            yaxis=dict(
                tickmode='array',
                tickvals=[1, 2, 3, 4],
                ticktext=['Low', 'Medium', 'High', 'Critical'],
                range=[0.5, 4.5]
            ),
            height=500,
            showlegend=True,
            legend=dict(
                title="MVP Priority",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        # Add quadrant lines
        fig.add_hline(y=2.5, line_dash="dash", line_color="gray", opacity=0.5)
        fig.add_vline(x=3, line_dash="dash", line_color="gray", opacity=0.5)
        
        # Add quadrant labels
        fig.add_annotation(x=1.5, y=3.5, text="Quick Wins<br>(Low Effort, High Impact)", 
                          showarrow=False, font=dict(size=10, color="green"))
        fig.add_annotation(x=4.5, y=3.5, text="Major Projects<br>(High Effort, High Impact)", 
                          showarrow=False, font=dict(size=10, color="orange"))
        fig.add_annotation(x=1.5, y=1.5, text="Fill-ins<br>(Low Effort, Low Impact)", 
                          showarrow=False, font=dict(size=10, color="gray"))
        fig.add_annotation(x=4.5, y=1.5, text="Questionable<br>(High Effort, Low Impact)", 
                          showarrow=False, font=dict(size=10, color="red"))
        
        # Display the plot
        st.plotly_chart(fig, use_container_width=True)
        
        # Add interpretation guide
        with st.expander("📖 How to Read This Matrix"):
            st.markdown("""
            **Quadrants Explained:**
            - **Quick Wins** (Top Left): High impact, low effort - prioritize these first
            - **Major Projects** (Top Right): High impact, high effort - plan carefully
            - **Fill-ins** (Bottom Left): Low impact, low effort - do when you have spare time
            - **Questionable** (Bottom Right): Low impact, high effort - avoid or reconsider
            
            **Priority Colors:**
            - 🔴 **Core**: Essential for MVP launch
            - 🟢 **Important**: Valuable but not critical for initial launch
            - 🟡 **Future**: Consider for later versions
            """)
    
    def render_feature_specifications(self, features: List[FeatureSpec]) -> None:
        """
        Render expandable feature specification sections organized by priority.
        
        Args:
            features: List of feature specifications to display
            
        Requirements: 6.3 (expandable feature specification sections - Core MVP vs Future)
        """
        if not features:
            st.info("No feature specifications available.")
            return
        
        st.subheader("🛠️ Feature Specifications")
        
        # Group features by priority
        core_features = [f for f in features if f.mvp_priority == MVPPriority.CORE]
        important_features = [f for f in features if f.mvp_priority == MVPPriority.IMPORTANT]
        future_features = [f for f in features if f.mvp_priority == MVPPriority.FUTURE]
        
        # Core MVP Features
        if core_features:
            with st.expander(f"🔴 Core MVP Features ({len(core_features)})", expanded=True):
                st.markdown("*Essential features required for initial product launch*")
                
                for i, feature in enumerate(core_features, 1):
                    self._render_feature_card(feature, f"core-{i}")
        
        # Important Features
        if important_features:
            with st.expander(f"🟡 Important Features ({len(important_features)})", expanded=False):
                st.markdown("*Valuable features for enhanced user experience*")
                
                for i, feature in enumerate(important_features, 1):
                    self._render_feature_card(feature, f"important-{i}")
        
        # Future Features
        if future_features:
            with st.expander(f"🟢 Future Features ({len(future_features)})", expanded=False):
                st.markdown("*Features to consider for future product versions*")
                
                for i, feature in enumerate(future_features, 1):
                    self._render_feature_card(feature, f"future-{i}")
        
        # Summary statistics
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Features", len(features))
        with col2:
            st.metric("Core MVP", len(core_features))
        with col3:
            st.metric("Important", len(important_features))
        with col4:
            st.metric("Future", len(future_features))
    
    def _render_feature_card(self, feature: FeatureSpec, key: str) -> None:
        """
        Render individual feature card with details.
        
        Args:
            feature: Feature specification to render
            key: Unique key for Streamlit components
        """
        # Priority badge color
        priority_colors = {
            MVPPriority.CORE: "🔴",
            MVPPriority.IMPORTANT: "🟡", 
            MVPPriority.FUTURE: "🟢"
        }
        
        # Effort badge color
        effort_colors = {
            "XS": "🟢", "S": "🟡", "M": "🟠", "L": "🔴", "XL": "🟣"
        }
        
        # Impact badge color  
        impact_colors = {
            "Low": "⚪", "Medium": "🟡", "High": "🟠", "Critical": "🔴"
        }
        
        with st.container():
            # Feature header
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{feature.name}**")
            with col2:
                st.markdown(f"{priority_colors.get(feature.mvp_priority, '⚪')} {feature.mvp_priority.value}")
            with col3:
                st.markdown(f"{effort_colors.get(feature.effort_estimate, '⚪')} {feature.effort_estimate}")
            with col4:
                st.markdown(f"{impact_colors.get(feature.business_impact, '⚪')} {feature.business_impact}")
            
            # User story
            st.markdown(f"*{feature.user_story}*")
            
            # Acceptance criteria
            if feature.acceptance_criteria:
                with st.expander(f"Acceptance Criteria ({len(feature.acceptance_criteria)})", key=f"criteria-{key}"):
                    for i, criterion in enumerate(feature.acceptance_criteria, 1):
                        st.markdown(f"{i}. {criterion}")
            
            # Dependencies
            if feature.dependencies:
                st.markdown(f"**Dependencies:** {', '.join(feature.dependencies)}")
            
            st.markdown("---")
    
    def render_gtm_strategy_display(self, gtm_strategy: GTMStrategy) -> None:
        """
        Render GTM strategy display with metrics and channels.
        
        Args:
            gtm_strategy: Go-to-market strategy to display
            
        Requirements: 6.4 (GTM strategy display with metrics and channels)
        """
        if not gtm_strategy:
            st.info("GTM strategy not yet developed.")
            return
        
        st.subheader("🚀 Go-to-Market Strategy")
        
        # Strategy overview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 Competitive Positioning")
            st.markdown(gtm_strategy.competitive_positioning)
            
            st.markdown("### 💰 Pricing Strategy")
            st.markdown(gtm_strategy.pricing_strategy)
        
        with col2:
            if gtm_strategy.budget_requirements:
                st.markdown("### 💵 Budget Requirements")
                st.info(gtm_strategy.budget_requirements)
        
        # Distribution channels
        st.markdown("### 📢 Distribution Channels")
        
        # Create columns for channels
        num_channels = len(gtm_strategy.distribution_channels)
        if num_channels > 0:
            cols = st.columns(min(num_channels, 3))  # Max 3 columns
            
            for i, channel in enumerate(gtm_strategy.distribution_channels):
                col_idx = i % 3
                with cols[col_idx]:
                    st.markdown(f"""
                    <div style="
                        background-color: #f0f2f6;
                        padding: 1rem;
                        border-radius: 0.5rem;
                        margin-bottom: 0.5rem;
                        border-left: 4px solid #4CAF50;
                    ">
                        <strong>Channel {i+1}</strong><br>
                        {channel}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Launch timeline
        st.markdown("### 📅 Launch Timeline")
        
        if gtm_strategy.launch_timeline:
            timeline_df = pd.DataFrame([
                {"Phase": phase.replace('_', ' ').title(), "Timeline": timeline}
                for phase, timeline in gtm_strategy.launch_timeline.items()
            ])
            
            # Create timeline visualization
            fig = go.Figure()
            
            phases = timeline_df['Phase'].tolist()
            timelines = timeline_df['Timeline'].tolist()
            
            # Add timeline bars
            fig.add_trace(go.Bar(
                y=phases,
                x=[1] * len(phases),  # Equal width bars
                orientation='h',
                text=timelines,
                textposition='inside',
                marker=dict(
                    color=['#FF6B6B', '#4ECDC4', '#95E1D3'][:len(phases)],
                    opacity=0.8
                ),
                showlegend=False
            ))
            
            fig.update_layout(
                title="Launch Timeline Overview",
                xaxis=dict(showticklabels=False, showgrid=False),
                yaxis=dict(title="Launch Phases"),
                height=200 + len(phases) * 50,
                margin=dict(l=0, r=0, t=50, b=0)
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Success metrics
        st.markdown("### 📈 Success Metrics")
        
        if gtm_strategy.success_metrics:
            # Display metrics in a grid
            metric_cols = st.columns(min(len(gtm_strategy.success_metrics), 3))
            
            for i, metric in enumerate(gtm_strategy.success_metrics):
                col_idx = i % 3
                with metric_cols[col_idx]:
                    st.markdown(f"""
                    <div style="
                        background-color: #e8f4fd;
                        padding: 1rem;
                        border-radius: 0.5rem;
                        margin-bottom: 0.5rem;
                        border-left: 4px solid #2196F3;
                        text-align: center;
                    ">
                        <strong>Metric {i+1}</strong><br>
                        {metric}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Strategy summary
        with st.expander("📋 Strategy Summary"):
            st.markdown(f"""
            **Distribution Channels:** {len(gtm_strategy.distribution_channels)} channels identified
            
            **Launch Phases:** {len(gtm_strategy.launch_timeline)} phases planned
            
            **Success Metrics:** {len(gtm_strategy.success_metrics)} metrics defined
            
            **Competitive Advantage:** {gtm_strategy.competitive_positioning[:200]}...
            """)
    
    def render_workflow_progress(self, state: ProductState) -> None:
        """
        Render workflow progress indicator.
        
        Args:
            state: Current product state
        """
        st.subheader("🔄 Workflow Progress")
        
        # Define workflow phases
        phases = [
            ("discovery", "🔍 Discovery"),
            ("validation", "✅ Validation"), 
            ("planning", "📋 Planning"),
            ("mvp_design", "🛠️ MVP Design"),
            ("gtm_planning", "🚀 GTM Planning")
        ]
        
        # Current phase index
        current_phase_idx = next(
            (i for i, (phase, _) in enumerate(phases) if phase == state.current_phase),
            0
        )
        
        # Create progress bar
        progress_cols = st.columns(len(phases))
        
        for i, (phase, label) in enumerate(phases):
            with progress_cols[i]:
                if i <= current_phase_idx:
                    st.markdown(f"""
                    <div style="
                        background-color: #4CAF50;
                        color: white;
                        padding: 0.5rem;
                        border-radius: 0.25rem;
                        text-align: center;
                        font-size: 0.8rem;
                    ">
                        {label}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="
                        background-color: #f0f2f6;
                        color: #666;
                        padding: 0.5rem;
                        border-radius: 0.25rem;
                        text-align: center;
                        font-size: 0.8rem;
                    ">
                        {label}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Progress percentage
        progress_pct = (current_phase_idx + 1) / len(phases)
        st.progress(progress_pct)
        st.caption(f"Progress: {int(progress_pct * 100)}% complete")
    
    def render_validation_results(self, state: ProductState) -> None:
        """
        Render business validation results.
        
        Args:
            state: Current product state with validation results
        """
        if not state.market_validation:
            return
        
        st.subheader("📊 Validation Results")
        
        # Overall score
        overall_score = state.market_validation.get("overall_score", "N/A")
        should_continue = state.market_validation.get("should_continue", "false").lower() == "true"
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if overall_score != "N/A":
                score_float = float(overall_score)
                score_color = "green" if score_float >= 7 else "red"
                st.metric(
                    "Business Viability Score",
                    f"{overall_score}/10",
                    delta="Viable" if score_float >= 7 else "Needs Work",
                    delta_color=score_color
                )
            else:
                st.metric("Business Viability Score", "N/A")
        
        with col2:
            recommendation = "✅ Proceed" if should_continue else "❌ Reconsider"
            st.metric("Recommendation", recommendation)
        
        with col3:
            validation_date = state.market_validation.get("validation_timestamp", "N/A")
            if validation_date != "N/A":
                try:
                    date_obj = datetime.fromisoformat(validation_date.replace('Z', '+00:00'))
                    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M")
                except:
                    formatted_date = validation_date
            else:
                formatted_date = "N/A"
            st.metric("Validated On", formatted_date)
        
        # Detailed reasoning
        reasoning = state.market_validation.get("reasoning", "")
        if reasoning:
            with st.expander("📝 Detailed Analysis"):
                st.markdown(reasoning)
        
        # Rejection report if applicable
        rejection_report = state.market_validation.get("rejection_report", "")
        if rejection_report:
            st.error("**Project Development Stopped**")
            with st.expander("📋 Rejection Report"):
                st.markdown(rejection_report)
    
    def render_session_management(self) -> None:
        """
        Render session management controls.
        """
        st.sidebar.subheader("💾 Session Management")
        
        # Current session info
        if st.session_state.session_id:
            st.sidebar.info(f"Session: {st.session_state.session_id[:8]}...")
            
            # Save session button
            if st.sidebar.button("💾 Save Session"):
                if st.session_state.current_state:
                    self.orchestrator.memory.save_session(
                        st.session_state.session_id,
                        st.session_state.current_state
                    )
                    st.sidebar.success("Session saved!")
        
        # Load session
        sessions = self.orchestrator.list_sessions()
        if sessions.get("sessions"):
            session_options = ["Select a session..."] + list(sessions["sessions"].keys())
            selected_session = st.sidebar.selectbox(
                "Load Previous Session:",
                session_options
            )
            
            if selected_session != "Select a session..." and st.sidebar.button("📂 Load Session"):
                loaded_state = self.orchestrator.memory.load_session(selected_session)
                if loaded_state:
                    st.session_state.current_state = loaded_state
                    st.session_state.session_id = selected_session
                    st.sidebar.success("Session loaded!")
                    st.rerun()
                else:
                    st.sidebar.error("Failed to load session")
        
        # Clear current session
        if st.sidebar.button("🗑️ Clear Current Session"):
            st.session_state.current_state = None
            st.session_state.session_id = None
            st.session_state.workflow_running = False
            st.sidebar.success("Session cleared!")
            st.rerun()