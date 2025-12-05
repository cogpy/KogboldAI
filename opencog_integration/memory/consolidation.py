"""
Memory Consolidation System

Handles the transfer of memories from short-term (sensory/working) to 
long-term storage (episodic/semantic/procedural) based on importance,
attention, and access patterns.

Implements sleep-like consolidation phases and intelligent memory organization.
"""

import time
import threading
import logging
from typing import List, Dict, Optional, Set
from dataclasses import dataclass

from .hierarchy import (
    MemoryHierarchy, MemoryItem, MemoryType,
    SensoryMemory, WorkingMemory, EpisodicMemory,
    SemanticMemory, ProceduralMemory
)

logger = logging.getLogger(__name__)


@dataclass
class ConsolidationRule:
    """
    Rule for memory consolidation decisions.
    """
    name: str
    source_type: MemoryType
    target_type: MemoryType
    min_importance: float = 0.5
    min_attention: float = 0.5
    min_access_count: int = 2
    min_strength: float = 0.6
    
    def should_consolidate(self, memory: MemoryItem) -> bool:
        """
        Check if memory meets consolidation criteria.
        
        Args:
            memory: Memory item to check
            
        Returns:
            True if memory should be consolidated
        """
        if memory.memory_type != self.source_type:
            return False
        
        if memory.importance < self.min_importance:
            return False
        
        if memory.attention_score < self.min_attention:
            return False
        
        if memory.access_count < self.min_access_count:
            return False
        
        if memory.compute_strength() < self.min_strength:
            return False
        
        return True


class MemoryConsolidator:
    """
    Manages memory consolidation from short-term to long-term storage.
    """
    
    def __init__(self, memory_hierarchy: MemoryHierarchy):
        self.hierarchy = memory_hierarchy
        self.consolidation_rules: List[ConsolidationRule] = []
        self._initialize_default_rules()
        self._lock = threading.RLock()
        
        # Consolidation statistics
        self.stats = {
            'total_consolidations': 0,
            'sensory_to_working': 0,
            'working_to_episodic': 0,
            'working_to_semantic': 0,
            'working_to_procedural': 0,
        }
    
    def _initialize_default_rules(self):
        """Initialize default consolidation rules."""
        
        # Sensory -> Working memory
        self.consolidation_rules.append(ConsolidationRule(
            name="sensory_to_working",
            source_type=MemoryType.SENSORY,
            target_type=MemoryType.WORKING,
            min_importance=0.4,
            min_attention=0.5,
            min_access_count=1,
            min_strength=0.5
        ))
        
        # Working -> Episodic memory (events)
        self.consolidation_rules.append(ConsolidationRule(
            name="working_to_episodic",
            source_type=MemoryType.WORKING,
            target_type=MemoryType.EPISODIC,
            min_importance=0.6,
            min_attention=0.6,
            min_access_count=2,
            min_strength=0.65
        ))
        
        # Working -> Semantic memory (facts)
        self.consolidation_rules.append(ConsolidationRule(
            name="working_to_semantic",
            source_type=MemoryType.WORKING,
            target_type=MemoryType.SEMANTIC,
            min_importance=0.7,
            min_attention=0.5,
            min_access_count=3,
            min_strength=0.7
        ))
        
        # Working -> Procedural memory (patterns)
        self.consolidation_rules.append(ConsolidationRule(
            name="working_to_procedural",
            source_type=MemoryType.WORKING,
            target_type=MemoryType.PROCEDURAL,
            min_importance=0.7,
            min_attention=0.6,
            min_access_count=4,
            min_strength=0.75
        ))
    
    def consolidate_sensory_to_working(self) -> int:
        """
        Consolidate important sensory memories to working memory.
        
        Returns:
            Number of memories consolidated
        """
        with self._lock:
            count = 0
            sensory_memories = self.hierarchy.sensory.get_all()
            
            for memory in sensory_memories:
                # Find matching rule
                for rule in self.consolidation_rules:
                    if rule.target_type == MemoryType.WORKING and rule.should_consolidate(memory):
                        # Promote to working memory
                        self.hierarchy.add_working(
                            content=memory.content,
                            importance=memory.importance,
                            **memory.metadata
                        )
                        count += 1
                        self.stats['sensory_to_working'] += 1
                        logger.debug(f"Consolidated sensory memory to working: {memory.memory_id}")
                        break
            
            return count
    
    def consolidate_working_to_longterm(self) -> Dict[str, int]:
        """
        Consolidate working memories to appropriate long-term storage.
        
        Returns:
            Dictionary of consolidation counts by target type
        """
        with self._lock:
            counts = {
                'episodic': 0,
                'semantic': 0,
                'procedural': 0
            }
            
            working_memories = self.hierarchy.working.get_all()
            
            for memory in working_memories:
                consolidated = False
                
                # Try each consolidation rule
                for rule in self.consolidation_rules:
                    if rule.source_type != MemoryType.WORKING:
                        continue
                    
                    if not rule.should_consolidate(memory):
                        continue
                    
                    # Determine target based on content type
                    target_type = self._determine_target_type(memory, rule.target_type)
                    
                    if target_type == MemoryType.EPISODIC:
                        # Events go to episodic memory
                        metadata_copy = memory.metadata.copy()
                        timestamp = metadata_copy.pop('timestamp', time.time())
                        self.hierarchy.add_episodic(
                            content=memory.content,
                            timestamp=timestamp,
                            importance=memory.importance,
                            **metadata_copy
                        )
                        counts['episodic'] += 1
                        self.stats['working_to_episodic'] += 1
                        consolidated = True
                    
                    elif target_type == MemoryType.SEMANTIC:
                        # Facts go to semantic memory
                        metadata_copy = memory.metadata.copy()
                        category = metadata_copy.pop('category', 'general')
                        self.hierarchy.add_semantic(
                            content=memory.content,
                            category=category,
                            importance=memory.importance,
                            **metadata_copy
                        )
                        counts['semantic'] += 1
                        self.stats['working_to_semantic'] += 1
                        consolidated = True
                    
                    elif target_type == MemoryType.PROCEDURAL:
                        # Patterns go to procedural memory
                        metadata_copy = memory.metadata.copy()
                        pattern_type = metadata_copy.pop('pattern_type', 'general')
                        self.hierarchy.add_procedural(
                            content=memory.content,
                            pattern_type=pattern_type,
                            importance=memory.importance,
                            **metadata_copy
                        )
                        counts['procedural'] += 1
                        self.stats['working_to_procedural'] += 1
                        consolidated = True
                    
                    if consolidated:
                        logger.debug(f"Consolidated working memory to {target_type.value}: {memory.memory_id}")
                        # Note: We don't remove from working memory yet - 
                        # it will naturally decay or be evicted
                        break
            
            return counts
    
    def _determine_target_type(self, memory: MemoryItem, suggested_type: MemoryType) -> MemoryType:
        """
        Determine the appropriate target memory type based on content.
        
        Args:
            memory: Memory item to consolidate
            suggested_type: Suggested target type from rule
            
        Returns:
            Target memory type
        """
        # Check metadata hints
        if 'memory_target' in memory.metadata:
            target_str = memory.metadata['memory_target']
            try:
                return MemoryType[target_str.upper()]
            except KeyError:
                pass
        
        # Check content type hints
        content_str = str(memory.content).lower()
        
        # Event indicators -> Episodic
        if any(word in content_str for word in ['happened', 'occurred', 'event', 'action', 'did']):
            return MemoryType.EPISODIC
        
        # Fact indicators -> Semantic
        if any(word in content_str for word in ['is', 'are', 'fact', 'knowledge', 'information']):
            return MemoryType.SEMANTIC
        
        # Pattern indicators -> Procedural
        if any(word in content_str for word in ['how to', 'pattern', 'rule', 'style', 'technique']):
            return MemoryType.PROCEDURAL
        
        # Default to suggested type
        return suggested_type
    
    def run_consolidation_cycle(self) -> Dict[str, any]:
        """
        Run a full consolidation cycle.
        
        Returns:
            Dictionary with consolidation results
        """
        with self._lock:
            results = {
                'sensory_to_working': 0,
                'working_to_longterm': {},
                'total': 0
            }
            
            # Phase 1: Sensory -> Working
            results['sensory_to_working'] = self.consolidate_sensory_to_working()
            
            # Phase 2: Working -> Long-term
            results['working_to_longterm'] = self.consolidate_working_to_longterm()
            
            # Calculate total
            results['total'] = results['sensory_to_working']
            for count in results['working_to_longterm'].values():
                results['total'] += count
            
            self.stats['total_consolidations'] += results['total']
            
            logger.info(f"Consolidation cycle complete: {results['total']} memories consolidated")
            
            return results
    
    def get_consolidation_stats(self) -> Dict[str, int]:
        """Get consolidation statistics."""
        with self._lock:
            return self.stats.copy()
    
    def add_consolidation_rule(self, rule: ConsolidationRule):
        """Add a custom consolidation rule."""
        with self._lock:
            self.consolidation_rules.append(rule)
            logger.info(f"Added consolidation rule: {rule.name}")
    
    def remove_consolidation_rule(self, rule_name: str) -> bool:
        """Remove a consolidation rule by name."""
        with self._lock:
            original_length = len(self.consolidation_rules)
            self.consolidation_rules = [
                rule for rule in self.consolidation_rules
                if rule.name != rule_name
            ]
            removed = len(self.consolidation_rules) < original_length
            if removed:
                logger.info(f"Removed consolidation rule: {rule_name}")
            return removed


class ForgettingMechanism:
    """
    Implements memory forgetting based on decay and relevance.
    """
    
    def __init__(self, memory_hierarchy: MemoryHierarchy):
        self.hierarchy = memory_hierarchy
        self.forgetting_threshold = 0.1
        self._lock = threading.RLock()
        
        # Forgetting statistics
        self.stats = {
            'total_forgotten': 0,
            'working_forgotten': 0,
            'episodic_forgotten': 0,
            'semantic_forgotten': 0,
            'procedural_forgotten': 0,
        }
    
    def forget_weak_memories(self) -> Dict[str, int]:
        """
        Remove weak memories that have decayed below threshold.
        
        Returns:
            Dictionary of forgetting counts by memory type
        """
        with self._lock:
            counts = {
                'working': 0,
                'episodic': 0,
                'semantic': 0,
                'procedural': 0
            }
            
            # Forget from working memory
            working_memories = self.hierarchy.working.get_all()
            for memory in working_memories:
                if memory.should_forget(self.forgetting_threshold):
                    self.hierarchy.working.remove(memory.memory_id)
                    counts['working'] += 1
                    self.stats['working_forgotten'] += 1
            
            # Note: We typically don't forget from episodic, semantic, or procedural
            # unless explicitly requested, as these are long-term stores
            
            self.stats['total_forgotten'] += sum(counts.values())
            
            if sum(counts.values()) > 0:
                logger.info(f"Forgot {sum(counts.values())} weak memories")
            
            return counts
    
    def get_forgetting_stats(self) -> Dict[str, int]:
        """Get forgetting statistics."""
        with self._lock:
            return self.stats.copy()


class ConsolidationScheduler:
    """
    Schedules and manages periodic memory consolidation.
    """
    
    def __init__(self, memory_hierarchy: MemoryHierarchy):
        self.hierarchy = memory_hierarchy
        self.consolidator = MemoryConsolidator(memory_hierarchy)
        self.forgetter = ForgettingMechanism(memory_hierarchy)
        
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._interval = 60.0  # Consolidation interval in seconds
        
    def start(self, interval: float = 60.0):
        """
        Start periodic consolidation.
        
        Args:
            interval: Consolidation interval in seconds
        """
        if self._running:
            logger.warning("Consolidation scheduler already running")
            return
        
        self._interval = interval
        self._running = True
        self._thread = threading.Thread(target=self._consolidation_loop, daemon=True)
        self._thread.start()
        logger.info(f"Started consolidation scheduler (interval={interval}s)")
    
    def stop(self):
        """Stop periodic consolidation."""
        if not self._running:
            return
        
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("Stopped consolidation scheduler")
    
    def _consolidation_loop(self):
        """Main consolidation loop."""
        while self._running:
            try:
                # Run consolidation cycle
                self.consolidator.run_consolidation_cycle()
                
                # Run forgetting mechanism
                self.forgetter.forget_weak_memories()
                
            except Exception as e:
                logger.error(f"Error in consolidation loop: {e}", exc_info=True)
            
            # Sleep until next cycle
            time.sleep(self._interval)
    
    def run_now(self) -> Dict[str, any]:
        """
        Run consolidation immediately (manual trigger).
        
        Returns:
            Consolidation results
        """
        results = self.consolidator.run_consolidation_cycle()
        forgetting_results = self.forgetter.forget_weak_memories()
        results['forgotten'] = forgetting_results
        return results
    
    def get_stats(self) -> Dict[str, any]:
        """Get all consolidation and forgetting statistics."""
        return {
            'consolidation': self.consolidator.get_consolidation_stats(),
            'forgetting': self.forgetter.get_forgetting_stats(),
            'memory': self.hierarchy.get_memory_stats()
        }


__all__ = [
    'ConsolidationRule',
    'MemoryConsolidator',
    'ForgettingMechanism',
    'ConsolidationScheduler',
]
