import streamlit as st
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, TypedDict, Annotated
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import re
from langgraph.graph import StateGraph, END
# Core Data Models
class ClarificationStatus(Enum):
    INITIAL = "initial"
    ANALYZING = "analyzing"
    QUESTIONING = "questioning"
    REVIEWING = "reviewing"
    COMPLETE = "complete"

@dataclass
class Requirement:
    id: str
    text: str
    category: str
    confidence_level: float
    clarifications_needed: List[str]
    stakeholder_responses: List[str]
    final_requirement: str
    status: str

@dataclass
class ClarificationState:
    messages: List[str]
    requirements: List[Requirement]
    ambiguities: List[str]
    stakeholder_responses: Dict[str, str]
    clarification_status: str
    project_context: str
    session_id: str
    task_breakdown: List[str]
    risk_assessment: List[str]

# Database Manager
class DatabaseManager:
    def __init__(self, db_path: str = "clarification_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clarification_sessions (
                session_id TEXT PRIMARY KEY,
                project_context TEXT,
                state_data TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_state(self, session_id: str, state: ClarificationState):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        state_json = json.dumps(asdict(state), default=str)
        
        cursor.execute('''
            INSERT OR REPLACE INTO clarification_sessions 
            (session_id, project_context, state_data, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, state.project_context, state_json, 
              datetime.now(), datetime.now()))
        
        conn.commit()
        conn.close()
    
    def load_state(self, session_id: str) -> Optional[ClarificationState]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT state_data FROM clarification_sessions 
            WHERE session_id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            state_dict = json.loads(result[0])
            # Convert back to ClarificationState
            requirements = [Requirement(**req) for req in state_dict['requirements']]
            state_dict['requirements'] = requirements
            return ClarificationState(**state_dict)
        return None
    
    def get_all_sessions(self) -> List[tuple]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT session_id, project_context, created_at 
            FROM clarification_sessions 
            ORDER BY updated_at DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        return results

# Core Agent Logic
class ClarificationAgent:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def analyze_requirements(self, project_description: str) -> List[Requirement]:
        """Analyze project description and extract requirements"""
        # Simple keyword-based requirement extraction
        sentences = project_description.split('.')
        requirements = []
        
        categories = {
            'functional': ['feature', 'function', 'should', 'must', 'user', 'system'],
            'technical': ['database', 'api', 'framework', 'technology', 'performance'],
            'business': ['cost', 'revenue', 'profit', 'business', 'market', 'customer'],
            'ui/ux': ['interface', 'design', 'user experience', 'layout', 'responsive']
        }
        
        for i, sentence in enumerate(sentences):
            if sentence.strip():
                category = 'general'
                for cat, keywords in categories.items():
                    if any(keyword in sentence.lower() for keyword in keywords):
                        category = cat
                        break
                
                confidence = 0.8 if len(sentence.split()) > 5 else 0.6
                
                requirements.append(Requirement(
                    id=str(uuid.uuid4()),
                    text=sentence.strip(),
                    category=category,
                    confidence_level=confidence,
                    clarifications_needed=[],
                    stakeholder_responses=[],
                    final_requirement=sentence.strip(),
                    status='pending'
                ))
        
        return requirements
    
    def detect_ambiguities(self, requirements: List[Requirement]) -> List[str]:
        """Detect ambiguous requirements"""
        ambiguities = []
        
        ambiguous_keywords = [
            'some', 'many', 'few', 'several', 'approximately', 'around',
            'fast', 'slow', 'big', 'small', 'good', 'bad', 'nice',
            'user-friendly', 'efficient', 'robust', 'scalable'
        ]
        
        for req in requirements:
            for keyword in ambiguous_keywords:
                if keyword in req.text.lower():
                    ambiguities.append(f"'{keyword}' in requirement: {req.text[:50]}...")
                    req.clarifications_needed.append(f"Please clarify what '{keyword}' means specifically")
        
        # Check for missing information
        missing_info_patterns = [
            (r'database', "What type of database? (SQL/NoSQL, specific technology?)"),
            (r'api', "What API specifications? (REST/GraphQL, authentication method?)"),
            (r'user', "What type of users? (roles, permissions, user groups?)"),
            (r'integration', "Which systems to integrate with? (specific APIs, data formats?)")
        ]
        
        for req in requirements:
            for pattern, question in missing_info_patterns:
                if re.search(pattern, req.text.lower()):
                    if question not in req.clarifications_needed:
                        req.clarifications_needed.append(question)
                        ambiguities.append(f"Missing specification in: {req.text[:50]}...")
        
        return list(set(ambiguities))
    
    def generate_questions(self, requirements: List[Requirement]) -> List[str]:
        """Generate clarification questions"""
        questions = []
        
        for req in requirements:
            if req.clarifications_needed:
                for clarification in req.clarifications_needed:
                    questions.append(f"For requirement '{req.text[:30]}...': {clarification}")
        
        # Add general project questions
        general_questions = [
            "What is the expected number of users?",
            "What is the project timeline?",
            "What is the budget range?",
            "Are there any specific technology constraints?",
            "What are the success metrics?",
            "Who are the main stakeholders?",
            "What are the security requirements?",
            "What are the performance requirements?"
        ]
        
        questions.extend(general_questions[:3])  # Add first 3 general questions
        return questions
    
    def decompose_tasks(self, requirements: List[Requirement]) -> List[str]:
        """Break down requirements into tasks"""
        tasks = []
        
        task_templates = {
            'functional': [
                "Design {feature} functionality",
                "Implement {feature} logic",
                "Test {feature} implementation"
            ],
            'technical': [
                "Set up {technology} infrastructure",
                "Configure {technology} environment",
                "Implement {technology} integration"
            ],
            'ui/ux': [
                "Design {component} interface",
                "Implement {component} frontend",
                "Test {component} usability"
            ]
        }
        
        for req in requirements:
            if req.category in task_templates:
                for template in task_templates[req.category]:
                    # Extract key terms from requirement
                    words = req.text.split()
                    key_term = next((word for word in words if len(word) > 4), "component")
                    task = template.format(feature=key_term, technology=key_term, component=key_term)
                    tasks.append(task)
        
        return tasks
    
    def assess_risks(self, requirements: List[Requirement]) -> List[str]:
        """Assess project risks"""
        risks = []
        
        risk_indicators = {
            'complexity': ['complex', 'advanced', 'sophisticated', 'multiple'],
            'integration': ['integrate', 'third-party', 'external', 'api'],
            'scalability': ['scale', 'growth', 'expand', 'large'],
            'security': ['secure', 'authentication', 'authorization', 'privacy'],
            'performance': ['fast', 'real-time', 'performance', 'speed']
        }
        
        for req in requirements:
            for risk_type, indicators in risk_indicators.items():
                if any(indicator in req.text.lower() for indicator in indicators):
                    risks.append(f"{risk_type.title()} risk: {req.text[:50]}...")
        
        return list(set(risks))

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Clarification AI Agent",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 Clarification AI Agent")
    #st.subtitle("Pre-Coding Phase Requirements Clarification System")
    
    # Initialize session state
    if 'db_manager' not in st.session_state:
        st.session_state.db_manager = DatabaseManager()
    
    if 'agent' not in st.session_state:
        st.session_state.agent = ClarificationAgent(st.session_state.db_manager)
    
    if 'current_state' not in st.session_state:
        st.session_state.current_state = None
    
    # Sidebar for session management
    with st.sidebar:
        st.header("Session Management")
        
        # Create new session
        if st.button("🆕 New Session"):
            session_id = str(uuid.uuid4())
            st.session_state.current_state = ClarificationState(
                messages=[],
                requirements=[],
                ambiguities=[],
                stakeholder_responses={},
                clarification_status=ClarificationStatus.INITIAL.value,
                project_context="",
                session_id=session_id,
                task_breakdown=[],
                risk_assessment=[]
            )
            st.rerun()
        
        # Load existing session
        sessions = st.session_state.db_manager.get_all_sessions()
        if sessions:
            st.subheader("Existing Sessions")
            for session_id, context, created_at in sessions:
                if st.button(f"📁 {context[:20]}..." if context else f"📁 {session_id[:8]}..."):
                    st.session_state.current_state = st.session_state.db_manager.load_state(session_id)
                    st.rerun()
    
    # Main content area
    if st.session_state.current_state is None:
        st.info("👆 Please create a new session or load an existing one from the sidebar")
        return
    
    state = st.session_state.current_state
    
    # Progress indicator
    progress_steps = {
        ClarificationStatus.INITIAL.value: 0,
        ClarificationStatus.ANALYZING.value: 25,
        ClarificationStatus.QUESTIONING.value: 50,
        ClarificationStatus.REVIEWING.value: 75,
        ClarificationStatus.COMPLETE.value: 100
    }
    
    progress = progress_steps.get(state.clarification_status, 0)
    st.progress(progress / 100)
    st.write(f"**Status:** {state.clarification_status.title()}")
    
    # Main workflow tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Project Input", 
        "🔍 Requirements Analysis", 
        "❓ Clarification Questions", 
        "📊 Project Overview",
        "📋 Final Documentation"
    ])
    
    with tab1:
        st.header("Project Description")
        
        project_description = st.text_area(
            "Enter your project description:",
            value=state.project_context,
            height=200,
            help="Describe your project in detail. Include features, requirements, and any specific needs."
        )
        
        if st.button("🚀 Analyze Project", type="primary"):
            if project_description.strip():
                state.project_context = project_description
                state.requirements = st.session_state.agent.analyze_requirements(project_description)
                state.ambiguities = st.session_state.agent.detect_ambiguities(state.requirements)
                state.task_breakdown = st.session_state.agent.decompose_tasks(state.requirements)
                state.risk_assessment = st.session_state.agent.assess_risks(state.requirements)
                state.clarification_status = ClarificationStatus.ANALYZING.value
                
                # Save state
                st.session_state.db_manager.save_state(state.session_id, state)
                st.success("✅ Project analyzed successfully!")
                st.rerun()
            else:
                st.error("Please enter a project description first.")
    
    with tab2:
        st.header("Requirements Analysis")
        
        if state.requirements:
            st.subheader("📋 Extracted Requirements")
            
            for i, req in enumerate(state.requirements):
                with st.expander(f"Requirement {i+1}: {req.text[:50]}..."):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Category:** {req.category}")
                        st.write(f"**Confidence:** {req.confidence_level:.1%}")
                        st.write(f"**Status:** {req.status}")
                    
                    with col2:
                        st.write("**Full Text:**")
                        st.write(req.text)
                    
                    if req.clarifications_needed:
                        st.write("**Clarifications Needed:**")
                        for clarification in req.clarifications_needed:
                            st.write(f"• {clarification}")
            
            st.subheader("⚠️ Detected Ambiguities")
            if state.ambiguities:
                for ambiguity in state.ambiguities:
                    st.warning(ambiguity)
            else:
                st.success("No major ambiguities detected!")
        
        else:
            st.info("No requirements analyzed yet. Please go to the Project Input tab first.")
    
    with tab3:
        st.header("Clarification Questions")
        
        if state.requirements:
            questions = st.session_state.agent.generate_questions(state.requirements)
            
            if questions:
                st.subheader("❓ Questions for Stakeholders")
                
                for i, question in enumerate(questions):
                    st.write(f"**Q{i+1}:** {question}")
                    
                    response_key = f"response_{i}"
                    response = st.text_area(
                        f"Response to Q{i+1}:",
                        key=response_key,
                        height=100
                    )
                    
                    if response:
                        state.stakeholder_responses[question] = response
                
                if st.button("💾 Save Responses"):
                    state.clarification_status = ClarificationStatus.REVIEWING.value
                    st.session_state.db_manager.save_state(state.session_id, state)
                    st.success("✅ Responses saved!")
                    st.rerun()
            else:
                st.info("No clarification questions generated.")
        else:
            st.info("Please analyze the project first.")
    
    with tab4:
        st.header("Project Overview")
        
        if state.requirements:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📈 Project Statistics")
                st.metric("Total Requirements", len(state.requirements))
                st.metric("Ambiguities Found", len(state.ambiguities))
                st.metric("Tasks Identified", len(state.task_breakdown))
                st.metric("Risks Identified", len(state.risk_assessment))
                
                # Requirements by category
                st.subheader("📊 Requirements by Category")
                categories = {}
                for req in state.requirements:
                    categories[req.category] = categories.get(req.category, 0) + 1
                
                for category, count in categories.items():
                    st.write(f"**{category.title()}:** {count}")
            
            with col2:
                st.subheader("🎯 Task Breakdown")
                if state.task_breakdown:
                    for i, task in enumerate(state.task_breakdown[:10]):  # Show first 10 tasks
                        st.write(f"{i+1}. {task}")
                    
                    if len(state.task_breakdown) > 10:
                        st.write(f"... and {len(state.task_breakdown) - 10} more tasks")
                
                st.subheader("⚠️ Risk Assessment")
                if state.risk_assessment:
                    for risk in state.risk_assessment:
                        st.error(risk)
                else:
                    st.success("No significant risks identified!")
    
    with tab5:
        st.header("Final Documentation")
        
        if state.stakeholder_responses:
            st.subheader("📄 Project Requirements Document (PRD)")
            
            # Generate PRD
            prd_content = f"""
# Project Requirements Document

## Project Overview
{state.project_context}

## Requirements Summary
Total Requirements: {len(state.requirements)}
Clarifications Addressed: {len(state.stakeholder_responses)}

## Detailed Requirements
"""
            
            for i, req in enumerate(state.requirements):
                prd_content += f"""
### Requirement {i+1}: {req.category.title()}
**Description:** {req.text}
**Confidence Level:** {req.confidence_level:.1%}
**Status:** {req.status}
"""
                
                if req.clarifications_needed:
                    prd_content += "\n**Clarifications:**\n"
                    for clarification in req.clarifications_needed:
                        prd_content += f"- {clarification}\n"
            
            prd_content += f"""
## Stakeholder Responses
"""
            
            for question, response in state.stakeholder_responses.items():
                prd_content += f"""
**Q:** {question}
**A:** {response}
"""
            
            prd_content += f"""
## Task Breakdown
"""
            for i, task in enumerate(state.task_breakdown):
                prd_content += f"{i+1}. {task}\n"
            
            prd_content += f"""
## Risk Assessment
"""
            for risk in state.risk_assessment:
                prd_content += f"- {risk}\n"
            
            st.text_area("PRD Content:", value=prd_content, height=400)
            
            # Mark as complete
            if st.button("✅ Mark Project as Complete", type="primary"):
                state.clarification_status = ClarificationStatus.COMPLETE.value
                st.session_state.db_manager.save_state(state.session_id, state)
                st.success("🎉 Project clarification completed!")
                st.balloons()
                st.rerun()
            
            # Download PRD
            st.download_button(
                label="📄 Download PRD",
                data=prd_content,
                file_name=f"PRD_{state.session_id[:8]}.md",
                mime="text/markdown"
            )
        
        else:
            st.info("Complete the clarification questions to generate the final documentation.")

if __name__ == "__main__":
    main()