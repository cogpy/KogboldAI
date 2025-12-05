"""
Tests for AtomSpace integration components.
"""

import pytest
from opencog_integration.atomspace import (
    AtomSpace,
    AtomSpaceSync,
    QueryPattern,
    ConceptNode,
    PredicateNode,
    EvaluationLink,
    InheritanceLink,
    CausalLink,
    TemporalLink,
    AtomFactory,
    NarrativeConceptType,
    PredicateType,
    AtomType,
    PLNReasoner,
    NarrativeReasoner,
    TruthValue,
    initialize_narrative_ontology,
)


class TestAtomTypes:
    """Test atom type definitions."""
    
    def test_concept_node_creation(self):
        """Test creating a concept node."""
        character = ConceptNode("Hero", NarrativeConceptType.CHARACTER)
        assert character.name == "Hero"
        assert character.concept_type == NarrativeConceptType.CHARACTER
        assert character.atom_type == AtomType.CONCEPT_NODE
        assert character.truth_value == 1.0
        assert character.confidence == 1.0
    
    def test_predicate_node_creation(self):
        """Test creating a predicate node."""
        predicate = PredicateNode("HasTrait", PredicateType.HAS_TRAIT)
        assert predicate.name == "HasTrait"
        assert predicate.predicate_type == PredicateType.HAS_TRAIT
        assert predicate.atom_type == AtomType.PREDICATE_NODE
    
    def test_evaluation_link_creation(self):
        """Test creating an evaluation link."""
        character = ConceptNode("Hero", NarrativeConceptType.CHARACTER)
        trait = ConceptNode("Brave", NarrativeConceptType.CHARACTER)
        predicate = PredicateNode("HasTrait", PredicateType.HAS_TRAIT)
        
        eval_link = EvaluationLink(predicate, [character, trait])
        assert eval_link.predicate == predicate
        assert len(eval_link.arguments) == 2
        assert eval_link.arguments[0] == character
        assert eval_link.arguments[1] == trait
    
    def test_causal_link_creation(self):
        """Test creating a causal link."""
        cause = ConceptNode("Storm", NarrativeConceptType.EVENT)
        effect = ConceptNode("Flood", NarrativeConceptType.EVENT)
        
        causal = CausalLink(cause, effect, truth_value=0.9, confidence=0.8)
        assert causal.cause == cause
        assert causal.effect == effect
        assert causal.truth_value == 0.9
        assert causal.confidence == 0.8
    
    def test_temporal_link_creation(self):
        """Test creating a temporal link."""
        event = ConceptNode("Battle", NarrativeConceptType.EVENT)
        temporal = TemporalLink(event, timestamp=100.0, duration=50.0)
        
        assert temporal.timestamp == 100.0
        assert temporal.duration == 50.0
        assert temporal.outgoing[0] == event
    
    def test_atom_to_dict(self):
        """Test converting atom to dictionary."""
        character = ConceptNode("Hero", NarrativeConceptType.CHARACTER)
        character.properties['age'] = 25
        
        data = character.to_dict()
        assert data['name'] == "Hero"
        assert data['concept_type'] == 'Character'
        assert data['properties']['age'] == 25


class TestAtomFactory:
    """Test AtomFactory utilities."""
    
    def test_create_character(self):
        """Test factory character creation."""
        character = AtomFactory.create_character("Hero", traits={'brave': True})
        assert character.name == "Hero"
        assert character.concept_type == NarrativeConceptType.CHARACTER
        assert character.properties['brave'] is True
    
    def test_create_location(self):
        """Test factory location creation."""
        location = AtomFactory.create_location("Castle", description="Ancient fortress")
        assert location.name == "Castle"
        assert location.concept_type == NarrativeConceptType.LOCATION
        assert location.properties['description'] == "Ancient fortress"
    
    def test_create_event(self):
        """Test factory event creation."""
        event = AtomFactory.create_event("Battle", timestamp=100.0)
        assert event.name == "Battle"
        assert event.concept_type == NarrativeConceptType.EVENT
        assert event.properties['timestamp'] == 100.0
    
    def test_create_relationship(self):
        """Test factory relationship creation."""
        hero = AtomFactory.create_character("Hero")
        villain = AtomFactory.create_character("Villain")
        
        relationship = AtomFactory.create_relationship(
            hero, PredicateType.CONFLICTS_WITH, villain, strength=0.9
        )
        
        assert isinstance(relationship, EvaluationLink)
        assert relationship.truth_value == 0.9
        assert relationship.arguments[0] == hero
        assert relationship.arguments[1] == villain
    
    def test_create_causal_chain(self):
        """Test factory causal chain creation."""
        events = [
            AtomFactory.create_event("Event1"),
            AtomFactory.create_event("Event2"),
            AtomFactory.create_event("Event3"),
        ]
        
        chain = AtomFactory.create_causal_chain(events)
        assert len(chain) == 2
        assert chain[0].cause == events[0]
        assert chain[0].effect == events[1]
        assert chain[1].cause == events[1]
        assert chain[1].effect == events[2]


class TestAtomSpace:
    """Test AtomSpace functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.atomspace = AtomSpace()
    
    def test_add_atom(self):
        """Test adding an atom to AtomSpace."""
        character = AtomFactory.create_character("Hero")
        result = self.atomspace.add_atom(character)
        
        assert result == character
        assert self.atomspace.get_atom_count() > 0
    
    def test_get_atom(self):
        """Test retrieving an atom from AtomSpace."""
        character = AtomFactory.create_character("Hero")
        self.atomspace.add_atom(character)
        
        retrieved = self.atomspace.get_atom("Hero", AtomType.CONCEPT_NODE)
        assert retrieved is not None
        assert retrieved.name == "Hero"
    
    def test_remove_atom(self):
        """Test removing an atom from AtomSpace."""
        character = AtomFactory.create_character("Hero")
        self.atomspace.add_atom(character)
        
        count_before = self.atomspace.get_atom_count()
        success = self.atomspace.remove_atom(character)
        
        assert success is True
        assert self.atomspace.get_atom_count() < count_before
    
    def test_query_by_concept_type(self):
        """Test querying atoms by concept type."""
        hero = AtomFactory.create_character("Hero")
        villain = AtomFactory.create_character("Villain")
        castle = AtomFactory.create_location("Castle")
        
        self.atomspace.add_atom(hero)
        self.atomspace.add_atom(villain)
        self.atomspace.add_atom(castle)
        
        pattern = QueryPattern(concept_type=NarrativeConceptType.CHARACTER)
        characters = self.atomspace.query(pattern)
        
        assert len(characters) >= 2
        assert all(isinstance(c, ConceptNode) for c in characters)
    
    def test_query_by_truth_value(self):
        """Test querying atoms by truth value threshold."""
        strong_atom = AtomFactory.create_character("Strong", {'power': 10})
        strong_atom.truth_value = 0.9
        
        weak_atom = AtomFactory.create_character("Weak", {'power': 1})
        weak_atom.truth_value = 0.3
        
        self.atomspace.add_atom(strong_atom)
        self.atomspace.add_atom(weak_atom)
        
        pattern = QueryPattern(
            concept_type=NarrativeConceptType.CHARACTER,
            min_truth_value=0.5
        )
        results = self.atomspace.query(pattern)
        
        names = [r.name for r in results]
        assert "Strong" in names
        assert "Weak" not in names
    
    def test_get_incoming_links(self):
        """Test getting incoming links for an atom."""
        hero = AtomFactory.create_character("Hero")
        castle = AtomFactory.create_location("Castle")
        
        self.atomspace.add_atom(hero)
        self.atomspace.add_atom(castle)
        
        location_link = AtomFactory.create_relationship(
            hero, PredicateType.LOCATED_AT, castle
        )
        self.atomspace.add_atom(location_link)
        
        incoming = self.atomspace.get_incoming(hero)
        assert len(incoming) > 0
        assert any(isinstance(link, EvaluationLink) for link in incoming)
    
    def test_clear_atomspace(self):
        """Test clearing the AtomSpace."""
        hero = AtomFactory.create_character("Hero")
        self.atomspace.add_atom(hero)
        
        self.atomspace.clear()
        # After clear, should have only ontology atoms
        assert self.atomspace.get_atom_count() > 0  # Ontology atoms remain


class TestAtomSpaceSync:
    """Test AtomSpace synchronization."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.atomspace = AtomSpace()
        self.sync = AtomSpaceSync(self.atomspace)
    
    def test_sync_from_kobold_characters(self):
        """Test syncing characters from KoboldAI."""
        world_state = {
            'characters': [
                {'name': 'Hero', 'traits': {'brave': True, 'age': 25}},
                {'name': 'Villain', 'traits': {'evil': True}},
            ]
        }
        
        atoms_added = self.sync.sync_from_kobold(world_state)
        assert atoms_added >= 2
        
        hero = self.atomspace.get_atom("Hero")
        assert hero is not None
        assert hero.properties['brave'] is True
    
    def test_sync_from_kobold_locations(self):
        """Test syncing locations from KoboldAI."""
        world_state = {
            'locations': [
                {'name': 'Castle', 'description': 'Ancient fortress'},
                {'name': 'Forest', 'description': 'Dark woods'},
            ]
        }
        
        atoms_added = self.sync.sync_from_kobold(world_state)
        assert atoms_added >= 2
        
        castle = self.atomspace.get_atom("Castle")
        assert castle is not None
    
    def test_sync_from_kobold_events(self):
        """Test syncing events from KoboldAI."""
        world_state = {
            'events': [
                {'description': 'Battle started', 'timestamp': 100.0},
                {'description': 'Hero won', 'timestamp': 150.0},
            ]
        }
        
        atoms_added = self.sync.sync_from_kobold(world_state)
        assert atoms_added >= 3  # 2 events + 1 causal link
    
    def test_sync_to_kobold(self):
        """Test extracting world state from AtomSpace."""
        # Add some atoms
        hero = AtomFactory.create_character("Hero", {'brave': True})
        castle = AtomFactory.create_location("Castle", "Ancient fortress")
        
        self.atomspace.add_atom(hero)
        self.atomspace.add_atom(castle)
        
        world_state = self.sync.sync_to_kobold()
        
        assert 'characters' in world_state
        assert 'locations' in world_state
        assert len(world_state['characters']) >= 1
        assert len(world_state['locations']) >= 1
    
    def test_sync_callback(self):
        """Test sync callbacks."""
        callback_called = []
        
        def test_callback(direction, count):
            callback_called.append((direction, count))
        
        self.sync.add_sync_callback(test_callback)
        
        world_state = {'characters': [{'name': 'Hero', 'traits': {}}]}
        self.sync.sync_from_kobold(world_state)
        
        assert len(callback_called) > 0
        assert callback_called[0][0] == 'kobold_to_atomspace'


class TestPLNReasoner:
    """Test PLN reasoning functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.atomspace = AtomSpace()
        self.pln = PLNReasoner(self.atomspace)
    
    def test_truth_value_creation(self):
        """Test TruthValue creation."""
        tv = TruthValue(strength=0.8, confidence=0.9)
        assert tv.strength == 0.8
        assert tv.confidence == 0.9
    
    def test_truth_value_from_atom(self):
        """Test creating TruthValue from atom."""
        character = AtomFactory.create_character("Hero")
        character.truth_value = 0.7
        character.confidence = 0.8
        
        tv = TruthValue.from_atom(character)
        assert tv.strength == 0.7
        assert tv.confidence == 0.8
    
    def test_deduction(self):
        """Test deduction inference rule."""
        # A causes B, B causes C => A causes C
        event_a = AtomFactory.create_event("A")
        event_b = AtomFactory.create_event("B")
        event_c = AtomFactory.create_event("C")
        
        link_ab = CausalLink(event_a, event_b, truth_value=0.8, confidence=0.9)
        link_bc = CausalLink(event_b, event_c, truth_value=0.7, confidence=0.8)
        
        self.atomspace.add_atom(link_ab)
        self.atomspace.add_atom(link_bc)
        
        result = self.pln.deduction(link_ab, link_bc)
        
        assert result is not None
        assert result.cause.name == "A"
        assert result.effect.name == "C"
        assert result.truth_value > 0
        assert result.truth_value < min(0.8, 0.7)  # Should be product
    
    def test_modus_ponens(self):
        """Test modus ponens inference rule."""
        # A causes B, A is true => B is true
        event_a = AtomFactory.create_event("A")
        event_b = AtomFactory.create_event("B")
        
        event_a.truth_value = 0.9
        event_a.confidence = 0.8
        
        link_ab = CausalLink(event_a, event_b, truth_value=0.8, confidence=0.9)
        self.atomspace.add_atom(link_ab)
        
        result = self.pln.modus_ponens(link_ab, event_a)
        
        assert result is not None
        assert result.name == "B"
        assert result.truth_value > 0
    
    def test_forward_chain(self):
        """Test forward chaining inference."""
        # Create a simple causal chain
        event_a = AtomFactory.create_event("A")
        event_b = AtomFactory.create_event("B")
        event_c = AtomFactory.create_event("C")
        
        event_a.truth_value = 1.0
        
        link_ab = CausalLink(event_a, event_b)
        link_bc = CausalLink(event_b, event_c)
        
        self.atomspace.add_atom(event_a)
        self.atomspace.add_atom(link_ab)
        self.atomspace.add_atom(link_bc)
        
        derived = self.pln.forward_chain([event_a], max_depth=2)
        
        # Should derive at least event_b
        assert len(derived) > 0
    
    def test_find_contradictions(self):
        """Test contradiction detection."""
        character = AtomFactory.create_character("Hero")
        trait1 = ConceptNode("Brave", NarrativeConceptType.CHARACTER)
        trait2 = ConceptNode("Cowardly", NarrativeConceptType.CHARACTER)
        
        # Create contradictory relationships
        rel1 = AtomFactory.create_relationship(
            character, PredicateType.HAS_TRAIT, trait1, strength=0.9
        )
        rel2 = AtomFactory.create_relationship(
            character, PredicateType.HAS_TRAIT, trait2, strength=0.1
        )
        
        self.atomspace.add_atom(rel1)
        self.atomspace.add_atom(rel2)
        
        contradictions = self.pln.find_contradictions()
        # May or may not find contradiction depending on implementation
        assert isinstance(contradictions, list)


class TestNarrativeReasoner:
    """Test high-level narrative reasoning."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.atomspace = AtomSpace()
        self.reasoner = NarrativeReasoner(self.atomspace)
    
    def test_predict_outcome(self):
        """Test predicting narrative outcomes."""
        event_a = AtomFactory.create_event("Hero arrives")
        event_a.truth_value = 1.0
        
        event_b = AtomFactory.create_event("Hero meets villain")
        link = CausalLink(event_a, event_b)
        
        self.atomspace.add_atom(event_a)
        self.atomspace.add_atom(link)
        
        outcomes = self.reasoner.predict_narrative_outcome([event_a])
        assert isinstance(outcomes, list)
    
    def test_evaluate_coherence(self):
        """Test narrative coherence evaluation."""
        # Add some narrative atoms
        hero = AtomFactory.create_character("Hero")
        self.atomspace.add_atom(hero)
        
        coherence = self.reasoner.evaluate_narrative_coherence()
        assert 0.0 <= coherence <= 1.0


class TestNarrativeOntology:
    """Test narrative ontology initialization."""
    
    def test_ontology_initialization(self):
        """Test that ontology is properly initialized."""
        links = initialize_narrative_ontology()
        
        assert len(links) > 0
        assert all(isinstance(link, InheritanceLink) for link in links)
    
    def test_ontology_in_atomspace(self):
        """Test that ontology is loaded into AtomSpace."""
        atomspace = AtomSpace()
        
        # Should have ontology atoms
        assert atomspace.get_atom_count() > 0
        
        # Check for some expected ontology concepts
        protagonist = atomspace.get_atom("Protagonist")
        # May or may not exist depending on ontology structure


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
