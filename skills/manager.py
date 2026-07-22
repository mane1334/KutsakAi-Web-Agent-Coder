"""Skills manager for initializing and managing all available skills."""

import logging
from typing import Dict, Optional
from .base_skill import SkillRegistry, SkillExecutor
from .web_skills import (
    HTMLCSSGeneratorSkill,
    JavaScriptFormatterSkill,
    TailwindCSSHelperSkill,
    AccessibilityCheckerSkill,
    ResponsiveDesignTesterSkill
)


class SkillsManager:
    """Manager for initializing and managing skills."""

    def __init__(self):
        """Initialize skills manager."""
        self.logger = logging.getLogger("SkillsManager")
        self.registry = SkillRegistry()
        self.executor = SkillExecutor(self.registry)
        self._initialize_default_skills()

    def _initialize_default_skills(self) -> None:
        """Initialize all default skills."""
        default_skills = [
            HTMLCSSGeneratorSkill(),
            JavaScriptFormatterSkill(),
            TailwindCSSHelperSkill(),
            AccessibilityCheckerSkill(),
            ResponsiveDesignTesterSkill(),
        ]

        for skill in default_skills:
            self.registry.register(skill)
            self.logger.info(f"Initialized skill: {skill.metadata.name}")

    def get_skill(self, skill_name: str):
        """Get a registered skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Skill instance or None
        """
        return self.registry.get(skill_name)

    def list_skills(self, category: Optional[str] = None) -> Dict:
        """List all registered skills.
        
        Args:
            category: Optional category filter
            
        Returns:
            Dictionary of skills
        """
        return self.registry.list_skills(category=category, enabled_only=True)

    def get_skills_info(self) -> list:
        """Get information about all registered skills.
        
        Returns:
            List of skill information dictionaries
        """
        return self.registry.get_info_all()

    async def execute_skill(self, skill_name: str, **kwargs):
        """Execute a skill.
        
        Args:
            skill_name: Name of the skill to execute
            **kwargs: Skill-specific parameters
            
        Returns:
            SkillResult with execution status and data
        """
        return await self.executor.execute(skill_name, **kwargs)

    def get_execution_history(self, skill_name: Optional[str] = None, limit: int = 10):
        """Get execution history.
        
        Args:
            skill_name: Optional skill name filter
            limit: Maximum number of records
            
        Returns:
            List of execution history records
        """
        return self.executor.get_execution_history(skill_name=skill_name, limit=limit)
