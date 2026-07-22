"""Skills system for KutsakAI Web Agent Coder.

This module provides a modular skills architecture that allows easy extension
of functionality with reusable skill components.
"""

from .base_skill import BaseSkill, SkillRegistry, SkillExecutor
from .web_skills import (
    HTMLCSSGeneratorSkill,
    JavaScriptFormatterSkill,
    TailwindCSSHelperSkill,
    AccessibilityCheckerSkill,
    ResponsiveDesignTesterSkill
)

__all__ = [
    'BaseSkill',
    'SkillRegistry',
    'SkillExecutor',
    'HTMLCSSGeneratorSkill',
    'JavaScriptFormatterSkill',
    'TailwindCSSHelperSkill',
    'AccessibilityCheckerSkill',
    'ResponsiveDesignTesterSkill',
]
