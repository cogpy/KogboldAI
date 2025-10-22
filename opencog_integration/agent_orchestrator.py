"""
Agent Orchestrator Module

This module implements the core autonomous user agent orchestrator using
OpenCog cognitive architecture principles. It manages multiple AI agents
and coordinates their interactions within the narrative generation system.
"""

import logging
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
import time
from collections import defaultdict

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Represents the current state of an agent in the orchestration system"""
    IDLE = "idle"
    ACTIVE = "active"  
    THINKING = "thinking"
    GENERATING = "generating"
    COORDINATING = "coordinating"
    SUSPENDED = "suspended"


@dataclass
class AgentProfile:
    """Profile configuration for an individual agent"""
    agent_id: str
    name: str
    role: str
    specialization: str
    personality_traits: Dict[str, float]
    capabilities: List[str]
    interaction_preferences: Dict[str, Any] = None
    memory_capacity: int = 1000
    creativity_level: float = 0.7
    focus_areas: List[str] = None
    
    def __post_init__(self):
        if self.interaction_preferences is None:
            self.interaction_preferences = {}
        if self.focus_areas is None:
            self.focus_areas = []


class CognitiveAgent:
    """
    Individual cognitive agent representing a participant in story generation.
    
    Each agent has its own cognitive model, memory, and decision-making processes
    based on OpenCog cognitive architecture principles.
    """
    
    def __init__(self, profile: AgentProfile):
        self.profile = profile
        self.state = AgentState.IDLE
        self.memory = {}
        self.attention_focus = None
        self.current_goals = []
        self.interaction_history = []
        self.cognitive_load = 0.0
        self.last_action_time = time.time()
        
    def update_state(self, new_state: AgentState, context: Dict[str, Any] = None):
        """Update agent state with context information"""
        old_state = self.state
        self.state = new_state
        self.last_action_time = time.time()
        
        if context:
            self.memory[f"state_change_{time.time()}"] = {
                'from': old_state.value,
                'to': new_state.value,
                'context': context,
                'timestamp': time.time()
            }
        
        logger.debug(f"Agent {self.profile.agent_id} state changed: {old_state.value} -> {new_state.value}")
    
    def add_goal(self, goal: str, priority: float = 0.5):
        """Add a new goal to the agent's goal stack"""
        self.current_goals.append({
            'goal': goal,
            'priority': priority,
            'created_at': time.time(),
            'status': 'active'
        })
        
    def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and generate cognitive response"""
        self.cognitive_load = min(1.0, self.cognitive_load + 0.1)
        
        # Simulate cognitive processing based on agent profile
        response = {
            'agent_id': self.profile.agent_id,
            'input_received': input_data,
            'cognitive_state': {
                'load': self.cognitive_load,
                'attention': self.attention_focus,
                'goals': len(self.current_goals)
            },
            'response_type': 'cognitive_processing',
            'timestamp': time.time()
        }
        
        # Update interaction history
        self.interaction_history.append({
            'input': input_data,
            'response': response,
            'timestamp': time.time()
        })
        
        return response


class AgentOrchestrator:
    """
    Main orchestrator class that manages multiple cognitive agents and coordinates
    their interactions for autonomous story generation and world-building.
    """
    
    def __init__(self):
        self.agents: Dict[str, CognitiveAgent] = {}
        self.active_sessions = {}
        self.coordination_rules = {}
        self.narrative_context = {}
        self.orchestration_thread = None
        self.is_running = False
        self._lock = threading.Lock()
        self.event_queue = []
        self.collaboration_matrix = defaultdict(dict)
        
    def register_agent(self, profile: AgentProfile) -> bool:
        """Register a new cognitive agent with the orchestrator"""
        try:
            with self._lock:
                if profile.agent_id in self.agents:
                    logger.warning(f"Agent {profile.agent_id} already registered")
                    return False
                
                agent = CognitiveAgent(profile)
                self.agents[profile.agent_id] = agent
                
                # Initialize collaboration matrix for this agent
                for existing_id in self.agents.keys():
                    if existing_id != profile.agent_id:
                        self.collaboration_matrix[profile.agent_id][existing_id] = 0.5
                        self.collaboration_matrix[existing_id][profile.agent_id] = 0.5
                
                logger.info(f"Registered agent: {profile.name} ({profile.agent_id})")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register agent {profile.agent_id}: {e}")
            return False
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Remove an agent from the orchestration system"""
        try:
            with self._lock:
                if agent_id not in self.agents:
                    logger.warning(f"Agent {agent_id} not found for unregistration")
                    return False
                
                # Clean up collaboration matrix
                del self.collaboration_matrix[agent_id]
                for other_id in self.collaboration_matrix:
                    if agent_id in self.collaboration_matrix[other_id]:
                        del self.collaboration_matrix[other_id][agent_id]
                
                del self.agents[agent_id]
                logger.info(f"Unregistered agent: {agent_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to unregister agent {agent_id}: {e}")
            return False
    
    def start_orchestration(self):
        """Start the autonomous orchestration process"""
        if self.is_running:
            logger.warning("Orchestration is already running")
            return
            
        self.is_running = True
        self.orchestration_thread = threading.Thread(target=self._orchestration_loop)
        self.orchestration_thread.daemon = True
        self.orchestration_thread.start()
        logger.info("Agent orchestration started")
    
    def stop_orchestration(self):
        """Stop the orchestration process"""
        self.is_running = False
        if self.orchestration_thread:
            self.orchestration_thread.join(timeout=5.0)
        logger.info("Agent orchestration stopped")
    
    def _orchestration_loop(self):
        """Main orchestration loop that coordinates agent interactions"""
        while self.is_running:
            try:
                # Process queued events
                self._process_event_queue()
                
                # Update agent states based on current narrative context
                self._update_agent_states()
                
                # Coordinate agent interactions
                self._coordinate_agents()
                
                # Brief pause to prevent excessive CPU usage
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error in orchestration loop: {e}")
                time.sleep(1.0)  # Longer pause on error
    
    def _process_event_queue(self):
        """Process events from the event queue"""
        with self._lock:
            while self.event_queue:
                event = self.event_queue.pop(0)
                self._handle_event(event)
    
    def _handle_event(self, event: Dict[str, Any]):
        """Handle individual events in the system"""
        event_type = event.get('type', 'unknown')
        
        if event_type == 'narrative_update':
            self._handle_narrative_update(event)
        elif event_type == 'agent_interaction':
            self._handle_agent_interaction(event)
        elif event_type == 'world_state_change':
            self._handle_world_state_change(event)
        else:
            logger.warning(f"Unknown event type: {event_type}")
    
    def _update_agent_states(self):
        """Update all agent states based on current conditions"""
        current_time = time.time()
        
        for agent_id, agent in self.agents.items():
            # Decrease cognitive load over time
            if current_time - agent.last_action_time > 5.0:
                agent.cognitive_load = max(0.0, agent.cognitive_load - 0.05)
            
            # Update agent state based on activity and goals
            if agent.current_goals and agent.state == AgentState.IDLE:
                agent.update_state(AgentState.ACTIVE)
            elif not agent.current_goals and agent.state == AgentState.ACTIVE:
                agent.update_state(AgentState.IDLE)
    
    def _coordinate_agents(self):
        """Coordinate interactions between agents"""
        active_agents = [agent for agent in self.agents.values() 
                        if agent.state in [AgentState.ACTIVE, AgentState.THINKING]]
        
        if len(active_agents) < 2:
            return
            
        # Find agents that should collaborate based on their current goals
        for i, agent1 in enumerate(active_agents):
            for agent2 in active_agents[i+1:]:
                compatibility = self.collaboration_matrix[agent1.profile.agent_id][agent2.profile.agent_id]
                
                # If agents are compatible, coordinate their efforts
                if compatibility > 0.6:
                    self._facilitate_collaboration(agent1, agent2)
    
    def _facilitate_collaboration(self, agent1: CognitiveAgent, agent2: CognitiveAgent):
        """Facilitate collaboration between two agents"""
        collaboration_event = {
            'type': 'collaboration',
            'agents': [agent1.profile.agent_id, agent2.profile.agent_id],
            'compatibility': self.collaboration_matrix[agent1.profile.agent_id][agent2.profile.agent_id],
            'timestamp': time.time()
        }
        
        # Both agents process the collaboration context
        agent1.process_input({'collaboration_request': agent2.profile, 'event': collaboration_event})
        agent2.process_input({'collaboration_request': agent1.profile, 'event': collaboration_event})
        
        # Update collaboration strength based on successful interaction
        self.collaboration_matrix[agent1.profile.agent_id][agent2.profile.agent_id] += 0.01
        self.collaboration_matrix[agent2.profile.agent_id][agent1.profile.agent_id] += 0.01
    
    def submit_narrative_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit narrative input to be processed by appropriate agents"""
        try:
            # Determine which agents should process this input
            relevant_agents = self._select_relevant_agents(input_data)
            
            results = {}
            for agent_id in relevant_agents:
                if agent_id in self.agents:
                    agent = self.agents[agent_id]
                    agent.update_state(AgentState.THINKING)
                    result = agent.process_input(input_data)
                    results[agent_id] = result
                    agent.update_state(AgentState.ACTIVE)
            
            return {
                'success': True,
                'agent_responses': results,
                'coordination_metadata': {
                    'processing_time': time.time(),
                    'agents_involved': list(relevant_agents)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to process narrative input: {e}")
            return {'success': False, 'error': str(e)}
    
    def _select_relevant_agents(self, input_data: Dict[str, Any]) -> List[str]:
        """Select agents most relevant to processing the given input"""
        # For now, select all active agents
        # In a more sophisticated implementation, this would use semantic matching
        # based on agent specializations and input content
        return [agent_id for agent_id, agent in self.agents.items() 
                if agent.state in [AgentState.IDLE, AgentState.ACTIVE]]
    
    def get_system_state(self) -> Dict[str, Any]:
        """Get current state of the orchestration system"""
        with self._lock:
            return {
                'is_running': self.is_running,
                'agent_count': len(self.agents),
                'agent_states': {
                    agent_id: {
                        'state': agent.state.value,
                        'cognitive_load': agent.cognitive_load,
                        'goal_count': len(agent.current_goals)
                    }
                    for agent_id, agent in self.agents.items()
                },
                'event_queue_size': len(self.event_queue),
                'active_sessions': len(self.active_sessions)
            }
    
    def _handle_narrative_update(self, event: Dict[str, Any]):
        """Handle narrative context updates"""
        self.narrative_context.update(event.get('data', {}))
        
        # Notify relevant agents about narrative changes
        for agent in self.agents.values():
            agent.process_input({
                'type': 'narrative_update',
                'context': self.narrative_context,
                'timestamp': time.time()
            })
    
    def _handle_agent_interaction(self, event: Dict[str, Any]):
        """Handle direct agent-to-agent interactions"""
        source_id = event.get('source_agent')
        target_id = event.get('target_agent')
        
        if source_id in self.agents and target_id in self.agents:
            source_agent = self.agents[source_id]
            target_agent = self.agents[target_id]
            
            # Process interaction
            interaction_data = {
                'type': 'agent_interaction',
                'from': source_agent.profile,
                'message': event.get('message', ''),
                'timestamp': time.time()
            }
            
            target_agent.process_input(interaction_data)
    
    def _handle_world_state_change(self, event: Dict[str, Any]):
        """Handle world state changes that affect all agents"""
        world_data = event.get('world_state', {})
        
        # Update all agents with world state information
        for agent in self.agents.values():
            agent.process_input({
                'type': 'world_state_update',
                'world_state': world_data,
                'timestamp': time.time()
            })