"""
Atom Types for Narrative Elements in OpenCog AtomSpace Integration

This module defines the atom types used to represent narrative elements,
story structure, character relationships, and world state in the OpenCog
AtomSpace knowledge representation system.

Atom Types Hierarchy:
- ConceptNode: Represents narrative concepts (characters, locations, objects)
- PredicateNode: Represents relationships and properties
- EvaluationLink: Links predicates to their arguments
- InheritanceLink: Represents type hierarchies
- ListLink: Groups multiple atoms
- TimeLink: Associates atoms with temporal information
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field


class AtomType(Enum):
    """Enumeration of atom types used in narrative representation."""
    
    # Node Types
    CONCEPT_NODE = "ConceptNode"
    PREDICATE_NODE = "PredicateNode"
    SCHEMA_NODE = "SchemaNode"
    
    # Link Types
    EVALUATION_LINK = "EvaluationLink"
    INHERITANCE_LINK = "InheritanceLink"
    SIMILARITY_LINK = "SimilarityLink"
    LIST_LINK = "ListLink"
    
    # Temporal Links
    TEMPORAL_LINK = "TemporalLink"
    SEQUENTIAL_LINK = "SequentialLink"
    
    # Narrative-specific Links
    CAUSAL_LINK = "CausalLink"
    MOTIVATION_LINK = "MotivationLink"
    CONFLICT_LINK = "ConflictLink"


class NarrativeConceptType(Enum):
    """Types of narrative concepts."""
    
    CHARACTER = "Character"
    LOCATION = "Location"
    OBJECT = "Object"
    EVENT = "Event"
    THEME = "Theme"
    PLOT_POINT = "PlotPoint"
    GOAL = "Goal"
    EMOTION = "Emotion"
    RELATIONSHIP = "Relationship"
    FACTION = "Faction"
    CULTURE = "Culture"
    MYTHOLOGY = "Mythology"


class PredicateType(Enum):
    """Types of predicates for relationships."""
    
    # Character predicates
    HAS_TRAIT = "HasTrait"
    HAS_GOAL = "HasGoal"
    HAS_EMOTION = "HasEmotion"
    HAS_RELATIONSHIP = "HasRelationship"
    HAS_MEMORY = "HasMemory"
    
    # Location predicates
    LOCATED_AT = "LocatedAt"
    CONTAINS = "Contains"
    CONNECTED_TO = "ConnectedTo"
    
    # Event predicates
    CAUSED_BY = "CausedBy"
    HAPPENED_AT = "HappenedAt"
    PARTICIPATED_IN = "ParticipatedIn"
    RESULTED_IN = "ResultedIn"
    
    # Narrative predicates
    HAS_PLOT_ROLE = "HasPlotRole"
    BELONGS_TO_THEME = "BelongsToTheme"
    FORESHADOWS = "Foreshadows"
    RESOLVES = "Resolves"
    
    # World predicates
    MEMBER_OF = "MemberOf"
    BELIEVES_IN = "BelievesIn"
    CONFLICTS_WITH = "ConflictsWith"


@dataclass(eq=False)
class Atom:
    """Base class for all atom representations."""
    
    atom_type: AtomType
    name: str
    truth_value: float = 1.0  # Strength of belief (0.0 to 1.0)
    confidence: float = 1.0   # Confidence in truth value (0.0 to 1.0)
    attention_value: float = 0.5  # Attention STI (0.0 to 1.0)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert atom to dictionary representation."""
        return {
            'atom_type': self.atom_type.value,
            'name': self.name,
            'truth_value': self.truth_value,
            'confidence': self.confidence,
            'attention_value': self.attention_value,
            'metadata': self.metadata
        }
    
    def __eq__(self, other) -> bool:
        """Compare atoms by type and name only."""
        if not isinstance(other, Atom):
            return False
        return self.atom_type == other.atom_type and self.name == other.name
    
    def __hash__(self) -> int:
        """Hash based on type and name."""
        return hash((self.atom_type, self.name))
    
    def __repr__(self) -> str:
        return f"{self.atom_type.value}({self.name}, tv={self.truth_value:.2f}, conf={self.confidence:.2f})"


@dataclass(eq=False)
class ConceptNode(Atom):
    """Represents a narrative concept (character, location, object, etc.)."""
    
    concept_type: NarrativeConceptType = NarrativeConceptType.CHARACTER
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def __init__(self, name: str, concept_type: NarrativeConceptType, **kwargs):
        # Extract properties if provided in kwargs
        properties = kwargs.pop('properties', {})
        
        super().__init__(
            atom_type=AtomType.CONCEPT_NODE,
            name=name,
            **kwargs
        )
        self.concept_type = concept_type
        self.properties = properties if properties else {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert concept node to dictionary."""
        data = super().to_dict()
        data['concept_type'] = self.concept_type.value
        data['properties'] = self.properties
        return data
    
    def __repr__(self) -> str:
        return f"ConceptNode({self.concept_type.value}:{self.name})"


@dataclass(eq=False)
class PredicateNode(Atom):
    """Represents a relationship or property predicate."""
    
    predicate_type: PredicateType = PredicateType.HAS_TRAIT
    
    def __init__(self, name: str, predicate_type: PredicateType, **kwargs):
        super().__init__(
            atom_type=AtomType.PREDICATE_NODE,
            name=name,
            **kwargs
        )
        self.predicate_type = predicate_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert predicate node to dictionary."""
        data = super().to_dict()
        data['predicate_type'] = self.predicate_type.value
        return data
    
    def __repr__(self) -> str:
        return f"PredicateNode({self.predicate_type.value})"


@dataclass(eq=False)
class Link(Atom):
    """Base class for links between atoms."""
    
    outgoing: List[Atom] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert link to dictionary."""
        data = super().to_dict()
        data['outgoing'] = [atom.to_dict() for atom in self.outgoing]
        return data


@dataclass(eq=False)
class EvaluationLink(Link):
    """Links a predicate to its arguments."""
    
    def __init__(self, predicate: PredicateNode, arguments: List[Atom], **kwargs):
        super().__init__(
            atom_type=AtomType.EVALUATION_LINK,
            name=f"Eval({predicate.name})",
            **kwargs
        )
        self.outgoing = [predicate] + arguments
    
    @property
    def predicate(self) -> PredicateNode:
        """Get the predicate of this evaluation."""
        return self.outgoing[0] if self.outgoing else None
    
    @property
    def arguments(self) -> List[Atom]:
        """Get the arguments of this evaluation."""
        return self.outgoing[1:] if len(self.outgoing) > 1 else []
    
    def __repr__(self) -> str:
        args_str = ", ".join(str(arg) for arg in self.arguments)
        return f"Eval({self.predicate.name}: {args_str})"


@dataclass(eq=False)
class InheritanceLink(Link):
    """Represents type hierarchy (X is a type of Y)."""
    
    def __init__(self, child: Atom, parent: Atom, **kwargs):
        super().__init__(
            atom_type=AtomType.INHERITANCE_LINK,
            name=f"Inheritance({child.name} -> {parent.name})",
            **kwargs
        )
        self.outgoing = [child, parent]
    
    @property
    def child(self) -> Atom:
        """Get the child (more specific) concept."""
        return self.outgoing[0] if self.outgoing else None
    
    @property
    def parent(self) -> Atom:
        """Get the parent (more general) concept."""
        return self.outgoing[1] if len(self.outgoing) > 1 else None
    
    def __repr__(self) -> str:
        return f"Inheritance({self.child} -> {self.parent})"


@dataclass(eq=False)
class TemporalLink(Link):
    """Associates atoms with temporal information."""
    
    timestamp: float = 0.0  # Story time or real time
    duration: Optional[float] = None
    
    def __init__(self, atom: Atom, timestamp: float, duration: Optional[float] = None, **kwargs):
        super().__init__(
            atom_type=AtomType.TEMPORAL_LINK,
            name=f"Temporal({atom.name}@{timestamp})",
            **kwargs
        )
        self.outgoing = [atom]
        self.timestamp = timestamp
        self.duration = duration
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert temporal link to dictionary."""
        data = super().to_dict()
        data['timestamp'] = self.timestamp
        data['duration'] = self.duration
        return data
    
    def __repr__(self) -> str:
        duration_str = f", dur={self.duration}" if self.duration else ""
        return f"Temporal({self.outgoing[0]}@t={self.timestamp}{duration_str})"


@dataclass(eq=False)
class CausalLink(Link):
    """Represents causal relationships between events."""
    
    def __init__(self, cause: Atom, effect: Atom, **kwargs):
        super().__init__(
            atom_type=AtomType.CAUSAL_LINK,
            name=f"Causal({cause.name} -> {effect.name})",
            **kwargs
        )
        self.outgoing = [cause, effect]
    
    @property
    def cause(self) -> Atom:
        """Get the cause event."""
        return self.outgoing[0] if self.outgoing else None
    
    @property
    def effect(self) -> Atom:
        """Get the effect event."""
        return self.outgoing[1] if len(self.outgoing) > 1 else None
    
    def __repr__(self) -> str:
        return f"Causal({self.cause} => {self.effect})"


class AtomFactory:
    """Factory for creating atoms with common patterns."""
    
    @staticmethod
    def create_character(name: str, traits: Dict[str, Any] = None) -> ConceptNode:
        """Create a character concept node."""
        node = ConceptNode(name, NarrativeConceptType.CHARACTER)
        if traits:
            node.properties = traits
        return node
    
    @staticmethod
    def create_location(name: str, description: str = "") -> ConceptNode:
        """Create a location concept node."""
        node = ConceptNode(name, NarrativeConceptType.LOCATION)
        if description:
            node.properties['description'] = description
        return node
    
    @staticmethod
    def create_event(name: str, timestamp: float = 0.0) -> ConceptNode:
        """Create an event concept node."""
        node = ConceptNode(name, NarrativeConceptType.EVENT)
        node.properties['timestamp'] = timestamp
        return node
    
    @staticmethod
    def create_relationship(subject: ConceptNode, predicate_type: PredicateType, 
                          object: ConceptNode, strength: float = 1.0) -> EvaluationLink:
        """Create a relationship evaluation link."""
        predicate = PredicateNode(predicate_type.value, predicate_type)
        return EvaluationLink(
            predicate=predicate,
            arguments=[subject, object],
            truth_value=strength
        )
    
    @staticmethod
    def create_location_link(character: ConceptNode, location: ConceptNode) -> EvaluationLink:
        """Create a 'located at' relationship."""
        return AtomFactory.create_relationship(
            character, PredicateType.LOCATED_AT, location
        )
    
    @staticmethod
    def create_causal_chain(events: List[ConceptNode]) -> List[CausalLink]:
        """Create a chain of causal links from a sequence of events."""
        links = []
        for i in range(len(events) - 1):
            link = CausalLink(events[i], events[i + 1])
            links.append(link)
        return links
    
    @staticmethod
    def create_inheritance_hierarchy(child_name: str, parent_name: str, 
                                    concept_type: NarrativeConceptType) -> InheritanceLink:
        """Create an inheritance relationship."""
        child = ConceptNode(child_name, concept_type)
        parent = ConceptNode(parent_name, concept_type)
        return InheritanceLink(child, parent)


# Predefined concept hierarchies for common narrative elements
NARRATIVE_ONTOLOGY = {
    'character_roles': [
        ('Protagonist', 'Character'),
        ('Antagonist', 'Character'),
        ('MentorFigure', 'Character'),
        ('SidekickAlly', 'Character'),
        ('TricksterArchetype', 'Character'),
    ],
    'location_types': [
        ('City', 'Location'),
        ('Village', 'Location'),
        ('Wilderness', 'Location'),
        ('Dungeon', 'Location'),
        ('MagicalRealm', 'Location'),
    ],
    'event_types': [
        ('Discovery', 'Event'),
        ('Conflict', 'Event'),
        ('Resolution', 'Event'),
        ('Betrayal', 'Event'),
        ('Revelation', 'Event'),
    ],
    'themes': [
        'Redemption',
        'Revenge',
        'Love',
        'Power',
        'Freedom',
        'Identity',
        'Sacrifice',
    ]
}


def initialize_narrative_ontology() -> List[InheritanceLink]:
    """
    Initialize the narrative ontology with predefined concept hierarchies.
    
    Returns:
        List of inheritance links representing the ontology
    """
    links = []
    
    # Create character role hierarchy
    for child, parent in NARRATIVE_ONTOLOGY['character_roles']:
        link = AtomFactory.create_inheritance_hierarchy(
            child, parent, NarrativeConceptType.CHARACTER
        )
        links.append(link)
    
    # Create location type hierarchy
    for child, parent in NARRATIVE_ONTOLOGY['location_types']:
        link = AtomFactory.create_inheritance_hierarchy(
            child, parent, NarrativeConceptType.LOCATION
        )
        links.append(link)
    
    # Create event type hierarchy
    for child, parent in NARRATIVE_ONTOLOGY['event_types']:
        link = AtomFactory.create_inheritance_hierarchy(
            child, parent, NarrativeConceptType.EVENT
        )
        links.append(link)
    
    return links


__all__ = [
    'AtomType',
    'NarrativeConceptType',
    'PredicateType',
    'Atom',
    'ConceptNode',
    'PredicateNode',
    'Link',
    'EvaluationLink',
    'InheritanceLink',
    'TemporalLink',
    'CausalLink',
    'AtomFactory',
    'NARRATIVE_ONTOLOGY',
    'initialize_narrative_ontology',
]
