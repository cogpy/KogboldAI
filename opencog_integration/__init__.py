"""
OpenCog Integration Module for KoboldAI

This module provides OpenCog cognitive architecture integration for autonomous
user agent orchestration in KoboldAI, enabling sophisticated story generation
and world-building through cognitive reasoning.
"""

from .agent_orchestrator import AgentOrchestrator
from .narrative_engine import NarrativeEngine  
from .world_builder import WorldBuilder
from .adventure_telos import AdventureTelos

__version__ = "1.0.0"
__author__ = "KoboldAI OpenCog Integration Team"

__all__ = [
    "AgentOrchestrator",
    "NarrativeEngine", 
    "WorldBuilder",
    "AdventureTelos"
]