"""
Memory System Package for Cognitive Agents

Implements a complete hierarchical memory system with:
- Multiple memory types (sensory, working, episodic, semantic, procedural)
- Memory consolidation from short-term to long-term
- Associative retrieval with spreading activation
- Attention-based memory management
- Forgetting curves and decay mechanisms
"""

from .hierarchy import (
    MemoryType,
    MemoryItem,
    SensoryMemory,
    WorkingMemory,
    EpisodicMemory,
    SemanticMemory,
    ProceduralMemory,
    MemoryHierarchy,
)

from .consolidation import (
    ConsolidationRule,
    MemoryConsolidator,
    ForgettingMechanism,
    ConsolidationScheduler,
)

from .retrieval import (
    MemoryRetriever,
    AssociativeRetriever,
    MemoryQuery,
)

__all__ = [
    # Hierarchy
    'MemoryType',
    'MemoryItem',
    'SensoryMemory',
    'WorkingMemory',
    'EpisodicMemory',
    'SemanticMemory',
    'ProceduralMemory',
    'MemoryHierarchy',
    
    # Consolidation
    'ConsolidationRule',
    'MemoryConsolidator',
    'ForgettingMechanism',
    'ConsolidationScheduler',
    
    # Retrieval
    'MemoryRetriever',
    'AssociativeRetriever',
    'MemoryQuery',
]
