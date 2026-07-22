"""Web development skills for KutsakAI."""

import asyncio
import re
import json
from typing import Dict, Any, List, Optional
from .base_skill import BaseSkill, SkillMetadata, SkillResult, SkillStatus


class HTMLCSSGeneratorSkill(BaseSkill):
    """Skill for generating HTML and CSS code."""

    def __init__(self):
        """Initialize HTML/CSS generator skill."""
        metadata = SkillMetadata(
            name="html_css_generator",
            version="1.0.0",
            description="Generate semantic HTML and optimized CSS code",
            category="web_generation",
            icon="🏗️",
            tags=["html", "css", "generation", "semantic"]
        )
        super().__init__(metadata)

    def validate_input(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate HTML/CSS generator input."""
        if 'component_type' not in kwargs:
            return False, "Missing 'component_type' parameter"
        if 'description' not in kwargs:
            return False, "Missing 'description' parameter"
        return True, None

    async def execute(self, **kwargs) -> SkillResult:
        """Generate HTML and CSS."""
        try:
            component_type = kwargs.get('component_type', '').lower()
            description = kwargs.get('description', '')
            framework = kwargs.get('framework', 'tailwind').lower()

            html_code = self._generate_html(component_type, description)
            css_code = self._generate_css(component_type, framework)

            return SkillResult(
                status=SkillStatus.SUCCESS,
                data={
                    'html': html_code,
                    'css': css_code,
                    'component_type': component_type,
                    'framework': framework
                },
                message=f"Generated {component_type} component"
            )
        except Exception as e:
            return SkillResult(
                status=SkillStatus.ERROR,
                error=str(e),
                message="Failed to generate HTML/CSS"
            )

    def _generate_html(self, component_type: str, description: str) -> str:
        """Generate HTML code."""
        templates = {
            'button': f'''<button class="btn" aria-label="{description}">
  {description}
</button>''',
            'card': f'''<article class="card">
  <header class="card-header">
    <h2>{description}</h2>
  </header>
  <section class="card-content">
    <!-- Content goes here -->
  </section>
  <footer class="card-footer">
    <!-- Footer content -->
  </footer>
</article>''',
            'form': f'''<form aria-label="{description}">
  <fieldset>
    <legend>{description}</legend>
    
    <div class="form-group">
      <label for="input-1">Input Label</label>
      <input type="text" id="input-1" name="input-1" required>
    </div>
    
    <button type="submit" class="btn-primary">Submit</button>
  </fieldset>
</form>''',
            'header': f'''<header role="banner">
  <nav aria-label="Main navigation">
    <h1>{description}</h1>
    <ul>
      <li><a href="#">Home</a></li>
      <li><a href="#">About</a></li>
      <li><a href="#">Contact</a></li>
    </ul>
  </nav>
</header>''',
        }
        return templates.get(component_type, f'<div class="{component_type}">{description}</div>')

    def _generate_css(self, component_type: str, framework: str) -> str:
        """Generate CSS code."""
        if framework == 'tailwind':
            return self._generate_tailwind_css(component_type)
        else:
            return self._generate_vanilla_css(component_type)

    def _generate_tailwind_css(self, component_type: str) -> str:
        """Generate Tailwind CSS classes."""
        classes = {
            'button': 'px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition',
            'card': 'rounded-lg shadow-md bg-white p-6 hover:shadow-lg transition',
            'form': 'space-y-4',
            'header': 'bg-gray-800 text-white p-4'
        }
        return f".{component_type} {{{classes.get(component_type, '')}\n}}"

    def _generate_vanilla_css(self, component_type: str) -> str:
        """Generate vanilla CSS."""
        css_templates = {
            'button': '''button {
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #0056b3;
}''',
            'card': '''article {
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  background: white;
  padding: 20px;
  transition: box-shadow 0.3s;
}

article:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}''',
        }
        return css_templates.get(component_type, f".{component_type} {{\n  /* Add your styles here */\n}}")


class JavaScriptFormatterSkill(BaseSkill):
    """Skill for formatting and optimizing JavaScript code."""

    def __init__(self):
        """Initialize JavaScript formatter skill."""
        metadata = SkillMetadata(
            name="javascript_formatter",
            version="1.0.0",
            description="Format, optimize, and validate JavaScript code",
            category="web_optimization",
            icon="⚡",
            tags=["javascript", "formatter", "optimization"]
        )
        super().__init__(metadata)

    def validate_input(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate JavaScript formatter input."""
        if 'code' not in kwargs:
            return False, "Missing 'code' parameter"
        return True, None

    async def execute(self, **kwargs) -> SkillResult:
        """Format JavaScript code."""
        try:
            code = kwargs.get('code', '')
            style = kwargs.get('style', 'expanded')
            optimize = kwargs.get('optimize', True)

            formatted = self._format_code(code, style)
            if optimize:
                formatted = self._optimize_code(formatted)

            issues = self._validate_code(code)

            result_data = {
                'formatted_code': formatted,
                'original_length': len(code),
                'formatted_length': len(formatted),
                'reduction_percentage': ((len(code) - len(formatted)) / len(code) * 100) if code else 0
            }

            if issues:
                result_data['issues'] = issues
                return SkillResult(
                    status=SkillStatus.SUCCESS,
                    data=result_data,
                    message=f"Formatted code with {len(issues)} issues found",
                    warnings=[f"Issue: {issue}" for issue in issues]
                )

            return SkillResult(
                status=SkillStatus.SUCCESS,
                data=result_data,
                message="Code formatted successfully"
            )
        except Exception as e:
            return SkillResult(
                status=SkillStatus.ERROR,
                error=str(e),
                message="Failed to format JavaScript"
            )

    def _format_code(self, code: str, style: str) -> str:
        """Format JavaScript code."""
        lines = code.split('\n')
        formatted_lines = []
        indent_level = 0
        indent_str = '  ' if style == 'expanded' else ''

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            
            if stripped.endswith('{'):
                formatted_lines.append(indent_str * indent_level + stripped)
                indent_level += 1
            elif stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
                formatted_lines.append(indent_str * indent_level + stripped)
            else:
                formatted_lines.append(indent_str * indent_level + stripped)

        return '\n'.join(formatted_lines)

    def _optimize_code(self, code: str) -> str:
        """Optimize JavaScript code."""
        code = re.sub(r'//.*?\n', '\n', code)
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        code = re.sub(r'\s+', ' ', code)
        return code.strip()

    def _validate_code(self, code: str) -> List[str]:
        """Validate JavaScript code."""
        issues = []
        
        open_braces = code.count('{')
        close_braces = code.count('}')
        if open_braces != close_braces:
            issues.append(f"Unmatched braces: {open_braces} opening, {close_braces} closing")
        
        open_parens = code.count('(')
        close_parens = code.count(')')
        if open_parens != close_parens:
            issues.append(f"Unmatched parentheses: {open_parens} opening, {close_parens} closing")
        
        return issues


class TailwindCSSHelperSkill(BaseSkill):
    """Skill for helping with Tailwind CSS."""

    def __init__(self):
        """Initialize Tailwind CSS helper skill."""
        metadata = SkillMetadata(
            name="tailwind_helper",
            version="1.0.0",
            description="Generate Tailwind CSS classes and components",
            category="web_styling",
            icon="🎨",
            tags=["tailwind", "css", "styling", "utility"]
        )
        super().__init__(metadata)

    def validate_input(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate Tailwind helper input."""
        if 'action' not in kwargs:
            return False, "Missing 'action' parameter"
        return True, None

    async def execute(self, **kwargs) -> SkillResult:
        """Execute Tailwind helper action."""
        try:
            action = kwargs.get('action', '').lower()
            description = kwargs.get('description', '')

            if action == 'generate_palette':
                result = self._generate_color_palette(description)
            elif action == 'component':
                result = self._generate_component(description)
            elif action == 'utilities':
                result = self._generate_utilities(description)
            else:
                return SkillResult(
                    status=SkillStatus.ERROR,
                    error=f"Unknown action: {action}",
                    message=f"Action '{action}' is not recognized"
                )

            return SkillResult(
                status=SkillStatus.SUCCESS,
                data=result,
                message=f"Generated Tailwind {action}"
            )
        except Exception as e:
            return SkillResult(
                status=SkillStatus.ERROR,
                error=str(e),
                message="Failed to generate Tailwind CSS"
            )

    def _generate_color_palette(self, description: str) -> Dict[str, str]:
        """Generate Tailwind color palette."""
        return {
            'primary': 'bg-blue-500 text-white',
            'secondary': 'bg-gray-500 text-white',
            'success': 'bg-green-500 text-white',
            'warning': 'bg-yellow-500 text-black',
            'danger': 'bg-red-500 text-white',
            'info': 'bg-cyan-500 text-white'
        }

    def _generate_component(self, description: str) -> Dict[str, str]:
        """Generate Tailwind component."""
        components = {
            'button': 'px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors',
            'card': 'bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow',
            'input': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500',
            'badge': 'inline-block px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold'
        }
        return {k: v for k, v in components.items() if k.lower() in description.lower()}

    def _generate_utilities(self, description: str) -> Dict[str, str]:
        """Generate Tailwind utility classes."""
        utilities = {
            'spacing': 'space-y-4 space-x-4',
            'flex': 'flex items-center justify-between',
            'grid': 'grid grid-cols-3 gap-4',
            'responsive': 'sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4',
            'animation': 'animate-pulse hover:animate-bounce'
        }
        return {k: v for k, v in utilities.items() if k.lower() in description.lower()}


class AccessibilityCheckerSkill(BaseSkill):
    """Skill for checking web accessibility (WCAG 2.1)."""

    def __init__(self):
        """Initialize accessibility checker skill."""
        metadata = SkillMetadata(
            name="accessibility_checker",
            version="1.0.0",
            description="Check and improve web accessibility (WCAG 2.1 AA)",
            category="web_quality",
            icon="♿",
            tags=["accessibility", "wcag", "a11y", "testing"]
        )
        super().__init__(metadata)

    def validate_input(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate accessibility checker input."""
        if 'html' not in kwargs:
            return False, "Missing 'html' parameter"
        return True, None

    async def execute(self, **kwargs) -> SkillResult:
        """Check HTML accessibility."""
        try:
            html = kwargs.get('html', '')
            level = kwargs.get('level', 'AA').upper()

            issues = self._check_accessibility(html, level)
            recommendations = self._generate_recommendations(issues)

            return SkillResult(
                status=SkillStatus.SUCCESS,
                data={
                    'issues': issues,
                    'recommendations': recommendations,
                    'wcag_level': level,
                    'score': self._calculate_accessibility_score(issues)
                },
                message=f"Found {len(issues)} accessibility issues",
                warnings=[f"Issue: {issue['message']}" for issue in issues]
            )
        except Exception as e:
            return SkillResult(
                status=SkillStatus.ERROR,
                error=str(e),
                message="Failed to check accessibility"
            )

    def _check_accessibility(self, html: str, level: str) -> List[Dict[str, str]]:
        """Check HTML for accessibility issues."""
        issues = []

        if '<img' in html and 'alt=' not in html:
            issues.append({
                'type': 'missing_alt',
                'severity': 'critical',
                'message': 'Images must have alt text',
                'wcag': '1.1.1'
            })

        if '<input' in html and '<label' not in html:
            issues.append({
                'type': 'missing_label',
                'severity': 'critical',
                'message': 'Form inputs must have associated labels',
                'wcag': '1.3.1'
            })

        h1_count = html.count('<h1')
        if h1_count == 0:
            issues.append({
                'type': 'missing_h1',
                'severity': 'high',
                'message': 'Page should have at least one H1 heading',
                'wcag': '1.3.1'
            })
        elif h1_count > 1:
            issues.append({
                'type': 'multiple_h1',
                'severity': 'medium',
                'message': 'Page should have only one H1 heading',
                'wcag': '1.3.1'
            })

        if 'style=' in html or 'color:' in html:
            issues.append({
                'type': 'color_contrast',
                'severity': 'medium',
                'message': 'Ensure sufficient color contrast (4.5:1 for normal text)',
                'wcag': '1.4.3'
            })

        if '<button' not in html and '<a href=' not in html:
            issues.append({
                'type': 'interactive_elements',
                'severity': 'high',
                'message': 'Page should have keyboard-accessible interactive elements',
                'wcag': '2.1.1'
            })

        return issues

    def _generate_recommendations(self, issues: List[Dict[str, str]]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []
        issue_types = [issue['type'] for issue in issues]

        if 'missing_alt' in issue_types:
            recommendations.append("Add descriptive alt text to all images")
        if 'missing_label' in issue_types:
            recommendations.append("Associate labels with form inputs using 'for' attribute")
        if 'missing_h1' in issue_types:
            recommendations.append("Add a meaningful H1 heading to the page")
        if 'color_contrast' in issue_types:
            recommendations.append("Ensure text has at least 4.5:1 contrast ratio")
        if 'interactive_elements' in issue_types:
            recommendations.append("Use semantic HTML (button, a) for interactive elements")

        return recommendations

    def _calculate_accessibility_score(self, issues: List[Dict[str, str]]) -> float:
        """Calculate accessibility score out of 100."""
        if not issues:
            return 100.0
        
        severity_weights = {'critical': 10, 'high': 5, 'medium': 2, 'low': 1}
        total_penalty = sum(severity_weights.get(issue.get('severity', 'medium'), 2) for issue in issues)
        
        score = max(0, 100 - total_penalty)
        return round(score, 1)


class ResponsiveDesignTesterSkill(BaseSkill):
    """Skill for testing responsive design."""

    def __init__(self):
        """Initialize responsive design tester skill."""
        metadata = SkillMetadata(
            name="responsive_tester",
            version="1.0.0",
            description="Test and validate responsive design breakpoints",
            category="web_testing",
            icon="📱",
            tags=["responsive", "mobile", "breakpoints", "testing"]
        )
        super().__init__(metadata)

    def validate_input(self, **kwargs) -> tuple[bool, Optional[str]]:
        """Validate responsive tester input."""
        if 'html' not in kwargs and 'css' not in kwargs:
            return False, "Missing 'html' or 'css' parameter"
        return True, None

    async def execute(self, **kwargs) -> SkillResult:
        """Test responsive design."""
        try:
            html = kwargs.get('html', '')
            css = kwargs.get('css', '')
            custom_breakpoints = kwargs.get('custom_breakpoints', [])

            breakpoints = custom_breakpoints or self._get_default_breakpoints()
            test_results = self._test_breakpoints(html, css, breakpoints)
            recommendations = self._generate_recommendations(test_results)

            return SkillResult(
                status=SkillStatus.SUCCESS,
                data={
                    'breakpoints': breakpoints,
                    'test_results': test_results,
                    'recommendations': recommendations,
                    'is_mobile_first': self._check_mobile_first(css)
                },
                message="Responsive design test completed"
            )
        except Exception as e:
            return SkillResult(
                status=SkillStatus.ERROR,
                error=str(e),
                message="Failed to test responsive design"
            )

    def _get_default_breakpoints(self) -> Dict[str, int]:
        """Get default responsive breakpoints."""
        return {
            'mobile': 320,
            'tablet': 768,
            'desktop': 1024,
            'wide': 1280
        }

    def _test_breakpoints(self, html: str, css: str, breakpoints: Dict[str, int]) -> Dict[str, bool]:
        """Test breakpoints in CSS."""
        results = {}
        
        for name, width in breakpoints.items():
            pattern = f'@media.*\({width}px\)'
            has_media_query = bool(re.search(pattern, css))
            results[name] = has_media_query

        return results

    def _check_mobile_first(self, css: str) -> bool:
        """Check if CSS uses mobile-first approach."""
        min_width_count = css.count('min-width')
        max_width_count = css.count('max-width')
        return min_width_count > max_width_count

    def _generate_recommendations(self, test_results: Dict[str, bool]) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        if not any(test_results.values()):
            recommendations.append("Add media queries for different screen sizes")
        
        missing_breakpoints = [k for k, v in test_results.items() if not v]
        if missing_breakpoints:
            recommendations.append(f"Add media queries for: {', '.join(missing_breakpoints)}")
        
        recommendations.append("Use flexible layouts (flexbox/grid) for better responsiveness")
        recommendations.append("Test with real devices or browser DevTools")

        return recommendations
