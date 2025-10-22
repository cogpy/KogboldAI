"""
KoboldAI Integration Module

This module integrates the OpenCog autonomous agent orchestrator with the
existing KoboldAI infrastructure, providing seamless connectivity between
the cognitive architecture and the AI story generation system.
"""

import logging
import threading
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import json

from .agent_orchestrator import AgentOrchestrator, AgentProfile, AgentState
from .adventure_telos import AdventureTelos, GoalType, GoalPriority
from .narrative_engine import NarrativeEngine, NarrativeElement
from .world_builder import WorldBuilder, LocationType, MythosType

logger = logging.getLogger(__name__)


@dataclass
class KoboldIntegrationConfig:
    """Configuration for KoboldAI OpenCog integration"""
    enabled: bool = True
    auto_start_orchestration: bool = True
    default_agent_count: int = 3
    world_auto_generation: bool = True
    narrative_coherence_threshold: float = 0.6
    max_simultaneous_goals: int = 5
    integration_mode: str = "collaborative"  # collaborative, autonomous, advisory


class OpenCogKoboldIntegrator:
    """
    Main integration class that connects OpenCog cognitive architecture
    with KoboldAI's story generation and management systems.
    """
    
    def __init__(self, config: KoboldIntegrationConfig = None):
        self.config = config or KoboldIntegrationConfig()
        
        # Core components
        self.orchestrator = AgentOrchestrator()
        self.adventure_telos = AdventureTelos()
        self.narrative_engine = NarrativeEngine()
        self.world_builder = WorldBuilder()
        
        # Integration state
        self.is_active = False
        self.integration_thread = None
        self._lock = threading.Lock()
        
        # KoboldAI connection points
        self.kobold_vars = None  # Will be set by aiserver
        self.generation_hooks = []
        self.story_processors = []
        
        # Session management
        self.active_sessions = {}
        self.session_contexts = {}
        
        # Callback system
        self.event_callbacks = {
            'generation_started': [],
            'generation_completed': [],
            'narrative_updated': [],
            'world_changed': [],
            'agent_action': []
        }
        
    def initialize(self, kobold_vars) -> bool:
        """Initialize the integration with KoboldAI variables"""
        try:
            self.kobold_vars = kobold_vars
            
            if self.config.enabled:
                # Set up default agents
                if self.config.default_agent_count > 0:
                    self._create_default_agents()
                
                # Initialize world if auto-generation is enabled
                if self.config.world_auto_generation:
                    self._initialize_default_world()
                
                # Start orchestration if configured
                if self.config.auto_start_orchestration:
                    self.start_autonomous_processing()
                
                logger.info("OpenCog-KoboldAI integration initialized successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to initialize OpenCog integration: {e}")
            return False
    
    def _create_default_agents(self):
        """Create default cognitive agents for story generation"""
        default_profiles = [
            AgentProfile(
                agent_id="storyteller",
                name="Master Storyteller",
                role="narrative_coordinator",
                specialization="story_structure",
                personality_traits={
                    'creativity': 0.8,
                    'coherence': 0.9,
                    'adaptability': 0.7
                },
                capabilities=['narrative_generation', 'plot_coordination', 'character_development'],
                interaction_preferences={'collaboration_style': 'leading'}
            ),
            AgentProfile(
                agent_id="world_keeper",
                name="World Keeper",
                role="world_manager",
                specialization="world_consistency",
                personality_traits={
                    'detail_oriented': 0.9,
                    'consistency': 0.95,
                    'creativity': 0.6
                },
                capabilities=['world_tracking', 'consistency_checking', 'lore_management'],
                interaction_preferences={'collaboration_style': 'supporting'}
            ),
            AgentProfile(
                agent_id="character_advocate",
                name="Character Advocate",
                role="character_manager",
                specialization="character_development",
                personality_traits={
                    'empathy': 0.9,
                    'psychology_understanding': 0.8,
                    'creativity': 0.7
                },
                capabilities=['character_consistency', 'dialogue_generation', 'motivation_tracking'],
                interaction_preferences={'collaboration_style': 'collaborative'}
            )
        ]
        
        for profile in default_profiles:
            success = self.orchestrator.register_agent(profile)
            if success:
                logger.info(f"Registered default agent: {profile.name}")
    
    def _initialize_default_world(self):
        """Initialize a default world for story generation"""
        default_config = {
            'name': 'KoboldAI Generated World',
            'scale': 'medium',
            'magic_level': 0.6,
            'technology_level': 'medieval',
            'themes': ['adventure', 'fantasy', 'mystery']
        }
        
        success = self.world_builder.initialize_world(default_config)
        if success:
            logger.info("Initialized default world for OpenCog integration")
    
    def start_autonomous_processing(self) -> bool:
        """Start autonomous processing integration"""
        if self.is_active:
            logger.warning("Autonomous processing already active")
            return False
        
        try:
            self.is_active = True
            self.orchestrator.start_orchestration()
            
            # Start integration processing thread
            self.integration_thread = threading.Thread(target=self._integration_loop)
            self.integration_thread.daemon = True
            self.integration_thread.start()
            
            logger.info("Started autonomous OpenCog processing")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start autonomous processing: {e}")
            self.is_active = False
            return False
    
    def stop_autonomous_processing(self):
        """Stop autonomous processing integration"""
        self.is_active = False
        
        if self.orchestrator:
            self.orchestrator.stop_orchestration()
        
        if self.integration_thread:
            self.integration_thread.join(timeout=5.0)
        
        logger.info("Stopped autonomous OpenCog processing")
    
    def _integration_loop(self):
        """Main integration loop that processes cognitive architecture feedback"""
        while self.is_active:
            try:
                # Process pending narrative updates
                self._process_narrative_updates()
                
                # Check for goal completions and new opportunities
                self._process_goal_updates()
                
                # Update world state based on story progression
                self._update_world_state()
                
                # Generate autonomous suggestions if configured
                if self.config.integration_mode in ['autonomous', 'advisory']:
                    self._generate_autonomous_suggestions()
                
                time.sleep(1.0)  # Process every second
                
            except Exception as e:
                logger.error(f"Error in integration loop: {e}")
                time.sleep(5.0)  # Longer pause on error
    
    def _process_narrative_updates(self):
        """Process updates from the narrative engine"""
        # Check if there are new story elements to process
        if self.kobold_vars and hasattr(self.kobold_vars, 'actions'):
            recent_actions = self.kobold_vars.actions[-5:]  # Last 5 actions
            
            for action in recent_actions:
                if not hasattr(action, '_opencog_processed'):
                    self._process_story_action(action)
                    action._opencog_processed = True
    
    def _process_story_action(self, action):
        """Process a single story action through the cognitive architecture"""
        try:
            # Extract narrative content
            content = getattr(action, 'text', str(action))
            
            # Add to narrative engine
            element_id = self.narrative_engine.add_narrative_element(
                element_type=self._determine_element_type(content),
                content=content,
                metadata={'source': 'kobold_action', 'timestamp': time.time()}
            )
            
            # Notify agents of new narrative content
            narrative_input = {
                'type': 'story_update',
                'content': content,
                'element_id': element_id,
                'timestamp': time.time()
            }
            
            response = self.orchestrator.submit_narrative_input(narrative_input)
            
            # Fire callbacks
            self._fire_callbacks('narrative_updated', {
                'action': action,
                'element_id': element_id,
                'agent_response': response
            })
            
        except Exception as e:
            logger.error(f"Error processing story action: {e}")
    
    def _determine_element_type(self, content: str) -> NarrativeElement:
        """Determine the narrative element type from content"""
        content_lower = content.lower()
        
        # Simple heuristic classification
        if any(word in content_lower for word in ['"', 'said', 'asked', 'replied']):
            return NarrativeElement.DIALOGUE
        elif any(word in content_lower for word in ['walked', 'ran', 'jumped', 'attacked', 'moved']):
            return NarrativeElement.ACTION
        elif any(word in content_lower for word in ['looked', 'saw', 'noticed', 'appeared']):
            return NarrativeElement.DESCRIPTION
        else:
            return NarrativeElement.DESCRIPTION  # Default fallback
    
    def _process_goal_updates(self):
        """Process updates from the adventure telos system"""
        # Check current agent goals and suggest new ones
        for agent_id, agent in self.orchestrator.agents.items():
            if len(agent.current_goals) < self.config.max_simultaneous_goals:
                # Generate context for goal suggestions
                context = self._build_agent_context(agent)
                suggestions = self.adventure_telos.generate_adventure_suggestions(context)
                
                # Add promising suggestions as goals
                for suggestion in suggestions[:2]:  # Add up to 2 new goals
                    goal_id = self.adventure_telos.create_goal(
                        goal_type=suggestion['type'],
                        description=suggestion['description'],
                        priority=suggestion['priority']
                    )
                    
                    # Activate the goal
                    self.adventure_telos.activate_goal(goal_id)
                    
                    # Add to agent's goal list
                    agent.add_goal(suggestion['description'], suggestion['priority'].value)
    
    def _build_agent_context(self, agent) -> Dict[str, Any]:
        """Build context for an agent based on current story state"""
        context = {
            'agent_id': agent.profile.agent_id,
            'agent_role': agent.profile.role,
            'specialization': agent.profile.specialization,
            'themes': list(self.narrative_engine.active_themes),
            'world_state': self.world_builder.get_world_state()
        }
        
        # Add story-specific context if available
        if self.kobold_vars:
            if hasattr(self.kobold_vars, 'memory'):
                context['memory'] = self.kobold_vars.memory
            if hasattr(self.kobold_vars, 'authornote'):
                context['author_note'] = self.kobold_vars.authornote
            if hasattr(self.kobold_vars, 'worldinfo'):
                context['world_info'] = self.kobold_vars.worldinfo
        
        return context
    
    def _update_world_state(self):
        """Update world state based on story progression"""
        # Check for significant narrative developments
        coherence_analysis = self.narrative_engine.analyze_narrative_coherence()
        
        if coherence_analysis['overall_coherence'] > 0.8:
            # High coherence - world is stable, possibly generate new opportunities
            if random.random() < 0.1:  # 10% chance per update cycle
                world_event = self.world_builder.generate_world_event('local')
                self._fire_callbacks('world_changed', {'event': world_event})
        
        elif coherence_analysis['overall_coherence'] < 0.4:
            # Low coherence - might need world stabilization
            logger.info("Low narrative coherence detected - considering world stabilization")
    
    def _generate_autonomous_suggestions(self):
        """Generate autonomous suggestions for story continuation"""
        if not self.kobold_vars:
            return
        
        # Build current context
        context = {
            'current_story_length': len(getattr(self.kobold_vars, 'actions', [])),
            'narrative_coherence': self.narrative_engine.analyze_narrative_coherence(),
            'world_state': self.world_builder.get_world_state(),
            'active_goals': len(self.adventure_telos.active_pursuits)
        }
        
        # Get suggestions from adventure telos
        telos_suggestion = self.adventure_telos.suggest_next_action(context)
        
        # Get narrative opportunities from world builder
        world_opportunities = self.world_builder.suggest_narrative_opportunities(context)
        
        # Combine and prioritize suggestions
        combined_suggestions = {
            'telos_action': telos_suggestion,
            'world_opportunities': world_opportunities,
            'timestamp': time.time()
        }
        
        # Fire callback for external processing
        self._fire_callbacks('agent_action', combined_suggestions)
    
    def register_generation_hook(self, hook_function: Callable):
        """Register a hook to be called during AI generation"""
        self.generation_hooks.append(hook_function)
    
    def register_story_processor(self, processor_function: Callable):
        """Register a processor for story content"""
        self.story_processors.append(processor_function)
    
    def register_event_callback(self, event_type: str, callback: Callable):
        """Register a callback for specific events"""
        if event_type in self.event_callbacks:
            self.event_callbacks[event_type].append(callback)
    
    def _fire_callbacks(self, event_type: str, data: Any):
        """Fire all callbacks for a specific event type"""
        for callback in self.event_callbacks.get(event_type, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Error in callback for {event_type}: {e}")
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """Process user input through the cognitive architecture"""
        try:
            # Submit to narrative engine
            element_id = self.narrative_engine.add_narrative_element(
                element_type=NarrativeElement.DIALOGUE,
                content=user_input,
                metadata={'source': 'user_input', 'timestamp': time.time()}
            )
            
            # Submit to agent orchestrator
            input_data = {
                'type': 'user_input',
                'content': user_input,
                'element_id': element_id,
                'timestamp': time.time()
            }
            
            orchestrator_response = self.orchestrator.submit_narrative_input(input_data)
            
            # Get suggestions from adventure telos
            context = {'user_input': user_input, 'timestamp': time.time()}
            telos_suggestions = self.adventure_telos.generate_adventure_suggestions(context)
            
            # Analyze narrative impact
            coherence = self.narrative_engine.analyze_narrative_coherence()
            
            return {
                'success': True,
                'element_id': element_id,
                'agent_responses': orchestrator_response,
                'adventure_suggestions': telos_suggestions,
                'narrative_coherence': coherence['overall_coherence'],
                'processing_metadata': {
                    'timestamp': time.time(),
                    'integration_active': self.is_active
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current status of the OpenCog integration"""
        return {
            'integration_active': self.is_active,
            'config': {
                'enabled': self.config.enabled,
                'integration_mode': self.config.integration_mode,
                'auto_start': self.config.auto_start_orchestration
            },
            'components': {
                'orchestrator': self.orchestrator.get_system_state(),
                'adventure_telos': self.adventure_telos.get_telos_state(),
                'narrative_engine': self.narrative_engine.get_narrative_state(),
                'world_builder': self.world_builder.get_world_state()
            },
            'sessions': {
                'active_sessions': len(self.active_sessions),
                'total_callbacks': sum(len(callbacks) for callbacks in self.event_callbacks.values())
            },
            'performance': {
                'thread_running': self.integration_thread.is_alive() if self.integration_thread else False,
                'last_update': time.time()
            }
        }
    
    def create_session(self, session_id: str, session_config: Dict[str, Any] = None) -> bool:
        """Create a new integration session"""
        if session_id in self.active_sessions:
            logger.warning(f"Session {session_id} already exists")
            return False
        
        try:
            session = {
                'session_id': session_id,
                'created_at': time.time(),
                'config': session_config or {},
                'narrative_context': {},
                'agent_states': {},
                'world_snapshot': self.world_builder.get_world_state()
            }
            
            self.active_sessions[session_id] = session
            self.session_contexts[session_id] = {}
            
            logger.info(f"Created OpenCog integration session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create session {session_id}: {e}")
            return False
    
    def end_session(self, session_id: str) -> bool:
        """End an integration session"""
        if session_id not in self.active_sessions:
            logger.warning(f"Session {session_id} not found")
            return False
        
        try:
            # Clean up session resources
            del self.active_sessions[session_id]
            if session_id in self.session_contexts:
                del self.session_contexts[session_id]
            
            logger.info(f"Ended OpenCog integration session: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            return False
    
    def export_session_data(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session data for persistence or analysis"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        return {
            'session_info': session,
            'narrative_state': self.narrative_engine.get_narrative_state(),
            'world_state': self.world_builder.get_world_state(),
            'orchestrator_state': self.orchestrator.get_system_state(),
            'telos_state': self.adventure_telos.get_telos_state(),
            'export_timestamp': time.time()
        }


# Global integration instance
_integration_instance: Optional[OpenCogKoboldIntegrator] = None


def get_integration() -> Optional[OpenCogKoboldIntegrator]:
    """Get the global integration instance"""
    return _integration_instance


def initialize_integration(kobold_vars, config: KoboldIntegrationConfig = None) -> bool:
    """Initialize the global OpenCog-KoboldAI integration"""
    global _integration_instance
    
    if _integration_instance is not None:
        logger.warning("OpenCog integration already initialized")
        return True
    
    try:
        _integration_instance = OpenCogKoboldIntegrator(config)
        success = _integration_instance.initialize(kobold_vars)
        
        if not success:
            _integration_instance = None
        
        return success
        
    except Exception as e:
        logger.error(f"Failed to initialize OpenCog integration: {e}")
        _integration_instance = None
        return False


def shutdown_integration():
    """Shutdown the global OpenCog integration"""
    global _integration_instance
    
    if _integration_instance:
        _integration_instance.stop_autonomous_processing()
        _integration_instance = None
        logger.info("OpenCog integration shutdown complete")