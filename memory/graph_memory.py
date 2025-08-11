"""Graph memory system for persistent state management."""

import pickle
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any

from models.data_models import ProductState

logger = logging.getLogger(__name__)


class GraphMemory:
    """
    Graph memory system with pickle-based persistence for session management.
    
    Provides session save/load functionality with error handling and backward
    compatibility for data model changes.
    """
    
    def __init__(self, memory_path: str = "graph_memory.pkl"):
        """
        Initialize GraphMemory with specified storage path.
        
        Args:
            memory_path: Path to the pickle file for persistence
        """
        self.memory_path = Path(memory_path)
        self.memory: Dict[str, Dict[str, Any]] = {}
        self._load_memory()
    
    def _load_memory(self) -> None:
        """
        Load memory from pickle file with error handling.
        
        Creates empty memory if file doesn't exist or is corrupted.
        """
        try:
            if self.memory_path.exists():
                with open(self.memory_path, 'rb') as f:
                    self.memory = pickle.load(f)
                logger.info(f"Loaded memory from {self.memory_path}")
            else:
                self.memory = {}
                logger.info(f"Created new memory store at {self.memory_path}")
        except (pickle.PickleError, EOFError, FileNotFoundError) as e:
            logger.error(f"Failed to load memory from {self.memory_path}: {e}")
            self.memory = {}
            # Create backup of corrupted file
            if self.memory_path.exists():
                backup_path = self.memory_path.with_suffix('.pkl.backup')
                self.memory_path.rename(backup_path)
                logger.info(f"Corrupted memory file backed up to {backup_path}")
    
    def _persist_memory(self) -> None:
        """
        Persist memory to pickle file with error handling.
        
        Creates directory if it doesn't exist and handles write errors gracefully.
        """
        try:
            # Ensure directory exists
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first, then rename for atomic operation
            temp_path = self.memory_path.with_suffix('.tmp')
            with open(temp_path, 'wb') as f:
                pickle.dump(self.memory, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Atomic rename
            temp_path.rename(self.memory_path)
            logger.debug(f"Memory persisted to {self.memory_path}")
            
        except (pickle.PickleError, OSError, IOError) as e:
            logger.error(f"Failed to persist memory to {self.memory_path}: {e}")
            # Clean up temporary file if it exists
            temp_path = self.memory_path.with_suffix('.tmp')
            if temp_path.exists():
                temp_path.unlink()
    
    def generate_session_id(self) -> str:
        """
        Generate a unique session ID.
        
        Returns:
            Unique session identifier string
        """
        session_id = str(uuid.uuid4())
        logger.info(f"Generated new session ID: {session_id}")
        return session_id
    
    def save_session(self, session_id: str, state, checkpoint_id: Optional[str] = None) -> bool:
        """
        Save session state with versioning, metadata, and checkpoint tracking.
        
        Args:
            session_id: Unique session identifier
            state: ProductState to save
            checkpoint_id: Optional checkpoint identifier for LangGraph integration
            
        Returns:
            True if save was successful, False otherwise
        """
        try:
            # Handle both dict and ProductState objects
            if isinstance(state, dict):
                # Convert dict to ProductState for proper handling
                try:
                    state = ProductState(**state)
                except Exception as conversion_error:
                    logger.error(f"Failed to convert dict to ProductState: {conversion_error}")
                    return False
            elif not isinstance(state, ProductState):
                logger.error(f"Invalid state type: {type(state)}, expected ProductState or dict")
                return False
            
            # Update state timestamp
            state.update_timestamp()
            
            # Set session_id in state if not already set
            if not state.session_id:
                state.session_id = session_id
            
            # Add checkpoint_id tracking if provided
            if checkpoint_id and checkpoint_id not in state.checkpoint_history:
                state.checkpoint_history.append(checkpoint_id)
            
            # Create session data with versioning and checkpoint tracking
            session_data = {
                'state': state.model_dump(),
                'timestamp': datetime.now(),
                'version': state.version if hasattr(state, 'version') else '2.0',
                'model_version': ProductState.__name__,
                'session_id': session_id,
                'checkpoint_id': checkpoint_id
            }
            
            self.memory[session_id] = session_data
            
            # Try to persist - if this fails, we still have in-memory state
            try:
                self._persist_memory()
            except Exception as persist_error:
                logger.error(f"Failed to persist session {session_id}: {persist_error}")
                # Remove from memory if persistence failed
                del self.memory[session_id]
                return False
            
            logger.info(f"Session {session_id} saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save session {session_id}: {e}")
            return False
    
    def load_session(self, session_id: str, checkpoint_id: Optional[str] = None) -> Optional[ProductState]:
        """
        Load session with backward compatibility handling and checkpoint support.
        
        Args:
            session_id: Session identifier to load
            checkpoint_id: Optional specific checkpoint to load (for future use)
            
        Returns:
            ProductState if found and valid, None otherwise
        """
        try:
            if session_id not in self.memory:
                logger.warning(f"Session {session_id} not found")
                return None
            
            session_data = self.memory[session_id]
            state_data = session_data['state']
            
            # Handle backward compatibility for checkpoint data
            state_data = self._handle_backward_compatibility(state_data, session_data, session_id)
            
            # Create ProductState with validation
            state = ProductState(**state_data)
            
            # Log checkpoint information if available
            loaded_checkpoint = session_data.get('checkpoint_id')
            if loaded_checkpoint:
                logger.info(f"Session {session_id} loaded successfully with checkpoint {loaded_checkpoint}")
            else:
                logger.info(f"Session {session_id} loaded successfully")
            return state
            
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None
    
    def _handle_backward_compatibility(self, state_data: Dict[str, Any], session_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """
        Handle backward compatibility for data model changes.
        
        Args:
            state_data: Raw state data from storage
            session_data: Complete session metadata
            session_id: Session identifier for fallback
            
        Returns:
            Updated state data compatible with current models
        """
        try:
            version = session_data.get('version', '1.0')
            
            # Add missing fields with defaults for existing sessions
            if 'session_id' not in state_data:
                state_data['session_id'] = session_data.get('session_id', session_id)
            
            if 'created_at' not in state_data:
                state_data['created_at'] = session_data.get('timestamp', datetime.now())
            
            if 'updated_at' not in state_data:
                state_data['updated_at'] = session_data.get('timestamp', datetime.now())
            
            if 'research_data' not in state_data:
                state_data['research_data'] = []
            
            if 'current_phase' not in state_data:
                state_data['current_phase'] = 'discovery'
            
            # Add new clarification support fields for backward compatibility (v2.0)
            if 'clarification_questions' not in state_data:
                state_data['clarification_questions'] = []
            
            if 'answered_questions' not in state_data:
                state_data['answered_questions'] = {}
            
            if 'gap_analysis' not in state_data:
                state_data['gap_analysis'] = []
            
            if 'checkpoint_history' not in state_data:
                state_data['checkpoint_history'] = []
            
            # Handle checkpoint_id from session metadata for backward compatibility
            if 'checkpoint_id' not in state_data and session_data.get('checkpoint_id'):
                checkpoint_id = session_data.get('checkpoint_id')
                if checkpoint_id and checkpoint_id not in state_data['checkpoint_history']:
                    state_data['checkpoint_history'].append(checkpoint_id)
            
            if 'version' not in state_data:
                # Determine version based on presence of new fields
                if any(field in state_data for field in ['clarification_questions', 'answered_questions', 'gap_analysis']):
                    state_data['version'] = '2.0'
                else:
                    state_data['version'] = '1.0'
            
            # Handle datetime serialization
            for field in ['created_at', 'updated_at']:
                if field in state_data and isinstance(state_data[field], str):
                    try:
                        state_data[field] = datetime.fromisoformat(state_data[field])
                    except ValueError:
                        state_data[field] = datetime.now()
            
            # Validate and clean up clarification data if present
            if 'clarification_questions' in state_data and state_data['clarification_questions']:
                # Ensure clarification questions are properly formatted
                valid_questions = []
                for question in state_data['clarification_questions']:
                    if isinstance(question, dict) and 'id' in question and 'text' in question:
                        valid_questions.append(question)
                state_data['clarification_questions'] = valid_questions
            
            # Validate answered_questions format
            if 'answered_questions' in state_data and state_data['answered_questions']:
                if not isinstance(state_data['answered_questions'], dict):
                    logger.warning(f"Invalid answered_questions format in session {session_id}, resetting to empty dict")
                    state_data['answered_questions'] = {}
            
            logger.debug(f"Applied backward compatibility for version {version} -> {state_data.get('version', '2.0')}")
            return state_data
            
        except Exception as e:
            logger.error(f"Failed to apply backward compatibility: {e}")
            return state_data
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session from memory.
        
        Args:
            session_id: Session identifier to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            if session_id in self.memory:
                del self.memory[session_id]
                self._persist_memory()
                logger.info(f"Session {session_id} deleted successfully")
                return True
            else:
                logger.warning(f"Session {session_id} not found for deletion")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    def list_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        List all sessions with metadata.
        
        Returns:
            Dictionary of session metadata keyed by session_id
        """
        try:
            session_list = {}
            for session_id, session_data in self.memory.items():
                session_list[session_id] = {
                    'timestamp': session_data.get('timestamp'),
                    'version': session_data.get('version'),
                    'current_phase': session_data.get('state', {}).get('current_phase', 'unknown'),
                    'user_query': session_data.get('state', {}).get('user_query', 'No query')[:100] + '...' if len(session_data.get('state', {}).get('user_query', '')) > 100 else session_data.get('state', {}).get('user_query', 'No query'),
                    'checkpoint_id': session_data.get('checkpoint_id'),
                    'checkpoint_count': len(session_data.get('state', {}).get('checkpoint_history', []))
                }
            
            logger.debug(f"Listed {len(session_list)} sessions")
            return session_list
            
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            return {}
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up sessions older than specified days.
        
        Args:
            days_old: Number of days after which sessions are considered old
            
        Returns:
            Number of sessions cleaned up
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            sessions_to_delete = []
            
            for session_id, session_data in self.memory.items():
                session_timestamp = session_data.get('timestamp', datetime.now())
                if session_timestamp < cutoff_date:
                    sessions_to_delete.append(session_id)
            
            for session_id in sessions_to_delete:
                del self.memory[session_id]
            
            if sessions_to_delete:
                self._persist_memory()
                logger.info(f"Cleaned up {len(sessions_to_delete)} old sessions")
            
            return len(sessions_to_delete)
            
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
            return 0
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory usage statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        try:
            stats = {
                'total_sessions': len(self.memory),
                'memory_file_size': self.memory_path.stat().st_size if self.memory_path.exists() else 0,
                'memory_file_path': str(self.memory_path),
                'oldest_session': None,
                'newest_session': None
            }
            
            if self.memory:
                timestamps = [session_data.get('timestamp', datetime.now()) 
                            for session_data in self.memory.values()]
                stats['oldest_session'] = min(timestamps)
                stats['newest_session'] = max(timestamps)
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {'error': str(e)}