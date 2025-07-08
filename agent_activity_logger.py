"""
Agent Activity Logger - Beautiful UI for tracking agent activities and tool calls
"""
import streamlit as st
import time
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from activity_styles import get_activity_styles, get_activity_card_html

class ActivityType(Enum):
    """Types of agent activities"""
    THINKING = "thinking"
    TOOL_CALL = "tool_call"
    SEARCH = "search"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    ERROR = "error"
    SUCCESS = "success"
    INFO = "info"

class ActivityStatus(Enum):
    """Status of activities"""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class ActivityLog:
    """Single activity log entry"""
    id: str
    type: ActivityType
    status: ActivityStatus
    title: str
    description: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = None
    duration: Optional[float] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
        if self.start_time is None:
            self.start_time = time.time()

class AgentActivityLogger:
    """Beautiful agent activity logger with real-time updates"""
    
    def __init__(self):
        if "activity_logs" not in st.session_state:
            st.session_state.activity_logs = []
        if "current_activities" not in st.session_state:
            st.session_state.current_activities = {}
        if "activity_container" not in st.session_state:
            st.session_state.activity_container = None
    
    def start_activity(self, 
                      activity_type: ActivityType, 
                      title: str, 
                      description: str,
                      details: Optional[Dict[str, Any]] = None) -> str:
        """Start a new activity and return its ID"""
        activity_id = str(uuid.uuid4())[:8]
        
        activity = ActivityLog(
            id=activity_id,
            type=activity_type,
            status=ActivityStatus.STARTED,
            title=title,
            description=description,
            details=details or {}
        )
        
        st.session_state.current_activities[activity_id] = activity
        st.session_state.activity_logs.append(activity)
        
        self._update_display()
        return activity_id
    
    def update_activity(self, 
                       activity_id: str, 
                       status: Optional[ActivityStatus] = None,
                       description: Optional[str] = None,
                       details: Optional[Dict[str, Any]] = None):
        """Update an existing activity"""
        if activity_id in st.session_state.current_activities:
            activity = st.session_state.current_activities[activity_id]
            
            if status:
                activity.status = status
            if description:
                activity.description = description
            if details:
                activity.details.update(details)
            
            # Update in logs list as well
            for i, log in enumerate(st.session_state.activity_logs):
                if log.id == activity_id:
                    st.session_state.activity_logs[i] = activity
                    break
            
            self._update_display()
    
    def complete_activity(self, 
                         activity_id: str, 
                         description: Optional[str] = None,
                         details: Optional[Dict[str, Any]] = None):
        """Complete an activity"""
        if activity_id in st.session_state.current_activities:
            activity = st.session_state.current_activities[activity_id]
            activity.status = ActivityStatus.COMPLETED
            activity.end_time = time.time()
            activity.duration = activity.end_time - activity.start_time
            
            if description:
                activity.description = description
            if details:
                activity.details.update(details)
            
            # Update in logs list
            for i, log in enumerate(st.session_state.activity_logs):
                if log.id == activity_id:
                    st.session_state.activity_logs[i] = activity
                    break
            
            # Remove from current activities
            del st.session_state.current_activities[activity_id]
            
            self._update_display()
    
    def fail_activity(self, 
                     activity_id: str, 
                     error_message: str,
                     details: Optional[Dict[str, Any]] = None):
        """Mark an activity as failed"""
        if activity_id in st.session_state.current_activities:
            activity = st.session_state.current_activities[activity_id]
            activity.status = ActivityStatus.FAILED
            activity.end_time = time.time()
            activity.duration = activity.end_time - activity.start_time
            activity.description = error_message
            
            if details:
                activity.details.update(details)
            
            # Update in logs list
            for i, log in enumerate(st.session_state.activity_logs):
                if log.id == activity_id:
                    st.session_state.activity_logs[i] = activity
                    break
            
            # Remove from current activities
            del st.session_state.current_activities[activity_id]
            
            self._update_display()
    
    def log_tool_call(self, 
                     tool_name: str, 
                     parameters: Dict[str, Any],
                     result: Optional[Any] = None,
                     error: Optional[str] = None) -> str:
        """Log a tool call with parameters and results"""
        activity_id = self.start_activity(
            ActivityType.TOOL_CALL,
            f"🔧 Tool Call: {tool_name}",
            f"Calling {tool_name} with parameters",
            {
                "tool_name": tool_name,
                "parameters": parameters,
                "result": result,
                "error": error
            }
        )
        
        if error:
            self.fail_activity(activity_id, f"Tool call failed: {error}")
        elif result is not None:
            self.complete_activity(
                activity_id, 
                f"Tool call completed successfully",
                {"result": result}
            )
        
        return activity_id
    
    def log_search(self, 
                  query: str, 
                  engine: str,
                  results_count: Optional[int] = None,
                  error: Optional[str] = None) -> str:
        """Log a web search activity"""
        activity_id = self.start_activity(
            ActivityType.SEARCH,
            f"🔍 Web Search: {query}",
            f"Searching with {engine}",
            {
                "query": query,
                "engine": engine,
                "results_count": results_count,
                "error": error
            }
        )
        
        if error:
            self.fail_activity(activity_id, f"Search failed: {error}")
        elif results_count is not None:
            self.complete_activity(
                activity_id,
                f"Found {results_count} results",
                {"results_count": results_count}
            )
        
        return activity_id
    
    def _update_display(self):
        """Update the activity display"""
        if st.session_state.activity_container:
            with st.session_state.activity_container:
                self._render_activities()
    
    def _render_activities(self):
        """Render the activity logs in a beautiful UI"""
        # Inject CSS styles
        st.markdown(get_activity_styles(), unsafe_allow_html=True)
        
        st.markdown("### 🤖 Agent Activity")
        
        # Show current activities (in progress)
        if st.session_state.current_activities:
            st.markdown("#### 🔄 Current Activities")
            for activity in st.session_state.current_activities.values():
                activity_html = get_activity_card_html(activity, is_current=True)
                st.markdown(activity_html, unsafe_allow_html=True)
        
        # Show recent completed activities
        recent_logs = [log for log in st.session_state.activity_logs 
                      if log.status in [ActivityStatus.COMPLETED, ActivityStatus.FAILED]][-10:]
        
        if recent_logs:
            st.markdown("#### 📋 Recent Activities")
            
            # Toggle for detailed view
            show_details = st.checkbox("Show detailed view", key="show_activity_details")
            
            # Create scrollable container for activities
            with st.container():
                for activity in reversed(recent_logs):
                    activity_html = get_activity_card_html(activity, show_details=show_details)
                    st.markdown(activity_html, unsafe_allow_html=True)
    
    def _render_activity_card(self, activity: ActivityLog, is_current: bool = False, show_details: bool = False):
        """Render a single activity card"""
        # Choose colors and icons based on activity type and status
        colors = {
            ActivityType.THINKING: "#3498db",
            ActivityType.TOOL_CALL: "#e74c3c",
            ActivityType.SEARCH: "#f39c12",
            ActivityType.ANALYSIS: "#9b59b6",
            ActivityType.GENERATION: "#2ecc71",
            ActivityType.ERROR: "#e74c3c",
            ActivityType.SUCCESS: "#27ae60",
            ActivityType.INFO: "#34495e"
        }
        
        status_icons = {
            ActivityStatus.STARTED: "🟡",
            ActivityStatus.IN_PROGRESS: "🔄",
            ActivityStatus.COMPLETED: "✅",
            ActivityStatus.FAILED: "❌"
        }
        
        color = colors.get(activity.type, "#95a5a6")
        icon = status_icons.get(activity.status, "⚪")
        
        # Create card container
        with st.container():
            if is_current:
                # Animated current activity
                st.markdown(f"""
                <div style="
                    border-left: 4px solid {color};
                    padding: 12px;
                    margin: 8px 0;
                    background: linear-gradient(90deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%);
                    border-radius: 8px;
                    animation: pulse 2s infinite;
                ">
                    <div style="display: flex; align-items: center; margin-bottom: 8px;">
                        <span style="font-size: 16px; margin-right: 8px;">{icon}</span>
                        <strong style="color: {color};">{activity.title}</strong>
                        <span style="margin-left: auto; font-size: 12px; color: #7f8c8d;">
                            {self._format_timestamp(activity.timestamp)}
                        </span>
                    </div>
                    <div style="color: #2c3e50; font-size: 14px;">
                        {activity.description}
                    </div>
                </div>
                
                <style>
                @keyframes pulse {{
                    0% {{ opacity: 1; }}
                    50% {{ opacity: 0.7; }}
                    100% {{ opacity: 1; }}
                }}
                </style>
                """, unsafe_allow_html=True)
            else:
                # Completed activity card
                duration_text = f" ({activity.duration:.2f}s)" if activity.duration else ""
                
                if show_details and activity.details:
                    # Detailed view with expandable details
                    with st.expander(f"{icon} {activity.title}{duration_text}", expanded=False):
                        st.write(f"**Description:** {activity.description}")
                        st.write(f"**Status:** {activity.status.value}")
                        st.write(f"**Time:** {self._format_timestamp(activity.timestamp)}")
                        
                        if activity.details:
                            st.write("**Details:**")
                            st.json(activity.details)
                else:
                    # Collapsed view
                    st.markdown(f"""
                    <div style="
                        border-left: 3px solid {color};
                        padding: 8px 12px;
                        margin: 4px 0;
                        background: rgba(248, 249, 250, 0.8);
                        border-radius: 6px;
                    ">
                        <div style="display: flex; align-items: center;">
                            <span style="margin-right: 8px;">{icon}</span>
                            <span style="font-weight: 500; color: #2c3e50;">{activity.title}</span>
                            <span style="margin-left: auto; font-size: 11px; color: #7f8c8d;">
                                {self._format_timestamp(activity.timestamp)}{duration_text}
                            </span>
                        </div>
                        <div style="font-size: 12px; color: #5d6d7e; margin-top: 4px;">
                            {activity.description}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format timestamp for display"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%H:%M:%S")
        except:
            return timestamp
    
    def create_activity_sidebar(self):
        """Create activity sidebar in Streamlit"""
        with st.sidebar:
            st.markdown("---")
            st.session_state.activity_container = st.container()
            self._render_activities()
    
    def clear_logs(self):
        """Clear all activity logs"""
        st.session_state.activity_logs = []
        st.session_state.current_activities = {}
        self._update_display()

# Context manager for easy activity logging
class ActivityContext:
    """Context manager for automatic activity logging"""
    
    def __init__(self, logger: AgentActivityLogger, activity_type: ActivityType, title: str, description: str):
        self.logger = logger
        self.activity_type = activity_type
        self.title = title
        self.description = description
        self.activity_id = None
    
    def __enter__(self):
        self.activity_id = self.logger.start_activity(
            self.activity_type, self.title, self.description
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.logger.fail_activity(
                self.activity_id, 
                f"Error: {str(exc_val)}"
            )
        else:
            self.logger.complete_activity(self.activity_id)
    
    def update(self, description: str, details: Optional[Dict[str, Any]] = None):
        """Update activity description and details"""
        self.logger.update_activity(self.activity_id, description=description, details=details)

# Example usage and testing
if __name__ == "__main__":
    # Test the activity logger
    logger = AgentActivityLogger()
    
    # Test different activity types
    thinking_id = logger.start_activity(
        ActivityType.THINKING,
        "🤔 Analyzing user request",
        "Processing user input and determining next steps"
    )
    
    time.sleep(1)
    
    search_id = logger.log_search(
        "Python web frameworks 2024",
        "duckduckgo",
        results_count=5
    )
    
    tool_id = logger.log_tool_call(
        "web_crawler",
        {"url": "https://example.com", "timeout": 30},
        result={"status": "success", "content_length": 1024}
    )
    
    logger.complete_activity(thinking_id, "Analysis complete, proceeding with search")
    
    print("Activity logger test completed!")