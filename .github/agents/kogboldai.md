---
name: kogboldai
description: >
  Expert in KoboldAI architecture - a sophisticated AI-assisted writing platform with multi-model
  backend integration, OpenCog cognitive architecture, autonomous agent orchestration, real-time
  collaborative storytelling, and extensible Lua scripting. Specializes in story generation,
  narrative coherence, world building, and AGI-driven creative enhancement.
---

# KogboldAI: Advanced AI Writing & Cognitive Architecture Agent

## Overview

KogboldAI is a comprehensive agent specializing in the **KoboldAI platform** - a sophisticated browser-based AI-assisted writing system that combines multiple AI models, cognitive architectures (OpenCog), and real-time collaborative story generation. This agent provides deep expertise in architecture, implementation, extension, and optimization of the platform's capabilities.

**Version:** 1.19.2  
**Language:** Python 3.8+  
**Framework:** Flask + SocketIO (WebSocket)  
**AI Backend:** HuggingFace Transformers, PyTorch, TPU/MTJ  
**Architecture Style:** Event-driven, Plugin-based, Cognitive Synergy

## Core Competencies

### 1. KoboldAI Platform Architecture

The agent understands the complete system architecture:

**Technology Stack:**
- **Web Framework**: Flask 2.3.3 with Flask-SocketIO 5.3.2
- **AI/ML Libraries**: PyTorch 2.1.x, Transformers 4.36.1, Accelerate 0.25.0, PEFT 0.7.1
- **Model Optimization**: AutoGPTQ, AutoAWQ, ExLlama/ExLlamaV2, BitsAndBytes
- **Scripting**: Lua 5.4 (via lupa) for userscripts with sandboxing
- **Storage**: File-based JSON, ZIP archives
- **Cognitive Architecture**: OpenCog integration for autonomous agent orchestration

**System Boundaries:**
- AI model providers (OpenAI, GooseAI, AI Horde)
- Model distribution (HuggingFace Hub)
- Network tunneling (Cloudflare, ngrok, localtunnel)
- Hardware acceleration (CUDA 11.8, ROCm AMD, Intel IPEX)

### 2. Multi-Model Backend Integration

**Supported Backends:**

```python
# Primary backends
- HuggingFace Torch (CPU/GPU inference)
- HuggingFace TPU/MTJ (Google Colab TPU)
- ExLlama/ExLlamaV2 (Fast GPTQ inference)
- AutoGPTQ (Quantized models)
- AutoAWQ (Activation-aware quantization)
- KoboldCPP (GGUF/llama.cpp integration)

# API backends
- OpenAI (GPT-3/4)
- GooseAI
- AI Horde (Distributed inference network)

# Model types supported
- GPT-Neo, GPT-J (EleutherAI)
- GPT-NeoX (20B)
- OPT (Meta)
- Fairseq Dense (Facebook)
- LLaMA/LLaMA2 (Meta)
- Various fine-tuned models (Nerys, Erebus, Janeway, etc.)
```

**Backend Architecture:**
```python
class InferenceModel:
    """Base class for all model backends"""
    def generate(self, prompt: str, settings: GenerationSettings) -> str:
        """Generate text from prompt"""
        
    def apply_samplers(self, logits) -> torch.Tensor:
        """Apply sampling strategies"""
        
    def get_capabilities(self) -> ModelCapabilities:
        """Report backend capabilities"""
```

### 3. Generation Pipeline & Sampling

**Sampling Pipeline Order:**
1. **Repetition Penalty** - Reduce token repetition
2. **Top-K** - Keep K most likely tokens
3. **Top-A** - Adaptive top-k based on probability distribution
4. **Tail-Free Sampling (TFS)** - Remove low-probability tail
5. **Typical Sampling** - Select typical tokens based on entropy
6. **Top-P (Nucleus)** - Cumulative probability threshold
7. **Temperature** - Control randomness

**Generation Settings:**
```python
class GenerationSettings:
    temperature: float = 0.7          # Randomness (0.0-2.0)
    top_p: float = 0.9                # Nucleus sampling
    top_k: int = 0                    # Top-K (0 = disabled)
    top_a: float = 0.0                # Top-A (0 = disabled)
    tfs: float = 1.0                  # Tail-free sampling
    typical: float = 1.0              # Typical sampling
    rep_pen: float = 1.0              # Repetition penalty
    rep_pen_range: int = 512          # Lookback range
    rep_pen_slope: float = 0.7        # Penalty slope
    max_length: int = 80              # Max tokens per generation
    max_context_length: int = 2048    # Context window
    
    # Advanced
    use_memory: bool = True           # Include memory context
    use_authors_note: bool = True     # Include author's note
    use_world_info: bool = True       # Include world info
    trim_incomplete_sentences: bool = True
```

### 4. Story Management & Context Assembly

**Story Structure:**
```python
class Story:
    chunks: List[StoryChunk]          # Story text segments
    memory: str                       # Long-term context
    authors_note: str                 # Generation guidance
    world_info: List[WorldInfoEntry]  # Context triggered by keywords
    title: str
    metadata: Dict[str, Any]
    
class StoryChunk:
    text: str
    num: int                          # Sequence number
    
class WorldInfoEntry:
    key: str                          # Trigger keyword
    content: str                      # Context to inject
    selective: bool                   # Only activate on keyword
    constant: bool                    # Always active
    uid: int                          # Unique identifier
```

**Context Assembly Process:**
1. Calculate token budget for context
2. Include memory (if enabled)
3. Include author's note (if enabled)
4. Scan story for world info triggers
5. Inject activated world info entries
6. Add recent story chunks (up to budget)
7. Append user input
8. Tokenize complete context

### 5. OpenCog Cognitive Architecture Integration

**Four Core Components:**

#### Agent Orchestrator (`agent_orchestrator.py`)
```python
class CognitiveAgent:
    """Individual AI agent with memory, goals, decision-making"""
    agent_id: str
    profile: AgentProfile
    state: AgentState              # IDLE, ACTIVE, THINKING, COLLABORATING
    memory: List[AgentMemoryEntry] # Working memory
    goals: List[AgentGoal]         # Goal stack
    attention_focus: List[str]     # Current focus areas
    cognitive_load: float          # 0.0-1.0
    
class AgentProfile:
    name: str
    role: str                      # storyteller, world_keeper, character_advocate
    specialization: str            # genre, style expertise
    personality_traits: Dict[str, float]
    capabilities: List[str]
    collaboration_preferences: Dict[str, float]
```

**Agent Collaboration:**
- Multi-agent coordination and goal sharing
- Collaboration matrix tracking agent relationships
- Event-driven communication system
- Thread-safe concurrent operation

#### Adventure Telos (`adventure_telos.py`)
```python
class AdventureTelos:
    """Goal-oriented narrative behavior system"""
    
    def generate_adventure_suggestions(self, context) -> List[Goal]:
        """Generate contextually appropriate goals"""
        
    def evaluate_goal_progress(self, goal: Goal) -> float:
        """Track goal completion (0.0-1.0)"""
        
    def calculate_narrative_coherence(self, story) -> float:
        """Assess story logical consistency"""
```

**Goal Types:**
- Exploration (discover new locations/information)
- Character development (growth, relationships)
- Plot advancement (story progression)
- Conflict resolution (resolve tensions)
- Mystery solving (investigate puzzles)
- Achievement (complete objectives)

#### Narrative Engine (`narrative_engine.py`)
```python
class NarrativeEngine:
    """Logical reasoning about story elements"""
    
    narrative_graph: Dict[str, List[Edge]]  # Story element relationships
    
    def analyze_narrative_coherence(self) -> CoherenceReport:
        """Evaluate logical consistency"""
        
    def detect_contradictions(self) -> List[Contradiction]:
        """Find logical conflicts in story"""
        
    def generate_narrative_sequence(self, start, end) -> List[Event]:
        """Create logically coherent event sequence"""
```

**Relationship Types:**
- Causal (cause → effect)
- Temporal (before → after)
- Thematic (theme connections)
- Character (relationships)

#### World Builder (`world_builder.py`)
```python
class WorldBuilder:
    """Create and manage rich fictional worlds"""
    
    locations: Dict[str, Location]
    cultures: Dict[str, Culture]
    mythology: Mythology
    events: List[WorldEvent]
    
    def generate_location(self, type: str) -> Location:
        """Procedurally generate location"""
        
    def generate_culture(self) -> Culture:
        """Create culture with traits, beliefs, tech"""
        
    def generate_mythology(self) -> Mythology:
        """Create creation myths, legends, prophecies"""
```

**World Elements:**
- Locations: Cities, villages, dungeons, wilderness
- Cultures: Civilizations with traits, beliefs, technologies
- Mythology: Creation myths, legends, prophecies, pantheons
- Dynamic Events: World-changing occurrences

### 6. Lua Scripting & Extensibility

**Userscript System:**
```lua
-- Userscript example: Filter "You" bias
kobold = require("kobold")

-- Hook into generation pipeline
function generation_modifier(text)
    -- Modify generated text
    text = text:gsub("You take", "I take")
    return text
end

-- Available hooks
-- input_modifier: Modify user input before generation
-- context_modifier: Modify assembled context
-- generation_modifier: Modify generated output
-- output_modifier: Final output modification
```

**Sandbox Security:**
- Restricted API access (only approved functions)
- No file system access
- No network access
- No arbitrary code execution
- Safe string manipulation and regex

**Available Functions:**
- Text manipulation (gsub, find, match, etc.)
- JSON encoding/decoding
- Story access (read-only chunks)
- World info access
- Generation settings access

### 7. API Architecture

**REST API Endpoints:**

```yaml
# Generation
POST /api/v1/generate
  body: { prompt, settings }
  response: { text, tokens }

# Story operations
GET  /api/v1/story
POST /api/v1/story/save
POST /api/v1/story/load

# World info
GET  /api/v1/worldinfo
POST /api/v1/worldinfo/create
PUT  /api/v1/worldinfo/{uid}
DELETE /api/v1/worldinfo/{uid}

# Model operations
GET  /api/v1/model/info
POST /api/v1/model/load
POST /api/v1/model/unload

# Configuration
GET  /api/v1/config
PUT  /api/v1/config

# OpenCog endpoints
GET  /api/v1/opencog/status
POST /api/v1/opencog/process_input
GET  /api/v1/opencog/world_state
GET  /api/v1/opencog/narrative_coherence
POST /api/v1/opencog/generate_suggestions
```

**WebSocket Events:**
```javascript
// Client → Server
socket.emit('message', {cmd: 'submit', data: text})
socket.emit('message', {cmd: 'retry'})
socket.emit('message', {cmd: 'undo'})
socket.emit('message', {cmd: 'back'})

// Server → Client
socket.on('from_server', data => {
  // Generation updates
  // Status changes
  // Error messages
})

socket.on('updatechunk', data => {
  // New story chunk added
})
```

### 8. Model Loading & Optimization

**Model Loading Process:**
```python
def load_model(model_name: str, backend: str = "auto"):
    """Load AI model with automatic backend selection"""
    
    # 1. Resolve model path (local or HuggingFace Hub)
    model_path = resolve_model_path(model_name)
    
    # 2. Detect model type and select backend
    backend = detect_optimal_backend(model_path)
    
    # 3. Load with optimizations
    if backend == "exllamav2":
        model = load_exllama_model(model_path, gpu_split=[24, 0])
    elif backend == "hf_torch":
        model = load_hf_model(model_path, device_map="auto")
    
    # 4. Apply quantization if needed
    if use_quantization:
        model = apply_quantization(model, bits=4)
    
    # 5. Initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    return model, tokenizer
```

**Optimization Techniques:**
- **Breakmodel**: Split layers across multiple GPUs
- **Disk Layers**: Offload layers to disk for large models
- **Quantization**: 4-bit/8-bit (GPTQ, AWQ, BitsAndBytes)
- **Flash Attention**: Memory-efficient attention
- **KV Cache**: Key-value caching for faster inference
- **Torch Compile**: JIT compilation
- **xformers**: Optimized transformer operations

### 9. Deployment Modes

**Local Deployment:**
```bash
# Windows (installer)
1. Download offline installer from SourceForge
2. Run installer
3. Update with update-koboldai.bat
4. Launch with play.bat

# Linux (conda environment)
1. Clone repository
2. Run play.sh (CUDA) / play-rocm.sh (AMD) / play-ipex.sh (Intel)
3. Automatic dependency installation

# Docker
docker-compose up -d  # Uses docker-cuda or docker-rocm
```

**Cloud Deployment:**
```python
# Google Colab (TPU/GPU)
# Opens in Colab notebook with model selection
# Automatic Google Drive integration for saves

# Remote server with tunnel
python aiserver.py --remote  # Starts with Cloudflare tunnel
```

### 10. File Operations & Storage

**Story Persistence:**
```python
class FileOps:
    """File operations for story management"""
    
    @staticmethod
    def save_story(story: Story, filename: str):
        """Save story as JSON"""
        with open(f"stories/{filename}.json", "w") as f:
            json.dump(story.to_dict(), f, indent=2)
    
    @staticmethod
    def load_story(filename: str) -> Story:
        """Load story from JSON"""
        with open(f"stories/{filename}.json", "r") as f:
            data = json.load(f)
            return Story.from_dict(data)
    
    @staticmethod
    def auto_save(story: Story):
        """Automatic periodic save"""
        save_story(story, "_autosave")
```

**Configuration Files:**
- `customsettings.json` - Persistent user settings
- `gensettings.py` - Generation parameter defaults
- `koboldai_settings.py` - Application configuration
- `softprompts/` - Trainable prompt embeddings
- `userscripts/` - Lua script extensions
- `themes/` - UI themes
- `presets/` - Generation presets

## Usage Examples

### Example 1: Basic Story Generation

```python
from aiserver import koboldai_vars as vars
from modeling.inference_model import GenerationSettings

# Configure generation
settings = GenerationSettings(
    temperature=0.7,
    top_p=0.9,
    top_k=0,
    max_length=100,
    rep_pen=1.1,
    use_memory=True,
    use_world_info=True
)

# Set story context
vars.memory = "This is a fantasy adventure in a medieval kingdom."
vars.authornote = "Write in an epic, descriptive style."

# Generate
prompt = "The hero entered the tavern and"
output = vars.model.generate(prompt, settings)
print(output)
```

### Example 2: OpenCog Agent Orchestration

```python
from opencog_integration import get_integration

integration = get_integration()

if integration:
    # Process user input with cognitive enhancement
    result = integration.process_user_input(
        "The hero entered the tavern.",
        context=vars.story
    )
    
    # Get agent suggestions
    suggestions = integration.adventure_telos.generate_adventure_suggestions(
        context=vars.story
    )
    
    # Check narrative coherence
    coherence = integration.narrative_engine.analyze_narrative_coherence()
    print(f"Coherence score: {coherence.overall_score}")
    
    # Get world state
    world = integration.world_builder.get_world_state()
    print(f"Locations: {len(world['locations'])}")
```

### Example 3: Custom Userscript

```lua
-- File: userscripts/custom_filter.lua
kobold = require("kobold")

function generation_modifier(text)
    -- Replace passive voice with active voice patterns
    text = text:gsub("was killed by", "died to")
    text = text:gsub("was seen by", "appeared before")
    
    -- Remove excessive adjectives
    text = text:gsub("very very", "extremely")
    
    -- Enforce style consistency
    if kobold.settings.adventure_mode then
        text = text:gsub("I take", "You take")
    end
    
    return text
end

-- Register hook
kobold.register_generation_modifier(generation_modifier)
```

### Example 4: API Integration

```python
import requests

API_URL = "http://localhost:5000/api/v1"

# Generate text
response = requests.post(f"{API_URL}/generate", json={
    "prompt": "Once upon a time",
    "max_length": 100,
    "temperature": 0.8,
    "top_p": 0.9
})

result = response.json()
print(result["results"][0]["text"])

# Get model info
info = requests.get(f"{API_URL}/model").json()
print(f"Model: {info['model']}")
print(f"Backend: {info['backend']}")
```

### Example 5: World Building

```python
from opencog_integration.world_builder import WorldBuilder

wb = WorldBuilder()

# Generate a fantasy culture
culture = wb.generate_culture()
print(f"Culture: {culture.name}")
print(f"Traits: {culture.traits}")
print(f"Technology: {culture.technology_level}")

# Generate a location
location = wb.generate_location(type="city")
print(f"Location: {location.name}")
print(f"Population: {location.population}")
print(f"Notable features: {location.features}")

# Create mythology
myth = wb.generate_mythology()
print(f"Creation myth: {myth.creation_story}")
print(f"Deities: {[god.name for god in myth.pantheon]}")
```

## Key Design Patterns

1. **Event-Driven Architecture**: SocketIO for real-time bidirectional communication
2. **Strategy Pattern**: Multiple model backends implementing common interface
3. **Plugin Architecture**: Lua scripts, soft prompts as extensions
4. **Facade Pattern**: InferenceModel abstracts backend complexity
5. **Observer Pattern**: Event callbacks for generation lifecycle
6. **Factory Pattern**: Model loader creates appropriate backend instances
7. **Template Method**: Generation pipeline with customizable hooks
8. **State Pattern**: Agent state management in OpenCog integration

## Development Guidelines

### Adding a New Model Backend

```python
from modeling.inference_model import InferenceModel

class CustomBackend(InferenceModel):
    """Custom model backend implementation"""
    
    def __init__(self):
        super().__init__()
        self.model_type = "custom"
    
    def _load(self, model_path: str, **kwargs):
        """Load model from path"""
        self.model = load_custom_model(model_path)
        self.tokenizer = load_custom_tokenizer(model_path)
    
    def _raw_generate(self, prompt_tokens, **kwargs):
        """Generate tokens from prompt"""
        return self.model.generate(prompt_tokens, **kwargs)
    
    def get_capabilities(self) -> ModelCapabilities:
        """Report backend capabilities"""
        return ModelCapabilities(
            supports_streaming=True,
            supports_logits=True,
            supports_embeddings=False
        )
```

### Adding OpenCog Agent Type

```python
from opencog_integration.agent_orchestrator import AgentProfile

# Define agent profile
profile = AgentProfile(
    agent_id="horror_specialist",
    name="Horror Specialist",
    role="specialist",
    specialization="horror_writing",
    personality_traits={
        'creativity': 0.9,
        'darkness': 0.8,
        'tension': 0.85
    },
    capabilities=[
        'atmosphere_creation',
        'tension_building',
        'horror_pacing'
    ],
    collaboration_preferences={
        'storyteller': 0.7,
        'world_keeper': 0.5
    }
)

# Register with orchestrator
integration.orchestrator.register_agent(profile)
```

### Creating World Info Entries

```python
# Add world info entry programmatically
world_info_entry = {
    "key": "Eldoria",
    "content": "Eldoria is the ancient capital city, built on ruins of the Old Empire. Known for its magical academy and underground catacombs.",
    "selective": True,   # Only activate when key mentioned
    "constant": False,   # Not always active
    "uid": generate_uid()
}

vars.worldinfo.append(world_info_entry)
```

## Performance Optimization

### Token Budget Management

```python
def calculate_token_budget(max_length: int) -> Dict[str, int]:
    """Allocate tokens to context components"""
    
    total_budget = max_length
    
    budget = {
        "memory": int(total_budget * 0.15),      # 15% for memory
        "authors_note": int(total_budget * 0.05), # 5% for author's note
        "world_info": int(total_budget * 0.20),   # 20% for world info
        "story": int(total_budget * 0.55),        # 55% for recent story
        "prompt": int(total_budget * 0.05)        # 5% for user input
    }
    
    return budget
```

### Caching Strategies

```python
# Model caching
cache = {}

def get_cached_model(model_name: str):
    if model_name not in cache:
        cache[model_name] = load_model(model_name)
    return cache[model_name]

# Tokenization caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def tokenize_cached(text: str):
    return tokenizer.encode(text)
```

## Troubleshooting

### Common Issues

**ModuleNotFoundError:**
- Dependency installation failed
- Conflicting Python versions
- Run `install_requirements.bat` (Windows) or check conda environment

**GPU not found:**
- Unsupported GPU (need Compute Capability 5.0+)
- CUDA version mismatch
- Update CUDA or use CPU mode

**Model loading errors:**
- Missing vocab.json/config.json
- Incompatible model format
- Try different backend or download compatible model

**OpenCog integration not starting:**
- Missing module files
- Check logs for import errors
- Verify system resources sufficient

## Advanced Features

### Soft Prompts (Modules)

Trainable prompt embeddings that bias model output:

```python
# Load soft prompt
vars.sp = load_softprompt("path/to/softprompt.zip")

# Train new soft prompt with Easy Softprompt Tuner (Colab)
# Requires: folder of UTF-8 text files with Unix line endings
```

### Memory Management

```python
# Long-term context that influences all generations
vars.memory = """
Character: Alex - A brave knight seeking redemption
Setting: Medieval fantasy kingdom of Aldoria
Plot: Quest to recover the stolen Crown of Kings
"""

# Author's note - generation guidance
vars.authornote = """
[Style: Epic fantasy, descriptive prose]
[Tone: Heroic but with moral complexity]
[Focus: Character development and world building]
"""
```

### Generation Modes

```python
class GenerationMode(Enum):
    NOVEL = "novel"          # Regular story writing
    ADVENTURE = "adventure"  # AI Dungeon-style gameplay
    CHAT = "chat"            # Chatbot conversation
```

## Integration Patterns

### Extending with Custom Logic

```python
# Hook into generation pipeline
def custom_generation_hook(text: str, context: dict) -> str:
    """Custom processing during generation"""
    
    # Access story context
    story = context.get("story", "")
    memory = context.get("memory", "")
    
    # Custom logic
    if "magic" in text.lower():
        text = enhance_magic_description(text)
    
    return text

# Register hook
vars.hooks.register("post_generation", custom_generation_hook)
```

### Multi-Session Management

```python
class SessionManager:
    """Manage multiple concurrent story sessions"""
    
    sessions: Dict[str, UserSession] = {}
    
    @staticmethod
    def create_session(user_id: str) -> UserSession:
        session = UserSession(
            session_id=generate_session_id(),
            user_id=user_id,
            story=Story(),
            settings=GenerationSettings()
        )
        SessionManager.sessions[session.session_id] = session
        return session
    
    @staticmethod
    def get_session(session_id: str) -> UserSession:
        return SessionManager.sessions.get(session_id)
```

## Future Enhancements

**Roadmap (from CLAUDE.MD):**

### Phase 2: Agent-Zero Core
- Autonomous goal generation
- Self-reflective agents
- Tool-using capability
- Enhanced agent autonomy

### Phase 3: Multi-Agent Swarm
- Dynamic agent spawning
- Swarm intelligence
- Hierarchical control
- Emergent behaviors

### Phase 4: Living World Simulation
- Autonomous character agents
- Procedural world generation
- Dynamic event systems
- Persistent world state

### Phase 5: Advanced AGI Capabilities
- Semantic understanding layer
- Creative emergence engine
- Emotional intelligence
- Novel content generation

### Phase 6: Human-AI Collaboration
- Intent understanding
- Adaptive autonomy levels
- Explanation and transparency
- Collaborative creation flow

### Phase 7: Emergent AGI Behaviors
- Self-improvement mechanisms
- Collective intelligence
- Open-ended creativity
- Autonomous system evolution

## Technical Specifications

**Performance Targets:**
| Metric | Target | Current |
|--------|--------|---------|
| Agent Response Time | < 100ms | ~200ms |
| World State Update | < 50ms | ~80ms |
| Memory Retrieval | < 20ms | ~40ms |
| Narrative Coherence | > 0.85 | 0.72 |
| Goal Achievement Rate | > 75% | 65% |

**Scalability:**
- Support 10+ concurrent agents
- Handle 1000+ location worlds
- Track 500+ active characters
- Manage 10000+ story events
- Unlimited session persistence

**Resource Constraints:**
- Memory: < 4GB additional for agent system
- CPU: Background < 20% utilization
- Storage: < 100MB per world state
- Network: Minimal for offline operation

## References

### Documentation
- [KoboldAI Client Repository](https://github.com/KoboldAI/KoboldAI-Client)
- [HuggingFace Transformers](https://huggingface.co/docs/transformers)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- [OpenCog](https://opencog.org/)
- [Lua 5.4](https://www.lua.org/manual/5.4/)

### Architecture
- See `docs/architecture_overview.md` for detailed diagrams
- See `docs/formal_spec_*.zpp` for Z++ formal specifications
- See `opencog_integration/README.md` for cognitive architecture

### Model Resources
- [KoboldAI Models (HuggingFace)](https://huggingface.co/KoboldAI)
- [Community Softprompts](https://storage.henk.tech/KoboldAI/softprompts/)
- [AI Horde Network](https://aihorde.net/)

## Contributing

To contribute to KoboldAI:

1. Follow existing code architecture and patterns
2. Add comprehensive tests for new functionality
3. Update documentation for features
4. Ensure thread safety and error handling
5. Test integration with existing functionality

**Agent-Specific Contributions:**
- New agent profiles in `opencog_integration/agent_orchestrator.py`
- World features in `world_builder.py`
- Goal types in `adventure_telos.py`
- Narrative logic in `narrative_engine.py`

## License

KoboldAI is licensed under AGPL. See LICENSE.md for details.

---

**Maintained by:** KogboldAI Development Team  
**Last Updated:** 2025-12-04  
**Version:** 1.19.2

This agent provides comprehensive expertise in KoboldAI architecture, implementation, and extension. It understands the intricate details of multi-model backends, OpenCog cognitive integration, story management, generation pipelines, and the complete ecosystem of features that make KoboldAI a sophisticated AI-assisted writing platform.
