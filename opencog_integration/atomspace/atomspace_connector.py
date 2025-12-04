"""
AtomSpace Connector for KoboldAI

This module provides the connection layer between KoboldAI's narrative state
and the OpenCog AtomSpace knowledge representation system. It handles:
- Bidirectional synchronization between KoboldAI world state and AtomSpace
- Conversion of narrative elements to/from atoms
- Query interface for pattern matching and inference
- Persistence of AtomSpace state

Note: This is a simulated AtomSpace implementation until full OpenCog
integration is available. It provides the same interface but uses an
in-memory graph structure.
"""

import threading
import json
from typing import Dict, List, Optional, Set, Any, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import logging

from .atom_types import (
    Atom, ConceptNode, PredicateNode, EvaluationLink,
    InheritanceLink, TemporalLink, CausalLink, Link,
    AtomType, NarrativeConceptType, PredicateType,
    AtomFactory, initialize_narrative_ontology
)

logger = logging.getLogger(__name__)


@dataclass
class QueryPattern:
    """Pattern for querying the AtomSpace."""
    
    atom_type: Optional[AtomType] = None
    name_pattern: Optional[str] = None
    concept_type: Optional[NarrativeConceptType] = None
    predicate_type: Optional[PredicateType] = None
    min_truth_value: float = 0.0
    min_confidence: float = 0.0
    min_attention: float = 0.0
    metadata_filters: Dict[str, Any] = field(default_factory=dict)
    
    def matches(self, atom: Atom) -> bool:
        """Check if an atom matches this pattern."""
        
        # Check atom type
        if self.atom_type and atom.atom_type != self.atom_type:
            return False
        
        # Check name pattern (simple substring match)
        if self.name_pattern and self.name_pattern not in atom.name:
            return False
        
        # Check concept type for ConceptNodes
        if self.concept_type and isinstance(atom, ConceptNode):
            if atom.concept_type != self.concept_type:
                return False
        
        # Check predicate type for PredicateNodes
        if self.predicate_type and isinstance(atom, PredicateNode):
            if atom.predicate_type != self.predicate_type:
                return False
        
        # Check truth value threshold
        if atom.truth_value < self.min_truth_value:
            return False
        
        # Check confidence threshold
        if atom.confidence < self.min_confidence:
            return False
        
        # Check attention value threshold
        if atom.attention_value < self.min_attention:
            return False
        
        # Check metadata filters
        for key, value in self.metadata_filters.items():
            if atom.metadata.get(key) != value:
                return False
        
        return True


class AtomSpace:
    """
    Simulated AtomSpace implementation providing OpenCog-like functionality.
    
    This implementation uses an in-memory graph structure and provides:
    - Storage and retrieval of atoms
    - Pattern matching and queries
    - Attention allocation and importance tracking
    - Link navigation and relationship traversal
    """
    
    def __init__(self):
        self._atoms: Dict[str, Atom] = {}
        self._links_by_type: Dict[AtomType, List[Link]] = defaultdict(list)
        self._incoming_sets: Dict[str, Set[str]] = defaultdict(set)  # Atoms that link to this atom
        self._outgoing_sets: Dict[str, Set[str]] = defaultdict(set)  # Atoms this atom links to
        self._index_by_type: Dict[NarrativeConceptType, Set[str]] = defaultdict(set)
        self._lock = threading.RLock()
        
        # Initialize with narrative ontology
        self._initialize_ontology()
    
    def _initialize_ontology(self):
        """Initialize the AtomSpace with narrative ontology."""
        try:
            ontology_links = initialize_narrative_ontology()
            for link in ontology_links:
                self.add_atom(link)
            logger.info(f"Initialized AtomSpace with {len(ontology_links)} ontology links")
        except Exception as e:
            logger.error(f"Error initializing ontology: {e}")
    
    def add_atom(self, atom: Atom) -> Atom:
        """
        Add an atom to the AtomSpace.
        
        Args:
            atom: The atom to add
            
        Returns:
            The atom (possibly merged with existing atom)
        """
        with self._lock:
            atom_id = self._get_atom_id(atom)
            
            # If atom already exists, merge truth values
            if atom_id in self._atoms:
                existing = self._atoms[atom_id]
                existing.truth_value = max(existing.truth_value, atom.truth_value)
                existing.confidence = max(existing.confidence, atom.confidence)
                existing.attention_value = max(existing.attention_value, atom.attention_value)
                existing.metadata.update(atom.metadata)
                return existing
            
            # Add new atom
            self._atoms[atom_id] = atom
            
            # Index by type
            if isinstance(atom, ConceptNode):
                self._index_by_type[atom.concept_type].add(atom_id)
            
            # Handle links
            if isinstance(atom, Link):
                self._links_by_type[atom.atom_type].append(atom)
                
                # Update incoming/outgoing sets
                for outgoing_atom in atom.outgoing:
                    outgoing_id = self._get_atom_id(outgoing_atom)
                    self._outgoing_sets[atom_id].add(outgoing_id)
                    self._incoming_sets[outgoing_id].add(atom_id)
                    
                    # Ensure outgoing atoms are in AtomSpace
                    if outgoing_id not in self._atoms:
                        self.add_atom(outgoing_atom)
            
            return atom
    
    def get_atom(self, name: str, atom_type: AtomType = None) -> Optional[Atom]:
        """
        Retrieve an atom by name and optionally type.
        
        Args:
            name: The name of the atom
            atom_type: Optional atom type filter
            
        Returns:
            The atom if found, None otherwise
        """
        with self._lock:
            for atom_id, atom in self._atoms.items():
                if atom.name == name:
                    if atom_type is None or atom.atom_type == atom_type:
                        return atom
            return None
    
    def remove_atom(self, atom: Atom) -> bool:
        """
        Remove an atom from the AtomSpace.
        
        Args:
            atom: The atom to remove
            
        Returns:
            True if removed, False if not found
        """
        with self._lock:
            atom_id = self._get_atom_id(atom)
            
            if atom_id not in self._atoms:
                return False
            
            # Remove from indexes
            if isinstance(atom, ConceptNode):
                self._index_by_type[atom.concept_type].discard(atom_id)
            
            if isinstance(atom, Link):
                self._links_by_type[atom.atom_type] = [
                    link for link in self._links_by_type[atom.atom_type]
                    if self._get_atom_id(link) != atom_id
                ]
            
            # Remove incoming/outgoing references
            for outgoing_id in self._outgoing_sets[atom_id]:
                self._incoming_sets[outgoing_id].discard(atom_id)
            
            for incoming_id in self._incoming_sets[atom_id]:
                self._outgoing_sets[incoming_id].discard(atom_id)
            
            del self._atoms[atom_id]
            del self._outgoing_sets[atom_id]
            del self._incoming_sets[atom_id]
            
            return True
    
    def query(self, pattern: QueryPattern) -> List[Atom]:
        """
        Query the AtomSpace using a pattern.
        
        Args:
            pattern: The query pattern
            
        Returns:
            List of matching atoms
        """
        with self._lock:
            results = []
            
            # Optimize by using type index if available
            if pattern.concept_type:
                atom_ids = self._index_by_type.get(pattern.concept_type, set())
                candidates = [self._atoms[aid] for aid in atom_ids]
            else:
                candidates = self._atoms.values()
            
            # Filter by pattern
            for atom in candidates:
                if pattern.matches(atom):
                    results.append(atom)
            
            return results
    
    def get_incoming(self, atom: Atom) -> List[Link]:
        """Get all links that include this atom in their outgoing set."""
        with self._lock:
            atom_id = self._get_atom_id(atom)
            incoming_ids = self._incoming_sets.get(atom_id, set())
            return [self._atoms[iid] for iid in incoming_ids if isinstance(self._atoms[iid], Link)]
    
    def get_outgoing(self, link: Link) -> List[Atom]:
        """Get the atoms in this link's outgoing set."""
        return link.outgoing if isinstance(link, Link) else []
    
    def get_all_atoms(self) -> List[Atom]:
        """Get all atoms in the AtomSpace."""
        with self._lock:
            return list(self._atoms.values())
    
    def get_atom_count(self) -> int:
        """Get the total number of atoms."""
        with self._lock:
            return len(self._atoms)
    
    def clear(self):
        """Clear all atoms from the AtomSpace."""
        with self._lock:
            self._atoms.clear()
            self._links_by_type.clear()
            self._incoming_sets.clear()
            self._outgoing_sets.clear()
            self._index_by_type.clear()
            self._initialize_ontology()
    
    def save_to_file(self, filepath: str):
        """Save AtomSpace to JSON file."""
        with self._lock:
            data = {
                'atoms': [atom.to_dict() for atom in self._atoms.values()]
            }
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved AtomSpace with {len(self._atoms)} atoms to {filepath}")
    
    def load_from_file(self, filepath: str):
        """Load AtomSpace from JSON file."""
        # Note: This is a simplified version - full implementation would need
        # to reconstruct atom objects with proper types
        with open(filepath, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded AtomSpace data from {filepath}")
        # TODO: Implement full deserialization
    
    def _get_atom_id(self, atom: Atom) -> str:
        """Generate a unique ID for an atom."""
        return f"{atom.atom_type.value}:{atom.name}"
    
    def __repr__(self) -> str:
        return f"AtomSpace(atoms={len(self._atoms)})"


class AtomSpaceSync:
    """
    Handles bidirectional synchronization between KoboldAI world state
    and the AtomSpace knowledge representation.
    """
    
    def __init__(self, atomspace: AtomSpace):
        self.atomspace = atomspace
        self.sync_callbacks: List[Callable] = []
        self._lock = threading.RLock()
    
    def sync_from_kobold(self, world_state: Dict[str, Any]) -> int:
        """
        Synchronize KoboldAI world state into AtomSpace.
        
        Args:
            world_state: Dictionary containing world builder state
            
        Returns:
            Number of atoms added/updated
        """
        with self._lock:
            atoms_added = 0
            
            # Sync characters
            if 'characters' in world_state:
                for char_data in world_state['characters']:
                    character = AtomFactory.create_character(
                        char_data['name'],
                        traits=char_data.get('traits', {})
                    )
                    self.atomspace.add_atom(character)
                    atoms_added += 1
            
            # Sync locations
            if 'locations' in world_state:
                for loc_data in world_state['locations']:
                    location = AtomFactory.create_location(
                        loc_data['name'],
                        description=loc_data.get('description', '')
                    )
                    self.atomspace.add_atom(location)
                    atoms_added += 1
            
            # Sync events
            if 'events' in world_state:
                events_nodes = []
                for event_data in world_state['events']:
                    event = AtomFactory.create_event(
                        event_data['description'],
                        timestamp=event_data.get('timestamp', 0.0)
                    )
                    self.atomspace.add_atom(event)
                    events_nodes.append(event)
                    atoms_added += 1
                
                # Create causal chain if events are sequential
                if len(events_nodes) > 1:
                    causal_links = AtomFactory.create_causal_chain(events_nodes)
                    for link in causal_links:
                        self.atomspace.add_atom(link)
                        atoms_added += 1
            
            # Sync relationships
            if 'relationships' in world_state:
                for rel_data in world_state['relationships']:
                    # Find subject and object atoms
                    subject = self.atomspace.get_atom(rel_data['subject'])
                    obj = self.atomspace.get_atom(rel_data['object'])
                    
                    if subject and obj and isinstance(subject, ConceptNode) and isinstance(obj, ConceptNode):
                        predicate_type = PredicateType[rel_data['type']]
                        relationship = AtomFactory.create_relationship(
                            subject, predicate_type, obj,
                            strength=rel_data.get('strength', 1.0)
                        )
                        self.atomspace.add_atom(relationship)
                        atoms_added += 1
            
            logger.info(f"Synced {atoms_added} atoms from KoboldAI to AtomSpace")
            
            # Trigger callbacks
            for callback in self.sync_callbacks:
                try:
                    callback('kobold_to_atomspace', atoms_added)
                except Exception as e:
                    logger.error(f"Error in sync callback: {e}")
            
            return atoms_added
    
    def sync_to_kobold(self) -> Dict[str, Any]:
        """
        Extract world state from AtomSpace for KoboldAI.
        
        Returns:
            Dictionary containing world state
        """
        with self._lock:
            world_state = {
                'characters': [],
                'locations': [],
                'events': [],
                'relationships': []
            }
            
            # Extract characters
            character_pattern = QueryPattern(concept_type=NarrativeConceptType.CHARACTER)
            characters = self.atomspace.query(character_pattern)
            for char in characters:
                if isinstance(char, ConceptNode):
                    world_state['characters'].append({
                        'name': char.name,
                        'traits': char.properties,
                        'truth_value': char.truth_value
                    })
            
            # Extract locations
            location_pattern = QueryPattern(concept_type=NarrativeConceptType.LOCATION)
            locations = self.atomspace.query(location_pattern)
            for loc in locations:
                if isinstance(loc, ConceptNode):
                    world_state['locations'].append({
                        'name': loc.name,
                        'description': loc.properties.get('description', ''),
                        'truth_value': loc.truth_value
                    })
            
            # Extract events
            event_pattern = QueryPattern(concept_type=NarrativeConceptType.EVENT)
            events = self.atomspace.query(event_pattern)
            for event in events:
                if isinstance(event, ConceptNode):
                    world_state['events'].append({
                        'description': event.name,
                        'timestamp': event.properties.get('timestamp', 0.0),
                        'truth_value': event.truth_value
                    })
            
            # Extract relationships
            all_atoms = self.atomspace.get_all_atoms()
            for atom in all_atoms:
                if isinstance(atom, EvaluationLink):
                    predicate = atom.predicate
                    args = atom.arguments
                    if len(args) >= 2:
                        world_state['relationships'].append({
                            'subject': args[0].name,
                            'type': predicate.predicate_type.name,
                            'object': args[1].name,
                            'strength': atom.truth_value
                        })
            
            logger.info(f"Extracted world state from AtomSpace: "
                       f"{len(world_state['characters'])} characters, "
                       f"{len(world_state['locations'])} locations, "
                       f"{len(world_state['events'])} events")
            
            return world_state
    
    def add_sync_callback(self, callback: Callable):
        """Add a callback to be triggered on sync operations."""
        with self._lock:
            self.sync_callbacks.append(callback)
    
    def remove_sync_callback(self, callback: Callable):
        """Remove a sync callback."""
        with self._lock:
            if callback in self.sync_callbacks:
                self.sync_callbacks.remove(callback)


# Global AtomSpace instance
_global_atomspace: Optional[AtomSpace] = None
_global_sync: Optional[AtomSpaceSync] = None


def get_atomspace() -> AtomSpace:
    """Get the global AtomSpace instance."""
    global _global_atomspace
    if _global_atomspace is None:
        _global_atomspace = AtomSpace()
        logger.info("Created global AtomSpace instance")
    return _global_atomspace


def get_atomspace_sync() -> AtomSpaceSync:
    """Get the global AtomSpaceSync instance."""
    global _global_sync
    if _global_sync is None:
        _global_sync = AtomSpaceSync(get_atomspace())
        logger.info("Created global AtomSpaceSync instance")
    return _global_sync


__all__ = [
    'AtomSpace',
    'AtomSpaceSync',
    'QueryPattern',
    'get_atomspace',
    'get_atomspace_sync',
]
