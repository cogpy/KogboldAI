"""
AtomSpace Integration Package for KoboldAI

This package provides OpenCog AtomSpace integration for knowledge representation
and probabilistic logic reasoning in narrative generation.
"""

from .atom_types import (
    AtomType,
    NarrativeConceptType,
    PredicateType,
    Atom,
    ConceptNode,
    PredicateNode,
    Link,
    EvaluationLink,
    InheritanceLink,
    TemporalLink,
    CausalLink,
    AtomFactory,
    NARRATIVE_ONTOLOGY,
    initialize_narrative_ontology,
)

from .atomspace_connector import (
    AtomSpace,
    AtomSpaceSync,
    QueryPattern,
    get_atomspace,
    get_atomspace_sync,
)

from .pln_reasoning import (
    PLNReasoner,
    NarrativeReasoner,
    TruthValue,
    InferenceRule,
)

__all__ = [
    # Atom types
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
    
    # AtomSpace
    'AtomSpace',
    'AtomSpaceSync',
    'QueryPattern',
    'get_atomspace',
    'get_atomspace_sync',
    
    # PLN Reasoning
    'PLNReasoner',
    'NarrativeReasoner',
    'TruthValue',
    'InferenceRule',
]
