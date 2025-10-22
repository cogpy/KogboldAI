"""
Adventure Telos Module

This module implements the adventure-driven agent telos (purpose/goal) system.
It provides goal-oriented behavior for agents focused on adventure and story
generation within the narrative framework.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import random

logger = logging.getLogger(__name__)


class GoalType(Enum):
    """Types of goals that can drive adventure agents"""
    EXPLORATION = "exploration"
    CHARACTER_DEVELOPMENT = "character_development"
    PLOT_ADVANCEMENT = "plot_advancement"
    CONFLICT_RESOLUTION = "conflict_resolution"
    WORLD_BUILDING = "world_building"
    MYSTERY_SOLVING = "mystery_solving"
    RELATIONSHIP_BUILDING = "relationship_building"
    QUEST_COMPLETION = "quest_completion"


class GoalPriority(Enum):
    """Priority levels for adventure goals"""
    CRITICAL = 1.0
    HIGH = 0.8
    MEDIUM = 0.6
    LOW = 0.4
    BACKGROUND = 0.2


class GoalStatus(Enum):
    """Status of goal progression"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SUSPENDED = "suspended"


@dataclass
class AdventureGoal:
    """Represents an adventure-oriented goal for agents"""
    goal_id: str
    goal_type: GoalType
    description: str
    priority: GoalPriority
    status: GoalStatus
    target_conditions: Dict[str, Any]
    progress_indicators: Dict[str, float]
    dependencies: List[str]
    created_at: float
    deadline: Optional[float] = None
    estimated_effort: float = 1.0
    narrative_context: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.narrative_context is None:
            self.narrative_context = {}


class AdventureTelos:
    """
    Adventure-driven agent telos system that provides purpose and goal-oriented
    behavior for autonomous agents in story generation and world-building contexts.
    """
    
    def __init__(self):
        self.goals: Dict[str, AdventureGoal] = {}
        self.goal_relationships = {}  # Graph of goal dependencies and conflicts
        self.active_pursuits = []  # Currently active goal pursuits
        self.achievement_history = []
        self.narrative_themes = {}
        self.character_arcs = {}
        self.plot_threads = {}
        
        # Adventure-specific parameters
        self.exploration_bias = 0.7
        self.conflict_tolerance = 0.5
        self.creativity_factor = 0.6
        self.coherence_weight = 0.8
        
    def create_goal(self, goal_type: GoalType, description: str, 
                   priority: GoalPriority = GoalPriority.MEDIUM,
                   narrative_context: Dict[str, Any] = None) -> str:
        """Create a new adventure goal"""
        goal_id = f"{goal_type.value}_{int(time.time() * 1000)}"
        
        goal = AdventureGoal(
            goal_id=goal_id,
            goal_type=goal_type,
            description=description,
            priority=priority,
            status=GoalStatus.INACTIVE,
            target_conditions={},
            progress_indicators={},
            dependencies=[],
            created_at=time.time(),
            narrative_context=narrative_context or {}
        )
        
        self.goals[goal_id] = goal
        logger.info(f"Created adventure goal: {description} ({goal_id})")
        return goal_id
    
    def activate_goal(self, goal_id: str) -> bool:
        """Activate a goal and begin pursuing it"""
        if goal_id not in self.goals:
            logger.error(f"Goal {goal_id} not found")
            return False
        
        goal = self.goals[goal_id]
        
        # Check dependencies
        if not self._check_dependencies(goal):
            logger.warning(f"Cannot activate goal {goal_id}: dependencies not met")
            return False
        
        goal.status = GoalStatus.ACTIVE
        self.active_pursuits.append(goal_id)
        
        logger.info(f"Activated adventure goal: {goal.description}")
        return True
    
    def _check_dependencies(self, goal: AdventureGoal) -> bool:
        """Check if all goal dependencies are satisfied"""
        for dep_id in goal.dependencies:
            if dep_id in self.goals:
                dep_goal = self.goals[dep_id]
                if dep_goal.status != GoalStatus.COMPLETED:
                    return False
        return True
    
    def update_goal_progress(self, goal_id: str, progress_data: Dict[str, Any]) -> bool:
        """Update progress on a specific goal"""
        if goal_id not in self.goals:
            logger.error(f"Goal {goal_id} not found for progress update")
            return False
        
        goal = self.goals[goal_id]
        
        # Update progress indicators
        for indicator, value in progress_data.items():
            goal.progress_indicators[indicator] = value
        
        # Check if goal should transition to in_progress
        if goal.status == GoalStatus.ACTIVE and any(goal.progress_indicators.values()):
            goal.status = GoalStatus.IN_PROGRESS
        
        # Check completion conditions
        if self._evaluate_goal_completion(goal):
            self._complete_goal(goal_id)
        
        return True
    
    def _evaluate_goal_completion(self, goal: AdventureGoal) -> bool:
        """Evaluate whether a goal has been completed"""
        # Check target conditions against progress indicators
        if not goal.target_conditions:
            # If no specific conditions, use heuristic based on progress
            avg_progress = sum(goal.progress_indicators.values()) / max(1, len(goal.progress_indicators))
            return avg_progress >= 0.9
        
        # Check specific target conditions
        for condition, target_value in goal.target_conditions.items():
            current_value = goal.progress_indicators.get(condition, 0.0)
            if current_value < target_value:
                return False
        
        return True
    
    def _complete_goal(self, goal_id: str):
        """Mark a goal as completed and handle side effects"""
        goal = self.goals[goal_id]
        goal.status = GoalStatus.COMPLETED
        
        if goal_id in self.active_pursuits:
            self.active_pursuits.remove(goal_id)
        
        # Record achievement
        achievement = {
            'goal_id': goal_id,
            'goal_type': goal.goal_type.value,
            'description': goal.description,
            'completed_at': time.time(),
            'duration': time.time() - goal.created_at,
            'narrative_impact': self._assess_narrative_impact(goal)
        }
        self.achievement_history.append(achievement)
        
        # Activate dependent goals
        self._activate_dependent_goals(goal_id)
        
        logger.info(f"Completed adventure goal: {goal.description}")
    
    def _assess_narrative_impact(self, goal: AdventureGoal) -> Dict[str, float]:
        """Assess the narrative impact of completing a goal"""
        impact = {
            'character_development': 0.0,
            'plot_advancement': 0.0,
            'world_expansion': 0.0,
            'emotional_resonance': 0.0,
            'conflict_resolution': 0.0
        }
        
        # Different goal types have different narrative impacts
        if goal.goal_type == GoalType.CHARACTER_DEVELOPMENT:
            impact['character_development'] = 0.8
            impact['emotional_resonance'] = 0.6
        elif goal.goal_type == GoalType.PLOT_ADVANCEMENT:
            impact['plot_advancement'] = 0.9
            impact['conflict_resolution'] = 0.5
        elif goal.goal_type == GoalType.WORLD_BUILDING:
            impact['world_expansion'] = 0.8
            impact['plot_advancement'] = 0.3
        elif goal.goal_type == GoalType.EXPLORATION:
            impact['world_expansion'] = 0.6
            impact['character_development'] = 0.4
        
        return impact
    
    def _activate_dependent_goals(self, completed_goal_id: str):
        """Activate goals that depend on the completed goal"""
        for goal_id, goal in self.goals.items():
            if (completed_goal_id in goal.dependencies and 
                goal.status == GoalStatus.INACTIVE):
                self.activate_goal(goal_id)
    
    def generate_adventure_suggestions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate adventure goal suggestions based on current context"""
        suggestions = []
        
        # Analyze current narrative state
        current_themes = context.get('themes', [])
        active_characters = context.get('characters', [])
        world_state = context.get('world_state', {})
        
        # Generate exploration goals
        if self.exploration_bias > 0.5:
            suggestions.extend(self._generate_exploration_goals(world_state))
        
        # Generate character development goals
        for character in active_characters:
            suggestions.extend(self._generate_character_goals(character))
        
        # Generate plot advancement goals
        suggestions.extend(self._generate_plot_goals(current_themes, world_state))
        
        # Generate conflict resolution goals
        unresolved_conflicts = context.get('conflicts', [])
        for conflict in unresolved_conflicts:
            suggestions.extend(self._generate_conflict_goals(conflict))
        
        return suggestions
    
    def _generate_exploration_goals(self, world_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate exploration-focused adventure goals"""
        goals = []
        
        unexplored_areas = world_state.get('unexplored_regions', [])
        for area in unexplored_areas:
            goals.append({
                'type': GoalType.EXPLORATION,
                'description': f"Explore the mysterious {area.get('name', 'region')}",
                'priority': GoalPriority.MEDIUM,
                'target_conditions': {'exploration_progress': 1.0},
                'narrative_context': {'region': area}
            })
        
        return goals
    
    def _generate_character_goals(self, character: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate character development goals"""
        goals = []
        
        character_name = character.get('name', 'Unknown')
        underdeveloped_traits = character.get('underdeveloped_traits', [])
        
        for trait in underdeveloped_traits:
            goals.append({
                'type': GoalType.CHARACTER_DEVELOPMENT,
                'description': f"Develop {character_name}'s {trait} trait",
                'priority': GoalPriority.HIGH,
                'target_conditions': {'trait_development': 0.8},
                'narrative_context': {'character': character, 'trait': trait}
            })
        
        return goals
    
    def _generate_plot_goals(self, themes: List[str], world_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate plot advancement goals"""
        goals = []
        
        for theme in themes:
            if theme not in self.plot_threads:
                goals.append({
                    'type': GoalType.PLOT_ADVANCEMENT,
                    'description': f"Advance the {theme} storyline",
                    'priority': GoalPriority.HIGH,
                    'target_conditions': {'plot_progression': 0.7},
                    'narrative_context': {'theme': theme}
                })
        
        return goals
    
    def _generate_conflict_goals(self, conflict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate conflict resolution goals"""
        goals = []
        
        conflict_type = conflict.get('type', 'general')
        parties = conflict.get('parties', [])
        
        goals.append({
            'type': GoalType.CONFLICT_RESOLUTION,
            'description': f"Resolve {conflict_type} conflict between {', '.join(parties)}",
            'priority': GoalPriority.HIGH,
            'target_conditions': {'resolution_progress': 1.0},
            'narrative_context': {'conflict': conflict}
        })
        
        return goals
    
    def prioritize_active_goals(self) -> List[str]:
        """Prioritize active goals based on various factors"""
        active_goals = [self.goals[goal_id] for goal_id in self.active_pursuits]
        
        # Sort by priority, deadline, and narrative coherence
        def goal_score(goal: AdventureGoal) -> float:
            score = goal.priority.value
            
            # Add urgency factor for deadlines
            if goal.deadline:
                time_remaining = goal.deadline - time.time()
                if time_remaining > 0:
                    urgency = 1.0 / (time_remaining / 3600 + 1)  # Hours
                    score += urgency * 0.3
            
            # Add coherence factor based on narrative context
            coherence = self._calculate_narrative_coherence(goal)
            score += coherence * self.coherence_weight * 0.2
            
            return score
        
        sorted_goals = sorted(active_goals, key=goal_score, reverse=True)
        return [goal.goal_id for goal in sorted_goals]
    
    def _calculate_narrative_coherence(self, goal: AdventureGoal) -> float:
        """Calculate how well a goal fits with current narrative state"""
        # Simple heuristic - in a full implementation, this would use
        # semantic analysis of the narrative context
        coherence = 0.5  # Base coherence
        
        # Check thematic alignment
        goal_themes = goal.narrative_context.get('themes', [])
        current_themes = set(self.narrative_themes.keys())
        
        if goal_themes:
            theme_overlap = len(set(goal_themes) & current_themes) / len(goal_themes)
            coherence += theme_overlap * 0.3
        
        return min(1.0, coherence)
    
    def get_telos_state(self) -> Dict[str, Any]:
        """Get current state of the adventure telos system"""
        return {
            'total_goals': len(self.goals),
            'active_goals': len(self.active_pursuits),
            'completed_goals': len([g for g in self.goals.values() 
                                  if g.status == GoalStatus.COMPLETED]),
            'goal_distribution': {
                goal_type.value: len([g for g in self.goals.values() 
                                    if g.goal_type == goal_type])
                for goal_type in GoalType
            },
            'recent_achievements': self.achievement_history[-5:],
            'narrative_parameters': {
                'exploration_bias': self.exploration_bias,
                'conflict_tolerance': self.conflict_tolerance,
                'creativity_factor': self.creativity_factor,
                'coherence_weight': self.coherence_weight
            }
        }
    
    def update_narrative_context(self, context: Dict[str, Any]):
        """Update the narrative context that influences goal generation and prioritization"""
        self.narrative_themes.update(context.get('themes', {}))
        self.character_arcs.update(context.get('character_arcs', {}))
        self.plot_threads.update(context.get('plot_threads', {}))
        
        # Adjust adventure parameters based on narrative context
        narrative_tone = context.get('tone', 'balanced')
        if narrative_tone == 'exploration-heavy':
            self.exploration_bias = 0.9
        elif narrative_tone == 'character-focused':
            self.exploration_bias = 0.4
        elif narrative_tone == 'action-packed':
            self.conflict_tolerance = 0.8
        
        logger.debug("Updated adventure telos narrative context")
    
    def suggest_next_action(self, agent_context: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest the next action for an agent based on current goals and context"""
        if not self.active_pursuits:
            return {'action': 'generate_new_goals', 'priority': 0.5}
        
        # Get highest priority goal
        prioritized_goals = self.prioritize_active_goals()
        if not prioritized_goals:
            return {'action': 'wait', 'priority': 0.1}
        
        top_goal_id = prioritized_goals[0]
        top_goal = self.goals[top_goal_id]
        
        # Generate action based on goal type and current progress
        action = self._generate_goal_action(top_goal, agent_context)
        
        return {
            'action': action['type'],
            'details': action['details'],
            'goal_id': top_goal_id,
            'priority': top_goal.priority.value,
            'expected_impact': action.get('expected_impact', 0.5)
        }
    
    def _generate_goal_action(self, goal: AdventureGoal, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a specific action to advance a goal"""
        if goal.goal_type == GoalType.EXPLORATION:
            return {
                'type': 'explore_location',
                'details': {
                    'target': goal.narrative_context.get('region', {}),
                    'approach': 'cautious' if context.get('risk_tolerance', 0.5) < 0.5 else 'bold'
                },
                'expected_impact': 0.7
            }
        
        elif goal.goal_type == GoalType.CHARACTER_DEVELOPMENT:
            return {
                'type': 'character_interaction',
                'details': {
                    'character': goal.narrative_context.get('character', {}),
                    'trait_focus': goal.narrative_context.get('trait', ''),
                    'interaction_type': 'challenge' if random.random() > 0.5 else 'support'
                },
                'expected_impact': 0.6
            }
        
        elif goal.goal_type == GoalType.PLOT_ADVANCEMENT:
            return {
                'type': 'advance_plot',
                'details': {
                    'theme': goal.narrative_context.get('theme', ''),
                    'advancement_method': 'revelation' if random.random() > 0.5 else 'action'
                },
                'expected_impact': 0.8
            }
        
        elif goal.goal_type == GoalType.CONFLICT_RESOLUTION:
            return {
                'type': 'address_conflict',
                'details': {
                    'conflict': goal.narrative_context.get('conflict', {}),
                    'approach': 'diplomatic' if self.conflict_tolerance < 0.5 else 'direct'
                },
                'expected_impact': 0.9
            }
        
        else:
            return {
                'type': 'general_action',
                'details': {'description': goal.description},
                'expected_impact': 0.4
            }