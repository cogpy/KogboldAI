"""
Hierarchical Memory System for Cognitive Agents

This module implements a multi-level memory hierarchy inspired by human cognition:
- Sensory Memory: Immediate perception (1-3 story beats, very short-term)
- Working Memory: Active narrative elements (~7 items, short-term)
- Episodic Memory: Story events with timestamps (long-term)
- Semantic Memory: World knowledge and facts (long-term)
- Procedural Memory: Writing patterns and style rules (long-term)

The hierarchy includes attention-based retrieval, memory consolidation,
and forgetting curves based on narrative relevance.
"""

import time
import threading
import math
from typing import List, Dict, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory in the hierarchy."""
    SENSORY = "sensory"
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


@dataclass
class MemoryItem:
    """
    Individual memory item with metadata.
    """
    content: Any
    memory_type: MemoryType
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    importance: float = 0.5  # 0.0 to 1.0
    attention_score: float = 0.5  # 0.0 to 1.0
    decay_rate: float = 0.1  # How fast memory fades
    associations: Set[str] = field(default_factory=set)  # Associated memory IDs
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate unique ID for memory item."""
        if 'id' not in self.metadata:
            self.metadata['id'] = f"{self.memory_type.value}_{id(self)}"
    
    @property
    def memory_id(self) -> str:
        """Get the unique ID of this memory."""
        return self.metadata['id']
    
    def access(self):
        """Record an access to this memory."""
        self.last_accessed = time.time()
        self.access_count += 1
        # Accessing memory boosts attention temporarily
        self.attention_score = min(1.0, self.attention_score + 0.1)
    
    def compute_strength(self, current_time: Optional[float] = None) -> float:
        """
        Compute current memory strength based on decay.
        
        Uses exponential decay: strength = e^(-decay_rate * time_since_access)
        
        Args:
            current_time: Current time (default: now)
            
        Returns:
            Memory strength (0.0 to 1.0)
        """
        if current_time is None:
            current_time = time.time()
        
        time_since_access = current_time - self.last_accessed
        
        # Exponential decay formula
        decay_factor = math.exp(-self.decay_rate * time_since_access / 3600)  # Decay per hour
        
        # Strength is combination of importance, attention, and decay
        base_strength = (self.importance + self.attention_score) / 2
        strength = base_strength * decay_factor
        
        # Frequently accessed memories decay slower
        frequency_boost = min(0.3, self.access_count * 0.01)
        
        return min(1.0, strength + frequency_boost)
    
    def should_forget(self, threshold: float = 0.1) -> bool:
        """
        Determine if memory should be forgotten.
        
        Args:
            threshold: Strength threshold below which memory is forgotten
            
        Returns:
            True if memory should be forgotten
        """
        return self.compute_strength() < threshold
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert memory item to dictionary."""
        return {
            'id': self.memory_id,
            'content': str(self.content),
            'memory_type': self.memory_type.value,
            'created_at': self.created_at,
            'last_accessed': self.last_accessed,
            'access_count': self.access_count,
            'importance': self.importance,
            'attention_score': self.attention_score,
            'strength': self.compute_strength(),
            'associations': list(self.associations),
            'metadata': self.metadata
        }


class SensoryMemory:
    """
    Sensory memory: Immediate perception of current narrative context.
    
    Holds 1-3 most recent story beats. Very short-term (seconds to minutes).
    """
    
    def __init__(self, capacity: int = 3):
        self.capacity = capacity
        self.memories: List[MemoryItem] = []
        self._lock = threading.RLock()
    
    def add(self, content: Any, importance: float = 0.5, **metadata) -> MemoryItem:
        """
        Add new sensory memory.
        
        Args:
            content: Memory content
            importance: Importance score
            **metadata: Additional metadata
            
        Returns:
            Created memory item
        """
        with self._lock:
            memory = MemoryItem(
                content=content,
                memory_type=MemoryType.SENSORY,
                importance=importance,
                decay_rate=1.0,  # Fast decay for sensory memory
                metadata=metadata
            )
            
            self.memories.append(memory)
            
            # Keep only most recent items
            if len(self.memories) > self.capacity:
                self.memories = self.memories[-self.capacity:]
            
            return memory
    
    def get_all(self) -> List[MemoryItem]:
        """Get all sensory memories."""
        with self._lock:
            return self.memories.copy()
    
    def clear(self):
        """Clear all sensory memories."""
        with self._lock:
            self.memories.clear()


class WorkingMemory:
    """
    Working memory: Active narrative elements currently being manipulated.
    
    Holds ~7 items as per Miller's Law. Short-term (minutes to hours).
    """
    
    def __init__(self, capacity: int = 7):
        self.capacity = capacity
        self.memories: Dict[str, MemoryItem] = {}
        self._lock = threading.RLock()
    
    def add(self, content: Any, importance: float = 0.5, **metadata) -> MemoryItem:
        """
        Add item to working memory.
        
        Args:
            content: Memory content
            importance: Importance score
            **metadata: Additional metadata
            
        Returns:
            Created memory item
        """
        with self._lock:
            memory = MemoryItem(
                content=content,
                memory_type=MemoryType.WORKING,
                importance=importance,
                attention_score=0.7,  # Working memory items start with high attention
                decay_rate=0.3,  # Moderate decay
                metadata=metadata
            )
            
            self.memories[memory.memory_id] = memory
            
            # If over capacity, remove least important/attended item
            if len(self.memories) > self.capacity:
                self._evict_least_important()
            
            return memory
    
    def get(self, memory_id: str) -> Optional[MemoryItem]:
        """Get memory item by ID."""
        with self._lock:
            memory = self.memories.get(memory_id)
            if memory:
                memory.access()
            return memory
    
    def get_all(self) -> List[MemoryItem]:
        """Get all working memories sorted by attention."""
        with self._lock:
            return sorted(
                self.memories.values(),
                key=lambda m: m.attention_score,
                reverse=True
            )
    
    def remove(self, memory_id: str) -> bool:
        """Remove memory from working memory."""
        with self._lock:
            if memory_id in self.memories:
                del self.memories[memory_id]
                return True
            return False
    
    def _evict_least_important(self):
        """Evict least important memory item."""
        if not self.memories:
            return
        
        # Find item with lowest combined importance and attention
        least_important = min(
            self.memories.values(),
            key=lambda m: (m.importance + m.attention_score) / 2
        )
        
        del self.memories[least_important.memory_id]
        logger.debug(f"Evicted from working memory: {least_important.memory_id}")
    
    def update_attention(self, memory_id: str, attention_delta: float):
        """Update attention score for a memory."""
        with self._lock:
            if memory_id in self.memories:
                memory = self.memories[memory_id]
                memory.attention_score = max(0.0, min(1.0, memory.attention_score + attention_delta))
    
    def clear(self):
        """Clear working memory."""
        with self._lock:
            self.memories.clear()


class EpisodicMemory:
    """
    Episodic memory: Story events with temporal context.
    
    Stores narrative events with timestamps. Long-term storage.
    """
    
    def __init__(self):
        self.memories: Dict[str, MemoryItem] = {}
        self._temporal_index: List[tuple] = []  # (timestamp, memory_id)
        self._lock = threading.RLock()
    
    def add(self, content: Any, timestamp: float = None, importance: float = 0.5, **metadata) -> MemoryItem:
        """
        Add episodic memory with temporal context.
        
        Args:
            content: Memory content (story event)
            timestamp: Event timestamp (default: now)
            importance: Importance score
            **metadata: Additional metadata
            
        Returns:
            Created memory item
        """
        with self._lock:
            if timestamp is None:
                timestamp = time.time()
            
            metadata['timestamp'] = timestamp
            
            memory = MemoryItem(
                content=content,
                memory_type=MemoryType.EPISODIC,
                importance=importance,
                decay_rate=0.05,  # Slow decay for episodic memories
                metadata=metadata
            )
            
            self.memories[memory.memory_id] = memory
            self._temporal_index.append((timestamp, memory.memory_id))
            self._temporal_index.sort()  # Keep sorted by timestamp
            
            return memory
    
    def get(self, memory_id: str) -> Optional[MemoryItem]:
        """Get memory by ID."""
        with self._lock:
            memory = self.memories.get(memory_id)
            if memory:
                memory.access()
            return memory
    
    def get_by_time_range(self, start_time: float, end_time: float) -> List[MemoryItem]:
        """
        Get memories within a time range.
        
        Args:
            start_time: Start timestamp
            end_time: End timestamp
            
        Returns:
            List of memories in time range
        """
        with self._lock:
            result = []
            for timestamp, memory_id in self._temporal_index:
                if start_time <= timestamp <= end_time:
                    memory = self.memories.get(memory_id)
                    if memory:
                        memory.access()
                        result.append(memory)
            return result
    
    def get_recent(self, count: int = 10) -> List[MemoryItem]:
        """Get most recent episodic memories."""
        with self._lock:
            recent_ids = [mid for _, mid in self._temporal_index[-count:]]
            return [self.memories[mid] for mid in reversed(recent_ids) if mid in self.memories]
    
    def get_all(self) -> List[MemoryItem]:
        """Get all episodic memories sorted by time."""
        with self._lock:
            return [
                self.memories[mid] for _, mid in self._temporal_index
                if mid in self.memories
            ]
    
    def clear(self):
        """Clear episodic memory."""
        with self._lock:
            self.memories.clear()
            self._temporal_index.clear()


class SemanticMemory:
    """
    Semantic memory: World knowledge and facts.
    
    Stores factual knowledge about the story world. Long-term storage.
    """
    
    def __init__(self):
        self.memories: Dict[str, MemoryItem] = {}
        self._category_index: Dict[str, Set[str]] = {}  # category -> memory_ids
        self._lock = threading.RLock()
    
    def add(self, content: Any, category: str = "general", importance: float = 0.7, **metadata) -> MemoryItem:
        """
        Add semantic memory (fact/knowledge).
        
        Args:
            content: Memory content (fact or knowledge)
            category: Category for organization
            importance: Importance score
            **metadata: Additional metadata
            
        Returns:
            Created memory item
        """
        with self._lock:
            metadata['category'] = category
            
            memory = MemoryItem(
                content=content,
                memory_type=MemoryType.SEMANTIC,
                importance=importance,
                decay_rate=0.01,  # Very slow decay for semantic memories
                metadata=metadata
            )
            
            self.memories[memory.memory_id] = memory
            
            # Index by category
            if category not in self._category_index:
                self._category_index[category] = set()
            self._category_index[category].add(memory.memory_id)
            
            return memory
    
    def get(self, memory_id: str) -> Optional[MemoryItem]:
        """Get memory by ID."""
        with self._lock:
            memory = self.memories.get(memory_id)
            if memory:
                memory.access()
            return memory
    
    def get_by_category(self, category: str) -> List[MemoryItem]:
        """Get all memories in a category."""
        with self._lock:
            memory_ids = self._category_index.get(category, set())
            return [self.memories[mid] for mid in memory_ids if mid in self.memories]
    
    def get_all_categories(self) -> List[str]:
        """Get list of all categories."""
        with self._lock:
            return list(self._category_index.keys())
    
    def get_all(self) -> List[MemoryItem]:
        """Get all semantic memories."""
        with self._lock:
            return list(self.memories.values())
    
    def clear(self):
        """Clear semantic memory."""
        with self._lock:
            self.memories.clear()
            self._category_index.clear()


class ProceduralMemory:
    """
    Procedural memory: Writing patterns and style rules.
    
    Stores "how to" knowledge for narrative generation. Long-term storage.
    """
    
    def __init__(self):
        self.memories: Dict[str, MemoryItem] = {}
        self._pattern_index: Dict[str, Set[str]] = {}  # pattern_type -> memory_ids
        self._lock = threading.RLock()
    
    def add(self, content: Any, pattern_type: str = "general", importance: float = 0.6, **metadata) -> MemoryItem:
        """
        Add procedural memory (pattern/rule).
        
        Args:
            content: Memory content (pattern or rule)
            pattern_type: Type of pattern
            importance: Importance score
            **metadata: Additional metadata
            
        Returns:
            Created memory item
        """
        with self._lock:
            metadata['pattern_type'] = pattern_type
            
            memory = MemoryItem(
                content=content,
                memory_type=MemoryType.PROCEDURAL,
                importance=importance,
                decay_rate=0.02,  # Very slow decay for procedural memories
                metadata=metadata
            )
            
            self.memories[memory.memory_id] = memory
            
            # Index by pattern type
            if pattern_type not in self._pattern_index:
                self._pattern_index[pattern_type] = set()
            self._pattern_index[pattern_type].add(memory.memory_id)
            
            return memory
    
    def get(self, memory_id: str) -> Optional[MemoryItem]:
        """Get memory by ID."""
        with self._lock:
            memory = self.memories.get(memory_id)
            if memory:
                memory.access()
            return memory
    
    def get_by_pattern_type(self, pattern_type: str) -> List[MemoryItem]:
        """Get all memories of a pattern type."""
        with self._lock:
            memory_ids = self._pattern_index.get(pattern_type, set())
            return [self.memories[mid] for mid in memory_ids if mid in self.memories]
    
    def get_all(self) -> List[MemoryItem]:
        """Get all procedural memories."""
        with self._lock:
            return list(self.memories.values())
    
    def clear(self):
        """Clear procedural memory."""
        with self._lock:
            self.memories.clear()
            self._pattern_index.clear()


class MemoryHierarchy:
    """
    Complete hierarchical memory system integrating all memory types.
    """
    
    def __init__(self):
        self.sensory = SensoryMemory()
        self.working = WorkingMemory()
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.procedural = ProceduralMemory()
        
        self._consolidation_threshold = 0.7  # Threshold for promoting to long-term
        self._forgetting_threshold = 0.1  # Threshold for forgetting
        
        logger.info("Initialized memory hierarchy")
    
    def add_sensory(self, content: Any, **kwargs) -> MemoryItem:
        """Add to sensory memory."""
        return self.sensory.add(content, **kwargs)
    
    def add_working(self, content: Any, **kwargs) -> MemoryItem:
        """Add to working memory."""
        return self.working.add(content, **kwargs)
    
    def add_episodic(self, content: Any, **kwargs) -> MemoryItem:
        """Add to episodic memory."""
        return self.episodic.add(content, **kwargs)
    
    def add_semantic(self, content: Any, **kwargs) -> MemoryItem:
        """Add to semantic memory."""
        return self.semantic.add(content, **kwargs)
    
    def add_procedural(self, content: Any, **kwargs) -> MemoryItem:
        """Add to procedural memory."""
        return self.procedural.add(content, **kwargs)
    
    def get_memory_stats(self) -> Dict[str, int]:
        """Get statistics about memory usage."""
        return {
            'sensory': len(self.sensory.get_all()),
            'working': len(self.working.get_all()),
            'episodic': len(self.episodic.get_all()),
            'semantic': len(self.semantic.get_all()),
            'procedural': len(self.procedural.get_all()),
        }
    
    def get_all_memories(self) -> Dict[MemoryType, List[MemoryItem]]:
        """Get all memories organized by type."""
        return {
            MemoryType.SENSORY: self.sensory.get_all(),
            MemoryType.WORKING: self.working.get_all(),
            MemoryType.EPISODIC: self.episodic.get_all(),
            MemoryType.SEMANTIC: self.semantic.get_all(),
            MemoryType.PROCEDURAL: self.procedural.get_all(),
        }
    
    def clear_all(self):
        """Clear all memory systems."""
        self.sensory.clear()
        self.working.clear()
        self.episodic.clear()
        self.semantic.clear()
        self.procedural.clear()
        logger.info("Cleared all memory systems")
    
    def __repr__(self) -> str:
        stats = self.get_memory_stats()
        return f"MemoryHierarchy(sensory={stats['sensory']}, working={stats['working']}, " \
               f"episodic={stats['episodic']}, semantic={stats['semantic']}, " \
               f"procedural={stats['procedural']})"


__all__ = [
    'MemoryType',
    'MemoryItem',
    'SensoryMemory',
    'WorkingMemory',
    'EpisodicMemory',
    'SemanticMemory',
    'ProceduralMemory',
    'MemoryHierarchy',
]
