"""
Associative Memory Retrieval System

Implements intelligent memory retrieval based on:
- Semantic similarity
- Attention scores
- Temporal proximity
- Association strength
- Context relevance
"""

import re
import math
import time
import logging
from typing import List, Dict, Optional, Set, Tuple
from collections import defaultdict

from .hierarchy import MemoryHierarchy, MemoryItem, MemoryType

logger = logging.getLogger(__name__)


class MemoryRetriever:
    """
    Retrieves memories using various strategies and scoring mechanisms.
    """
    
    def __init__(self, memory_hierarchy: MemoryHierarchy):
        self.hierarchy = memory_hierarchy
        
        # Retrieval weights for different factors
        self.weights = {
            'importance': 0.3,
            'attention': 0.25,
            'strength': 0.2,
            'recency': 0.15,
            'relevance': 0.1
        }
    
    def retrieve_by_importance(self, memory_type: Optional[MemoryType] = None,
                              top_k: int = 10) -> List[MemoryItem]:
        """
        Retrieve most important memories.
        
        Args:
            memory_type: Filter by memory type (None = all types)
            top_k: Number of memories to retrieve
            
        Returns:
            List of top memories sorted by importance
        """
        memories = self._get_memories_by_type(memory_type)
        
        # Sort by importance
        sorted_memories = sorted(
            memories,
            key=lambda m: m.importance,
            reverse=True
        )
        
        return sorted_memories[:top_k]
    
    def retrieve_by_attention(self, memory_type: Optional[MemoryType] = None,
                             top_k: int = 10) -> List[MemoryItem]:
        """
        Retrieve memories with highest attention scores.
        
        Args:
            memory_type: Filter by memory type
            top_k: Number of memories to retrieve
            
        Returns:
            List of top memories sorted by attention
        """
        memories = self._get_memories_by_type(memory_type)
        
        sorted_memories = sorted(
            memories,
            key=lambda m: m.attention_score,
            reverse=True
        )
        
        return sorted_memories[:top_k]
    
    def retrieve_recent(self, memory_type: Optional[MemoryType] = None,
                       top_k: int = 10) -> List[MemoryItem]:
        """
        Retrieve most recently accessed memories.
        
        Args:
            memory_type: Filter by memory type
            top_k: Number of memories to retrieve
            
        Returns:
            List of recent memories
        """
        memories = self._get_memories_by_type(memory_type)
        
        sorted_memories = sorted(
            memories,
            key=lambda m: m.last_accessed,
            reverse=True
        )
        
        return sorted_memories[:top_k]
    
    def retrieve_by_strength(self, memory_type: Optional[MemoryType] = None,
                            top_k: int = 10) -> List[MemoryItem]:
        """
        Retrieve strongest memories (considering decay).
        
        Args:
            memory_type: Filter by memory type
            top_k: Number of memories to retrieve
            
        Returns:
            List of strongest memories
        """
        memories = self._get_memories_by_type(memory_type)
        
        sorted_memories = sorted(
            memories,
            key=lambda m: m.compute_strength(),
            reverse=True
        )
        
        return sorted_memories[:top_k]
    
    def retrieve_by_combined_score(self, memory_type: Optional[MemoryType] = None,
                                   top_k: int = 10,
                                   custom_weights: Optional[Dict[str, float]] = None) -> List[MemoryItem]:
        """
        Retrieve memories using combined scoring.
        
        Args:
            memory_type: Filter by memory type
            top_k: Number of memories to retrieve
            custom_weights: Custom weights for scoring factors
            
        Returns:
            List of top memories by combined score
        """
        memories = self._get_memories_by_type(memory_type)
        
        if not memories:
            return []
        
        weights = custom_weights if custom_weights else self.weights
        
        # Compute combined scores
        scored_memories = []
        for memory in memories:
            score = self._compute_combined_score(memory, weights)
            scored_memories.append((score, memory))
        
        # Sort by score
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        return [memory for _, memory in scored_memories[:top_k]]
    
    def retrieve_associated(self, memory_id: str, top_k: int = 10) -> List[MemoryItem]:
        """
        Retrieve memories associated with a given memory.
        
        Args:
            memory_id: ID of the anchor memory
            top_k: Number of associated memories to retrieve
            
        Returns:
            List of associated memories
        """
        # Find the anchor memory across all memory types
        anchor_memory = None
        all_memories = self._get_all_memories()
        
        for memory in all_memories:
            if memory.memory_id == memory_id:
                anchor_memory = memory
                break
        
        if not anchor_memory:
            return []
        
        # Get memories that are in anchor's associations
        associated = []
        for memory in all_memories:
            if memory.memory_id in anchor_memory.associations:
                associated.append(memory)
            elif anchor_memory.memory_id in memory.associations:
                # Bidirectional association
                associated.append(memory)
        
        # Sort by strength
        associated.sort(key=lambda m: m.compute_strength(), reverse=True)
        
        return associated[:top_k]
    
    def retrieve_by_semantic_similarity(self, query: str,
                                       memory_type: Optional[MemoryType] = None,
                                       top_k: int = 10) -> List[Tuple[float, MemoryItem]]:
        """
        Retrieve memories similar to query text.
        
        Note: This is a simple keyword-based similarity. For production,
        consider using embeddings (e.g., sentence-transformers).
        
        Args:
            query: Query string
            memory_type: Filter by memory type
            top_k: Number of memories to retrieve
            
        Returns:
            List of (similarity_score, memory) tuples
        """
        memories = self._get_memories_by_type(memory_type)
        
        if not memories:
            return []
        
        # Tokenize query
        query_tokens = set(self._tokenize(query.lower()))
        
        # Compute similarity scores
        scored_memories = []
        for memory in memories:
            content_str = str(memory.content).lower()
            content_tokens = set(self._tokenize(content_str))
            
            # Simple Jaccard similarity
            similarity = self._jaccard_similarity(query_tokens, content_tokens)
            
            # Weight by memory strength
            weighted_similarity = similarity * memory.compute_strength()
            
            if weighted_similarity > 0:
                scored_memories.append((weighted_similarity, memory))
        
        # Sort by similarity
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        return scored_memories[:top_k]
    
    def retrieve_context_relevant(self, context: Dict[str, any],
                                  memory_type: Optional[MemoryType] = None,
                                  top_k: int = 10) -> List[MemoryItem]:
        """
        Retrieve memories relevant to given context.
        
        Args:
            context: Context dictionary with keys like 'characters', 'location', 'theme', etc.
            memory_type: Filter by memory type
            top_k: Number of memories to retrieve
            
        Returns:
            List of context-relevant memories
        """
        memories = self._get_memories_by_type(memory_type)
        
        if not memories:
            return []
        
        scored_memories = []
        for memory in memories:
            relevance = self._compute_context_relevance(memory, context)
            if relevance > 0:
                scored_memories.append((relevance, memory))
        
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        return [memory for _, memory in scored_memories[:top_k]]
    
    def _compute_combined_score(self, memory: MemoryItem,
                               weights: Dict[str, float]) -> float:
        """Compute combined score for a memory."""
        score = 0.0
        
        # Importance component
        if 'importance' in weights:
            score += weights['importance'] * memory.importance
        
        # Attention component
        if 'attention' in weights:
            score += weights['attention'] * memory.attention_score
        
        # Strength (with decay) component
        if 'strength' in weights:
            score += weights['strength'] * memory.compute_strength()
        
        # Recency component (normalized)
        if 'recency' in weights:
            time_since_access = time.time() - memory.last_accessed
            recency_score = math.exp(-time_since_access / 3600)  # Decay over hours
            score += weights['recency'] * recency_score
        
        return score
    
    def _compute_context_relevance(self, memory: MemoryItem,
                                   context: Dict[str, any]) -> float:
        """Compute how relevant a memory is to the given context."""
        relevance = 0.0
        
        content_str = str(memory.content).lower()
        
        # Check each context element
        for key, value in context.items():
            if value is None:
                continue
            
            value_str = str(value).lower()
            
            # Simple containment check
            if value_str in content_str:
                relevance += 0.3
            
            # Check metadata
            if key in memory.metadata:
                if str(memory.metadata[key]).lower() == value_str:
                    relevance += 0.5
        
        # Boost by memory strength
        relevance *= memory.compute_strength()
        
        return relevance
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization by splitting on whitespace and punctuation."""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text)
        return [word for word in text.split() if len(word) > 2]
    
    def _jaccard_similarity(self, set1: Set[str], set2: Set[str]) -> float:
        """Compute Jaccard similarity between two sets."""
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def _get_memories_by_type(self, memory_type: Optional[MemoryType]) -> List[MemoryItem]:
        """Get all memories of a specific type or all types."""
        if memory_type is None:
            return self._get_all_memories()
        
        if memory_type == MemoryType.SENSORY:
            return self.hierarchy.sensory.get_all()
        elif memory_type == MemoryType.WORKING:
            return self.hierarchy.working.get_all()
        elif memory_type == MemoryType.EPISODIC:
            return self.hierarchy.episodic.get_all()
        elif memory_type == MemoryType.SEMANTIC:
            return self.hierarchy.semantic.get_all()
        elif memory_type == MemoryType.PROCEDURAL:
            return self.hierarchy.procedural.get_all()
        else:
            return []
    
    def _get_all_memories(self) -> List[MemoryItem]:
        """Get all memories from all memory types."""
        all_memories = []
        all_memories.extend(self.hierarchy.sensory.get_all())
        all_memories.extend(self.hierarchy.working.get_all())
        all_memories.extend(self.hierarchy.episodic.get_all())
        all_memories.extend(self.hierarchy.semantic.get_all())
        all_memories.extend(self.hierarchy.procedural.get_all())
        return all_memories


class AssociativeRetriever:
    """
    Advanced associative retrieval using spreading activation.
    """
    
    def __init__(self, memory_hierarchy: MemoryHierarchy):
        self.hierarchy = memory_hierarchy
        self.retriever = MemoryRetriever(memory_hierarchy)
        
        # Spreading activation parameters
        self.activation_decay = 0.8
        self.max_spread_depth = 3
    
    def spreading_activation(self, seed_memory_ids: List[str],
                            top_k: int = 10) -> List[Tuple[float, MemoryItem]]:
        """
        Retrieve memories using spreading activation from seed memories.
        
        Args:
            seed_memory_ids: Initial memory IDs to activate
            top_k: Number of memories to retrieve
            
        Returns:
            List of (activation, memory) tuples
        """
        # Initialize activation levels
        activations: Dict[str, float] = defaultdict(float)
        
        # Seed initial activations
        for memory_id in seed_memory_ids:
            activations[memory_id] = 1.0
        
        # Spread activation
        for depth in range(self.max_spread_depth):
            new_activations = activations.copy()
            
            for memory_id, activation in activations.items():
                if activation < 0.1:  # Skip weak activations
                    continue
                
                # Get associated memories
                associated = self.retriever.retrieve_associated(memory_id, top_k=20)
                
                # Spread activation to associated memories
                spread_amount = activation * self.activation_decay
                for assoc_memory in associated:
                    new_activations[assoc_memory.memory_id] += spread_amount / len(associated)
            
            activations = new_activations
        
        # Get memories with highest activation
        all_memories = self.retriever._get_all_memories()
        scored_memories = []
        
        for memory in all_memories:
            if memory.memory_id in activations:
                activation = activations[memory.memory_id]
                if memory.memory_id not in seed_memory_ids:  # Exclude seeds
                    scored_memories.append((activation, memory))
        
        # Sort by activation
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        
        return scored_memories[:top_k]
    
    def associative_chain(self, start_memory_id: str,
                         chain_length: int = 5) -> List[MemoryItem]:
        """
        Follow associative chains from a starting memory.
        
        Args:
            start_memory_id: Starting memory ID
            chain_length: Length of associative chain
            
        Returns:
            List of memories in the chain
        """
        chain = []
        current_id = start_memory_id
        visited = set()
        
        for _ in range(chain_length):
            if current_id in visited:
                break
            
            # Get associated memories
            associated = self.retriever.retrieve_associated(current_id, top_k=5)
            
            if not associated:
                break
            
            # Pick strongest unvisited association
            next_memory = None
            for memory in associated:
                if memory.memory_id not in visited:
                    next_memory = memory
                    break
            
            if next_memory is None:
                break
            
            chain.append(next_memory)
            visited.add(next_memory.memory_id)
            current_id = next_memory.memory_id
        
        return chain


class MemoryQuery:
    """
    High-level memory query interface combining multiple retrieval strategies.
    """
    
    def __init__(self, memory_hierarchy: MemoryHierarchy):
        self.hierarchy = memory_hierarchy
        self.retriever = MemoryRetriever(memory_hierarchy)
        self.associative = AssociativeRetriever(memory_hierarchy)
    
    def query(self, query_text: str,
             memory_type: Optional[MemoryType] = None,
             top_k: int = 10,
             use_associations: bool = False) -> List[MemoryItem]:
        """
        Query memories using text and optionally associations.
        
        Args:
            query_text: Query string
            memory_type: Filter by memory type
            top_k: Number of results
            use_associations: Whether to use spreading activation
            
        Returns:
            List of relevant memories
        """
        # Primary retrieval by semantic similarity
        similar_memories = self.retriever.retrieve_by_semantic_similarity(
            query_text, memory_type, top_k=top_k * 2
        )
        
        if not use_associations:
            return [memory for _, memory in similar_memories[:top_k]]
        
        # Use spreading activation from similar memories
        seed_ids = [memory.memory_id for _, memory in similar_memories[:3]]
        
        if not seed_ids:
            return []
        
        activated_memories = self.associative.spreading_activation(
            seed_ids, top_k=top_k
        )
        
        # Combine and deduplicate
        combined = {}
        for score, memory in similar_memories:
            combined[memory.memory_id] = (score * 1.5, memory)  # Boost direct matches
        
        for activation, memory in activated_memories:
            if memory.memory_id not in combined:
                combined[memory.memory_id] = (activation, memory)
            else:
                # Take max score
                existing_score = combined[memory.memory_id][0]
                combined[memory.memory_id] = (max(existing_score, activation), memory)
        
        # Sort by combined score
        result = sorted(combined.values(), key=lambda x: x[0], reverse=True)
        
        return [memory for _, memory in result[:top_k]]


__all__ = [
    'MemoryRetriever',
    'AssociativeRetriever',
    'MemoryQuery',
]
