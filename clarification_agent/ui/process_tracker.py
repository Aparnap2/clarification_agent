"""
Simple process tracking component that extends existing functionality.
Reuses session state and integrates with existing ConversationAgent.
"""
import streamlit as st
from datetime import datetime
from typing import Dict, Any, List, Optional


class ProcessTracker:
    """Lightweight process tracking that extends existing session state."""
    
    @staticmethod
    def initialize():
        """Initialize process tracking in session state."""
        if "process_tracker" not in st.session_state:
            st.session_state.process_tracker = {
                "llm_calls": [],
                "citations": [],
                "clarity_scores": {},
                "current_step": None
            }
    
    @staticmethod
    def log_llm_call(prompt: str, response: str, model: str = "deepseek"):
        """Log an LLM call."""
        ProcessTracker.initialize()
        
        call_data = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "prompt": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            "response": response[:200] + "..." if len(response) > 200 else response,
            "model": model,
            "tokens": len(prompt.split()) + len(response.split())
        }
        
        st.session_state.process_tracker["llm_calls"].append(call_data)
        
        # Keep only last 5 calls to save memory
        if len(st.session_state.process_tracker["llm_calls"]) > 5:
            st.session_state.process_tracker["llm_calls"].pop(0)
    
    @staticmethod
    def add_citation(url: str, title: str, snippet: str):
        """Add a web citation."""
        ProcessTracker.initialize()
        
        citation = {
            "url": url,
            "title": title,
            "snippet": snippet[:150] + "..." if len(snippet) > 150 else snippet,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        
        st.session_state.process_tracker["citations"].append(citation)
        
        # Keep only last 3 citations
        if len(st.session_state.process_tracker["citations"]) > 3:
            st.session_state.process_tracker["citations"].pop(0)
    
    @staticmethod
    def set_current_step(step_name: str):
        """Set the current processing step."""
        ProcessTracker.initialize()
        st.session_state.process_tracker["current_step"] = {
            "name": step_name,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
    
    @staticmethod
    def render_sidebar_summary():
        """Render a compact summary in sidebar."""
        ProcessTracker.initialize()
        tracker = st.session_state.process_tracker
        
        if tracker["llm_calls"] or tracker["citations"]:
            st.sidebar.markdown("### 📊 Process Summary")
            
            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.metric("LLM Calls", len(tracker["llm_calls"]))
            with col2:
                st.metric("Citations", len(tracker["citations"]))
            
            if tracker["current_step"]:
                st.sidebar.info(f"**Current:** {tracker['current_step']['name']}")
    
    @staticmethod
    def render_expandable_details():
        """Render expandable process details."""
        ProcessTracker.initialize()
        tracker = st.session_state.process_tracker
        
        with st.expander("🔍 Process Details", expanded=False):
            # Recent LLM Calls
            if tracker["llm_calls"]:
                st.markdown("**Recent LLM Calls:**")
                for call in tracker["llm_calls"][-2:]:  # Show last 2
                    st.markdown(f"- {call['timestamp']} - {call['model']} ({call['tokens']} tokens)")
                    with st.expander(f"Call details", expanded=False):
                        st.text(f"Prompt: {call['prompt']}")
                        st.text(f"Response: {call['response']}")
            
            # Citations
            if tracker["citations"]:
                st.markdown("**Web Citations:**")
                for citation in tracker["citations"]:
                    st.markdown(f"- [{citation['title']}]({citation['url']})")
                    st.caption(citation['snippet'])
    
    @staticmethod
    def get_stats():
        """Get simple stats for display."""
        ProcessTracker.initialize()
        tracker = st.session_state.process_tracker
        
        return {
            "total_calls": len(tracker["llm_calls"]),
            "total_citations": len(tracker["citations"]),
            "total_tokens": sum(call.get("tokens", 0) for call in tracker["llm_calls"])
        }