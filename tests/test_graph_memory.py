"""Unit tests for GraphMemory class."""

import pytest
import tempfile
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from memory.graph_memory import GraphMemory
from models.data_models import ProductState, BusinessModel, FeatureSpec, GTMStrategy
from models.enums import MVPPriority, MarketValidationLevel


class TestGraphMemory:
    """Test suite for GraphMemory class."""
    
    @pytest.fixture
    def temp_memory_path(self):
        """Create temporary file path for testing."""
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def sample_product_state(self):
        """Create sample ProductState for testing."""
        business_model = BusinessModel(
            value_proposition="Revolutionary AI assistant for developers",
            target_customer="Software developers and teams",
            revenue_streams=["subscription", "enterprise"],
            key_metrics=["MRR", "user_retention"]
        )
        
        feature_spec = FeatureSpec(
            name="User Authentication",
            user_story="As a user, I want to log in securely, so that my data is protected",
            acceptance_criteria=[
                "WHEN user enters valid credentials THEN system SHALL authenticate successfully",
                "WHEN user enters invalid credentials THEN system SHALL reject access",
                "WHEN user is authenticated THEN system SHALL provide access token"
            ],
            mvp_priority=MVPPriority.CORE,
            effort_estimate="M",
            business_impact="High"
        )
        
        gtm_strategy = GTMStrategy(
            distribution_channels=["direct_sales", "partner_network", "online_marketing"],
            pricing_strategy="Freemium with premium tiers",
            launch_timeline={
                "mvp_launch": "Q1 2024",
                "growth": "Q2-Q3 2024", 
                "expansion": "Q4 2024"
            },
            success_metrics=["user_acquisition", "revenue_growth"],
            competitive_positioning="AI-first development assistant"
        )
        
        return ProductState(
            user_query="Build an AI assistant for developers",
            business_model=business_model,
            feature_specifications=[feature_spec],
            gtm_strategy=gtm_strategy,
            current_phase="planning"
        )
    
    def test_init_new_memory(self, temp_memory_path):
        """Test initialization with new memory file."""
        memory = GraphMemory(temp_memory_path)
        assert memory.memory == {}
        assert memory.memory_path == Path(temp_memory_path)
    
    def test_init_existing_memory(self, temp_memory_path):
        """Test initialization with existing memory file."""
        # Create existing memory file
        test_data = {"test_session": {"state": {}, "timestamp": datetime.now()}}
        with open(temp_memory_path, 'wb') as f:
            pickle.dump(test_data, f)
        
        memory = GraphMemory(temp_memory_path)
        assert "test_session" in memory.memory
    
    def test_init_corrupted_memory(self, temp_memory_path):
        """Test initialization with corrupted memory file."""
        # Create corrupted file
        with open(temp_memory_path, 'w') as f:
            f.write("corrupted data")
        
        memory = GraphMemory(temp_memory_path)
        assert memory.memory == {}
        # Check backup was created
        backup_path = Path(temp_memory_path).with_suffix('.pkl.backup')
        assert backup_path.exists()
        backup_path.unlink()  # Cleanup
    
    def test_generate_session_id(self, temp_memory_path):
        """Test session ID generation."""
        memory = GraphMemory(temp_memory_path)
        session_id1 = memory.generate_session_id()
        session_id2 = memory.generate_session_id()
        
        assert session_id1 != session_id2
        assert len(session_id1) == 36  # UUID4 length
        assert '-' in session_id1
    
    def test_save_session_success(self, temp_memory_path, sample_product_state):
        """Test successful session save."""
        memory = GraphMemory(temp_memory_path)
        session_id = memory.generate_session_id()
        
        result = memory.save_session(session_id, sample_product_state)
        
        assert result is True
        assert session_id in memory.memory
        assert memory.memory[session_id]['version'] == '1.0'
        assert memory.memory[session_id]['session_id'] == session_id
        assert 'timestamp' in memory.memory[session_id]
    
    def test_save_session_updates_timestamp(self, temp_memory_path, sample_product_state):
        """Test that save_session updates the state timestamp."""
        memory = GraphMemory(temp_memory_path)
        session_id = memory.generate_session_id()
        
        original_timestamp = sample_product_state.updated_at
        memory.save_session(session_id, sample_product_state)
        
        # Timestamp should be updated
        assert sample_product_state.updated_at > original_timestamp
    
    def test_load_session_success(self, temp_memory_path, sample_product_state):
        """Test successful session load."""
        memory = GraphMemory(temp_memory_path)
        session_id = memory.generate_session_id()
        
        # Save first
        memory.save_session(session_id, sample_product_state)
        
        # Load
        loaded_state = memory.load_session(session_id)
        
        assert loaded_state is not None
        assert loaded_state.user_query == sample_product_state.user_query
        assert loaded_state.current_phase == sample_product_state.current_phase
        assert loaded_state.business_model.value_proposition == sample_product_state.business_model.value_proposition
    
    def test_load_session_not_found(self, temp_memory_path):
        """Test loading non-existent session."""
        memory = GraphMemory(temp_memory_path)
        
        loaded_state = memory.load_session("non_existent_session")
        
        assert loaded_state is None
    
    def test_backward_compatibility(self, temp_memory_path):
        """Test backward compatibility handling."""
        memory = GraphMemory(temp_memory_path)
        
        # Create old format session data (missing some fields)
        old_session_data = {
            'state': {
                'user_query': 'Test query',
                'current_phase': 'discovery'
                # Missing session_id, created_at, updated_at, research_data
            },
            'timestamp': datetime.now(),
            'version': '0.9'
        }
        
        memory.memory['test_session'] = old_session_data
        
        # Load should handle missing fields
        loaded_state = memory.load_session('test_session')
        
        assert loaded_state is not None
        assert loaded_state.user_query == 'Test query'
        assert loaded_state.session_id == 'test_session'
        assert loaded_state.research_data == []
        assert isinstance(loaded_state.created_at, datetime)
        assert isinstance(loaded_state.updated_at, datetime)
    
    def test_delete_session_success(self, temp_memory_path, sample_product_state):
        """Test successful session deletion."""
        memory = GraphMemory(temp_memory_path)
        session_id = memory.generate_session_id()
        
        # Save first
        memory.save_session(session_id, sample_product_state)
        assert session_id in memory.memory
        
        # Delete
        result = memory.delete_session(session_id)
        
        assert result is True
        assert session_id not in memory.memory
    
    def test_delete_session_not_found(self, temp_memory_path):
        """Test deleting non-existent session."""
        memory = GraphMemory(temp_memory_path)
        
        result = memory.delete_session("non_existent_session")
        
        assert result is False
    
    def test_list_sessions(self, temp_memory_path, sample_product_state):
        """Test listing sessions."""
        memory = GraphMemory(temp_memory_path)
        session_id1 = memory.generate_session_id()
        session_id2 = memory.generate_session_id()
        
        # Save multiple sessions
        memory.save_session(session_id1, sample_product_state)
        
        sample_product_state.user_query = "Different query"
        sample_product_state.current_phase = "validation"
        memory.save_session(session_id2, sample_product_state)
        
        # List sessions
        sessions = memory.list_sessions()
        
        assert len(sessions) == 2
        assert session_id1 in sessions
        assert session_id2 in sessions
        assert 'timestamp' in sessions[session_id1]
        assert 'current_phase' in sessions[session_id1]
        assert 'user_query' in sessions[session_id1]
    
    def test_cleanup_old_sessions(self, temp_memory_path, sample_product_state):
        """Test cleanup of old sessions."""
        memory = GraphMemory(temp_memory_path)
        
        # Create old session
        old_timestamp = datetime.now() - timedelta(days=35)
        old_session_data = {
            'state': sample_product_state.model_dump(),
            'timestamp': old_timestamp,
            'version': '1.0'
        }
        memory.memory['old_session'] = old_session_data
        
        # Create recent session
        session_id = memory.generate_session_id()
        memory.save_session(session_id, sample_product_state)
        
        # Cleanup sessions older than 30 days
        cleaned_count = memory.cleanup_old_sessions(days_old=30)
        
        assert cleaned_count == 1
        assert 'old_session' not in memory.memory
        assert session_id in memory.memory
    
    def test_get_memory_stats(self, temp_memory_path, sample_product_state):
        """Test memory statistics."""
        memory = GraphMemory(temp_memory_path)
        session_id = memory.generate_session_id()
        memory.save_session(session_id, sample_product_state)
        
        stats = memory.get_memory_stats()
        
        assert 'total_sessions' in stats
        assert stats['total_sessions'] == 1
        assert 'memory_file_size' in stats
        assert stats['memory_file_size'] > 0
        assert 'oldest_session' in stats
        assert 'newest_session' in stats
    
    def test_persistence_error_handling(self, temp_memory_path, sample_product_state):
        """Test error handling during persistence."""
        memory = GraphMemory(temp_memory_path)
        session_id = memory.generate_session_id()
        
        # Mock the _persist_memory method to raise error
        with patch.object(memory, '_persist_memory', side_effect=OSError("Permission denied")):
            result = memory.save_session(session_id, sample_product_state)
            assert result is False
    
    def test_load_error_handling(self, temp_memory_path):
        """Test error handling during load."""
        memory = GraphMemory(temp_memory_path)
        
        # Create invalid session data
        memory.memory['invalid_session'] = {
            'state': {'invalid': 'data'},  # Missing required fields
            'timestamp': datetime.now(),
            'version': '1.0'
        }
        
        loaded_state = memory.load_session('invalid_session')
        assert loaded_state is None


if __name__ == "__main__":
    pytest.main([__file__])