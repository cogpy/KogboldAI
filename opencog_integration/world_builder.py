"""
World Builder Module

This module implements the world-building arena mythos framework that creates
and manages fictional worlds, mythologies, and settings within the OpenCog
integration system.
"""

import logging
import time
import json
import random
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

logger = logging.getLogger(__name__)


class WorldAspect(Enum):
    """Different aspects of world-building"""
    GEOGRAPHY = "geography"
    HISTORY = "history"
    CULTURE = "culture"
    POLITICS = "politics"
    ECONOMICS = "economics"
    RELIGION = "religion"
    MAGIC_SYSTEM = "magic_system"
    TECHNOLOGY = "technology"
    SOCIAL_STRUCTURE = "social_structure"
    NATURAL_LAWS = "natural_laws"


class MythosType(Enum):
    """Types of mythological elements"""
    CREATION_MYTH = "creation_myth"
    HERO_LEGEND = "hero_legend"
    DIVINE_PANTHEON = "divine_pantheon"
    ANCIENT_PROPHECY = "ancient_prophecy"
    FOLKLORE = "folklore"
    ORIGIN_STORY = "origin_story"
    COSMOLOGY = "cosmology"
    SACRED_RITUAL = "sacred_ritual"


class LocationType(Enum):
    """Types of locations in the world"""
    CITY = "city"
    VILLAGE = "village"
    WILDERNESS = "wilderness"
    DUNGEON = "dungeon"
    TEMPLE = "temple"
    CASTLE = "castle"
    RUINS = "ruins"
    MAGICAL_REALM = "magical_realm"
    NATURAL_WONDER = "natural_wonder"
    SETTLEMENT = "settlement"


@dataclass
class WorldLocation:
    """Represents a location in the world"""
    location_id: str
    name: str
    location_type: LocationType
    description: str
    coordinates: Tuple[float, float] = (0.0, 0.0)
    size_category: str = "medium"  # small, medium, large, massive
    population: int = 0
    notable_features: List[str] = field(default_factory=list)
    connected_locations: Dict[str, float] = field(default_factory=dict)  # location_id -> distance
    cultural_influences: List[str] = field(default_factory=list)
    historical_events: List[Dict[str, Any]] = field(default_factory=list)
    resources: Dict[str, int] = field(default_factory=dict)
    political_control: Optional[str] = None
    magical_properties: Dict[str, Any] = field(default_factory=dict)
    danger_level: float = 0.5
    accessibility: float = 0.7


@dataclass
class MythosElement:
    """Represents a mythological element"""
    mythos_id: str
    name: str
    mythos_type: MythosType
    narrative_content: str
    cultural_origin: str
    historical_period: str
    associated_locations: List[str] = field(default_factory=list)
    associated_characters: List[str] = field(default_factory=list)
    symbolic_meaning: Dict[str, str] = field(default_factory=dict)
    influence_scope: str = "local"  # local, regional, global
    truth_level: float = 0.5  # 0=pure myth, 1=historical fact
    narrative_power: float = 0.7


@dataclass
class CulturalGroup:
    """Represents a cultural group or civilization"""
    culture_id: str
    name: str
    population: int
    primary_locations: List[str]
    cultural_traits: Dict[str, float]  # trait_name -> strength (0-1)
    belief_systems: List[str]
    technologies: List[str]
    languages: List[str]
    government_type: str
    relations: Dict[str, float]  # other_culture_id -> relationship (-1 to 1)
    notable_achievements: List[str] = field(default_factory=list)
    current_conflicts: List[str] = field(default_factory=list)


class WorldBuilder:
    """
    World-building arena that creates and manages fictional worlds with
    rich mythologies, cultures, and interconnected narrative elements.
    """
    
    def __init__(self):
        self.world_name = "Unnamed World"
        self.world_seed = random.randint(1000, 9999)
        
        # Core world data
        self.locations: Dict[str, WorldLocation] = {}
        self.mythos_elements: Dict[str, MythosElement] = {}
        self.cultural_groups: Dict[str, CulturalGroup] = {}
        
        # World metadata
        self.world_aspects: Dict[WorldAspect, Dict[str, Any]] = {
            aspect: {} for aspect in WorldAspect
        }
        
        # Narrative connections
        self.location_network = defaultdict(dict)
        self.cultural_relations = defaultdict(dict)
        self.mythos_connections = defaultdict(list)
        
        # World generation parameters
        self.world_scale = "medium"  # small, medium, large, epic
        self.magic_level = 0.5  # 0=no magic, 1=high magic
        self.technology_level = "medieval"
        self.conflict_level = 0.4
        self.mystery_factor = 0.6
        
        # Generative rules and patterns
        self.naming_patterns = {
            'fantasy': ['elven', 'dwarven', 'ancient', 'mystical'],
            'historical': ['celtic', 'norse', 'roman', 'medieval'],
            'modern': ['contemporary', 'urban', 'technological']
        }
        
        self.world_themes = set()
        self.active_storylines = {}
        
    def initialize_world(self, world_config: Dict[str, Any]) -> bool:
        """Initialize a new world with the given configuration"""
        try:
            self.world_name = world_config.get('name', f'World_{self.world_seed}')
            self.world_scale = world_config.get('scale', 'medium')
            self.magic_level = world_config.get('magic_level', 0.5)
            self.technology_level = world_config.get('technology_level', 'medieval')
            self.world_themes = set(world_config.get('themes', []))
            
            # Generate initial world structure
            self._generate_initial_geography(world_config)
            self._generate_initial_cultures(world_config)
            self._generate_foundational_mythos(world_config)
            
            logger.info(f"Initialized world: {self.world_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize world: {e}")
            return False
    
    def _generate_initial_geography(self, config: Dict[str, Any]):
        """Generate initial geographical features and locations"""
        scale_multipliers = {
            'small': 3,
            'medium': 7,
            'large': 15,
            'epic': 30
        }
        
        num_locations = scale_multipliers.get(self.world_scale, 7)
        
        # Generate primary locations
        location_types = [
            LocationType.CITY,
            LocationType.VILLAGE,
            LocationType.WILDERNESS,
            LocationType.RUINS,
            LocationType.NATURAL_WONDER
        ]
        
        for i in range(num_locations):
            location_type = random.choice(location_types)
            location_id = self.create_location(
                name=self._generate_location_name(location_type),
                location_type=location_type,
                description=self._generate_location_description(location_type),
                auto_position=True
            )
            
            # Establish some connections
            if i > 0:
                existing_locations = list(self.locations.keys())[:i]
                for existing_id in random.sample(existing_locations, 
                                               min(2, len(existing_locations))):
                    self._establish_location_connection(location_id, existing_id)
    
    def _generate_initial_cultures(self, config: Dict[str, Any]):
        """Generate initial cultural groups"""
        num_cultures = max(1, len(self.locations) // 3)
        
        for i in range(num_cultures):
            culture_id = self.create_cultural_group(
                name=self._generate_culture_name(),
                government_type=random.choice(['monarchy', 'republic', 'tribal', 'theocracy']),
                population=random.randint(1000, 100000),
                primary_locations=self._select_culture_locations()
            )
    
    def _generate_foundational_mythos(self, config: Dict[str, Any]):
        """Generate foundational mythological elements"""
        mythos_types = [
            MythosType.CREATION_MYTH,
            MythosType.ORIGIN_STORY,
            MythosType.ANCIENT_PROPHECY
        ]
        
        for mythos_type in mythos_types:
            self.create_mythos_element(
                name=self._generate_mythos_name(mythos_type),
                mythos_type=mythos_type,
                narrative_content=self._generate_mythos_narrative(mythos_type),
                cultural_origin=list(self.cultural_groups.keys())[0] if self.cultural_groups else "ancient"
            )
    
    def create_location(self, name: str, location_type: LocationType, 
                       description: str, coordinates: Tuple[float, float] = None,
                       auto_position: bool = False) -> str:
        """Create a new location in the world"""
        
        location_id = f"{location_type.value}_{len(self.locations)}"
        
        if auto_position or coordinates is None:
            coordinates = self._generate_location_coordinates()
        
        location = WorldLocation(
            location_id=location_id,
            name=name,
            location_type=location_type,
            description=description,
            coordinates=coordinates
        )
        
        # Set appropriate defaults based on location type
        self._configure_location_defaults(location)
        
        self.locations[location_id] = location
        
        logger.info(f"Created location: {name} ({location_type.value})")
        return location_id
    
    def _configure_location_defaults(self, location: WorldLocation):
        """Configure default properties based on location type"""
        type_configs = {
            LocationType.CITY: {
                'population': random.randint(10000, 100000),
                'size_category': 'large',
                'danger_level': 0.2,
                'accessibility': 0.9
            },
            LocationType.VILLAGE: {
                'population': random.randint(100, 2000),
                'size_category': 'small',
                'danger_level': 0.1,
                'accessibility': 0.8
            },
            LocationType.WILDERNESS: {
                'population': 0,
                'size_category': 'large',
                'danger_level': 0.6,
                'accessibility': 0.4
            },
            LocationType.DUNGEON: {
                'population': 0,
                'size_category': 'medium',
                'danger_level': 0.9,
                'accessibility': 0.2
            },
            LocationType.RUINS: {
                'population': 0,
                'size_category': 'medium',
                'danger_level': 0.5,
                'accessibility': 0.5
            }
        }
        
        config = type_configs.get(location.location_type, {})
        
        for attr, value in config.items():
            if hasattr(location, attr):
                setattr(location, attr, value)
        
        # Add type-specific features
        self._add_location_features(location)
    
    def _add_location_features(self, location: WorldLocation):
        """Add notable features based on location type"""
        feature_sets = {
            LocationType.CITY: ['marketplace', 'walls', 'guild halls', 'temples'],
            LocationType.VILLAGE: ['inn', 'blacksmith', 'well', 'fields'],
            LocationType.WILDERNESS: ['forest', 'river', 'hills', 'wildlife'],
            LocationType.DUNGEON: ['traps', 'monsters', 'treasure', 'ancient magic'],
            LocationType.RUINS: ['crumbling walls', 'mysterious artifacts', 'overgrowth', 'echoes of the past'],
            LocationType.TEMPLE: ['altar', 'sacred texts', 'priests', 'divine presence'],
            LocationType.CASTLE: ['fortifications', 'throne room', 'armory', 'towers']
        }
        
        features = feature_sets.get(location.location_type, ['mysterious aura'])
        location.notable_features = random.sample(features, min(3, len(features)))
    
    def _generate_location_coordinates(self) -> Tuple[float, float]:
        """Generate random coordinates for a location"""
        # Simple random placement in a 100x100 grid
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        return (x, y)
    
    def _generate_location_name(self, location_type: LocationType) -> str:
        """Generate a name for a location"""
        prefixes = ['New', 'Old', 'Great', 'Little', 'North', 'South', 'East', 'West']
        
        base_names = {
            LocationType.CITY: ['Haven', 'Crossing', 'Gate', 'Port', 'Bridge'],
            LocationType.VILLAGE: ['Brook', 'Mill', 'Field', 'Glen', 'Dale'],
            LocationType.WILDERNESS: ['Woods', 'Forest', 'Marsh', 'Moor', 'Vale'],
            LocationType.RUINS: ['Fallen', 'Lost', 'Forgotten', 'Ancient', 'Broken'],
            LocationType.NATURAL_WONDER: ['Falls', 'Peak', 'Chasm', 'Spring', 'Grove']
        }
        
        names = base_names.get(location_type, ['Place'])
        
        if random.random() < 0.7:  # 70% chance of prefix
            return f"{random.choice(prefixes)} {random.choice(names)}"
        else:
            return random.choice(names)
    
    def _generate_location_description(self, location_type: LocationType) -> str:
        """Generate a description for a location"""
        templates = {
            LocationType.CITY: [
                "A bustling metropolis with towering walls and busy streets.",
                "A magnificent city where traders and nobles gather.",
                "An ancient city with a rich history and diverse population."
            ],
            LocationType.VILLAGE: [
                "A quiet village surrounded by peaceful countryside.",
                "A small farming community where everyone knows each other.",
                "A humble settlement nestled in a beautiful valley."
            ],
            LocationType.WILDERNESS: [
                "Untamed wilderness where few dare to venture.",
                "A vast expanse of natural beauty and hidden dangers.",
                "Wild lands filled with mystery and ancient secrets."
            ]
        }
        
        template_list = templates.get(location_type, ["A mysterious place."])
        return random.choice(template_list)
    
    def _establish_location_connection(self, location1_id: str, location2_id: str):
        """Establish a connection between two locations"""
        if location1_id not in self.locations or location2_id not in self.locations:
            return
        
        loc1 = self.locations[location1_id]
        loc2 = self.locations[location2_id]
        
        # Calculate distance
        distance = ((loc1.coordinates[0] - loc2.coordinates[0]) ** 2 + 
                   (loc1.coordinates[1] - loc2.coordinates[1]) ** 2) ** 0.5
        
        # Establish bidirectional connection
        loc1.connected_locations[location2_id] = distance
        loc2.connected_locations[location1_id] = distance
        
        # Update network graph
        self.location_network[location1_id][location2_id] = distance
        self.location_network[location2_id][location1_id] = distance
    
    def create_cultural_group(self, name: str, government_type: str, 
                            population: int, primary_locations: List[str]) -> str:
        """Create a new cultural group"""
        
        culture_id = f"culture_{len(self.cultural_groups)}"
        
        culture = CulturalGroup(
            culture_id=culture_id,
            name=name,
            population=population,
            primary_locations=primary_locations,
            cultural_traits=self._generate_cultural_traits(),
            belief_systems=self._generate_belief_systems(),
            technologies=self._generate_technologies(),
            languages=[f"{name} Common"],
            government_type=government_type,
            relations={}
        )
        
        self.cultural_groups[culture_id] = culture
        
        # Establish relations with existing cultures
        for existing_id in self.cultural_groups:
            if existing_id != culture_id:
                # Generate relationship (-1 to 1)
                relationship = random.uniform(-0.5, 0.5)
                culture.relations[existing_id] = relationship
                self.cultural_groups[existing_id].relations[culture_id] = relationship
        
        logger.info(f"Created cultural group: {name}")
        return culture_id
    
    def _generate_cultural_traits(self) -> Dict[str, float]:
        """Generate cultural traits for a group"""
        traits = [
            'militaristic', 'peaceful', 'scholarly', 'artistic', 'mercantile',
            'religious', 'individualistic', 'collectivist', 'innovative', 'traditional'
        ]
        
        selected_traits = random.sample(traits, random.randint(3, 6))
        return {trait: random.uniform(0.3, 0.9) for trait in selected_traits}
    
    def _generate_belief_systems(self) -> List[str]:
        """Generate belief systems for a culture"""
        systems = [
            'Ancestor Worship', 'Nature Worship', 'Divine Pantheon',
            'Monotheism', 'Philosophy of Balance', 'Elemental Spirits'
        ]
        return random.sample(systems, random.randint(1, 3))
    
    def _generate_technologies(self) -> List[str]:
        """Generate technologies based on world tech level"""
        tech_levels = {
            'primitive': ['fire', 'stone tools', 'basic agriculture'],
            'ancient': ['bronze working', 'writing', 'pottery', 'wheel'],
            'medieval': ['iron working', 'advanced agriculture', 'castle building', 'navigation'],
            'renaissance': ['printing', 'gunpowder', 'clockwork', 'optics'],
            'industrial': ['steam power', 'factories', 'railways', 'electricity'],
            'modern': ['computers', 'telecommunications', 'space travel', 'nuclear power']
        }
        
        available_techs = tech_levels.get(self.technology_level, tech_levels['medieval'])
        return random.sample(available_techs, random.randint(2, len(available_techs)))
    
    def _select_culture_locations(self) -> List[str]:
        """Select primary locations for a culture"""
        available_locations = list(self.locations.keys())
        if not available_locations:
            return []
        
        num_locations = min(random.randint(1, 3), len(available_locations))
        return random.sample(available_locations, num_locations)
    
    def _generate_culture_name(self) -> str:
        """Generate a name for a cultural group"""
        prefixes = ['High', 'Deep', 'Iron', 'Stone', 'River', 'Mountain', 'Forest', 'Desert']
        suffixes = ['folk', 'people', 'clan', 'tribe', 'nation', 'empire', 'kingdom']
        
        if random.random() < 0.6:
            return f"{random.choice(prefixes)} {random.choice(suffixes)}"
        else:
            return random.choice(suffixes).title()
    
    def create_mythos_element(self, name: str, mythos_type: MythosType,
                            narrative_content: str, cultural_origin: str) -> str:
        """Create a new mythological element"""
        
        mythos_id = f"{mythos_type.value}_{len(self.mythos_elements)}"
        
        mythos = MythosElement(
            mythos_id=mythos_id,
            name=name,
            mythos_type=mythos_type,
            narrative_content=narrative_content,
            cultural_origin=cultural_origin,
            historical_period=self._determine_historical_period(mythos_type)
        )
        
        self.mythos_elements[mythos_id] = mythos
        
        # Connect to relevant locations and cultures
        self._establish_mythos_connections(mythos_id)
        
        logger.info(f"Created mythos element: {name} ({mythos_type.value})")
        return mythos_id
    
    def _determine_historical_period(self, mythos_type: MythosType) -> str:
        """Determine appropriate historical period for mythos type"""
        period_mapping = {
            MythosType.CREATION_MYTH: "primordial",
            MythosType.ORIGIN_STORY: "ancient",
            MythosType.HERO_LEGEND: "legendary",
            MythosType.ANCIENT_PROPHECY: "ancient",
            MythosType.DIVINE_PANTHEON: "ancient",
            MythosType.FOLKLORE: "traditional",
            MythosType.COSMOLOGY: "primordial",
            MythosType.SACRED_RITUAL: "ancient"
        }
        
        return period_mapping.get(mythos_type, "unknown")
    
    def _establish_mythos_connections(self, mythos_id: str):
        """Establish connections between mythos and world elements"""
        mythos = self.mythos_elements[mythos_id]
        
        # Connect to relevant locations (based on cultural origin)
        origin_culture = None
        for culture_id, culture in self.cultural_groups.items():
            if culture_id == mythos.cultural_origin or culture.name == mythos.cultural_origin:
                origin_culture = culture
                break
        
        if origin_culture:
            mythos.associated_locations.extend(origin_culture.primary_locations)
        
        # Add to connections graph
        self.mythos_connections[mythos.cultural_origin].append(mythos_id)
    
    def _generate_mythos_name(self, mythos_type: MythosType) -> str:
        """Generate a name for a mythological element"""
        name_templates = {
            MythosType.CREATION_MYTH: ["The First {}", "Origin of {}", "The Great {}"],
            MythosType.HERO_LEGEND: ["Legend of {}", "The {}'s Tale", "Song of {}"],
            MythosType.DIVINE_PANTHEON: ["The {} Gods", "Divine {}", "Sacred {}"],
            MythosType.ANCIENT_PROPHECY: ["The {} Prophecy", "Oracle of {}", "Vision of {}"]
        }
        
        templates = name_templates.get(mythos_type, ["The {}"])
        template = random.choice(templates)
        
        elements = ['Dawn', 'Shadow', 'Fire', 'Water', 'Earth', 'Sky', 'Stars', 'Moon']
        element = random.choice(elements)
        
        return template.format(element)
    
    def _generate_mythos_narrative(self, mythos_type: MythosType) -> str:
        """Generate narrative content for a mythological element"""
        narratives = {
            MythosType.CREATION_MYTH: [
                "In the beginning, there was only void, until the first spark ignited creation.",
                "From the cosmic egg emerged the world, shaped by divine will and ancient magic.",
                "The world was born from the dreams of sleeping gods, each dream becoming reality."
            ],
            MythosType.HERO_LEGEND: [
                "A great hero arose in times of darkness, wielding legendary power against evil.",
                "The chosen champion faced impossible odds to save their people from destruction.",
                "Through courage and sacrifice, the hero's deeds became eternal legend."
            ],
            MythosType.ANCIENT_PROPHECY: [
                "It was foretold that in the darkest hour, a light would pierce the shadows.",
                "The ancient seers spoke of a time when the world would face its greatest trial.",
                "The prophecy speaks of signs and portents that herald great change."
            ]
        }
        
        narrative_list = narratives.get(mythos_type, ["A mysterious tale from ancient times."])
        return random.choice(narrative_list)
    
    def expand_world_region(self, center_location_id: str, expansion_theme: str) -> List[str]:
        """Expand the world around a specific location with a thematic focus"""
        if center_location_id not in self.locations:
            logger.error(f"Center location {center_location_id} not found")
            return []
        
        center = self.locations[center_location_id]
        new_location_ids = []
        
        # Determine expansion size based on theme and existing connections
        expansion_size = random.randint(2, 5)
        
        # Generate connected locations based on theme
        theme_location_types = self._get_theme_location_types(expansion_theme)
        
        for i in range(expansion_size):
            location_type = random.choice(theme_location_types)
            
            # Position near the center location
            offset_x = random.uniform(-10, 10)
            offset_y = random.uniform(-10, 10)
            new_coordinates = (
                center.coordinates[0] + offset_x,
                center.coordinates[1] + offset_y
            )
            
            location_id = self.create_location(
                name=self._generate_themed_location_name(location_type, expansion_theme),
                location_type=location_type,
                description=self._generate_themed_description(location_type, expansion_theme),
                coordinates=new_coordinates
            )
            
            new_location_ids.append(location_id)
            
            # Connect to center and potentially to each other
            self._establish_location_connection(center_location_id, location_id)
            
            if i > 0 and random.random() < 0.4:  # 40% chance of inter-connection
                self._establish_location_connection(new_location_ids[-2], location_id)
        
        logger.info(f"Expanded world region around {center.name} with theme '{expansion_theme}'")
        return new_location_ids
    
    def _get_theme_location_types(self, theme: str) -> List[LocationType]:
        """Get appropriate location types for a theme"""
        theme_mappings = {
            'wilderness': [LocationType.WILDERNESS, LocationType.NATURAL_WONDER],
            'civilization': [LocationType.CITY, LocationType.VILLAGE, LocationType.CASTLE],
            'mystery': [LocationType.RUINS, LocationType.TEMPLE, LocationType.MAGICAL_REALM],
            'adventure': [LocationType.DUNGEON, LocationType.RUINS, LocationType.WILDERNESS],
            'political': [LocationType.CASTLE, LocationType.CITY, LocationType.SETTLEMENT]
        }
        
        return theme_mappings.get(theme, list(LocationType))
    
    def _generate_themed_location_name(self, location_type: LocationType, theme: str) -> str:
        """Generate a location name that fits the theme"""
        theme_prefixes = {
            'wilderness': ['Wild', 'Untamed', 'Savage', 'Primal'],
            'mystery': ['Hidden', 'Secret', 'Lost', 'Forgotten', 'Ancient'],
            'adventure': ['Dangerous', 'Treacherous', 'Perilous', 'Bold'],
            'political': ['Royal', 'Noble', 'Imperial', 'Sovereign']
        }
        
        prefixes = theme_prefixes.get(theme, ['New', 'Great'])
        base_name = self._generate_location_name(location_type)
        
        if random.random() < 0.8:  # 80% chance of themed prefix
            return f"{random.choice(prefixes)} {base_name}"
        
        return base_name
    
    def _generate_themed_description(self, location_type: LocationType, theme: str) -> str:
        """Generate a themed description for a location"""
        base_description = self._generate_location_description(location_type)
        
        theme_additions = {
            'wilderness': "The untamed nature here speaks of ancient, primal forces.",
            'mystery': "An air of mystery and hidden secrets permeates this place.",
            'adventure': "This location promises excitement and danger for the bold.",
            'political': "The influence of rulers and nobles is strongly felt here."
        }
        
        addition = theme_additions.get(theme, "")
        
        if addition:
            return f"{base_description} {addition}"
        
        return base_description
    
    def generate_world_event(self, event_scope: str = "local") -> Dict[str, Any]:
        """Generate a world event that affects the ongoing narrative"""
        
        event_types = {
            'local': ['festival', 'conflict', 'discovery', 'natural_disaster', 'arrival'],
            'regional': ['war', 'alliance', 'plague', 'magical_phenomenon', 'migration'],
            'global': ['prophetic_fulfillment', 'divine_intervention', 'cataclysm', 'new_age']
        }
        
        available_events = event_types.get(event_scope, event_types['local'])
        event_type = random.choice(available_events)
        
        event = {
            'event_id': f"event_{int(time.time())}",
            'type': event_type,
            'scope': event_scope,
            'name': self._generate_event_name(event_type),
            'description': self._generate_event_description(event_type),
            'affected_locations': self._select_affected_locations(event_scope),
            'affected_cultures': self._select_affected_cultures(event_scope),
            'duration': self._determine_event_duration(event_type),
            'consequences': self._generate_event_consequences(event_type),
            'narrative_hooks': self._generate_narrative_hooks(event_type),
            'timestamp': time.time()
        }
        
        # Apply event effects to world state
        self._apply_event_effects(event)
        
        logger.info(f"Generated world event: {event['name']} ({event_scope})")
        return event
    
    def _generate_event_name(self, event_type: str) -> str:
        """Generate a name for a world event"""
        event_names = {
            'festival': ['Harvest Festival', 'Midsummer Celebration', 'Victory Day'],
            'conflict': ['Border Skirmish', 'Trade War', 'Succession Crisis'],
            'discovery': ['Ancient Ruins Found', 'New Trade Route', 'Magical Discovery'],
            'natural_disaster': ['Great Storm', 'Earthquake', 'Flood'],
            'war': ['The Great War', 'Campaign of Conquest', 'Liberation War'],
            'plague': ['The Wasting Sickness', 'Red Death', 'Mind Plague'],
            'cataclysm': ['The Sundering', 'World\'s End', 'The Great Collapse']
        }
        
        names = event_names.get(event_type, ['Mysterious Event'])
        return random.choice(names)
    
    def _generate_event_description(self, event_type: str) -> str:
        """Generate a description for a world event"""
        descriptions = {
            'festival': "A joyous celebration brings communities together in revelry.",
            'conflict': "Tensions escalate into open conflict between opposing forces.",
            'discovery': "A significant discovery changes understanding of the world.",
            'natural_disaster': "Nature unleashes its fury upon the land.",
            'war': "Nations clash in a struggle that will reshape the world.",
            'cataclysm': "A world-changing event threatens everything known."
        }
        
        return descriptions.get(event_type, "Something significant happens.")
    
    def _select_affected_locations(self, scope: str) -> List[str]:
        """Select locations affected by an event based on scope"""
        all_locations = list(self.locations.keys())
        
        if scope == 'local':
            return random.sample(all_locations, min(2, len(all_locations)))
        elif scope == 'regional':
            return random.sample(all_locations, min(len(all_locations) // 2, len(all_locations)))
        else:  # global
            return all_locations
    
    def _select_affected_cultures(self, scope: str) -> List[str]:
        """Select cultures affected by an event based on scope"""
        all_cultures = list(self.cultural_groups.keys())
        
        if scope == 'local':
            return random.sample(all_cultures, min(1, len(all_cultures)))
        elif scope == 'regional':
            return random.sample(all_cultures, min(len(all_cultures) // 2, len(all_cultures)))
        else:  # global
            return all_cultures
    
    def _determine_event_duration(self, event_type: str) -> int:
        """Determine event duration in days"""
        durations = {
            'festival': random.randint(1, 7),
            'conflict': random.randint(30, 365),
            'discovery': 1,  # Discovery is instantaneous, effects are permanent
            'natural_disaster': random.randint(1, 30),
            'war': random.randint(365, 365 * 3),
            'plague': random.randint(30, 365 * 2),
            'cataclysm': 1  # Instant but permanent effects
        }
        
        return durations.get(event_type, 30)
    
    def _generate_event_consequences(self, event_type: str) -> List[str]:
        """Generate consequences of an event"""
        consequences = {
            'festival': ['Improved morale', 'Strengthened community bonds', 'Economic boost'],
            'conflict': ['Casualties', 'Economic disruption', 'Political tension'],
            'discovery': ['New opportunities', 'Changed worldview', 'Potential dangers'],
            'natural_disaster': ['Destruction', 'Displacement', 'Resource scarcity'],
            'war': ['Massive casualties', 'Political restructuring', 'Economic collapse'],
            'cataclysm': ['World reshaped', 'Civilization threatened', 'New realities']
        }
        
        possible_consequences = consequences.get(event_type, ['Unknown effects'])
        return random.sample(possible_consequences, min(3, len(possible_consequences)))
    
    def _generate_narrative_hooks(self, event_type: str) -> List[str]:
        """Generate narrative hooks from an event"""
        hooks = {
            'festival': ['Mysterious visitor arrives', 'Competition with high stakes', 'Hidden agenda revealed'],
            'conflict': ['Heroes needed for mission', 'Innocent caught in crossfire', 'Secret alliance opportunity'],
            'discovery': ['Exploration required', 'Competing interests', 'Ancient guardians awakened'],
            'natural_disaster': ['Rescue mission needed', 'Survivors require aid', 'Cause investigation'],
            'war': ['Choose sides', 'Secret mission', 'Prevent escalation'],
            'cataclysm': ['Survive the chaos', 'Find new hope', 'Understand the cause']
        }
        
        possible_hooks = hooks.get(event_type, ['Investigate the situation'])
        return random.sample(possible_hooks, min(2, len(possible_hooks)))
    
    def _apply_event_effects(self, event: Dict[str, Any]):
        """Apply the effects of an event to the world state"""
        # Modify affected locations
        for location_id in event['affected_locations']:
            if location_id in self.locations:
                location = self.locations[location_id]
                
                # Add event to location history
                location.historical_events.append({
                    'event_id': event['event_id'],
                    'event_name': event['name'],
                    'timestamp': event['timestamp'],
                    'type': event['type']
                })
        
        # Update cultural relations based on event
        if event['type'] in ['conflict', 'war']:
            affected_cultures = event['affected_cultures']
            if len(affected_cultures) >= 2:
                # Worsen relations between affected cultures
                for i, culture1_id in enumerate(affected_cultures):
                    for culture2_id in affected_cultures[i+1:]:
                        if (culture1_id in self.cultural_groups and 
                            culture2_id in self.cultural_groups):
                            current_relation = self.cultural_groups[culture1_id].relations.get(culture2_id, 0.0)
                            new_relation = max(-1.0, current_relation - 0.3)
                            self.cultural_groups[culture1_id].relations[culture2_id] = new_relation
                            self.cultural_groups[culture2_id].relations[culture1_id] = new_relation
    
    def get_world_state(self) -> Dict[str, Any]:
        """Get comprehensive world state information"""
        return {
            'world_name': self.world_name,
            'world_seed': self.world_seed,
            'scale': self.world_scale,
            'magic_level': self.magic_level,
            'technology_level': self.technology_level,
            'themes': list(self.world_themes),
            'statistics': {
                'total_locations': len(self.locations),
                'total_cultures': len(self.cultural_groups),
                'total_mythos': len(self.mythos_elements),
                'location_connections': sum(len(loc.connected_locations) for loc in self.locations.values()) // 2,
                'cultural_relationships': sum(len(culture.relations) for culture in self.cultural_groups.values()) // 2
            },
            'recent_events': list(self.active_storylines.keys())[-5:],  # Last 5 events
            'world_parameters': {
                'conflict_level': self.conflict_level,
                'mystery_factor': self.mystery_factor
            }
        }
    
    def get_location_details(self, location_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific location"""
        if location_id not in self.locations:
            return None
        
        location = self.locations[location_id]
        
        # Find associated cultural groups
        associated_cultures = []
        for culture_id, culture in self.cultural_groups.items():
            if location_id in culture.primary_locations:
                associated_cultures.append({
                    'id': culture_id,
                    'name': culture.name,
                    'government': culture.government_type,
                    'influence': 'primary'
                })
        
        # Find relevant mythos
        relevant_mythos = []
        for mythos_id, mythos in self.mythos_elements.items():
            if location_id in mythos.associated_locations:
                relevant_mythos.append({
                    'id': mythos_id,
                    'name': mythos.name,
                    'type': mythos.mythos_type.value,
                    'influence': mythos.influence_scope
                })
        
        return {
            'location': location.__dict__,
            'associated_cultures': associated_cultures,
            'relevant_mythos': relevant_mythos,
            'nearby_locations': [
                {
                    'id': nearby_id,
                    'name': self.locations[nearby_id].name,
                    'distance': distance,
                    'type': self.locations[nearby_id].location_type.value
                }
                for nearby_id, distance in location.connected_locations.items()
                if nearby_id in self.locations
            ]
        }
    
    def suggest_narrative_opportunities(self, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest narrative opportunities based on current world state"""
        opportunities = []
        
        current_location = current_context.get('location_id')
        
        if current_location and current_location in self.locations:
            location = self.locations[current_location]
            
            # Suggest exploration of connected locations
            for connected_id in location.connected_locations:
                if connected_id in self.locations:
                    connected_location = self.locations[connected_id]
                    opportunities.append({
                        'type': 'exploration',
                        'title': f"Explore {connected_location.name}",
                        'description': f"Journey to the {connected_location.location_type.value} of {connected_location.name}",
                        'location_id': connected_id,
                        'difficulty': connected_location.danger_level,
                        'potential_rewards': ['discovery', 'adventure', 'knowledge']
                    })
            
            # Suggest cultural interactions
            for culture_id, culture in self.cultural_groups.items():
                if current_location in culture.primary_locations:
                    opportunities.append({
                        'type': 'cultural_interaction',
                        'title': f"Engage with {culture.name}",
                        'description': f"Interact with the {culture.government_type} culture of {culture.name}",
                        'culture_id': culture_id,
                        'difficulty': 0.3,
                        'potential_rewards': ['alliance', 'knowledge', 'resources']
                    })
            
            # Suggest mythos investigation
            for mythos_id, mythos in self.mythos_elements.items():
                if current_location in mythos.associated_locations:
                    opportunities.append({
                        'type': 'mythos_investigation',
                        'title': f"Investigate {mythos.name}",
                        'description': f"Delve into the {mythos.mythos_type.value}: {mythos.name}",
                        'mythos_id': mythos_id,
                        'difficulty': 1.0 - mythos.truth_level,
                        'potential_rewards': ['truth', 'power', 'understanding']
                    })
        
        # Sort by potential interest and difficulty balance
        opportunities.sort(key=lambda x: x.get('difficulty', 0.5))
        
        return opportunities[:5]  # Return top 5 opportunities