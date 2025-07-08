"""
Enhanced visualizations for the Clarification Agent.
Provides interactive workflow visualization and progress tracking.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List, Optional
from clarification_agent.config.node_config import get_node_config_manager


class WorkflowVisualizer:
    """Creates interactive visualizations for the workflow."""
    
    def __init__(self):
        self.config_manager = get_node_config_manager()
    
    def render_progress_bar(self, current_node: str) -> None:
        """Render an animated progress bar showing workflow progress."""
        node_order = self.config_manager.get_node_order()
        
        if current_node not in node_order:
            return
        
        current_index = node_order.index(current_node)
        total_nodes = len(node_order)
        progress = (current_index + 1) / total_nodes
        
        # Create progress bar with custom styling
        st.markdown(f"""
        <div style="margin: 10px 0;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="font-weight: bold;">Workflow Progress</span>
                <span style="color: #666;">Step {current_index + 1} of {total_nodes}</span>
            </div>
            <div style="width: 100%; background-color: #e0e0e0; border-radius: 10px; height: 20px; overflow: hidden;">
                <div style="width: {progress * 100}%; background: linear-gradient(90deg, #4CAF50, #81C784); height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show current node info
        node_config = self.config_manager.get_node_config(current_node)
        st.info(f"**{node_config['emoji']} {node_config['label']}**: {node_config['purpose']}")
    
    def render_workflow_flowchart(self, current_node: str, completed_nodes: set) -> None:
        """Render an interactive flowchart of the workflow."""
        nodes_config = self.config_manager.get_all_nodes()
        node_order = self.config_manager.get_node_order()
        
        # Prepare data for Plotly
        node_labels = []
        node_colors = []
        node_positions_x = []
        node_positions_y = []
        
        # Create a horizontal flow layout
        for i, node_id in enumerate(node_order):
            node_config = nodes_config[node_id]
            node_labels.append(f"{node_config['emoji']} {node_config['label']}")
            
            # Color based on status
            if node_id == current_node:
                node_colors.append('#FF5722')  # Active - Orange/Red
            elif node_id in completed_nodes:
                node_colors.append('#4CAF50')  # Completed - Green
            else:
                node_colors.append('#E0E0E0')  # Pending - Gray
            
            # Position nodes horizontally
            node_positions_x.append(i * 2)
            node_positions_y.append(0)
        
        # Create edges for connections
        edge_x = []
        edge_y = []
        
        for i in range(len(node_order) - 1):
            # Line from current node to next
            edge_x.extend([i * 2, (i + 1) * 2, None])
            edge_y.extend([0, 0, None])
        
        # Create the plot
        fig = go.Figure()
        
        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            mode='lines',
            line=dict(width=2, color='#CCCCCC'),
            hoverinfo='none',
            showlegend=False
        ))
        
        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_positions_x, y=node_positions_y,
            mode='markers+text',
            marker=dict(
                size=40,
                color=node_colors,
                line=dict(width=2, color='white')
            ),
            text=node_labels,
            textposition="bottom center",
            textfont=dict(size=10),
            hovertemplate='<b>%{text}</b><extra></extra>',
            showlegend=False
        ))
        
        # Update layout
        fig.update_layout(
            title="Workflow Progress",
            showlegend=False,
            height=200,
            margin=dict(l=20, r=20, t=40, b=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def render_node_details_tabs(self, node_id: str, process_data: Dict[str, Any]) -> None:
        """Render tabbed interface for node details."""
        node_config = self.config_manager.get_node_config(node_id)
        
        tabs = st.tabs(["📋 Node Info", "🤖 LLM Calls", "📚 Citations", "⚙️ Settings"])
        
        with tabs[0]:  # Node Info
            st.markdown(f"### {node_config['emoji']} {node_config['label']}")
            st.write(f"**Purpose**: {node_config['purpose']}")
            
            # Show clarity rules
            if node_config.get('clarity_rules'):
                st.markdown("**Clarity Rules**:")
                for rule in node_config['clarity_rules']:
                    st.write(f"- {rule['type']}: {rule.get('message', 'Custom validation')}")
            
            # Show node capabilities
            capabilities = []
            if node_config.get('optional'):
                capabilities.append("Optional")
            if node_config.get('retry'):
                capabilities.append("Retryable")
            if node_config.get('skip'):
                capabilities.append("Skippable")
            if node_config.get('web_search'):
                capabilities.append("Web Search Enabled")
            
            if capabilities:
                st.markdown(f"**Capabilities**: {', '.join(capabilities)}")
        
        with tabs[1]:  # LLM Calls
            llm_calls = process_data.get('llm_calls', [])
            if llm_calls:
                st.markdown("**Recent LLM Interactions**:")
                for i, call in enumerate(llm_calls[-3:], 1):  # Show last 3
                    with st.expander(f"Call {i} - {call.get('timestamp', 'Unknown time')}", expanded=i == 1):
                        st.markdown("**Prompt**:")
                        st.code(call.get('prompt', 'No prompt recorded'), language='text')
                        st.markdown("**Response**:")
                        st.code(call.get('response', 'No response recorded'), language='text')
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("Model", call.get('model', 'Unknown'))
                        with col2:
                            st.metric("Tokens", call.get('tokens', 0))
            else:
                st.info("No LLM calls recorded for this session")
        
        with tabs[2]:  # Citations
            citations = process_data.get('citations', [])
            if citations:
                st.markdown("**Web Search Results & Citations**:")
                for citation in citations:
                    with st.expander(f"📄 {citation.get('title', 'Untitled')}", expanded=False):
                        st.markdown(f"**URL**: [{citation.get('url', 'No URL')}]({citation.get('url', '#')})")
                        st.markdown(f"**Source**: {citation.get('source', 'Unknown')}")
                        st.markdown("**Snippet**:")
                        st.write(citation.get('snippet', 'No content available'))
                        if citation.get('timestamp'):
                            st.caption(f"Retrieved: {citation['timestamp']}")
            else:
                st.info("No citations available")
        
        with tabs[3]:  # Settings
            st.markdown("**Node Configuration**:")
            
            # Show transitions
            transitions = node_config.get('transitions', {})
            if transitions:
                st.markdown("**Available Transitions**:")
                for trans_type, target in transitions.items():
                    st.write(f"- {trans_type}: → {target}")
            
            # Show parallel nodes
            parallel_nodes = node_config.get('parallel_nodes', [])
            if parallel_nodes:
                st.markdown(f"**Parallel Nodes**: {', '.join(parallel_nodes)}")
            
            # Show web search config
            if node_config.get('web_search'):
                search_query = node_config.get('search_query', 'No query template')
                st.markdown(f"**Search Query Template**: `{search_query}`")
    
    def render_project_summary_card(self, project_data: Dict[str, Any]) -> None:
        """Render a visually appealing project summary."""
        st.markdown("### 🎯 Project Summary")
        
        # Create a card-like layout
        with st.container():
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 15px;
                color: white;
                margin: 10px 0;
            ">
                <h3 style="margin: 0; color: white;">✨ Project Overview</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Project details in columns
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📝 Project Name**")
                st.write(project_data.get('name', 'Unnamed Project'))
                
                st.markdown("**🎯 Description**")
                st.write(project_data.get('description', 'No description available'))
            
            with col2:
                st.markdown("**⭐ MVP Features**")
                features = project_data.get('mvp_features', [])
                if features:
                    for feature in features[:5]:  # Show first 5
                        st.write(f"• {feature}")
                    if len(features) > 5:
                        st.caption(f"... and {len(features) - 5} more")
                else:
                    st.write("No features specified")
            
            with col3:
                st.markdown("**🛠️ Tech Stack**")
                tech_stack = project_data.get('tech_stack', [])
                if tech_stack:
                    for tech in tech_stack:
                        st.write(f"• {tech}")
                else:
                    st.write("No technologies specified")
            
            # Excluded features
            excluded = project_data.get('excluded_features', [])
            if excluded:
                st.markdown("**🚫 Excluded from MVP**")
                for item in excluded[:3]:  # Show first 3
                    st.write(f"• {item}")
                if len(excluded) > 3:
                    st.caption(f"... and {len(excluded) - 3} more exclusions")
    
    def render_statistics_dashboard(self, process_data: Dict[str, Any]) -> None:
        """Render a statistics dashboard."""
        st.markdown("### 📊 Session Statistics")
        
        # Calculate statistics
        total_llm_calls = len(process_data.get('llm_calls', []))
        total_citations = len(process_data.get('citations', []))
        total_tokens = sum(call.get('tokens', 0) for call in process_data.get('llm_calls', []))
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="🤖 LLM Calls",
                value=total_llm_calls,
                help="Total number of LLM API calls made"
            )
        
        with col2:
            st.metric(
                label="📚 Citations",
                value=total_citations,
                help="Web search results and citations found"
            )
        
        with col3:
            st.metric(
                label="🔤 Tokens Used",
                value=f"{total_tokens:,}",
                help="Estimated total tokens processed"
            )
        
        with col4:
            # Calculate session duration if timestamps available
            llm_calls = process_data.get('llm_calls', [])
            if len(llm_calls) >= 2:
                # Simple duration calculation
                st.metric(
                    label="⏱️ Duration",
                    value="Active",
                    help="Session is currently active"
                )
            else:
                st.metric(
                    label="⏱️ Duration",
                    value="< 1 min",
                    help="Session duration"
                )


# Convenience functions for easy integration
def render_enhanced_workflow_sidebar(current_node: str, completed_nodes: set, process_data: Dict[str, Any]):
    """Render enhanced workflow visualization in sidebar."""
    visualizer = WorkflowVisualizer()
    
    st.sidebar.markdown("## 🗺️ Workflow")
    visualizer.render_progress_bar(current_node)
    
    st.sidebar.markdown("---")
    visualizer.render_statistics_dashboard(process_data)

def render_enhanced_process_details(current_node: str, process_data: Dict[str, Any]):
    """Render enhanced process details with tabs."""
    visualizer = WorkflowVisualizer()
    
    with st.expander("🔍 Enhanced Process Details", expanded=False):
        visualizer.render_node_details_tabs(current_node, process_data)

def render_project_completion_summary(project_data: Dict[str, Any]):
    """Render project completion summary."""
    visualizer = WorkflowVisualizer()
    visualizer.render_project_summary_card(project_data)