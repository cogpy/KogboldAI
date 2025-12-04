# KogboldAI - CLAUDE.MD

## Project Overview

KogboldAI is a browser-based AI-assisted writing platform featuring multiple gameplay modes (Novel, Adventure, Chatbot) with deep integration of OpenCog cognitive architecture for autonomous AGI-driven world-building and story-telling orchestration.

**Version:** 1.19.2
**License:** AGPL-3.0
**Primary Language:** Python 3.10+

---

## Architecture Summary

### Core Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Main Server | `aiserver.py` | Flask web server, REST API, model orchestration |
| Settings Manager | `koboldai_settings.py` | Configuration and state management |
| OpenCog Integration | `opencog_integration/` | Cognitive architecture for autonomous agents |
| Model Backends | `modeling/` | Multi-backend inference (HuggingFace, ExLlama, OpenAI) |
| Web Frontend | `static/`, `templates/` | Browser-based UI |
| Userscripts | `userscripts/` | Lua 5.4 automation scripts |

### OpenCog Cognitive Architecture (3,195+ lines)

```
opencog_integration/
├── __init__.py              # Module exports and initialization
├── kobold_integration.py    # Main KoboldAI integration layer (558 lines)
├── agent_orchestrator.py    # Multi-agent coordination system (387 lines)
├── narrative_engine.py      # Story coherence and logic (812 lines)
├── world_builder.py         # Procedural world generation (935 lines)
├── adventure_telos.py       # Goal-oriented behavior system (482 lines)
└── README.md                # Integration documentation
```

### Model Inference Backends

- **HuggingFace** - Generic transformer models
- **ExLlama/ExLlamaV2** - Quantized high-speed inference
- **KoboldCpp** - C++ CPU/GPU acceleration
- **OpenAI/GooseAI** - Cloud API integration
- **KoboldAI Horde** - Distributed inference network

---

## REST API Endpoints

### OpenCog Integration API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/opencog/status` | Integration status and health |
| POST | `/api/v1/opencog/process_input` | Process narrative input through agents |
| GET | `/api/v1/opencog/world_state` | Current world state and entities |
| GET | `/api/v1/opencog/narrative_coherence` | Analyze story consistency |
| POST | `/api/v1/opencog/generate_suggestions` | Generate autonomous suggestions |

### Story Management API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/latest/story` | Retrieve current story content |
| POST | `/api/latest/story/submit` | Submit new story content |
| GET | `/api/latest/world_info` | World information entries |

---

## Current Agent Architecture

### Default Cognitive Agents

1. **Master Storyteller** (`story_structure`)
   - Capabilities: narrative_generation, plot_coordination, character_development
   - Traits: creativity 0.8, coherence 0.9, adaptability 0.7

2. **World Keeper** (`world_consistency`)
   - Capabilities: world_tracking, consistency_checking, lore_management
   - Traits: detail_oriented 0.9, consistency 0.95, creativity 0.6

3. **Character Advocate** (`character_development`)
   - Capabilities: character_consistency, dialogue_generation, motivation_tracking
   - Traits: empathy 0.9, psychology_understanding 0.8, creativity 0.7

### Agent States

`IDLE` -> `ACTIVE` -> `THINKING` -> `GENERATING` -> `COORDINATING` -> `SUSPENDED`

---

## Development Commands

```bash
# Run server
./play.sh                    # Linux/Mac
play.bat                     # Windows

# Run tests
python -m pytest tests/

# OpenCog integration tests
python -m pytest tests/opencog_integration/
```

---

## Code Conventions

- **Type Hints:** Use Python 3.10+ type annotations
- **Docstrings:** Google-style docstrings for public APIs
- **Testing:** pytest with coverage for all new features
- **Async:** Use threading for background agent operations
- **Thread Safety:** Lock-protected shared state

---

# AGI ORCHESTRATION DEVELOPMENT ROADMAP

## Vision Statement

Transform KogboldAI into a fully autonomous AGI-driven creative engine where OpenCog cognitive agents orchestrate complex world-building and narrative generation with minimal human intervention, implementing agent-zero principles for self-directed goal pursuit and emergent storytelling.

---

## Phase 1: Foundation Enhancement (Current → v2.0)

### 1.1 AtomSpace Integration

**Goal:** Connect to external OpenCog AtomSpace for persistent knowledge representation.

**Tasks:**
- [ ] Implement AtomSpace Python bindings (`opencog_integration/atomspace_connector.py`)
- [ ] Create bidirectional sync between KoboldAI world state and AtomSpace
- [ ] Define atom types for narrative elements:
  ```
  (ConceptNode "Character:Protagonist")
  (PredicateNode "HasRelationship")
  (EvaluationLink
    (PredicateNode "LocatedAt")
    (ListLink
      (ConceptNode "Character:Hero")
      (ConceptNode "Location:Castle")))
  ```
- [ ] Implement Pattern Matcher queries for narrative inference
- [ ] Add PLN (Probabilistic Logic Networks) for story reasoning

**Files to Create:**
- `opencog_integration/atomspace_connector.py`
- `opencog_integration/atom_types.py`
- `opencog_integration/pln_reasoning.py`

### 1.2 Agent Memory Architecture

**Goal:** Implement hierarchical memory systems with attention-based retrieval.

**Architecture:**
```
MemorySystem
├── SensoryMemory (immediate context, 1-3 story beats)
├── WorkingMemory (active narrative elements, ~7 items)
├── EpisodicMemory (story events, timestamped)
├── SemanticMemory (world knowledge, facts)
└── ProceduralMemory (writing patterns, style rules)
```

**Tasks:**
- [ ] Create `MemoryHierarchy` class with attention scoring
- [ ] Implement memory consolidation (working -> long-term)
- [ ] Add forgetting curves based on narrative relevance
- [ ] Create associative memory retrieval with semantic similarity
- [ ] Implement memory compression for long stories

**Files to Create:**
- `opencog_integration/memory/hierarchy.py`
- `opencog_integration/memory/consolidation.py`
- `opencog_integration/memory/retrieval.py`

### 1.3 Enhanced Narrative Reasoning

**Goal:** Expand narrative engine with causal inference and counterfactual reasoning.

**Tasks:**
- [ ] Implement causal graph construction from story events
- [ ] Add counterfactual generation ("What if X hadn't happened?")
- [ ] Create narrative tension modeling
- [ ] Implement Chekhov's Gun tracking (setup/payoff detection)
- [ ] Add dramatic irony detection and orchestration

---

## Phase 2: Agent-Zero Implementation (v2.0 → v2.5)

### 2.1 Autonomous Goal Generation

**Goal:** Implement self-directed goal creation inspired by agent-zero architecture.

**Core Principles:**
- Agents generate their own objectives based on narrative state
- Goals emerge from world inconsistencies and story opportunities
- Self-correcting behavior when narratives diverge from coherence

**Tasks:**
- [ ] Create `AutonomousGoalGenerator` class
- [ ] Implement narrative opportunity detection
- [ ] Add goal priority self-adjustment based on story flow
- [ ] Create goal conflict resolution with multi-agent voting
- [ ] Implement meta-goals (story-level objectives)

**Files to Create:**
- `opencog_integration/agent_zero/goal_generator.py`
- `opencog_integration/agent_zero/opportunity_detector.py`
- `opencog_integration/agent_zero/meta_goals.py`

### 2.2 Self-Reflective Agents

**Goal:** Enable agents to evaluate and improve their own outputs.

**Architecture:**
```python
class ReflectiveAgent(CognitiveAgent):
    def generate(self, context):
        output = self._initial_generation(context)
        critique = self._self_critique(output)
        if critique.needs_revision:
            output = self._revise(output, critique)
        return output

    def _self_critique(self, output):
        # Evaluate coherence, creativity, engagement
        # Return structured feedback
```

**Tasks:**
- [ ] Implement self-critique mechanisms
- [ ] Add iterative refinement loops
- [ ] Create quality thresholds for autonomous approval
- [ ] Implement learning from critique patterns
- [ ] Add inter-agent critique and feedback

### 2.3 Tool-Using Agents

**Goal:** Agents can invoke external tools for research, calculation, and world management.

**Tool Categories:**
1. **Research Tools** - Web search for real-world context
2. **Calculation Tools** - Timeline management, distance calculations
3. **World Tools** - Map generation, relationship graphing
4. **Memory Tools** - Long-term storage queries
5. **Generation Tools** - Specialized content generation (names, dialogue)

**Tasks:**
- [ ] Create `ToolRegistry` for agent-accessible tools
- [ ] Implement tool selection reasoning
- [ ] Add tool chaining for complex operations
- [ ] Create sandboxed execution environment
- [ ] Implement tool result integration into narrative

**Files to Create:**
- `opencog_integration/agent_zero/tools/registry.py`
- `opencog_integration/agent_zero/tools/research.py`
- `opencog_integration/agent_zero/tools/world_tools.py`
- `opencog_integration/agent_zero/tools/executor.py`

---

## Phase 3: Multi-Agent Orchestration (v2.5 → v3.0)

### 3.1 Agent Specialization Framework

**Goal:** Create dynamically spawning specialist agents.

**Agent Types to Implement:**

| Agent | Specialization | Trigger Conditions |
|-------|---------------|-------------------|
| **Combat Choreographer** | Action sequences | Combat detected in narrative |
| **Dialogue Director** | Conversations | Multi-character dialogue scenes |
| **Mystery Weaver** | Plot threads | Mystery/investigation elements |
| **Romance Architect** | Relationships | Romantic subplot development |
| **Horror Master** | Tension/fear | Dark/horror genre elements |
| **Comedy Writer** | Humor | Comedic moments and timing |
| **Lore Keeper** | World consistency | Worldbuilding elements |
| **Timeline Guardian** | Temporal logic | Time-sensitive events |

**Tasks:**
- [ ] Create `AgentSpawner` for dynamic agent creation
- [ ] Implement agent lifecycle management (spawn, work, retire)
- [ ] Add agent specialization inheritance
- [ ] Create agent collaboration protocols
- [ ] Implement agent competition for narrative control

### 3.2 Swarm Intelligence Layer

**Goal:** Enable emergent behavior from agent collective.

**Architecture:**
```
SwarmOrchestrator
├── PheromoneTrails (narrative emphasis markers)
├── ConsensusProtocol (decision aggregation)
├── EmergentBehavior (collective pattern detection)
└── AdaptiveWeighting (agent influence adjustment)
```

**Tasks:**
- [ ] Implement stigmergy-based communication
- [ ] Create weighted voting for narrative decisions
- [ ] Add emergent pattern recognition
- [ ] Implement collective memory formation
- [ ] Create adaptive agent influence based on performance

### 3.3 Hierarchical Control Structure

**Goal:** Multi-level orchestration from meta-narrative to sentence level.

**Hierarchy:**
```
Level 0: Meta-Orchestrator (overall story arc)
    └── Level 1: Arc Directors (major plot segments)
        └── Level 2: Scene Managers (individual scenes)
            └── Level 3: Beat Handlers (story beats)
                └── Level 4: Content Generators (actual text)
```

**Tasks:**
- [ ] Implement hierarchical agent structure
- [ ] Create bidirectional communication protocols
- [ ] Add constraint propagation (top-down)
- [ ] Implement feedback aggregation (bottom-up)
- [ ] Create dynamic hierarchy restructuring

---

## Phase 4: World Simulation Engine (v3.0 → v3.5)

### 4.1 Living World System

**Goal:** Autonomous world state evolution independent of narrative focus.

**Simulation Components:**
- **Economic Simulation** - Resource flow, trade, wealth distribution
- **Political Simulation** - Power dynamics, alliances, conflicts
- **Social Simulation** - Population dynamics, cultural drift
- **Environmental Simulation** - Weather, seasons, natural events
- **Temporal Simulation** - Time passage, aging, historical events

**Tasks:**
- [ ] Create `WorldSimulator` background process
- [ ] Implement agent-based NPC behavior models
- [ ] Add procedural event generation
- [ ] Create world state persistence
- [ ] Implement butterfly effect tracking (small changes → large consequences)

**Files to Create:**
- `opencog_integration/world_sim/simulator.py`
- `opencog_integration/world_sim/economics.py`
- `opencog_integration/world_sim/politics.py`
- `opencog_integration/world_sim/social.py`
- `opencog_integration/world_sim/environment.py`

### 4.2 Character Autonomous Behavior

**Goal:** NPCs act independently with believable motivations.

**Character Mind Architecture:**
```python
class CharacterMind:
    personality: PersonalityModel      # Big Five + custom traits
    beliefs: BeliefSystem              # What they think is true
    desires: DesireHierarchy           # What they want
    intentions: IntentionStack         # Current plans
    relationships: RelationshipGraph   # Social connections
    memory: CharacterMemory            # Personal history
```

**Tasks:**
- [ ] Implement BDI (Belief-Desire-Intention) agent model
- [ ] Create personality-driven decision making
- [ ] Add relationship dynamics simulation
- [ ] Implement character goal generation
- [ ] Create character memory with perspective filtering

### 4.3 Dynamic World Events

**Goal:** Procedural generation of world-changing events.

**Event Categories:**
- Natural disasters (earthquakes, storms, plagues)
- Political events (wars, treaties, successions)
- Economic events (booms, crashes, discoveries)
- Social events (movements, migrations, innovations)
- Supernatural events (magical phenomena, divine intervention)

**Tasks:**
- [ ] Create `EventGenerator` with weighted random selection
- [ ] Implement event chain reactions
- [ ] Add event foreshadowing (subtle hints before events)
- [ ] Create narrative integration hooks
- [ ] Implement player influence on event probabilities

---

## Phase 5: Advanced AGI Capabilities (v3.5 → v4.0)

### 5.1 Semantic Understanding Layer

**Goal:** Deep comprehension of narrative meaning and subtext.

**Tasks:**
- [ ] Integrate large language model embeddings
- [ ] Implement theme extraction and tracking
- [ ] Create symbolic AI + neural hybrid reasoning
- [ ] Add metaphor and symbolism detection
- [ ] Implement narrative tone analysis

### 5.2 Creative Emergence Engine

**Goal:** Generate truly novel narrative elements through combinatorial creativity.

**Techniques:**
- **Conceptual Blending** - Merge disparate concepts into new ideas
- **Analogical Reasoning** - Apply patterns from one domain to another
- **Constraint Relaxation** - Temporarily break rules for innovation
- **Bisociation** - Find unexpected connections between concepts

**Tasks:**
- [ ] Implement conceptual blending framework
- [ ] Create analogy engine for cross-domain mapping
- [ ] Add controlled constraint violation
- [ ] Implement novelty detection and scoring
- [ ] Create creativity vs coherence balancing

### 5.3 Emotional Intelligence

**Goal:** Understand and generate emotionally resonant narratives.

**Tasks:**
- [ ] Implement emotional arc tracking
- [ ] Create reader engagement prediction
- [ ] Add pacing optimization for emotional impact
- [ ] Implement character emotional state modeling
- [ ] Create empathy-driven narrative decisions

---

## Phase 6: Human-AI Collaboration (v4.0 → v4.5)

### 6.1 Intent Understanding

**Goal:** Deeply understand human creative intent from minimal input.

**Tasks:**
- [ ] Implement intent classification from prompts
- [ ] Create preference learning from user choices
- [ ] Add style adaptation to user writing
- [ ] Implement creative vision alignment
- [ ] Create collaborative goal negotiation

### 6.2 Adaptive Autonomy Levels

**Goal:** Dynamically adjust AI autonomy based on context.

**Autonomy Spectrum:**
```
Full Manual ←──────────────────────────→ Full Autonomous
    │          │           │           │
 Suggestions  Drafts   Autonomous   Self-Directed
   Only      + Review   Writing     World Evolution
```

**Tasks:**
- [ ] Create autonomy level configuration
- [ ] Implement context-based autonomy adjustment
- [ ] Add user trust calibration
- [ ] Create seamless handoff between modes
- [ ] Implement intervention points for user guidance

### 6.3 Explanation and Transparency

**Goal:** Make agent reasoning understandable to users.

**Tasks:**
- [ ] Implement reasoning trace visualization
- [ ] Create natural language explanations for decisions
- [ ] Add confidence indicators for suggestions
- [ ] Implement alternative path exploration UI
- [ ] Create agent thought bubble debugging mode

---

## Phase 7: Emergent AGI Behaviors (v4.5 → v5.0)

### 7.1 Self-Improvement Mechanisms

**Goal:** Agents learn and improve from experience.

**Tasks:**
- [ ] Implement feedback loop from story outcomes
- [ ] Create strategy evolution based on success metrics
- [ ] Add cross-session learning persistence
- [ ] Implement agent skill tree development
- [ ] Create meta-learning for faster adaptation

### 7.2 Collective Intelligence

**Goal:** Agent collective exceeds individual capabilities.

**Tasks:**
- [ ] Implement knowledge synthesis across agents
- [ ] Create distributed problem-solving
- [ ] Add emergent specialization discovery
- [ ] Implement collective memory consolidation
- [ ] Create wisdom accumulation over time

### 7.3 Open-Ended Creativity

**Goal:** Enable unbounded creative exploration.

**Tasks:**
- [ ] Remove artificial constraints on idea generation
- [ ] Implement divergent thinking promotion
- [ ] Create safe exploration of edge cases
- [ ] Add surprising but coherent narrative elements
- [ ] Implement boundary-pushing content generation

---

## Integration Checkpoints

### Milestone 1: Enhanced Foundation (Phase 1 Complete)
- [ ] AtomSpace integration functional
- [ ] Hierarchical memory operational
- [ ] Enhanced narrative reasoning deployed
- [ ] All existing tests passing
- [ ] Performance benchmarks met

### Milestone 2: Agent-Zero Core (Phase 2 Complete)
- [ ] Autonomous goal generation working
- [ ] Self-reflective agents operational
- [ ] Tool-using capability deployed
- [ ] Agent autonomy measurably improved
- [ ] User testing feedback incorporated

### Milestone 3: Swarm Orchestration (Phase 3 Complete)
- [ ] Dynamic agent spawning functional
- [ ] Swarm intelligence operational
- [ ] Hierarchical control working
- [ ] Multi-agent coordination smooth
- [ ] Emergent behaviors observed

### Milestone 4: Living World (Phase 4 Complete)
- [ ] World simulation running
- [ ] Character autonomy functional
- [ ] Dynamic events generating
- [ ] World persistence stable
- [ ] Narrative integration seamless

### Milestone 5: AGI Capabilities (Phase 5 Complete)
- [ ] Semantic understanding deployed
- [ ] Creative emergence working
- [ ] Emotional intelligence operational
- [ ] Novel content generation verified
- [ ] Quality metrics achieved

### Milestone 6: Collaboration (Phase 6 Complete)
- [ ] Intent understanding accurate
- [ ] Adaptive autonomy working
- [ ] Explanations clear and helpful
- [ ] User satisfaction measured
- [ ] Collaboration flow optimized

### Milestone 7: Emergent AGI (Phase 7 Complete)
- [ ] Self-improvement measurable
- [ ] Collective intelligence demonstrated
- [ ] Open-ended creativity validated
- [ ] Long-term stability confirmed
- [ ] AGI capabilities benchmarked

---

## Technical Specifications

### Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Agent Response Time | < 100ms | ~200ms |
| World State Update | < 50ms | ~80ms |
| Memory Retrieval | < 20ms | ~40ms |
| Narrative Coherence | > 0.85 | 0.72 |
| Goal Achievement Rate | > 75% | 65% |
| User Satisfaction | > 4.0/5 | TBD |

### Scalability Requirements

- Support 10+ concurrent agents
- Handle worlds with 1000+ locations
- Track 500+ active characters
- Manage 10000+ story events
- Persist across unlimited sessions

### Resource Constraints

- Memory: < 4GB additional for agent system
- CPU: Background tasks < 20% utilization
- Storage: < 100MB per world state
- Network: Minimal for offline operation

---

## Testing Strategy

### Unit Tests
```bash
pytest tests/opencog_integration/ -v
```

### Integration Tests
```bash
pytest tests/opencog_integration/test_kobold_integration.py -v
```

### Performance Tests
```bash
pytest tests/performance/ --benchmark
```

### Narrative Quality Tests
```bash
python -m opencog_integration.quality_assessment
```

---

## Contributing

### Adding New Agents

1. Create agent profile in `agent_orchestrator.py`
2. Define capabilities and traits
3. Implement specialized processing methods
4. Add to default agent creation
5. Write tests in `tests/opencog_integration/`

### Adding New World Features

1. Extend classes in `world_builder.py`
2. Add to world state serialization
3. Implement narrative integration hooks
4. Add procedural generation logic
5. Write tests and documentation

### Adding New Goals

1. Extend `GoalType` enum in `adventure_telos.py`
2. Create goal template with conditions
3. Implement progress tracking
4. Add to goal generation logic
5. Test with various narratives

---

## Dependencies

### Core Requirements
- Python 3.10+
- Flask 2.0+
- PyTorch 2.0+
- transformers 4.30+

### OpenCog Requirements (Future)
- opencog 0.14+
- atomspace 5.0+
- cogutil 2.0+

### Agent-Zero Requirements (Future)
- langchain 0.1+
- semantic-kernel 0.1+
- autogen 0.1+

---

## Glossary

| Term | Definition |
|------|------------|
| **AtomSpace** | OpenCog's hypergraph knowledge representation |
| **PLN** | Probabilistic Logic Networks for uncertain reasoning |
| **BDI** | Belief-Desire-Intention agent architecture |
| **Agent-Zero** | Self-directed autonomous agent framework |
| **Telos** | Goal-directed behavior system |
| **Stigmergy** | Indirect agent communication through environment |
| **Swarm Intelligence** | Collective behavior emergence from simple agents |

---

## References

- [OpenCog Hyperon](https://wiki.opencog.org/w/Hyperon)
- [Agent-Zero Framework](https://github.com/frdel/agent-zero)
- [KoboldAI Documentation](https://github.com/KoboldAI/KoboldAI-Client)
- [Autonomous Agents and Multi-Agent Systems](https://www.springer.com/journal/10458)
- [Narrative Intelligence](https://narrativeintelligence.org/)

---

## Changelog

### v1.19.2 (Current)
- Initial OpenCog integration complete
- Agent orchestrator implemented
- World builder operational
- Narrative engine functional
- Adventure telos system active

### v2.0 (Planned)
- AtomSpace integration
- Enhanced memory architecture
- Advanced narrative reasoning

### v2.5 (Planned)
- Agent-zero core implementation
- Self-reflective agents
- Tool-using capabilities

### v3.0 (Planned)
- Multi-agent orchestration
- Swarm intelligence
- Hierarchical control

---

*Last Updated: 2025-12-04*
*Maintained by: KogboldAI Development Team*
