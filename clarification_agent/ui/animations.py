"""
Simple CSS animations for enhanced UI experience.
Modular component that can be injected into existing Streamlit apps.
"""
import streamlit as st


def inject_chat_animations():
    """Inject CSS animations into the current Streamlit app."""
    st.markdown("""
    <style>
    /* Fade-in animation for new messages */
    .fade-in {
        animation: fadeIn 0.6s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Active node pulsing */
    .active-node {
        animation: pulse 2s infinite;
        border-left: 4px solid #4CAF50;
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.1) 0%, rgba(76, 175, 80, 0.05) 100%);
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(76, 175, 80, 0); }
        100% { box-shadow: 0 0 0 0 rgba(76, 175, 80, 0); }
    }
    
    /* Processing indicator */
    .processing {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 12px;
        background: rgba(33, 150, 243, 0.1);
        border-radius: 6px;
        margin: 4px 0;
    }
    
    .typing-dots::after {
        content: '...';
        animation: typing 1.5s infinite;
    }
    
    @keyframes typing {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    </style>
    """, unsafe_allow_html=True)


def show_typing_indicator(message="Processing..."):
    """Show a simple typing indicator."""
    return f"""
    <div class="processing fade-in">
        <span class="typing-dots">{message}</span>
    </div>
    """


def create_animated_container(content, is_active=False):
    """Create an animated container for content."""
    classes = "fade-in"
    if is_active:
        classes += " active-node"
    
    return f'<div class="{classes}">{content}</div>'