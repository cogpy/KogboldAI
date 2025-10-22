"""
Narrative Engine Module

This module implements the story-weaving narrative logos (logic) system that
handles narrative reasoning, story coherence, and logical narrative construction
within the OpenCog integration framework.
"""

import logging
import time
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import json
import random
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class NarrativeElement(Enum):
    """Types of narrative elements"""
    CHARACTER = "character"
    SETTING = "setting"
    PLOT_POINT = "plot_point"
    CONFLICT = "conflict"
    THEME = "theme"
    DIALOGUE = "dialogue"
    ACTION = "action"
    DESCRIPTION = "description"
    TRANSITION = "transition"


class LogicalRelation(Enum):
    """Types of logical relationships between narrative elements"""
    CAUSATION = "causation"         # A causes B
    SEQUENCE = "sequence"           # A happens before B
    CONTRADICTION = "contradiction" # A contradicts B
    SUPPORT = "support"            # A supports/reinforces B
    PARALLEL = "parallel"          # A happens alongside B
    IMPLICATION = "implication"    # A implies B
    EXCLUSION = "exclusion"        # A excludes B


class NarrativeCoherence(Enum):
    """Levels of narrative coherence"""
    EXCELLENT = 0.9
    GOOD = 0.7
    ACCEPTABLE = 0.5
    POOR = 0.3
    BROKEN = 0.1


@dataclass
class NarrativeNode:
    """Represents a single narrative element with logical connections"""
    node_id: str
    element_type: NarrativeElement
    content: str
    timestamp: float
    metadata: Dict[str, Any]
    logical_connections: Dict[str, LogicalRelation]  # node_id -> relation
    coherence_score: float = 0.5
    narrative_weight: float = 1.0


@dataclass
class StoryArc:
    """Represents a complete story arc with logical progression"""
    arc_id: str
    title: str
    nodes: List[str]  # List of node IDs in sequence
    themes: List[str]
    character_roles: Dict[str, str]  # character -> role
    coherence_metrics: Dict[str, float]
    completion_status: float = 0.0


class NarrativeEngine:
    """
    Story-weaving narrative engine that implements logical reasoning about
    narrative elements and maintains story coherence through cognitive
    architecture principles.
    """
    
    def __init__(self):
        self.narrative_graph: Dict[str, NarrativeNode] = {}
        self.story_arcs: Dict[str, StoryArc] = {}
        self.active_themes = set()
        self.character_registry = {}
        self.setting_registry = {}
        self.plot_threads = defaultdict(list)
        
        # Narrative logic parameters
        self.coherence_threshold = 0.6
        self.max_story_length = 1000  # Maximum narrative nodes
        self.theme_consistency_weight = 0.8
        self.character_consistency_weight = 0.9
        self.temporal_consistency_weight = 0.7
        
        # Story generation parameters
        self.creativity_factor = 0.6
        self.surprise_factor = 0.3
        self.predictability_balance = 0.5
        
        # Logical reasoning cache
        self._coherence_cache = {}
        self._logical_inference_cache = {}
        
    def add_narrative_element(self, element_type: NarrativeElement, 
                            content: str, metadata: Dict[str, Any] = None) -> str:
        """Add a new narrative element to the story graph"""
        node_id = f"{element_type.value}_{int(time.time() * 1000)}"
        
        node = NarrativeNode(
            node_id=node_id,
            element_type=element_type,
            content=content,
            timestamp=time.time(),
            metadata=metadata or {},
            logical_connections={},
            coherence_score=0.5
        )
        
        self.narrative_graph[node_id] = node
        
        # Automatically establish logical connections
        self._establish_logical_connections(node_id)
        
        # Update coherence scores
        self._update_coherence_scores([node_id])
        
        logger.info(f"Added narrative element: {element_type.value} - {content[:50]}...")
        return node_id
    
    def _establish_logical_connections(self, new_node_id: str):
        """Establish logical connections between the new node and existing nodes"""
        new_node = self.narrative_graph[new_node_id]
        
        # Find potential connections based on content similarity and logical relationships
        for existing_id, existing_node in self.narrative_graph.items():
            if existing_id == new_node_id:
                continue
                
            # Calculate logical relationship
            relation = self._infer_logical_relation(new_node, existing_node)
            
            if relation:
                new_node.logical_connections[existing_id] = relation
                existing_node.logical_connections[new_node_id] = self._get_inverse_relation(relation)
    
    def _infer_logical_relation(self, node1: NarrativeNode, 
                              node2: NarrativeNode) -> Optional[LogicalRelation]:
        """Infer the logical relationship between two narrative nodes"""
        
        # Check cache first
        cache_key = f"{node1.node_id}:{node2.node_id}"
        if cache_key in self._logical_inference_cache:
            return self._logical_inference_cache[cache_key]
        
        relation = None
        
        # Time-based relationships
        if abs(node1.timestamp - node2.timestamp) < 60:  # Within 1 minute
            relation = LogicalRelation.PARALLEL
        elif node1.timestamp > node2.timestamp:
            relation = LogicalRelation.SEQUENCE
        
        # Content-based relationships
        content_similarity = self._calculate_content_similarity(node1.content, node2.content)
        
        if content_similarity > 0.8:
            relation = LogicalRelation.SUPPORT
        elif self._detect_contradiction(node1.content, node2.content):
            relation = LogicalRelation.CONTRADICTION
        elif self._detect_causation(node1, node2):
            relation = LogicalRelation.CAUSATION
        
        # Element type specific relationships
        if node1.element_type == NarrativeElement.CHARACTER and node2.element_type == NarrativeElement.CHARACTER:
            if self._characters_interact(node1, node2):
                relation = LogicalRelation.PARALLEL
        
        # Cache the result
        self._logical_inference_cache[cache_key] = relation
        
        return relation
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """Calculate semantic similarity between two pieces of content"""
        # Simple word overlap similarity (in practice, would use embeddings)
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union) if union else 0.0
    
    def _detect_contradiction(self, content1: str, content2: str) -> bool:
        """Detect logical contradictions between two content pieces"""
        # Simple contradiction patterns
        contradiction_patterns = [
            (r'\bnot\b', r'\bis\b'),
            (r'\balive\b', r'\bdead\b'),
            (r'\bday\b', r'\bnight\b'),
            (r'\bhappy\b', r'\bsad\b'),
            (r'\bgood\b', r'\bevil\b')
        ]
        
        content1_lower = content1.lower()
        content2_lower = content2.lower()
        
        for pattern1, pattern2 in contradiction_patterns:
            if (re.search(pattern1, content1_lower) and re.search(pattern2, content2_lower)) or \
               (re.search(pattern2, content1_lower) and re.search(pattern1, content2_lower)):
                return True
        
        return False
    
    def _detect_causation(self, node1: NarrativeNode, node2: NarrativeNode) -> bool:
        """Detect causal relationships between narrative nodes"""
        # Simple causation detection based on temporal order and content patterns
        if node1.timestamp >= node2.timestamp:
            return False
        
        causation_patterns = [
            r'\bbecause\b', r'\btherefore\b', r'\bas a result\b', 
            r'\bconsequently\b', r'\bleading to\b', r'\bcaused by\b'
        ]
        
        combined_content = f"{node1.content} {node2.content}".lower()
        
        return any(re.search(pattern, combined_content) for pattern in causation_patterns)
    
    def _characters_interact(self, node1: NarrativeNode, node2: NarrativeNode) -> bool:
        """Detect if two character nodes represent interacting characters"""
        # Extract character names from content
        char1_names = self._extract_character_names(node1.content)
        char2_names = self._extract_character_names(node2.content)
        
        # Check for shared characters
        return bool(char1_names & char2_names)
    
    def _extract_character_names(self, content: str) -> Set[str]:
        """Extract character names from content"""
        # Simple name extraction (in practice, would use NER)
        # Look for capitalized words that might be names
        words = content.split()
        names = set()
        
        for word in words:
            # Simple heuristic: capitalized words that aren't at sentence start
            if word[0].isupper() and len(word) > 2 and word.isalpha():
                names.add(word)
        
        # Filter against known character registry
        return names & set(self.character_registry.keys())
    
    def _get_inverse_relation(self, relation: LogicalRelation) -> LogicalRelation:
        """Get the inverse of a logical relation"""
        inverses = {
            LogicalRelation.CAUSATION: LogicalRelation.SEQUENCE,
            LogicalRelation.SEQUENCE: LogicalRelation.SEQUENCE,
            LogicalRelation.CONTRADICTION: LogicalRelation.CONTRADICTION,
            LogicalRelation.SUPPORT: LogicalRelation.SUPPORT,
            LogicalRelation.PARALLEL: LogicalRelation.PARALLEL,
            LogicalRelation.IMPLICATION: LogicalRelation.IMPLICATION,
            LogicalRelation.EXCLUSION: LogicalRelation.EXCLUSION
        }
        return inverses.get(relation, relation)
    
    def _update_coherence_scores(self, node_ids: List[str]):
        """Update coherence scores for the specified nodes and their neighbors"""
        for node_id in node_ids:
            if node_id not in self.narrative_graph:
                continue
                
            node = self.narrative_graph[node_id]
            coherence = self._calculate_node_coherence(node)
            node.coherence_score = coherence
            
            # Update connected nodes
            for connected_id in node.logical_connections:
                if connected_id in self.narrative_graph:
                    connected_node = self.narrative_graph[connected_id]
                    connected_coherence = self._calculate_node_coherence(connected_node)
                    connected_node.coherence_score = connected_coherence
    
    def _calculate_node_coherence(self, node: NarrativeNode) -> float:
        """Calculate coherence score for a single narrative node"""
        if not node.logical_connections:
            return 0.5  # Neutral coherence for isolated nodes
        
        # Check cache
        cache_key = f"coherence_{node.node_id}_{len(node.logical_connections)}"
        if cache_key in self._coherence_cache:
            return self._coherence_cache[cache_key]
        
        coherence_factors = []
        
        # Factor 1: Consistency of logical relationships
        consistent_relations = 0
        total_relations = len(node.logical_connections)
        
        for connected_id, relation in node.logical_connections.items():
            if self._validate_logical_consistency(node, connected_id, relation):
                consistent_relations += 1
        
        logical_consistency = consistent_relations / total_relations if total_relations > 0 else 0.5
        coherence_factors.append(logical_consistency * self.theme_consistency_weight)
        
        # Factor 2: Temporal consistency
        temporal_score = self._calculate_temporal_consistency(node)
        coherence_factors.append(temporal_score * self.temporal_consistency_weight)
        
        # Factor 3: Character consistency (if applicable)
        if node.element_type == NarrativeElement.CHARACTER:
            character_score = self._calculate_character_consistency(node)
            coherence_factors.append(character_score * self.character_consistency_weight)
        
        # Calculate weighted average
        final_coherence = sum(coherence_factors) / len(coherence_factors) if coherence_factors else 0.5
        
        # Cache result
        self._coherence_cache[cache_key] = final_coherence
        
        return final_coherence
    
    def _validate_logical_consistency(self, node: NarrativeNode, 
                                   connected_id: str, relation: LogicalRelation) -> bool:
        """Validate that a logical relationship is consistent"""
        if connected_id not in self.narrative_graph:
            return False
        
        connected_node = self.narrative_graph[connected_id]
        
        # Check for contradictory relationships
        if relation == LogicalRelation.CONTRADICTION:
            return True  # Contradictions are valid logical relationships
        
        # Check temporal consistency for sequence/causation
        if relation in [LogicalRelation.SEQUENCE, LogicalRelation.CAUSATION]:
            return node.timestamp <= connected_node.timestamp
        
        # Check for support consistency
        if relation == LogicalRelation.SUPPORT:
            return not self._detect_contradiction(node.content, connected_node.content)
        
        return True
    
    def _calculate_temporal_consistency(self, node: NarrativeNode) -> float:
        """Calculate temporal consistency score for a node"""
        temporal_violations = 0
        temporal_checks = 0
        
        for connected_id, relation in node.logical_connections.items():
            if connected_id not in self.narrative_graph:
                continue
                
            connected_node = self.narrative_graph[connected_id]
            temporal_checks += 1
            
            # Check temporal ordering for sequential relationships
            if relation == LogicalRelation.SEQUENCE:
                if node.timestamp > connected_node.timestamp:
                    temporal_violations += 1
            elif relation == LogicalRelation.CAUSATION:
                if node.timestamp >= connected_node.timestamp:
                    temporal_violations += 1
        
        if temporal_checks == 0:
            return 0.7  # Neutral score for no temporal relationships
        
        return 1.0 - (temporal_violations / temporal_checks)
    
    def _calculate_character_consistency(self, node: NarrativeNode) -> float:
        """Calculate character consistency score"""
        # Extract character information from the node
        character_names = self._extract_character_names(node.content)
        
        if not character_names:
            return 0.7  # Neutral score for no characters
        
        consistency_score = 0.0
        character_count = 0
        
        for character_name in character_names:
            if character_name in self.character_registry:
                character_info = self.character_registry[character_name]
                
                # Check consistency with established character traits
                consistency = self._check_character_trait_consistency(
                    node.content, character_info
                )
                consistency_score += consistency
                character_count += 1
        
        return consistency_score / character_count if character_count > 0 else 0.7
    
    def _check_character_trait_consistency(self, content: str, 
                                         character_info: Dict[str, Any]) -> float:
        """Check if content is consistent with character traits"""
        established_traits = character_info.get('traits', [])
        
        # Simple trait consistency check
        positive_indicators = 0
        total_checks = 0
        
        for trait in established_traits:
            trait_lower = trait.lower()
            content_lower = content.lower()
            
            # Check if content supports the trait
            if trait_lower in content_lower:
                positive_indicators += 1
            
            total_checks += 1
        
        if total_checks == 0:
            return 0.7  # Neutral if no traits to check
        
        return positive_indicators / total_checks
    
    def weave_narrative_segment(self, context: Dict[str, Any], 
                              target_length: int = 3) -> List[str]:
        """Weave a coherent narrative segment using logical reasoning"""
        
        # Select starting point based on context
        starting_nodes = self._select_narrative_starting_points(context)
        
        if not starting_nodes:
            # Create a new starting point
            start_content = self._generate_opening_content(context)
            start_id = self.add_narrative_element(
                NarrativeElement.DESCRIPTION, start_content, context
            )
            starting_nodes = [start_id]
        
        # Build narrative sequence using logical connections
        narrative_sequence = []
        
        for start_id in starting_nodes[:1]:  # Use first starting point
            sequence = self._build_logical_sequence(start_id, target_length, context)
            narrative_sequence.extend(sequence)
        
        return narrative_sequence
    
    def _select_narrative_starting_points(self, context: Dict[str, Any]) -> List[str]:
        """Select appropriate starting points for narrative weaving"""
        candidates = []
        
        # Look for nodes matching the context
        for node_id, node in self.narrative_graph.items():
            relevance = self._calculate_context_relevance(node, context)
            if relevance > 0.6:
                candidates.append((node_id, relevance))
        
        # Sort by relevance and return top candidates
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [node_id for node_id, _ in candidates[:3]]
    
    def _calculate_context_relevance(self, node: NarrativeNode, 
                                   context: Dict[str, Any]) -> float:
        """Calculate how relevant a node is to the given context"""
        relevance = 0.0
        
        # Check theme alignment
        context_themes = set(context.get('themes', []))
        if context_themes:
            node_themes = set(node.metadata.get('themes', []))
            theme_overlap = len(context_themes & node_themes) / len(context_themes)
            relevance += theme_overlap * 0.4
        
        # Check character alignment
        context_characters = set(context.get('characters', []))
        node_characters = self._extract_character_names(node.content)
        if context_characters and node_characters:
            character_overlap = len(context_characters & node_characters) / len(context_characters)
            relevance += character_overlap * 0.3
        
        # Check setting alignment
        context_setting = context.get('setting', '')
        if context_setting and context_setting.lower() in node.content.lower():
            relevance += 0.3
        
        return min(1.0, relevance)
    
    def _generate_opening_content(self, context: Dict[str, Any]) -> str:
        """Generate opening content based on context"""
        templates = [
            "In the {setting}, {character} begins a new adventure.",
            "The story continues in {setting} where {character} faces a challenge.",
            "As {character} explores {setting}, something unexpected happens.",
            "In the heart of {setting}, {character} discovers something important."
        ]
        
        template = random.choice(templates)
        
        # Fill in template with context information
        setting = context.get('setting', 'mysterious place')
        characters = context.get('characters', ['the protagonist'])
        character = characters[0] if characters else 'the protagonist'
        
        return template.format(setting=setting, character=character)
    
    def _build_logical_sequence(self, start_id: str, target_length: int, 
                              context: Dict[str, Any]) -> List[str]:
        """Build a logically coherent sequence from a starting node"""
        sequence = [start_id]
        current_id = start_id
        
        for _ in range(target_length - 1):
            next_id = self._select_next_logical_node(current_id, context, sequence)
            
            if not next_id:
                # Generate a new node if no logical continuation exists
                next_id = self._generate_continuation_node(current_id, context)
            
            sequence.append(next_id)
            current_id = next_id
        
        return sequence
    
    def _select_next_logical_node(self, current_id: str, context: Dict[str, Any], 
                                existing_sequence: List[str]) -> Optional[str]:
        """Select the next logical node in the sequence"""
        if current_id not in self.narrative_graph:
            return None
        
        current_node = self.narrative_graph[current_id]
        candidates = []
        
        # Look for nodes with logical connections
        for connected_id, relation in current_node.logical_connections.items():
            if connected_id in existing_sequence:
                continue  # Avoid cycles
            
            connected_node = self.narrative_graph[connected_id]
            
            # Score based on logical relationship strength
            score = self._score_logical_continuation(current_node, connected_node, relation, context)
            candidates.append((connected_id, score))
        
        # Select best candidate
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return None
    
    def _score_logical_continuation(self, current_node: NarrativeNode, 
                                  next_node: NarrativeNode, relation: LogicalRelation,
                                  context: Dict[str, Any]) -> float:
        """Score how good a continuation this node would be"""
        score = 0.0
        
        # Base score from relationship type
        relation_scores = {
            LogicalRelation.SEQUENCE: 0.8,
            LogicalRelation.CAUSATION: 0.9,
            LogicalRelation.SUPPORT: 0.7,
            LogicalRelation.PARALLEL: 0.5,
            LogicalRelation.IMPLICATION: 0.6,
            LogicalRelation.CONTRADICTION: 0.3,
            LogicalRelation.EXCLUSION: 0.2
        }
        score += relation_scores.get(relation, 0.4)
        
        # Context relevance bonus
        context_relevance = self._calculate_context_relevance(next_node, context)
        score += context_relevance * 0.3
        
        # Coherence bonus
        score += next_node.coherence_score * 0.2
        
        # Temporal consistency bonus
        if next_node.timestamp > current_node.timestamp:
            score += 0.1
        
        return score
    
    def _generate_continuation_node(self, current_id: str, context: Dict[str, Any]) -> str:
        """Generate a new node that continues from the current node"""
        if current_id not in self.narrative_graph:
            return self.add_narrative_element(
                NarrativeElement.DESCRIPTION,
                "The story continues...",
                context
            )
        
        current_node = self.narrative_graph[current_id]
        
        # Generate continuation based on current node type and content
        continuation_content = self._generate_contextual_continuation(current_node, context)
        
        # Determine appropriate element type for continuation
        next_element_type = self._determine_continuation_type(current_node)
        
        return self.add_narrative_element(
            next_element_type,
            continuation_content,
            context
        )
    
    def _generate_contextual_continuation(self, current_node: NarrativeNode, 
                                        context: Dict[str, Any]) -> str:
        """Generate contextually appropriate continuation content"""
        # Simple template-based generation (in practice, would use LLM)
        continuation_templates = {
            NarrativeElement.DESCRIPTION: [
                "The scene shifts to reveal {element}.",
                "Suddenly, {element} appears.",
                "Meanwhile, {element} unfolds."
            ],
            NarrativeElement.ACTION: [
                "Next, the character decides to {action}.",
                "In response, {character} {action}.",
                "The situation leads to {action}."
            ],
            NarrativeElement.DIALOGUE: [
                '"{character} says something important.',
                'The conversation continues with {character}.',
                'Someone responds to the previous statement.'
            ]
        }
        
        templates = continuation_templates.get(
            current_node.element_type, 
            continuation_templates[NarrativeElement.DESCRIPTION]
        )
        
        template = random.choice(templates)
        
        # Simple variable substitution
        characters = context.get('characters', ['someone'])
        character = random.choice(characters)
        element = context.get('setting', 'something interesting')
        action = random.choice(['investigate', 'explore', 'react', 'speak'])
        
        return template.format(character=character, element=element, action=action)
    
    def _determine_continuation_type(self, current_node: NarrativeNode) -> NarrativeElement:
        """Determine appropriate element type for continuation"""
        type_transitions = {
            NarrativeElement.DESCRIPTION: [NarrativeElement.ACTION, NarrativeElement.DIALOGUE],
            NarrativeElement.ACTION: [NarrativeElement.DESCRIPTION, NarrativeElement.DIALOGUE],
            NarrativeElement.DIALOGUE: [NarrativeElement.ACTION, NarrativeElement.DESCRIPTION],
            NarrativeElement.CHARACTER: [NarrativeElement.ACTION, NarrativeElement.DIALOGUE],
            NarrativeElement.SETTING: [NarrativeElement.DESCRIPTION, NarrativeElement.ACTION]
        }
        
        possible_types = type_transitions.get(
            current_node.element_type, 
            [NarrativeElement.DESCRIPTION]
        )
        
        return random.choice(possible_types)
    
    def analyze_narrative_coherence(self) -> Dict[str, Any]:
        """Analyze overall narrative coherence"""
        if not self.narrative_graph:
            return {'overall_coherence': 0.0, 'analysis': 'No narrative elements found'}
        
        # Calculate overall coherence metrics
        total_coherence = sum(node.coherence_score for node in self.narrative_graph.values())
        overall_coherence = total_coherence / len(self.narrative_graph)
        
        # Analyze logical consistency
        logical_violations = self._count_logical_violations()
        logical_consistency = 1.0 - (logical_violations / max(1, len(self.narrative_graph)))
        
        # Analyze temporal consistency
        temporal_consistency = self._analyze_temporal_consistency()
        
        # Analyze theme consistency
        theme_consistency = self._analyze_theme_consistency()
        
        return {
            'overall_coherence': overall_coherence,
            'logical_consistency': logical_consistency,
            'temporal_consistency': temporal_consistency,
            'theme_consistency': theme_consistency,
            'total_elements': len(self.narrative_graph),
            'logical_violations': logical_violations,
            'coherence_distribution': self._get_coherence_distribution(),
            'recommendations': self._generate_coherence_recommendations(overall_coherence)
        }
    
    def _count_logical_violations(self) -> int:
        """Count logical violations in the narrative graph"""
        violations = 0
        
        for node in self.narrative_graph.values():
            for connected_id, relation in node.logical_connections.items():
                if not self._validate_logical_consistency(node, connected_id, relation):
                    violations += 1
        
        return violations // 2  # Each violation is counted twice (once for each node)
    
    def _analyze_temporal_consistency(self) -> float:
        """Analyze temporal consistency across the narrative"""
        temporal_scores = []
        
        for node in self.narrative_graph.values():
            temporal_score = self._calculate_temporal_consistency(node)
            temporal_scores.append(temporal_score)
        
        return sum(temporal_scores) / len(temporal_scores) if temporal_scores else 0.5
    
    def _analyze_theme_consistency(self) -> float:
        """Analyze consistency of themes throughout the narrative"""
        if not self.active_themes:
            return 0.7  # Neutral score for no established themes
        
        theme_violations = 0
        theme_checks = 0
        
        for node in self.narrative_graph.values():
            node_themes = set(node.metadata.get('themes', []))
            
            # Check if node themes conflict with active themes
            for theme in node_themes:
                theme_checks += 1
                if theme not in self.active_themes:
                    # Check if this is a conflicting theme
                    if self._themes_conflict(theme, self.active_themes):
                        theme_violations += 1
        
        if theme_checks == 0:
            return 0.7
        
        return 1.0 - (theme_violations / theme_checks)
    
    def _themes_conflict(self, theme: str, active_themes: Set[str]) -> bool:
        """Check if a theme conflicts with active themes"""
        # Simple conflict detection (could be expanded)
        conflict_pairs = [
            ('comedy', 'tragedy'),
            ('hope', 'despair'),
            ('peace', 'war'),
            ('love', 'hatred')
        ]
        
        theme_lower = theme.lower()
        
        for theme1, theme2 in conflict_pairs:
            if theme_lower == theme1 and theme2 in [t.lower() for t in active_themes]:
                return True
            if theme_lower == theme2 and theme1 in [t.lower() for t in active_themes]:
                return True
        
        return False
    
    def _get_coherence_distribution(self) -> Dict[str, int]:
        """Get distribution of coherence levels"""
        distribution = {level.name: 0 for level in NarrativeCoherence}
        
        for node in self.narrative_graph.values():
            if node.coherence_score >= NarrativeCoherence.EXCELLENT.value:
                distribution['EXCELLENT'] += 1
            elif node.coherence_score >= NarrativeCoherence.GOOD.value:
                distribution['GOOD'] += 1
            elif node.coherence_score >= NarrativeCoherence.ACCEPTABLE.value:
                distribution['ACCEPTABLE'] += 1
            elif node.coherence_score >= NarrativeCoherence.POOR.value:
                distribution['POOR'] += 1
            else:
                distribution['BROKEN'] += 1
        
        return distribution
    
    def _generate_coherence_recommendations(self, overall_coherence: float) -> List[str]:
        """Generate recommendations for improving narrative coherence"""
        recommendations = []
        
        if overall_coherence < 0.4:
            recommendations.append("Consider restructuring the narrative to improve logical flow")
            recommendations.append("Review character consistency across scenes")
        
        if overall_coherence < 0.6:
            recommendations.append("Strengthen causal relationships between events")
            recommendations.append("Ensure temporal consistency in scene ordering")
        
        if overall_coherence < 0.8:
            recommendations.append("Enhance thematic consistency throughout the story")
            recommendations.append("Resolve any remaining logical contradictions")
        
        if not recommendations:
            recommendations.append("Narrative coherence is excellent - maintain current quality")
        
        return recommendations
    
    def get_narrative_state(self) -> Dict[str, Any]:
        """Get current state of the narrative engine"""
        return {
            'total_elements': len(self.narrative_graph),
            'active_themes': list(self.active_themes),
            'story_arcs': len(self.story_arcs),
            'character_count': len(self.character_registry),
            'setting_count': len(self.setting_registry),
            'coherence_metrics': self.analyze_narrative_coherence(),
            'engine_parameters': {
                'coherence_threshold': self.coherence_threshold,
                'creativity_factor': self.creativity_factor,
                'surprise_factor': self.surprise_factor,
                'predictability_balance': self.predictability_balance
            }
        }