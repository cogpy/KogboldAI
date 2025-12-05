# OpenCog Autonomous Agent Orchestrator for KoboldAI

This module implements an OpenCog-inspired cognitive architecture for KoboldAI that provides autonomous user agent orchestration, adventure-driven narrative generation, and sophisticated world-building capabilities.

## Overview

The OpenCog integration now includes **seven main components** for KoboldAI:

1. **Agent Orchestrator** - Manages multiple autonomous cognitive agents that collaborate on story generation
2. **Adventure Telos** - Provides goal-oriented behavior and purpose-driven narrative agents  
3. **Narrative Engine** - Implements story-weaving logic and maintains narrative coherence
4. **World Builder** - Creates and manages fictional worlds with rich mythologies and interconnected elements
5. **AtomSpace Integration** *(NEW)* - Knowledge representation system for narrative elements using probabilistic logic
6. **Memory Hierarchy** *(NEW)* - Multi-level memory system with consolidation and retrieval
7. **KoboldAI Integration** - Seamless integration with KoboldAI's story generation

## Architecture

### AtomSpace Integration (`atomspace/`)

**NEW in Phase 1.1** - Complete knowledge representation system for narrative elements:

- **Atom Types** (`atom_types.py`): Defines narrative concepts, predicates, and relationships
  - ConceptNode: Characters, locations, events, themes
  - PredicateNode: Relationships like HasTrait, LocatedAt, CausedBy
  - Links: Evaluation, Inheritance, Causal, Temporal connections

- **AtomSpace Connector** (`atomspace_connector.py`): In-memory knowledge graph
  - Pattern matching and queries
  - Bidirectional sync with KoboldAI world state
  - Incoming/outgoing link navigation
  - Persistent storage capabilities

- **PLN Reasoning** (`pln_reasoning.py`): Probabilistic Logic Networks for story logic
  - Deduction, Abduction, Modus Ponens inference rules
  - Forward and backward chaining
  - Contradiction detection and resolution
  - Narrative likelihood computation
  - Truth values with confidence scores

Key features:
- OpenCog-compatible knowledge representation
- Logical inference over narrative elements
- Uncertain reasoning with confidence tracking
- Automatic narrative consistency checking

### Memory Hierarchy (`memory/`)

**NEW in Phase 1.2** - Complete hierarchical memory system inspired by human cognition:

- **Memory Types** (`hierarchy.py`):
  - **Sensory Memory**: Immediate perception (1-3 story beats, seconds-minutes)
  - **Working Memory**: Active narrative elements (~7 items, minutes-hours)
  - **Episodic Memory**: Story events with timestamps (long-term)
  - **Semantic Memory**: World knowledge and facts (long-term)
  - **Procedural Memory**: Writing patterns and style rules (long-term)

- **Memory Consolidation** (`consolidation.py`):
  - Automatic transfer from short-term to long-term storage
  - Importance and attention-based promotion
  - Forgetting mechanism for weak memories
  - Configurable consolidation rules
  - Background consolidation scheduler

- **Memory Retrieval** (`retrieval.py`):
  - Retrieval by importance, attention, recency, strength
  - Semantic similarity matching
  - Associative retrieval with spreading activation
  - Context-aware memory queries
  - Combined scoring with custom weights

Key features:
- Multi-level memory hierarchy
- Automatic memory consolidation
- Attention-based memory management
- Decay curves and forgetting
- Associative retrieval
- Thread-safe operations

### Agent Orchestrator (`agent_orchestrator.py`)

The Agent Orchestrator manages multiple cognitive agents that work together to enhance story generation:

- **CognitiveAgent**: Individual AI agents with their own memory, goals, and decision-making processes
- **AgentProfile**: Configuration defining agent personality, capabilities, and interaction preferences
- **Collaboration Matrix**: Tracks and manages agent-to-agent relationships and compatibility

Key features:
- Multi-agent coordination and collaboration
- Dynamic goal assignment and management
- Event-driven communication system
- Thread-safe operation with real-time processing

### Adventure Telos (`adventure_telos.py`)

The Adventure Telos system provides goal-oriented behavior for narrative agents:

- **Goal Types**: Exploration, character development, plot advancement, conflict resolution, etc.
- **Priority System**: Dynamic prioritization based on narrative context and urgency
- **Achievement Tracking**: Records completed goals and their narrative impact
- **Context-Aware Suggestions**: Generates appropriate goals based on current story state

Key features:
- Adventure-driven goal generation
- Narrative coherence scoring
- Automatic goal activation and completion
- Story impact assessment

### Narrative Engine (`narrative_engine.py`)

The Narrative Engine implements logical reasoning about story elements:

- **Narrative Graph**: Represents story elements and their logical relationships
- **Coherence Analysis**: Evaluates narrative consistency and identifies contradictions
- **Story Weaving**: Generates coherent narrative sequences using logical inference
- **Relationship Mapping**: Tracks causal, temporal, and thematic connections

Key features:
- Logical story progression
- Contradiction detection and resolution  
- Temporal and causal consistency checking
- Automated narrative element classification

### World Builder (`world_builder.py`)

The World Builder creates and manages rich fictional worlds:

- **Locations**: Cities, villages, wilderness areas, dungeons, and magical realms
- **Cultures**: Civilizations with their own traits, beliefs, technologies, and relationships
- **Mythology**: Creation myths, legends, prophecies, and divine pantheons
- **Dynamic Events**: World events that affect ongoing narratives

Key features:
- Procedural world generation
- Cultural relationship simulation
- Mythological framework creation
- Event-driven world evolution

### KoboldAI Integration (`kobold_integration.py`)

The integration module connects the cognitive architecture with KoboldAI:

- **Seamless Integration**: Automatic initialization with existing KoboldAI variables
- **Real-time Processing**: Continuous monitoring and enhancement of story generation
- **API Endpoints**: RESTful API for external access to OpenCog functionality
- **Session Management**: Support for multiple simultaneous story sessions

## Installation and Setup

The OpenCog integration is automatically initialized when KoboldAI starts if the modules are available. No additional installation is required beyond having the module files in the `opencog_integration` directory.

### Configuration

The integration can be configured using `KoboldIntegrationConfig`:

```python
config = KoboldIntegrationConfig(
    enabled=True,                    # Enable/disable integration
    auto_start_orchestration=True,   # Auto-start agent orchestration
    default_agent_count=3,           # Number of default agents
    world_auto_generation=True,      # Auto-generate default world
    integration_mode="collaborative" # collaborative, autonomous, advisory
)
```

## API Endpoints

The integration adds several new API endpoints to KoboldAI:

### GET `/api/v1/opencog/status`
Returns the current status of the OpenCog integration.

### POST `/api/v1/opencog/process_input`
Process user input through the cognitive architecture for enhanced story generation.

### GET `/api/v1/opencog/world_state`
Get current world state from the OpenCog world builder.

### GET `/api/v1/opencog/narrative_coherence`
Analyze narrative coherence using the OpenCog narrative engine.

### POST `/api/v1/opencog/generate_suggestions`
Generate story suggestions using the adventure telos system.

## Usage Examples

### Basic Usage

The OpenCog integration works automatically in the background once initialized. It:
- Monitors story generation and provides autonomous enhancements
- Maintains narrative coherence and world consistency
- Generates contextually appropriate suggestions
- Coordinates multiple AI agents for collaborative storytelling

### Programmatic Access

```python
from opencog_integration import get_integration

# Get the integration instance
integration = get_integration()

if integration:
    # Process user input
    result = integration.process_user_input("The hero entered the tavern.")
    
    # Get world state
    world_state = integration.world_builder.get_world_state()
    
    # Analyze narrative coherence
    coherence = integration.narrative_engine.analyze_narrative_coherence()
    
    # Generate suggestions
    suggestions = integration.adventure_telos.generate_adventure_suggestions(context)
```

### Using AtomSpace for Knowledge Representation

```python
from opencog_integration.atomspace import (
    AtomFactory, get_atomspace, get_atomspace_sync,
    PLNReasoner, NarrativeReasoner
)

# Get AtomSpace instance
atomspace = get_atomspace()

# Create narrative elements
hero = AtomFactory.create_character("Hero", traits={'brave': True, 'loyal': True})
villain = AtomFactory.create_character("Villain", traits={'cunning': True})
castle = AtomFactory.create_location("Castle", "Ancient fortress on a hill")

# Add to AtomSpace
atomspace.add_atom(hero)
atomspace.add_atom(villain)
atomspace.add_atom(castle)

# Create relationships
conflict = AtomFactory.create_relationship(
    hero, PredicateType.CONFLICTS_WITH, villain, strength=0.9
)
location = AtomFactory.create_location_link(hero, castle)

atomspace.add_atom(conflict)
atomspace.add_atom(location)

# Use PLN reasoning
pln = PLNReasoner(atomspace)
narrative_reasoner = NarrativeReasoner(atomspace)

# Find plot holes (contradictions)
contradictions = narrative_reasoner.find_plot_holes()

# Evaluate narrative coherence
coherence = narrative_reasoner.evaluate_narrative_coherence()
print(f"Narrative coherence: {coherence}")

# Sync with KoboldAI world state
sync = get_atomspace_sync()
world_state = {'characters': [...], 'locations': [...]}
sync.sync_from_kobold(world_state)
```

### Using Memory Hierarchy

```python
from opencog_integration.memory import (
    MemoryHierarchy, MemoryRetriever, MemoryQuery,
    ConsolidationScheduler
)

# Create memory hierarchy
memory = MemoryHierarchy()

# Add memories to different levels
memory.add_sensory("The dragon roars", importance=0.7)
memory.add_working("Hero draws sword", importance=0.8)
memory.add_episodic("Battle at dawn", timestamp=time.time(), importance=0.9)
memory.add_semantic("Dragons breathe fire", category="creatures", importance=0.8)
memory.add_procedural("Build tension before action", pattern_type="pacing")

# Retrieve memories
retriever = MemoryRetriever(memory)

# By importance
important_memories = retriever.retrieve_by_importance(top_k=5)

# By semantic similarity
similar = retriever.retrieve_by_semantic_similarity("dragon fight", top_k=3)

# Context-aware retrieval
context = {'characters': ['hero'], 'location': 'battlefield'}
relevant = retriever.retrieve_context_relevant(context, top_k=5)

# Query interface
query = MemoryQuery(memory)
results = query.query("dragon battle", top_k=10, use_associations=True)

# Start automatic consolidation
scheduler = ConsolidationScheduler(memory)
scheduler.start(interval=60.0)  # Consolidate every 60 seconds

# Or consolidate manually
results = scheduler.run_now()
print(f"Consolidated {results['total']} memories")

# Get statistics
stats = scheduler.get_stats()
print(f"Memory stats: {stats['memory']}")
print(f"Consolidation stats: {stats['consolidation']}")
```

### Custom Agent Creation

```python
from opencog_integration.agent_orchestrator import AgentProfile

# Create a custom agent
profile = AgentProfile(
    agent_id="custom_agent",
    name="Custom Story Agent",
    role="specialist",
    specialization="horror_writing",
    personality_traits={'creativity': 0.9, 'darkness': 0.8},
    capabilities=['atmosphere_creation', 'tension_building']
)

# Register with orchestrator
integration.orchestrator.register_agent(profile)
```

## Features

### Autonomous Operation
- Continuous monitoring of story generation
- Real-time narrative enhancement
- Automatic goal generation and management
- Dynamic agent coordination

### Cognitive Architecture
- Multi-agent reasoning and collaboration
- Goal-oriented behavior modeling
- Logical narrative inference
- Contextual decision making

### World Building
- Procedural world generation
- Dynamic cultural simulation
- Mythological framework creation
- Event-driven narrative evolution

### Narrative Coherence
- Logical consistency checking
- Contradiction detection and resolution
- Temporal relationship tracking
- Thematic coherence analysis

## Benefits

1. **Enhanced Storytelling**: Multi-agent collaboration provides richer, more diverse narrative perspectives
2. **Consistency Maintenance**: Automatic tracking and enforcement of world and character consistency
3. **Goal-Driven Narratives**: Purpose-driven story progression based on adventure goals and objectives
4. **Rich World Building**: Procedurally generated worlds with deep lore and interconnected elements
5. **Logical Coherence**: Maintains narrative logic and resolves contradictions automatically

## Technical Details

### Thread Safety
All components are designed to be thread-safe and can operate concurrently with KoboldAI's main processing loops.

### Performance
The integration is designed to have minimal impact on KoboldAI's performance, with most processing happening asynchronously in background threads.

### Extensibility
The modular architecture allows for easy extension and customization of individual components without affecting the overall system.

### Error Handling
Comprehensive error handling ensures that the integration gracefully handles failures without impacting KoboldAI's core functionality.

## Troubleshooting

### Integration Not Starting
- Check that all module files are present in the `opencog_integration` directory
- Verify no import errors in the KoboldAI logs
- Ensure sufficient system resources for multi-agent processing

### Performance Issues
- Reduce the number of default agents in the configuration
- Disable auto-start orchestration for manual control
- Monitor system resources and adjust accordingly

### API Errors
- Verify that the integration is properly initialized
- Check that the specific component (orchestrator, telos, etc.) is functioning
- Review error logs for specific failure details

## Future Enhancements

Planned future enhancements include:
- Integration with external OpenCog AtomSpace
- Machine learning-based agent personality development
- Advanced semantic reasoning for narrative elements
- Multi-modal story generation (text, images, audio)
- Collaborative human-AI story editing interfaces

## Contributing

To contribute to the OpenCog integration:
1. Follow the existing code architecture and patterns
2. Add comprehensive tests for new functionality
3. Update documentation for any new features
4. Ensure thread safety and error handling
5. Test integration with existing KoboldAI functionality

## License

This integration follows the same license as KoboldAI (AGPL). See the main KoboldAI LICENSE.md for details.