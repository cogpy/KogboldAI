# KoboldAI Formal Architecture Documentation & Specifications

This directory contains comprehensive technical architecture documentation and formal Z++ specifications for the KoboldAI system.

## Overview

KoboldAI is a sophisticated AI-assisted writing platform that integrates multiple AI models, cognitive architectures (OpenCog), and real-time collaborative story generation. These documents provide both high-level architecture overviews and rigorous formal specifications of the system's behavior.

## Documentation Structure

### 1. Architecture Overview (`architecture_overview.md`)

Comprehensive visual architecture documentation with Mermaid diagrams covering:

- **Technology Stack**: Backend frameworks, AI/ML libraries, external integrations
- **System Architecture**: High-level component interactions
- **Component Flows**: Sequence diagrams showing request/response patterns
- **Data Flow**: Context assembly, generation pipeline, output processing
- **Model Backends**: Multiple inference engine integrations
- **OpenCog Integration**: Autonomous agent orchestration
- **Storage & Persistence**: File-based storage systems
- **API Architecture**: REST API and WebSocket endpoints
- **Security & Sandboxing**: Lua script sandbox, model security
- **Generation Pipeline**: Token sampling and selection process

**Key Features Documented:**
- 13 detailed Mermaid diagrams
- Component interaction flows
- Design patterns used
- Deployment modes
- Scalability considerations

### 2. Data Model Specification (`formal_spec_data_model.zpp`)

Formal Z++ specification of the KoboldAI data layer including:

**Base Types & Constants:**
- JSON-compatible value types
- Generation modes (novel, adventure, chatbot)
- Agent states for cognitive architecture
- Model backend types

**Core Data Structures:**
- `StoryChunk` - Individual story text segments
- `StoryRegister` - Ordered collection of story chunks
- `MemoryContext` - Long-term context information
- `AuthorsNote` - Generation guidance directives
- `WorldInfoEntry` - Context triggered by keywords
- `Story` - Complete story with metadata

**Model Configuration:**
- `GenerationParameters` - Sampling and generation control
- `ModelCapabilities` - Backend feature flags
- `ModelConfig` - Model loading configuration

**OpenCog Agent Models:**
- `AgentProfile` - Cognitive agent configuration
- `AgentMemoryEntry` - Individual memory items
- `AgentGoal` - Goal stack entries
- `CognitiveAgent` - Runtime agent state

**Session & Runtime:**
- `UserSession` - Active user session state
- `SoftPrompt` - Trainable prompt embeddings
- `LuaUserscript` - User-defined scripts
- `GenerationRequest/Result` - API request/response models

**Total:** 20+ formally specified schemas with complete invariants

### 3. System State Specification (`formal_spec_system_state.zpp`)

Formal specification of the complete runtime system state:

**Core Application State:**
- `LoadedModelState` - AI model runtime information
- `ActiveGeneration` - Ongoing generation tracking
- `SoftPromptState` - Active soft prompt state
- `LuaScriptState` - Lua runtime state
- `ApplicationConfig` - Global configuration

**Session Management:**
- `SessionManagerState` - Multi-session management
- `WebSocketState` - Real-time connection state

**OpenCog Cognitive Architecture:**
- `AgentOrchestratorState` - Agent coordination
- `NarrativeEngineState` - Story coherence tracking
- `WorldBuilderState` - Autonomous world generation
- `AdventureTelosState` - Goal-directed adventure management
- `OpenCogIntegrationState` - Overall integration state

**Complete System State:**
- `SystemState` - Top-level system state
- `InitSystemState` - Initialization specification

**State Predicates:**
- `SystemReady` - System operational readiness
- `CanGenerate` - Generation capability check
- `OpenCogActive` - Cognitive architecture operational
- `ModelLoadedSuccessfully` - Model verification

**Total:** 15+ state schemas with 50+ invariants

### 4. Operations Specification (`formal_spec_operations.zpp`)

Formal specification of all system operations (state transitions):

**Model Loading Operations:**
- `LoadModel` - Load AI model into memory
- `UnloadModel` - Unload model and free resources
- `ApplySoftPrompt` - Apply soft prompt to model

**Session Management Operations:**
- `CreateSession` - Create new user session
- `CloseSession` - Terminate session and cleanup
- `ConnectWebSocket` - Establish WebSocket connection

**Story Management Operations:**
- `LoadStory` - Load story from file
- `SaveStory` - Save story to file
- `AppendStoryChunk` - Add text to story

**Text Generation Operations:**
- `StartGeneration` - Initiate generation
- `GenerateToken` - Generate single token iteratively
- `CompleteGeneration` - Finalize generation
- `AbortGeneration` - Stop ongoing generation

**OpenCog Agent Operations:**
- `RegisterAgent` - Register cognitive agent
- `UpdateAgentState` - Change agent state
- `CoordinateAgents` - Multi-agent collaboration
- `UpdateNarrativeState` - Update narrative engine

**Lua Script Operations:**
- `LoadLuaScript` - Load userscript
- `ExecuteLuaHook` - Execute script hooks

**Composite Operations:**
- `FullGenerationPipeline` - Complete generation workflow
- `InitializeOpenCog` - Initialize cognitive architecture

**Total:** 20+ formally specified operations with pre/post-conditions

### 5. External Integrations Specification (`formal_spec_integrations.zpp`)

Formal contracts for external service integrations:

**AI Model Provider Integrations:**
- `OpenAIAPI` - OpenAI API (GPT-3/4)
- `OpenAIGenerationRequest` - OpenAI generation contract
- `GooseAIAPI` - GooseAI API integration
- `GooseAIGenerationRequest` - GooseAI generation contract
- `AIHordeAPI` - Distributed AI Horde network
- `AIHordeGenerationRequest` - Async generation submission
- `AIHordePollResult` - Result polling contract

**HuggingFace Hub Integration:**
- `HuggingFaceHub` - Model repository integration
- `DownloadModel` - Model download from Hub
- `CheckModelUpdate` - Version checking

**Network Tunneling Integrations:**
- `CloudflareTunnel` - Cloudflare tunnel integration
- `StartCloudflareTunnel` - Tunnel initialization
- `NgrokTunnel` - ngrok tunnel integration
- `StartNgrokTunnel` - ngrok initialization

**WebSocket Communication:**
- `WebSocketMessage` - Message format specification
- `ClientSubmitGeneration` - Client generation request
- `ServerSendUpdate` - Server update messages

**REST API Contracts:**
- `APIGenerateEndpoint` - POST /api/v1/generate
- `APIModelInfoEndpoint` - GET /api/v1/model

**Error Handling:**
- `APIRequestWithRetry` - Retry logic with backoff
- `ExternalServiceHealthCheck` - Service health verification

**Total:** 15+ integration contracts with error handling

## Z++ Formal Specification Language

These specifications use Z++ notation, an object-oriented extension of the Z formal specification language. Key notations used:

### Schema Notation
```
┌─ SchemaName ────────────────
│ variable : Type
│ 
│ /* Invariant predicates */
│ constraint_expression
└─────────────────────────────
```

### State Changes
- `ΔSystemState` - State before (unprimed) and after (primed) operation
- `ΞSystemState` - Read-only operation (state unchanged)
- `variable'` - Value after state change
- `variable` - Value before state change

### Common Symbols
- `∈` - Element of
- `∉` - Not element of
- `⊆` - Subset
- `∪` - Union
- `∩` - Intersection
- `∖` - Set difference
- `↦` - Maplet (key-value pair)
- `⟨⟩` - Empty sequence
- `^` - Sequence concatenation
- `#` - Cardinality (size)
- `∀` - For all
- `∃` - There exists
- `∧` - Logical AND
- `∨` - Logical OR
- `⇒` - Implies
- `ℕ` - Natural numbers
- `ℤ` - Integers
- `ℝ` - Real numbers
- `ℙ` - Power set

## Key Architectural Insights

### System Characteristics

1. **Event-Driven Architecture**: Real-time bidirectional communication via Flask-SocketIO
2. **Multi-Backend Support**: Pluggable model backends (HuggingFace, ExLlama, APIs)
3. **Cognitive Integration**: Optional OpenCog autonomous agent orchestration
4. **Extensibility**: Lua scripting sandbox for user customization
5. **State Management**: Session-based with WebSocket persistence

### Critical Invariants

From the formal specifications, key system invariants include:

1. **Model State**: `is_loaded ⇒ vocab_size > 0 ∧ max_sequence_length > 0`
2. **Generation**: Active generations must reference valid sessions
3. **Agent Collaboration**: Collaboration matrix is symmetric
4. **Memory Bounds**: Agent memory never exceeds capacity
5. **Token Budget**: Context must fit within model limits
6. **Tunneling**: Only one tunnel service active at a time

### Security Boundaries

1. **Lua Sandbox**: Restricted API access, no file system or network access
2. **Model Loading**: Restricted unpickler prevents arbitrary code execution
3. **WebSocket**: Session-based authentication
4. **API**: Input validation via Marshmallow schemas

## Verification & Validation

These formal specifications enable:

1. **Property Checking**: Verify system invariants hold
2. **Operation Correctness**: Validate pre/post-conditions
3. **Integration Contracts**: Verify external API interactions
4. **State Consistency**: Ensure state transitions maintain invariants
5. **Concurrency Safety**: Identify race conditions in multi-session scenarios

## Usage Guide

### For Developers

- **Understanding Architecture**: Start with `architecture_overview.md`
- **Implementing Features**: Reference `formal_spec_operations.zpp`
- **Debugging**: Check state invariants in `formal_spec_system_state.zpp`
- **Integration**: Consult `formal_spec_integrations.zpp`

### For Researchers

- **Formal Verification**: Use Z++ specs as basis for theorem proving
- **Property Analysis**: Extract and verify system properties
- **Architecture Analysis**: Understand design decisions and trade-offs

### For Security Auditors

- **Security Boundaries**: Review sandbox and validation specs
- **Attack Surface**: Analyze external integration contracts
- **Invariant Violations**: Check for exploitable state inconsistencies

## Methodology

This documentation was generated using:

1. **Static Code Analysis**: Examination of Python source code
2. **Architecture Recovery**: Reverse engineering from implementation
3. **Formal Modeling**: Translation to Z++ formal notation
4. **Validation**: Cross-reference with existing tests and API documentation

## Maintenance

These specifications should be updated when:

- New model backends are added
- API endpoints change
- State management is modified
- External integrations are added/removed
- OpenCog components are enhanced

## Version History

- **v1.0.0** (2025-12-04): Initial formal specification
  - Complete architecture documentation
  - Data model formalization (20+ schemas)
  - System state specification (15+ schemas)
  - Operations specification (20+ operations)
  - External integrations specification (15+ contracts)

## References

### Formal Methods
- **Z Notation**: ISO/IEC 13568:2002 Standard
- **Z++**: Object-oriented extension of Z
- **Formal Specification**: System behavior modeling

### KoboldAI
- **Repository**: https://github.com/KoboldAI/KoboldAI-Client
- **Version**: 1.19.2
- **Documentation**: README.md

### Related Technologies
- **Flask**: https://flask.palletsprojects.com/
- **Flask-SocketIO**: https://flask-socketio.readthedocs.io/
- **HuggingFace**: https://huggingface.co/docs
- **PyTorch**: https://pytorch.org/docs/
- **OpenCog**: https://opencog.org/

## License

This documentation is provided as part of the KoboldAI project and follows the same AGPL license as the main project.

## Contributing

To contribute to this documentation:

1. Understand the Z++ notation
2. Analyze the relevant source code
3. Update or add specifications
4. Ensure consistency with existing schemas
5. Validate invariants and operations
6. Submit for review

## Contact

For questions about these specifications:
- Open an issue in the KoboldAI repository
- Reference the specific specification file and line number
- Provide context about the use case or concern
