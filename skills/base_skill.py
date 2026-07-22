"""Base skill class and registry for extensible skill system."""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class SkillStatus(Enum):
    """Skill execution status."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


@dataclass
class SkillMetadata:
    """Metadata for a skill."""
    name: str
    version: str
    description: str
    category: str
    icon: str = "⚙️"
    author: str = "KutsakAI"
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True
    tags: List[str] = field(default_factory=list)


@dataclass
class SkillResult:
    """Result of skill execution."""
    status: SkillStatus
    data: Any = None
    error: Optional[str] = None
    message: str = ""
    execution_time: float = 0.0
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'status': self.status.value,
            'data': self.data,
            'error': self.error,
            'message': self.message,
            'execution_time': self.execution_time,
            'warnings': self.warnings
        }


class BaseSkill(ABC):
    """Base class for all skills."""

    def __init__(self, metadata: SkillMetadata):
        """Initialize skill.
        
        Args:
            metadata: Skill metadata
        """
        self.metadata = metadata
        self.logger = logging.getLogger(f"skill.{metadata.name}")
        self.status = SkillStatus.IDLE
        self._callbacks: Dict[str, List[Callable]] = {
            'on_start': [],
            'on_success': [],
            'on_error': [],
            'on_complete': []
        }

    @abstractmethod
    async def execute(self, **kwargs) -> SkillResult:
        """Execute the skill.
        
        Args:
            **kwargs: Skill-specific parameters
            
        Returns:
            SkillResult with execution status and data
        """
        pass

    def validate_input(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate skill input.
        
        Args:
            **kwargs: Input parameters
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        return True, None

    def on_callback(self, event: str, callback: Callable) -> None:
        """Register callback for skill events.
        
        Args:
            event: Event name (on_start, on_success, on_error, on_complete)
            callback: Callback function
        """
        if event in self._callbacks:
            self._callbacks[event].append(callback)

    def _emit_callback(self, event: str, *args, **kwargs) -> None:
        """Emit callback event.
        
        Args:
            event: Event name
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        if event in self._callbacks:
            for callback in self._callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    self.logger.error(f"Error in callback {event}: {e}")

    def get_info(self) -> Dict[str, Any]:
        """Get skill information.
        
        Returns:
            Dictionary with skill metadata
        """
        return {
            'name': self.metadata.name,
            'version': self.metadata.version,
            'description': self.metadata.description,
            'category': self.metadata.category,
            'icon': self.metadata.icon,
            'author': self.metadata.author,
            'enabled': self.metadata.enabled,
            'tags': self.metadata.tags,
            'dependencies': self.metadata.dependencies,
        }


class SkillRegistry:
    """Registry for managing skills."""

    def __init__(self):
        """Initialize skill registry."""
        self._skills: Dict[str, BaseSkill] = {}
        self.logger = logging.getLogger("SkillRegistry")

    def register(self, skill: BaseSkill) -> None:
        """Register a skill.
        
        Args:
            skill: Skill instance to register
        """
        skill_name = skill.metadata.name
        if skill_name in self._skills:
            self.logger.warning(f"Skill '{skill_name}' already registered, overwriting")
        self._skills[skill_name] = skill
        self.logger.info(f"Skill '{skill_name}' registered")

    def unregister(self, skill_name: str) -> bool:
        """Unregister a skill.
        
        Args:
            skill_name: Name of skill to unregister
            
        Returns:
            True if skill was unregistered, False if not found
        """
        if skill_name in self._skills:
            del self._skills[skill_name]
            self.logger.info(f"Skill '{skill_name}' unregistered")
            return True
        return False

    def get(self, skill_name: str) -> Optional[BaseSkill]:
        """Get a registered skill.
        
        Args:
            skill_name: Name of skill to retrieve
            
        Returns:
            Skill instance or None if not found
        """
        return self._skills.get(skill_name)

    def list_skills(self, category: Optional[str] = None, enabled_only: bool = False) -> Dict[str, BaseSkill]:
        """List registered skills.
        
        Args:
            category: Filter by category (optional)
            enabled_only: Only return enabled skills
            
        Returns:
            Dictionary of skill name to skill instance
        """
        result = {}
        for name, skill in self._skills.items():
            if enabled_only and not skill.metadata.enabled:
                continue
            if category and skill.metadata.category != category:
                continue
            result[name] = skill
        return result

    def get_info_all(self) -> List[Dict[str, Any]]:
        """Get information for all registered skills.
        
        Returns:
            List of skill information dictionaries
        """
        return [skill.get_info() for skill in self._skills.values()]


class SkillExecutor:
    """Executor for running skills."""

    def __init__(self, registry: SkillRegistry):
        """Initialize skill executor.
        
        Args:
            registry: SkillRegistry instance
        """
        self.registry = registry
        self.logger = logging.getLogger("SkillExecutor")
        self._execution_history: List[Dict[str, Any]] = []

    async def execute(self, skill_name: str, **kwargs) -> SkillResult:
        """Execute a skill.
        
        Args:
            skill_name: Name of skill to execute
            **kwargs: Skill-specific parameters
            
        Returns:
            SkillResult with execution status and data
        """
        skill = self.registry.get(skill_name)
        if not skill:
            return SkillResult(
                status=SkillStatus.ERROR,
                error=f"Skill '{skill_name}' not found",
                message=f"Skill '{skill_name}' not found in registry"
            )

        if not skill.metadata.enabled:
            return SkillResult(
                status=SkillStatus.ERROR,
                error=f"Skill '{skill_name}' is disabled",
                message=f"Skill '{skill_name}' is currently disabled"
            )

        is_valid, error_msg = skill.validate_input(**kwargs)
        if not is_valid:
            return SkillResult(
                status=SkillStatus.ERROR,
                error="Invalid input",
                message=error_msg or "Input validation failed"
            )

        try:
            import time
            start_time = time.time()
            skill._emit_callback('on_start', skill_name, kwargs)
            
            result = await skill.execute(**kwargs)
            result.execution_time = time.time() - start_time
            
            if result.status == SkillStatus.SUCCESS:
                skill._emit_callback('on_success', skill_name, result)
            elif result.status == SkillStatus.ERROR:
                skill._emit_callback('on_error', skill_name, result)
            
            skill._emit_callback('on_complete', skill_name, result)
            self._record_execution(skill_name, result)
            
            return result
        except Exception as e:
            self.logger.error(f"Error executing skill '{skill_name}': {e}")
            result = SkillResult(
                status=SkillStatus.ERROR,
                error=str(e),
                message=f"Unexpected error executing skill '{skill_name}'"
            )
            skill._emit_callback('on_error', skill_name, result)
            skill._emit_callback('on_complete', skill_name, result)
            self._record_execution(skill_name, result)
            return result

    def _record_execution(self, skill_name: str, result: SkillResult) -> None:
        """Record skill execution in history.
        
        Args:
            skill_name: Name of executed skill
            result: Execution result
        """
        import time
        self._execution_history.append({
            'skill': skill_name,
            'timestamp': time.time(),
            'status': result.status.value,
            'execution_time': result.execution_time
        })
        if len(self._execution_history) > 100:
            self._execution_history = self._execution_history[-100:]

    def get_execution_history(self, skill_name: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get execution history.
        
        Args:
            skill_name: Filter by skill name (optional)
            limit: Maximum number of records to return
            
        Returns:
            List of execution history records
        """
        history = self._execution_history
        if skill_name:
            history = [h for h in history if h['skill'] == skill_name]
        return history[-limit:]
