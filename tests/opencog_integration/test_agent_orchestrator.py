"""
Tests for the Agent Orchestrator module
"""

import pytest
import time
from unittest.mock import Mock, patch

from opencog_integration.agent_orchestrator import (
    AgentOrchestrator, AgentProfile, CognitiveAgent, AgentState
)


class TestAgentProfile:
    """Test the AgentProfile dataclass"""
    
    def test_agent_profile_creation(self):
        """Test creating an agent profile"""
        profile = AgentProfile(
            agent_id="test_agent",
            name="Test Agent",
            role="tester",
            specialization="testing",
            personality_traits={'creativity': 0.7},
            capabilities=['test_execution']
        )
        
        assert profile.agent_id == "test_agent"
        assert profile.name == "Test Agent"
        assert profile.role == "tester"
        assert profile.creativity_level == 0.7  # default value
        assert 'test_execution' in profile.capabilities


class TestCognitiveAgent:
    """Test the CognitiveAgent class"""
    
    @pytest.fixture
    def sample_profile(self):
        """Create a sample agent profile for testing"""
        return AgentProfile(
            agent_id="test_agent",
            name="Test Agent",
            role="tester",
            specialization="testing",
            personality_traits={'creativity': 0.8},
            capabilities=['test_execution', 'analysis']
        )
    
    def test_agent_creation(self, sample_profile):
        """Test creating a cognitive agent"""
        agent = CognitiveAgent(sample_profile)
        
        assert agent.profile == sample_profile
        assert agent.state == AgentState.IDLE
        assert agent.cognitive_load == 0.0
        assert len(agent.memory) == 0
        assert len(agent.current_goals) == 0
    
    def test_agent_state_update(self, sample_profile):
        """Test updating agent state"""
        agent = CognitiveAgent(sample_profile)
        
        agent.update_state(AgentState.ACTIVE, {'reason': 'test'})
        
        assert agent.state == AgentState.ACTIVE
        assert len(agent.memory) == 1
        
        # Check memory contains state change information
        memory_keys = list(agent.memory.keys())
        assert 'state_change_' in memory_keys[0]
    
    def test_agent_goal_management(self, sample_profile):
        """Test agent goal addition and management"""
        agent = CognitiveAgent(sample_profile)
        
        agent.add_goal("Complete test task", priority=0.8)
        
        assert len(agent.current_goals) == 1
        assert agent.current_goals[0]['goal'] == "Complete test task"
        assert agent.current_goals[0]['priority'] == 0.8
        assert agent.current_goals[0]['status'] == 'active'
    
    def test_agent_input_processing(self, sample_profile):
        """Test agent input processing"""
        agent = CognitiveAgent(sample_profile)
        
        input_data = {'type': 'test_input', 'content': 'Hello Agent'}
        response = agent.process_input(input_data)
        
        assert response['agent_id'] == "test_agent"
        assert response['input_received'] == input_data
        assert 'cognitive_state' in response
        assert agent.cognitive_load > 0.0
        assert len(agent.interaction_history) == 1


class TestAgentOrchestrator:
    """Test the AgentOrchestrator class"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create an orchestrator instance for testing"""
        return AgentOrchestrator()
    
    @pytest.fixture
    def sample_profile(self):
        """Create a sample agent profile for testing"""
        return AgentProfile(
            agent_id="orchestrator_test_agent",
            name="Orchestrator Test Agent",
            role="tester",
            specialization="orchestration_testing",
            personality_traits={'cooperation': 0.9},
            capabilities=['collaboration', 'testing']
        )
    
    def test_orchestrator_creation(self, orchestrator):
        """Test creating an orchestrator"""
        assert len(orchestrator.agents) == 0
        assert not orchestrator.is_running
        assert orchestrator.orchestration_thread is None
    
    def test_agent_registration(self, orchestrator, sample_profile):
        """Test registering an agent with the orchestrator"""
        success = orchestrator.register_agent(sample_profile)
        
        assert success is True
        assert sample_profile.agent_id in orchestrator.agents
        assert len(orchestrator.agents) == 1
        
        # Test duplicate registration
        duplicate_success = orchestrator.register_agent(sample_profile)
        assert duplicate_success is False
    
    def test_agent_unregistration(self, orchestrator, sample_profile):
        """Test unregistering an agent"""
        # First register an agent
        orchestrator.register_agent(sample_profile)
        assert len(orchestrator.agents) == 1
        
        # Then unregister it
        success = orchestrator.unregister_agent(sample_profile.agent_id)
        
        assert success is True
        assert sample_profile.agent_id not in orchestrator.agents
        assert len(orchestrator.agents) == 0
        
        # Test unregistering non-existent agent
        fail_success = orchestrator.unregister_agent("non_existent")
        assert fail_success is False
    
    def test_orchestration_lifecycle(self, orchestrator):
        """Test starting and stopping orchestration"""
        # Start orchestration
        orchestrator.start_orchestration()
        
        assert orchestrator.is_running is True
        assert orchestrator.orchestration_thread is not None
        
        # Brief pause to let thread start
        time.sleep(0.1)
        assert orchestrator.orchestration_thread.is_alive()
        
        # Stop orchestration
        orchestrator.stop_orchestration()
        
        assert orchestrator.is_running is False
    
    def test_narrative_input_processing(self, orchestrator, sample_profile):
        """Test processing narrative input through orchestrator"""
        # Register an agent
        orchestrator.register_agent(sample_profile)
        
        input_data = {
            'type': 'story_update',
            'content': 'The hero walked into the tavern.',
            'timestamp': time.time()
        }
        
        result = orchestrator.submit_narrative_input(input_data)
        
        assert result['success'] is True
        assert 'agent_responses' in result
        assert sample_profile.agent_id in result['agent_responses']
        assert 'coordination_metadata' in result
    
    def test_system_state_reporting(self, orchestrator, sample_profile):
        """Test getting system state information"""
        # Initially empty
        state = orchestrator.get_system_state()
        
        assert state['agent_count'] == 0
        assert state['is_running'] is False
        assert state['event_queue_size'] == 0
        
        # After adding an agent
        orchestrator.register_agent(sample_profile)
        state = orchestrator.get_system_state()
        
        assert state['agent_count'] == 1
        assert sample_profile.agent_id in state['agent_states']
    
    def test_collaboration_matrix(self, orchestrator):
        """Test agent collaboration matrix functionality"""
        # Create two test agents
        profile1 = AgentProfile(
            agent_id="collab_agent_1",
            name="Collaboration Agent 1",
            role="collaborator",
            specialization="teamwork",
            personality_traits={'cooperation': 0.8},
            capabilities=['collaboration']
        )
        
        profile2 = AgentProfile(
            agent_id="collab_agent_2",
            name="Collaboration Agent 2",
            role="collaborator",
            specialization="teamwork",
            personality_traits={'cooperation': 0.7},
            capabilities=['collaboration']
        )
        
        # Register both agents
        orchestrator.register_agent(profile1)
        orchestrator.register_agent(profile2)
        
        # Check collaboration matrix was initialized
        assert profile1.agent_id in orchestrator.collaboration_matrix
        assert profile2.agent_id in orchestrator.collaboration_matrix
        assert profile2.agent_id in orchestrator.collaboration_matrix[profile1.agent_id]
        assert profile1.agent_id in orchestrator.collaboration_matrix[profile2.agent_id]
        
        # Check initial collaboration values
        initial_value = orchestrator.collaboration_matrix[profile1.agent_id][profile2.agent_id]
        assert 0.0 <= initial_value <= 1.0
    
    def test_error_handling(self, orchestrator):
        """Test error handling in orchestrator methods"""
        # Test processing input with no agents
        input_data = {'type': 'test', 'content': 'test content'}
        result = orchestrator.submit_narrative_input(input_data)
        
        assert result['success'] is True  # Should succeed even with no agents
        assert result['agent_responses'] == {}
    
    def test_event_queue_processing(self, orchestrator):
        """Test event queue functionality"""
        # Add an event to the queue
        test_event = {
            'type': 'narrative_update',
            'data': {'content': 'Test narrative update'},
            'timestamp': time.time()
        }
        
        orchestrator.event_queue.append(test_event)
        
        # Process the queue
        orchestrator._process_event_queue()
        
        # Queue should be empty after processing
        assert len(orchestrator.event_queue) == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])