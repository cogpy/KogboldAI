"""
Probabilistic Logic Networks (PLN) Reasoning for Narrative Intelligence

This module implements PLN reasoning capabilities for story logic, enabling:
- Probabilistic inference over narrative elements
- Uncertain reasoning about character motivations and plot outcomes
- Logical deduction with confidence scores
- Forward and backward chaining for story progression

PLN combines probability theory with logical inference to handle uncertainty
in narrative reasoning.
"""

import math
import logging
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from .atom_types import (
    Atom, ConceptNode, PredicateNode, EvaluationLink,
    InheritanceLink, CausalLink, Link
)
from .atomspace_connector import AtomSpace, QueryPattern

logger = logging.getLogger(__name__)


class InferenceRule(Enum):
    """PLN inference rules."""
    
    DEDUCTION = "deduction"          # A→B, B→C ⇒ A→C
    ABDUCTION = "abduction"          # A→B, B ⇒ A (with lower confidence)
    INDUCTION = "induction"          # A→B (multiple instances) ⇒ general rule
    MODUS_PONENS = "modus_ponens"    # A→B, A ⇒ B
    ANALOGY = "analogy"              # A→B, C similar to A ⇒ C→B
    INHERITANCE = "inheritance"      # X inherits from Y ⇒ X has Y's properties


@dataclass
class TruthValue:
    """
    PLN truth value representing uncertain knowledge.
    
    Attributes:
        strength: Probability or degree of belief (0.0 to 1.0)
        confidence: Confidence in the strength estimate (0.0 to 1.0)
        count: Evidence count (used for computing confidence)
    """
    
    strength: float = 0.5
    confidence: float = 0.5
    count: float = 1.0
    
    def __post_init__(self):
        """Validate truth value ranges."""
        self.strength = max(0.0, min(1.0, self.strength))
        self.confidence = max(0.0, min(1.0, self.confidence))
        self.count = max(0.0, self.count)
    
    def to_atom_values(self) -> Tuple[float, float]:
        """Convert to atom truth_value and confidence."""
        return self.strength, self.confidence
    
    @classmethod
    def from_atom(cls, atom: Atom) -> 'TruthValue':
        """Create TruthValue from an atom."""
        return cls(
            strength=atom.truth_value,
            confidence=atom.confidence,
            count=1.0
        )
    
    def __repr__(self) -> str:
        return f"TV(s={self.strength:.3f}, c={self.confidence:.3f})"


class PLNReasoner:
    """
    Probabilistic Logic Networks reasoning engine for narrative intelligence.
    """
    
    def __init__(self, atomspace: AtomSpace):
        self.atomspace = atomspace
        self.inference_history: List[Dict] = []
        self.max_iterations = 100
        self.min_confidence_threshold = 0.1
    
    def deduction(self, premise1: Link, premise2: Link) -> Optional[Link]:
        """
        Deduction rule: A→B, B→C ⇒ A→C
        
        Args:
            premise1: First causal/inheritance link (A→B)
            premise2: Second causal/inheritance link (B→C)
            
        Returns:
            Deduced link (A→C) with computed truth value, or None if invalid
        """
        # Check if links chain properly
        if not self._links_chain(premise1, premise2):
            return None
        
        # Get truth values
        tv1 = TruthValue.from_atom(premise1)
        tv2 = TruthValue.from_atom(premise2)
        
        # Compute deduction truth value
        result_tv = self._deduction_formula(tv1, tv2)
        
        # Create result link
        if isinstance(premise1, CausalLink):
            result = CausalLink(
                premise1.cause,
                premise2.effect,
                truth_value=result_tv.strength,
                confidence=result_tv.confidence
            )
        elif isinstance(premise1, InheritanceLink):
            result = InheritanceLink(
                premise1.child,
                premise2.parent,
                truth_value=result_tv.strength,
                confidence=result_tv.confidence
            )
        else:
            return None
        
        # Record inference
        self._record_inference(InferenceRule.DEDUCTION, [premise1, premise2], result)
        
        return result
    
    def abduction(self, implication: Link, consequent: Atom) -> Optional[Link]:
        """
        Abduction rule: A→B, B observed ⇒ A (with reduced confidence)
        
        This allows reasoning backwards from effects to possible causes.
        
        Args:
            implication: Causal link (A→B)
            consequent: Observed consequent (B)
            
        Returns:
            Abduced antecedent with truth value
        """
        if not isinstance(implication, CausalLink):
            return None
        
        # Check if consequent matches
        if implication.effect.name != consequent.name:
            return None
        
        tv_impl = TruthValue.from_atom(implication)
        tv_cons = TruthValue.from_atom(consequent)
        
        # Abduction formula (reduces confidence significantly)
        result_tv = self._abduction_formula(tv_impl, tv_cons)
        
        # The cause is likely true
        result = CausalLink(
            implication.cause,
            consequent,
            truth_value=result_tv.strength,
            confidence=result_tv.confidence
        )
        
        self._record_inference(InferenceRule.ABDUCTION, [implication, consequent], result)
        
        return result
    
    def modus_ponens(self, implication: Link, antecedent: Atom) -> Optional[Atom]:
        """
        Modus Ponens: A→B, A is true ⇒ B is true
        
        Args:
            implication: Causal link (A→B)
            antecedent: Observed antecedent (A)
            
        Returns:
            Consequent with computed truth value
        """
        if not isinstance(implication, CausalLink):
            return None
        
        # Check if antecedent matches
        if implication.cause.name != antecedent.name:
            return None
        
        tv_impl = TruthValue.from_atom(implication)
        tv_ante = TruthValue.from_atom(antecedent)
        
        # Modus ponens formula
        result_tv = self._modus_ponens_formula(tv_impl, tv_ante)
        
        # Update consequent
        consequent = implication.effect
        consequent.truth_value = result_tv.strength
        consequent.confidence = result_tv.confidence
        
        self._record_inference(InferenceRule.MODUS_PONENS, [implication, antecedent], consequent)
        
        return consequent
    
    def inheritance_reasoning(self, inheritance: InheritanceLink, 
                            child_property: EvaluationLink) -> Optional[EvaluationLink]:
        """
        Inheritance reasoning: If X inherits from Y and X has property P,
        then Y might have property P (induction), or if Y has P, then X has P (deduction).
        
        Args:
            inheritance: X inherits from Y
            child_property: Property of X
            
        Returns:
            Property link for Y with computed truth value
        """
        if not isinstance(inheritance, InheritanceLink):
            return None
        
        # Inheritance dilutes properties slightly
        tv_inh = TruthValue.from_atom(inheritance)
        tv_prop = TruthValue.from_atom(child_property)
        
        # Compute inherited property strength
        result_tv = TruthValue(
            strength=tv_prop.strength * tv_inh.strength,
            confidence=min(tv_prop.confidence, tv_inh.confidence) * 0.9,
            count=1.0
        )
        
        # Create parent property
        # Note: This is simplified - full implementation would properly handle arguments
        parent_property = EvaluationLink(
            child_property.predicate,
            [inheritance.parent] + child_property.arguments[1:],
            truth_value=result_tv.strength,
            confidence=result_tv.confidence
        )
        
        self._record_inference(InferenceRule.INHERITANCE, [inheritance, child_property], parent_property)
        
        return parent_property
    
    def forward_chain(self, initial_atoms: List[Atom], max_depth: int = 3) -> List[Atom]:
        """
        Forward chaining inference: Start with known facts and derive conclusions.
        
        Args:
            initial_atoms: Starting atoms (known facts)
            max_depth: Maximum inference depth
            
        Returns:
            List of derived atoms
        """
        derived_atoms = set()
        current_atoms = set(initial_atoms)
        
        for depth in range(max_depth):
            new_atoms = set()
            
            # Try all inference rules on current atoms
            for atom in current_atoms:
                # Find causal links from this atom
                if isinstance(atom, ConceptNode):
                    # Look for links where this is the cause
                    causal_links = [
                        link for link in self.atomspace.get_incoming(atom)
                        if isinstance(link, CausalLink) and link.cause.name == atom.name
                    ]
                    
                    for link in causal_links:
                        # Apply modus ponens
                        result = self.modus_ponens(link, atom)
                        if result and result not in current_atoms:
                            new_atoms.add(result)
                            self.atomspace.add_atom(result)
            
            if not new_atoms:
                break
            
            derived_atoms.update(new_atoms)
            current_atoms.update(new_atoms)
        
        logger.info(f"Forward chain derived {len(derived_atoms)} new atoms in {depth + 1} iterations")
        return list(derived_atoms)
    
    def backward_chain(self, goal: Atom, max_depth: int = 3) -> List[List[Atom]]:
        """
        Backward chaining inference: Start with goal and find supporting evidence.
        
        Args:
            goal: Goal atom to prove
            max_depth: Maximum inference depth
            
        Returns:
            List of proof paths (each path is a list of atoms)
        """
        proof_paths = []
        
        def _search(current_goal: Atom, path: List[Atom], depth: int):
            if depth >= max_depth:
                return
            
            # Check if goal is already known
            existing = self.atomspace.get_atom(current_goal.name, current_goal.atom_type)
            if existing and existing.truth_value > 0.5:
                proof_paths.append(path + [existing])
                return
            
            # Find causal links that could lead to this goal
            incoming = self.atomspace.get_incoming(current_goal)
            for link in incoming:
                if isinstance(link, CausalLink) and link.effect.name == current_goal.name:
                    # Need to prove the cause
                    _search(link.cause, path + [link], depth + 1)
        
        _search(goal, [], 0)
        
        logger.info(f"Backward chain found {len(proof_paths)} proof paths for {goal.name}")
        return proof_paths
    
    def compute_narrative_likelihood(self, scenario_atoms: List[Atom]) -> float:
        """
        Compute the likelihood of a narrative scenario based on atom truth values.
        
        Args:
            scenario_atoms: Atoms describing the scenario
            
        Returns:
            Overall likelihood score (0.0 to 1.0)
        """
        if not scenario_atoms:
            return 0.0
        
        # Combine truth values using geometric mean weighted by confidence
        weighted_sum = 0.0
        total_confidence = 0.0
        
        for atom in scenario_atoms:
            tv = TruthValue.from_atom(atom)
            weight = tv.confidence
            weighted_sum += tv.strength * weight
            total_confidence += weight
        
        if total_confidence == 0:
            return 0.0
        
        likelihood = weighted_sum / total_confidence
        return likelihood
    
    def find_contradictions(self) -> List[Tuple[Atom, Atom]]:
        """
        Find contradictory atoms in the AtomSpace.
        
        Returns:
            List of contradictory atom pairs
        """
        contradictions = []
        all_atoms = self.atomspace.get_all_atoms()
        
        # Simple contradiction detection: same predicate with very different truth values
        evaluation_links: Dict[str, List[EvaluationLink]] = {}
        
        for atom in all_atoms:
            if isinstance(atom, EvaluationLink):
                key = self._evaluation_key(atom)
                if key not in evaluation_links:
                    evaluation_links[key] = []
                evaluation_links[key].append(atom)
        
        # Check for contradictions
        for key, links in evaluation_links.items():
            if len(links) > 1:
                for i in range(len(links)):
                    for j in range(i + 1, len(links)):
                        # If truth values are very different, it's a contradiction
                        diff = abs(links[i].truth_value - links[j].truth_value)
                        if diff > 0.7:  # Threshold for contradiction
                            contradictions.append((links[i], links[j]))
        
        return contradictions
    
    def resolve_contradiction(self, atom1: Atom, atom2: Atom) -> Atom:
        """
        Resolve contradiction by choosing atom with higher confidence.
        
        Args:
            atom1: First contradictory atom
            atom2: Second contradictory atom
            
        Returns:
            The atom to keep (higher confidence)
        """
        tv1 = TruthValue.from_atom(atom1)
        tv2 = TruthValue.from_atom(atom2)
        
        if tv1.confidence >= tv2.confidence:
            return atom1
        else:
            return atom2
    
    def _deduction_formula(self, tv1: TruthValue, tv2: TruthValue) -> TruthValue:
        """Compute truth value for deduction rule."""
        # Strength: product of strengths
        strength = tv1.strength * tv2.strength
        
        # Confidence: minimum of confidences, slightly reduced
        confidence = min(tv1.confidence, tv2.confidence) * 0.95
        
        return TruthValue(strength=strength, confidence=confidence)
    
    def _abduction_formula(self, tv_impl: TruthValue, tv_cons: TruthValue) -> TruthValue:
        """Compute truth value for abduction rule."""
        # Abduction is less certain than deduction
        # Strength based on implication strength and consequent strength
        strength = tv_impl.strength * tv_cons.strength * 0.8
        
        # Confidence significantly reduced
        confidence = min(tv_impl.confidence, tv_cons.confidence) * 0.5
        
        return TruthValue(strength=strength, confidence=confidence)
    
    def _modus_ponens_formula(self, tv_impl: TruthValue, tv_ante: TruthValue) -> TruthValue:
        """Compute truth value for modus ponens rule."""
        # Strength: product of strengths
        strength = tv_impl.strength * tv_ante.strength
        
        # Confidence: minimum of confidences
        confidence = min(tv_impl.confidence, tv_ante.confidence)
        
        return TruthValue(strength=strength, confidence=confidence)
    
    def _links_chain(self, link1: Link, link2: Link) -> bool:
        """Check if two links can chain (B in A→B matches B in B→C)."""
        if isinstance(link1, CausalLink) and isinstance(link2, CausalLink):
            return link1.effect.name == link2.cause.name
        elif isinstance(link1, InheritanceLink) and isinstance(link2, InheritanceLink):
            return link1.parent.name == link2.child.name
        return False
    
    def _evaluation_key(self, eval_link: EvaluationLink) -> str:
        """Generate a key for an evaluation link for contradiction detection."""
        predicate = eval_link.predicate.name
        args = "_".join(arg.name for arg in eval_link.arguments)
        return f"{predicate}_{args}"
    
    def _record_inference(self, rule: InferenceRule, premises: List[Atom], conclusion: Atom):
        """Record an inference in the history."""
        self.inference_history.append({
            'rule': rule.value,
            'premises': [p.name for p in premises],
            'conclusion': conclusion.name,
            'truth_value': conclusion.truth_value,
            'confidence': conclusion.confidence
        })
    
    def get_inference_history(self) -> List[Dict]:
        """Get the history of all inferences."""
        return self.inference_history.copy()
    
    def clear_history(self):
        """Clear the inference history."""
        self.inference_history.clear()


class NarrativeReasoner:
    """
    High-level narrative reasoning using PLN.
    """
    
    def __init__(self, atomspace: AtomSpace):
        self.atomspace = atomspace
        self.pln = PLNReasoner(atomspace)
    
    def infer_character_motivation(self, character: ConceptNode, 
                                   action: ConceptNode) -> Optional[ConceptNode]:
        """
        Infer character motivation from their action.
        
        Args:
            character: Character performing action
            action: Action taken
            
        Returns:
            Inferred motivation concept
        """
        # Look for motivation patterns in AtomSpace
        # This is a simplified version
        causal_links = [
            link for link in self.atomspace.get_all_atoms()
            if isinstance(link, CausalLink)
        ]
        
        # Find links where action is the effect
        for link in causal_links:
            if link.effect.name == action.name:
                # The cause might be the motivation
                result = self.pln.abduction(link, action)
                if result:
                    return result.cause
        
        return None
    
    def predict_narrative_outcome(self, current_situation: List[Atom]) -> List[Atom]:
        """
        Predict likely outcomes given current narrative situation.
        
        Args:
            current_situation: Current narrative state atoms
            
        Returns:
            List of predicted outcome atoms
        """
        return self.pln.forward_chain(current_situation, max_depth=2)
    
    def find_plot_holes(self) -> List[Tuple[Atom, Atom]]:
        """
        Find plot holes (contradictions) in the narrative.
        
        Returns:
            List of contradictory atom pairs
        """
        return self.pln.find_contradictions()
    
    def evaluate_narrative_coherence(self) -> float:
        """
        Evaluate overall narrative coherence.
        
        Returns:
            Coherence score (0.0 to 1.0)
        """
        all_atoms = self.atomspace.get_all_atoms()
        
        # Count contradictions
        contradictions = self.pln.find_contradictions()
        contradiction_penalty = len(contradictions) * 0.1
        
        # Compute average truth value
        if all_atoms:
            avg_truth = sum(atom.truth_value for atom in all_atoms) / len(all_atoms)
            avg_confidence = sum(atom.confidence for atom in all_atoms) / len(all_atoms)
            
            coherence = (avg_truth * avg_confidence) - contradiction_penalty
            return max(0.0, min(1.0, coherence))
        
        return 0.5


__all__ = [
    'PLNReasoner',
    'NarrativeReasoner',
    'TruthValue',
    'InferenceRule',
]
