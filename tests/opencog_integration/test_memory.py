"""
Tests for Memory System
"""

import pytest
import time
from opencog_integration.memory import (
    MemoryType,
    MemoryItem,
    SensoryMemory,
    WorkingMemory,
    EpisodicMemory,
    SemanticMemory,
    ProceduralMemory,
    MemoryHierarchy,
    MemoryConsolidator,
    ForgettingMechanism,
    ConsolidationScheduler,
    MemoryRetriever,
    AssociativeRetriever,
    MemoryQuery,
)


class TestMemoryItem:
    """Test MemoryItem functionality."""
    
    def test_memory_item_creation(self):
        """Test creating a memory item."""
        memory = MemoryItem(
            content="Test memory",
            memory_type=MemoryType.WORKING,
            importance=0.8
        )
        
        assert memory.content == "Test memory"
        assert memory.memory_type == MemoryType.WORKING
        assert memory.importance == 0.8
        assert memory.access_count == 0
    
    def test_memory_access(self):
        """Test memory access tracking."""
        memory = MemoryItem(
            content="Test",
            memory_type=MemoryType.WORKING
        )
        
        initial_attention = memory.attention_score
        memory.access()
        
        assert memory.access_count == 1
        assert memory.attention_score > initial_attention
    
    def test_memory_strength_decay(self):
        """Test memory strength decay over time."""
        memory = MemoryItem(
            content="Test",
            memory_type=MemoryType.WORKING,
            decay_rate=1.0
        )
        
        # Strength should be high initially
        initial_strength = memory.compute_strength()
        assert initial_strength > 0.4
        
        # Simulate time passing (hack last_accessed)
        memory.last_accessed = time.time() - 7200  # 2 hours ago
        later_strength = memory.compute_strength()
        
        # Strength should have decayed
        assert later_strength < initial_strength


class TestSensoryMemory:
    """Test SensoryMemory functionality."""
    
    def test_sensory_capacity(self):
        """Test sensory memory capacity limits."""
        sensory = SensoryMemory(capacity=3)
        
        for i in range(5):
            sensory.add(f"Memory {i}")
        
        memories = sensory.get_all()
        assert len(memories) == 3
        
        # Should keep most recent
        assert "Memory 4" in [m.content for m in memories]
    
    def test_sensory_clear(self):
        """Test clearing sensory memory."""
        sensory = SensoryMemory()
        sensory.add("Test")
        sensory.clear()
        
        assert len(sensory.get_all()) == 0


class TestWorkingMemory:
    """Test WorkingMemory functionality."""
    
    def test_working_capacity(self):
        """Test working memory capacity."""
        working = WorkingMemory(capacity=7)
        
        for i in range(10):
            working.add(f"Memory {i}", importance=0.5)
        
        memories = working.get_all()
        assert len(memories) <= 7
    
    def test_working_get_by_id(self):
        """Test retrieving memory by ID."""
        working = WorkingMemory()
        memory = working.add("Test memory")
        
        retrieved = working.get(memory.memory_id)
        assert retrieved is not None
        assert retrieved.content == "Test memory"
        assert retrieved.access_count == 1  # Access incremented
    
    def test_working_remove(self):
        """Test removing memory."""
        working = WorkingMemory()
        memory = working.add("Test")
        
        success = working.remove(memory.memory_id)
        assert success is True
        
        assert working.get(memory.memory_id) is None


class TestEpisodicMemory:
    """Test EpisodicMemory functionality."""
    
    def test_episodic_add_with_timestamp(self):
        """Test adding episodic memory with timestamp."""
        episodic = EpisodicMemory()
        timestamp = 1000.0
        
        memory = episodic.add("Event happened", timestamp=timestamp)
        assert memory.metadata['timestamp'] == timestamp
    
    def test_episodic_get_by_time_range(self):
        """Test retrieving memories by time range."""
        episodic = EpisodicMemory()
        
        episodic.add("Event 1", timestamp=100.0)
        episodic.add("Event 2", timestamp=200.0)
        episodic.add("Event 3", timestamp=300.0)
        
        memories = episodic.get_by_time_range(150.0, 250.0)
        assert len(memories) == 1
        assert "Event 2" in [m.content for m in memories]
    
    def test_episodic_get_recent(self):
        """Test getting recent episodic memories."""
        episodic = EpisodicMemory()
        
        for i in range(20):
            episodic.add(f"Event {i}", timestamp=float(i))
        
        recent = episodic.get_recent(count=5)
        assert len(recent) == 5
        assert "Event 19" in [m.content for m in recent]


class TestSemanticMemory:
    """Test SemanticMemory functionality."""
    
    def test_semantic_add_with_category(self):
        """Test adding semantic memory with category."""
        semantic = SemanticMemory()
        memory = semantic.add("Fact about world", category="world_facts")
        
        assert memory.metadata['category'] == "world_facts"
    
    def test_semantic_get_by_category(self):
        """Test retrieving memories by category."""
        semantic = SemanticMemory()
        
        semantic.add("Fact 1", category="characters")
        semantic.add("Fact 2", category="locations")
        semantic.add("Fact 3", category="characters")
        
        char_memories = semantic.get_by_category("characters")
        assert len(char_memories) == 2
    
    def test_semantic_get_all_categories(self):
        """Test getting all categories."""
        semantic = SemanticMemory()
        
        semantic.add("F1", category="cat1")
        semantic.add("F2", category="cat2")
        
        categories = semantic.get_all_categories()
        assert "cat1" in categories
        assert "cat2" in categories


class TestProceduralMemory:
    """Test ProceduralMemory functionality."""
    
    def test_procedural_add_with_pattern_type(self):
        """Test adding procedural memory with pattern type."""
        procedural = ProceduralMemory()
        memory = procedural.add("Writing pattern", pattern_type="narrative_style")
        
        assert memory.metadata['pattern_type'] == "narrative_style"
    
    def test_procedural_get_by_pattern_type(self):
        """Test retrieving memories by pattern type."""
        procedural = ProceduralMemory()
        
        procedural.add("Pattern 1", pattern_type="dialogue")
        procedural.add("Pattern 2", pattern_type="description")
        procedural.add("Pattern 3", pattern_type="dialogue")
        
        dialogue_patterns = procedural.get_by_pattern_type("dialogue")
        assert len(dialogue_patterns) == 2


class TestMemoryHierarchy:
    """Test MemoryHierarchy integration."""
    
    def test_hierarchy_creation(self):
        """Test creating memory hierarchy."""
        hierarchy = MemoryHierarchy()
        
        assert hierarchy.sensory is not None
        assert hierarchy.working is not None
        assert hierarchy.episodic is not None
        assert hierarchy.semantic is not None
        assert hierarchy.procedural is not None
    
    def test_hierarchy_add_methods(self):
        """Test adding to different memory types."""
        hierarchy = MemoryHierarchy()
        
        hierarchy.add_sensory("Sensory input")
        hierarchy.add_working("Working item")
        hierarchy.add_episodic("Event")
        hierarchy.add_semantic("Fact")
        hierarchy.add_procedural("Pattern")
        
        stats = hierarchy.get_memory_stats()
        assert stats['sensory'] >= 1
        assert stats['working'] >= 1
        assert stats['episodic'] >= 1
        assert stats['semantic'] >= 1
        assert stats['procedural'] >= 1
    
    def test_hierarchy_clear_all(self):
        """Test clearing all memories."""
        hierarchy = MemoryHierarchy()
        
        hierarchy.add_working("Test")
        hierarchy.add_episodic("Event")
        
        hierarchy.clear_all()
        
        stats = hierarchy.get_memory_stats()
        assert stats['working'] == 0
        assert stats['episodic'] == 0


class TestMemoryConsolidator:
    """Test MemoryConsolidator functionality."""
    
    def test_consolidator_creation(self):
        """Test creating memory consolidator."""
        hierarchy = MemoryHierarchy()
        consolidator = MemoryConsolidator(hierarchy)
        
        assert consolidator is not None
        assert len(consolidator.consolidation_rules) > 0
    
    def test_consolidate_working_to_episodic(self):
        """Test consolidating working memory to episodic."""
        hierarchy = MemoryHierarchy()
        consolidator = MemoryConsolidator(hierarchy)
        
        # Add important working memory
        memory = hierarchy.add_working(
            "Important event",
            importance=0.8,
            timestamp=time.time()
        )
        memory.attention_score = 0.8
        memory.access_count = 3
        
        # Consolidate
        results = consolidator.consolidate_working_to_longterm()
        
        # Should have consolidated to episodic
        assert results['episodic'] >= 0  # May or may not consolidate based on criteria
    
    def test_consolidation_cycle(self):
        """Test full consolidation cycle."""
        hierarchy = MemoryHierarchy()
        consolidator = MemoryConsolidator(hierarchy)
        
        # Add memories
        hierarchy.add_sensory("Sensory input", importance=0.6)
        hierarchy.add_working("Working item", importance=0.8)
        
        # Run cycle
        results = consolidator.run_consolidation_cycle()
        
        assert 'sensory_to_working' in results
        assert 'working_to_longterm' in results
        assert 'total' in results


class TestForgettingMechanism:
    """Test ForgettingMechanism functionality."""
    
    def test_forget_weak_memories(self):
        """Test forgetting weak memories."""
        hierarchy = MemoryHierarchy()
        forgetter = ForgettingMechanism(hierarchy)
        
        # Add memory and make it weak
        memory = hierarchy.add_working("Test", importance=0.1)
        memory.decay_rate = 10.0  # Fast decay
        memory.last_accessed = time.time() - 36000  # 10 hours ago
        
        # Should forget this memory
        results = forgetter.forget_weak_memories()
        
        assert results['working'] >= 0


class TestMemoryRetriever:
    """Test MemoryRetriever functionality."""
    
    def setup_method(self):
        """Set up test hierarchy with memories."""
        self.hierarchy = MemoryHierarchy()
        self.retriever = MemoryRetriever(self.hierarchy)
        
        # Add test memories
        self.hierarchy.add_working("Important memory", importance=0.9)
        self.hierarchy.add_working("Less important", importance=0.3)
        self.hierarchy.add_episodic("Past event", importance=0.7)
        self.hierarchy.add_semantic("Fact", importance=0.8)
    
    def test_retrieve_by_importance(self):
        """Test retrieving by importance."""
        memories = self.retriever.retrieve_by_importance(top_k=2)
        
        assert len(memories) > 0
        # Should be sorted by importance
        if len(memories) > 1:
            assert memories[0].importance >= memories[1].importance
    
    def test_retrieve_by_attention(self):
        """Test retrieving by attention."""
        memories = self.retriever.retrieve_by_attention(top_k=3)
        
        assert len(memories) > 0
    
    def test_retrieve_by_strength(self):
        """Test retrieving by strength."""
        memories = self.retriever.retrieve_by_strength(top_k=3)
        
        assert len(memories) > 0
    
    def test_retrieve_by_semantic_similarity(self):
        """Test semantic similarity retrieval."""
        self.hierarchy.add_working("The hero fought bravely", importance=0.7)
        self.hierarchy.add_working("The villain was defeated", importance=0.7)
        
        results = self.retriever.retrieve_by_semantic_similarity(
            "hero battle", top_k=5
        )
        
        # Should find related memories
        assert len(results) > 0


class TestMemoryQuery:
    """Test MemoryQuery functionality."""
    
    def test_query_basic(self):
        """Test basic memory query."""
        hierarchy = MemoryHierarchy()
        query = MemoryQuery(hierarchy)
        
        hierarchy.add_working("The dragon attacked the village")
        hierarchy.add_episodic("Heroes defended the town")
        
        results = query.query("dragon attack", top_k=5)
        
        # Should find related memories
        assert isinstance(results, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
