"""
Beautiful CSS styles for agent activity logging
"""

def get_activity_styles():
    """Return CSS styles for beautiful activity logging"""
    return """
    <style>
    /* Activity Card Animations */
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.02); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    @keyframes shimmer {
        0% { background-position: -200px 0; }
        100% { background-position: calc(200px + 100%) 0; }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Activity Container */
    .activity-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        animation: slideInRight 0.3s ease-out;
    }
    
    /* Current Activity (In Progress) */
    .activity-current {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.3);
        animation: pulse 2s infinite;
        position: relative;
        overflow: hidden;
    }
    
    .activity-current::before {
        content: '';
        position: absolute;
        top: 0;
        left: -200px;
        width: 200px;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        animation: shimmer 2s infinite;
    }
    
    /* Completed Activity */
    .activity-completed {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        border-left: 4px solid #27ae60;
        border-radius: 8px;
        padding: 12px;
        margin: 6px 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        animation: fadeIn 0.5s ease-in;
        transition: all 0.3s ease;
    }
    
    .activity-completed:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    /* Failed Activity */
    .activity-failed {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-left: 4px solid #e74c3c;
        border-radius: 8px;
        padding: 12px;
        margin: 6px 0;
        box-shadow: 0 2px 4px rgba(231, 76, 60, 0.2);
        animation: fadeIn 0.5s ease-in;
    }
    
    /* Activity Types */
    .activity-thinking {
        border-left-color: #3498db;
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
    }
    
    .activity-search {
        border-left-color: #f39c12;
        background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 100%);
    }
    
    .activity-tool-call {
        border-left-color: #e74c3c;
        background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
    }
    
    .activity-analysis {
        border-left-color: #9b59b6;
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
    }
    
    .activity-generation {
        border-left-color: #2ecc71;
        background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
    }
    
    /* Activity Header */
    .activity-header {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        font-weight: 600;
    }
    
    .activity-icon {
        font-size: 18px;
        margin-right: 10px;
        animation: fadeIn 0.3s ease-in;
    }
    
    .activity-title {
        flex-grow: 1;
        font-size: 14px;
        color: #2c3e50;
    }
    
    .activity-timestamp {
        font-size: 11px;
        color: #7f8c8d;
        font-weight: normal;
    }
    
    .activity-duration {
        font-size: 10px;
        color: #95a5a6;
        margin-left: 8px;
        background: rgba(255, 255, 255, 0.7);
        padding: 2px 6px;
        border-radius: 10px;
    }
    
    /* Activity Description */
    .activity-description {
        font-size: 13px;
        color: #34495e;
        line-height: 1.4;
        margin-bottom: 8px;
    }
    
    /* Activity Details */
    .activity-details {
        background: rgba(255, 255, 255, 0.8);
        border-radius: 6px;
        padding: 8px;
        margin-top: 8px;
        font-size: 11px;
        color: #5d6d7e;
        border: 1px solid rgba(0, 0, 0, 0.1);
    }
    
    /* Status Indicators */
    .status-started {
        color: #f39c12;
        animation: pulse 1.5s infinite;
    }
    
    .status-in-progress {
        color: #3498db;
        animation: pulse 2s infinite;
    }
    
    .status-completed {
        color: #27ae60;
    }
    
    .status-failed {
        color: #e74c3c;
    }
    
    /* Progress Bar */
    .activity-progress {
        width: 100%;
        height: 4px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 2px;
        overflow: hidden;
        margin-top: 8px;
    }
    
    .activity-progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #667eea, #764ba2);
        border-radius: 2px;
        animation: shimmer 2s infinite;
    }
    
    /* Tool Call Specific Styles */
    .tool-call-params {
        background: rgba(52, 73, 94, 0.1);
        border-radius: 4px;
        padding: 6px;
        margin: 4px 0;
        font-family: 'Courier New', monospace;
        font-size: 10px;
        border-left: 3px solid #34495e;
    }
    
    .tool-call-result {
        background: rgba(39, 174, 96, 0.1);
        border-radius: 4px;
        padding: 6px;
        margin: 4px 0;
        font-family: 'Courier New', monospace;
        font-size: 10px;
        border-left: 3px solid #27ae60;
    }
    
    /* Search Result Styles */
    .search-query {
        background: rgba(243, 156, 18, 0.1);
        border-radius: 4px;
        padding: 4px 8px;
        margin: 4px 0;
        font-weight: 600;
        color: #f39c12;
        border-left: 3px solid #f39c12;
    }
    
    .search-results-count {
        background: rgba(52, 152, 219, 0.1);
        border-radius: 4px;
        padding: 4px 8px;
        margin: 4px 0;
        color: #3498db;
        font-size: 11px;
        border-left: 3px solid #3498db;
    }
    
    /* Responsive Design */
    @media (max-width: 768px) {
        .activity-container,
        .activity-current,
        .activity-completed,
        .activity-failed {
            margin: 4px 0;
            padding: 10px;
        }
        
        .activity-title {
            font-size: 12px;
        }
        
        .activity-description {
            font-size: 11px;
        }
    }
    
    /* Dark Mode Support */
    @media (prefers-color-scheme: dark) {
        .activity-completed {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: #ecf0f1;
        }
        
        .activity-title {
            color: #ecf0f1;
        }
        
        .activity-description {
            color: #bdc3c7;
        }
        
        .activity-details {
            background: rgba(0, 0, 0, 0.3);
            color: #95a5a6;
        }
    }
    
    /* Scrollbar Styling */
    .activity-scroll::-webkit-scrollbar {
        width: 6px;
    }
    
    .activity-scroll::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
    }
    
    .activity-scroll::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;
    }
    
    .activity-scroll::-webkit-scrollbar-thumb:hover {
        background: #a8a8a8;
    }
    </style>
    """

def get_activity_card_html(activity, is_current=False, show_details=False):
    """Generate HTML for an activity card with beautiful styling"""
    
    # Activity type classes
    type_classes = {
        "thinking": "activity-thinking",
        "tool_call": "activity-tool-call", 
        "search": "activity-search",
        "analysis": "activity-analysis",
        "generation": "activity-generation"
    }
    
    # Status icons and classes
    status_config = {
        "started": {"icon": "🟡", "class": "status-started"},
        "in_progress": {"icon": "🔄", "class": "status-in-progress"},
        "completed": {"icon": "✅", "class": "status-completed"},
        "failed": {"icon": "❌", "class": "status-failed"}
    }
    
    activity_type = activity.type.value if hasattr(activity.type, 'value') else str(activity.type)
    activity_status = activity.status.value if hasattr(activity.status, 'value') else str(activity.status)
    
    type_class = type_classes.get(activity_type, "")
    status_info = status_config.get(activity_status, {"icon": "⚪", "class": ""})
    
    # Base container class
    if is_current:
        container_class = "activity-current"
    elif activity_status == "completed":
        container_class = f"activity-completed {type_class}"
    elif activity_status == "failed":
        container_class = "activity-failed"
    else:
        container_class = f"activity-container {type_class}"
    
    # Format timestamp
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(activity.timestamp.replace('Z', '+00:00'))
        formatted_time = dt.strftime("%H:%M:%S")
    except:
        formatted_time = activity.timestamp
    
    # Duration text
    duration_text = ""
    if activity.duration:
        duration_text = f'<span class="activity-duration">({activity.duration:.2f}s)</span>'
    
    # Build HTML
    html = f"""
    <div class="{container_class}">
        <div class="activity-header">
            <span class="activity-icon {status_info['class']}">{status_info['icon']}</span>
            <span class="activity-title">{activity.title}</span>
            <span class="activity-timestamp">{formatted_time}</span>
            {duration_text}
        </div>
        <div class="activity-description">{activity.description}</div>
    """
    
    # Add progress bar for current activities
    if is_current:
        html += """
        <div class="activity-progress">
            <div class="activity-progress-bar"></div>
        </div>
        """
    
    # Add details if requested and available
    if show_details and activity.details:
        html += '<div class="activity-details">'
        
        # Special formatting for different activity types
        if activity_type == "tool_call":
            if "tool_name" in activity.details:
                html += f'<div class="tool-call-params"><strong>Tool:</strong> {activity.details["tool_name"]}</div>'
            if "parameters" in activity.details:
                html += f'<div class="tool-call-params"><strong>Parameters:</strong> {activity.details["parameters"]}</div>'
            if "result" in activity.details:
                html += f'<div class="tool-call-result"><strong>Result:</strong> {activity.details["result"]}</div>'
        
        elif activity_type == "search":
            if "query" in activity.details:
                html += f'<div class="search-query">Query: {activity.details["query"]}</div>'
            if "engine" in activity.details:
                html += f'<div class="search-results-count">Engine: {activity.details["engine"]}</div>'
            if "results_count" in activity.details:
                html += f'<div class="search-results-count">Results: {activity.details["results_count"]}</div>'
        
        else:
            # Generic details display
            for key, value in activity.details.items():
                if isinstance(value, (str, int, float, bool)):
                    html += f'<div><strong>{key}:</strong> {value}</div>'
        
        html += '</div>'
    
    html += '</div>'
    
    return html

# Example usage
if __name__ == "__main__":
    print("Activity styles module loaded successfully!")
    print("Use get_activity_styles() to get CSS styles")
    print("Use get_activity_card_html() to generate activity cards")