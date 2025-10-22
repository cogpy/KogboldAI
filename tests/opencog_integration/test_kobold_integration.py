"""
Tests for the KoboldAI Integration module
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from opencog_integration.kobold_integration import (
    OpenCogKoboldIntegrator, KoboldIntegrationConfig,
    initialize_integration, get_integration, shutdown_integration
)


class TestKoboldIntegrationConfig:
    """Test the KoboldIntegrationConfig dataclass"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = KoboldIntegrationConfig()
        
        assert config.enabled is True
        assert config.auto_start_orchestration is True
        assert config.default_agent_count == 3
        assert config.world_auto_generation is True
        assert config.narrative_coherence_threshold == 0.6
        assert config.max_simultaneous_goals == 5
        assert config.integration_mode == "collaborative"
    
    def test_custom_config(self):
        """Test custom configuration values"""
        config = KoboldIntegrationConfig(
            enabled=False,
            auto_start_orchestration=False,
            default_agent_count=5,
            integration_mode="autonomous"
        )
        
        assert config.enabled is False
        assert config.auto_start_orchestration is False
        assert config.default_agent_count == 5
        assert config.integration_mode == "autonomous"


class TestOpenCogKoboldIntegrator:
    """Test the OpenCogKoboldIntegrator class"""
    
    @pytest.fixture
    def integrator(self):
        """Create an integrator instance for testing"""
        config = KoboldIntegrationConfig(auto_start_orchestration=False)
        return OpenCogKoboldIntegrator(config)
    
    @pytest.fixture
    def mock_kobold_vars(self):
        """Create mock KoboldAI variables"""
        mock_vars = Mock()
        mock_vars.actions = []
        mock_vars.memory = "Test memory content"
        mock_vars.authornote = "Test author note"
        mock_vars.worldinfo = {}
        return mock_vars
    
    def test_integrator_creation(self, integrator):
        """Test creating an integrator instance"""
        assert integrator.config is not None
        assert integrator.orchestrator is not None
        assert integrator.adventure_telos is not None
        assert integrator.narrative_engine is not None
        assert integrator.world_builder is not None
        assert not integrator.is_active
    
    def test_initialization_success(self, integrator, mock_kobold_vars):
        """Test successful initialization"""
        success = integrator.initialize(mock_kobold_vars)
        
        assert success is True
        assert integrator.kobold_vars == mock_kobold_vars
        
        # Check that default agents were created
        agent_count = len(integrator.orchestrator.agents)
        assert agent_count == integrator.config.default_agent_count
    
    def test_initialization_with_disabled_config(self, mock_kobold_vars):
        """Test initialization with disabled configuration"""
        config = KoboldIntegrationConfig(enabled=False)
        integrator = OpenCogKoboldIntegrator(config)
        
        success = integrator.initialize(mock_kobold_vars)
        
        # Should still succeed but not create agents
        assert success is True
        assert len(integrator.orchestrator.agents) == 0
    
    def test_autonomous_processing_lifecycle(self, integrator, mock_kobold_vars):
        """Test starting and stopping autonomous processing"""
        integrator.initialize(mock_kobold_vars)
        
        # Start processing
        success = integrator.start_autonomous_processing()
        
        assert success is True
        assert integrator.is_active is True
        assert integrator.orchestrator.is_running is True
        
        # Brief pause to let threads start
        time.sleep(0.1)
        
        # Stop processing
        integrator.stop_autonomous_processing()
        
        assert integrator.is_active is False
    
    def test_user_input_processing(self, integrator, mock_kobold_vars):
        """Test processing user input"""
        integrator.initialize(mock_kobold_vars)
        
        user_input = "The brave knight entered the dark castle."
        result = integrator.process_user_input(user_input)
        
        assert result['success'] is True
        assert 'element_id' in result
        assert 'agent_responses' in result
        assert 'adventure_suggestions' in result
        assert 'narrative_coherence' in result
        assert 'processing_metadata' in result
    
    def test_session_management(self, integrator, mock_kobold_vars):
        """Test session creation and management"""
        integrator.initialize(mock_kobold_vars)
        
        # Create a session
        session_config = {'theme': 'fantasy', 'difficulty': 'medium'}
        success = integrator.create_session('test_session', session_config)
        
        assert success is True
        assert 'test_session' in integrator.active_sessions
        
        # Test duplicate session creation
        duplicate_success = integrator.create_session('test_session')
        assert duplicate_success is False
        
        # End the session
        end_success = integrator.end_session('test_session')
        assert end_success is True
        assert 'test_session' not in integrator.active_sessions
    
    def test_session_data_export(self, integrator, mock_kobold_vars):
        """Test exporting session data"""
        integrator.initialize(mock_kobold_vars)
        integrator.create_session('export_test')
        
        export_data = integrator.export_session_data('export_test')
        
        assert export_data is not None
        assert 'session_info' in export_data
        assert 'narrative_state' in export_data
        assert 'world_state' in export_data
        assert 'orchestrator_state' in export_data
        assert 'telos_state' in export_data
        assert 'export_timestamp' in export_data
        
        # Test exporting non-existent session
        no_export = integrator.export_session_data('non_existent')
        assert no_export is None
    
    def test_callback_system(self, integrator, mock_kobold_vars):
        """Test the event callback system"""
        integrator.initialize(mock_kobold_vars)
        
        # Register a callback
        callback_called = []
        
        def test_callback(data):
            callback_called.append(data)
        
        integrator.register_event_callback('narrative_updated', test_callback)
        
        # Fire the callback
        test_data = {'test': 'data'}
        integrator._fire_callbacks('narrative_updated', test_data)
        
        assert len(callback_called) == 1
        assert callback_called[0] == test_data
    
    def test_integration_status(self, integrator, mock_kobold_vars):
        """Test getting integration status"""
        integrator.initialize(mock_kobold_vars)
        
        status = integrator.get_integration_status()
        
        assert 'integration_active' in status
        assert 'config' in status
        assert 'components' in status
        assert 'sessions' in status
        assert 'performance' in status
        
        # Check component status
        assert 'orchestrator' in status['components']
        assert 'adventure_telos' in status['components']
        assert 'narrative_engine' in status['components']
        assert 'world_builder' in status['components']
    
    def test_hook_registration(self, integrator):
        """Test registering hooks and processors"""
        def test_generation_hook(data):
            return data
        
        def test_story_processor(story):
            return story
        
        integrator.register_generation_hook(test_generation_hook)
        integrator.register_story_processor(test_story_processor)
        
        assert test_generation_hook in integrator.generation_hooks
        assert test_story_processor in integrator.story_processors
    
    def test_error_handling_in_initialization(self):
        """Test error handling during initialization"""
        config = KoboldIntegrationConfig()
        integrator = OpenCogKoboldIntegrator(config)
        
        # Test initialization with None kobold_vars
        success = integrator.initialize(None)
        
        # Should handle gracefully
        assert success is True  # Still succeeds with None vars
    
    def test_narrative_element_type_determination(self, integrator):
        """Test determining narrative element types from content"""
        # Test dialogue detection
        dialogue_content = 'The hero said "Hello there!"'
        element_type = integrator._determine_element_type(dialogue_content)
        
        from opencog_integration.narrative_engine import NarrativeElement
        assert element_type == NarrativeElement.DIALOGUE
        
        # Test action detection
        action_content = 'The knight walked across the bridge.'
        element_type = integrator._determine_element_type(action_content)
        assert element_type == NarrativeElement.ACTION
        
        # Test description detection
        description_content = 'The castle appeared magnificent in the moonlight.'
        element_type = integrator._determine_element_type(description_content)
        assert element_type == NarrativeElement.DESCRIPTION
    
    def test_agent_context_building(self, integrator, mock_kobold_vars):
        """Test building agent context"""
        integrator.initialize(mock_kobold_vars)
        
        # Get an agent to test with
        agent = list(integrator.orchestrator.agents.values())[0]
        context = integrator._build_agent_context(agent)
        
        assert 'agent_id' in context
        assert 'agent_role' in context
        assert 'specialization' in context
        assert 'themes' in context
        assert 'world_state' in context
        assert 'memory' in context
        assert 'author_note' in context
        assert 'world_info' in context


class TestGlobalIntegrationFunctions:
    """Test global integration management functions"""
    
    def setUp(self):
        """Ensure clean state before each test"""
        # Clear any existing global integration
        shutdown_integration()
    
    def tearDown(self):
        """Clean up after each test"""
        shutdown_integration()
    
    def test_initialize_global_integration(self):
        """Test initializing global integration"""
        self.setUp()
        
        mock_vars = Mock()
        mock_vars.actions = []
        
        config = KoboldIntegrationConfig(auto_start_orchestration=False)
        success = initialize_integration(mock_vars, config)
        
        assert success is True
        
        integration = get_integration()
        assert integration is not None
        assert integration.kobold_vars == mock_vars
        
        self.tearDown()
    
    def test_get_integration_when_none(self):
        """Test getting integration when none exists"""
        self.setUp()
        
        integration = get_integration()
        assert integration is None
    
    def test_duplicate_initialization(self):
        """Test attempting to initialize integration twice"""
        self.setUp()
        
        mock_vars = Mock()
        mock_vars.actions = []
        
        # First initialization
        success1 = initialize_integration(mock_vars)
        assert success1 is True
        
        # Second initialization should return True but not recreate
        success2 = initialize_integration(mock_vars)
        assert success2 is True
        
        # Should be the same instance
        integration1 = get_integration()
        integration2 = get_integration()
        assert integration1 is integration2
        
        self.tearDown()
    
    def test_shutdown_integration(self):
        """Test shutting down integration"""
        self.setUp()
        
        mock_vars = Mock()
        mock_vars.actions = []
        
        # Initialize first
        initialize_integration(mock_vars)
        assert get_integration() is not None
        
        # Then shutdown
        shutdown_integration()
        assert get_integration() is None
    
    def test_shutdown_when_none_exists(self):
        """Test shutting down when no integration exists"""
        self.setUp()
        
        # Should not raise any errors
        shutdown_integration()
        assert get_integration() is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])