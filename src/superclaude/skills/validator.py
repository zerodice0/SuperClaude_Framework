"""
Skill Metadata Validator

Validates skill YAML frontmatter against the extended schema.
Ensures all required fields are present and properly formatted.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import yaml


@dataclass
class ValidationError:
    """Represents a validation error"""
    field: str
    message: str
    severity: str  # error, warning
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of skill validation"""
    valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    skill_name: str

    def __str__(self) -> str:
        lines = [f"Validation Result for '{self.skill_name}':"]

        if self.valid:
            lines.append("✅ VALID")
        else:
            lines.append("❌ INVALID")

        if self.errors:
            lines.append(f"\nErrors ({len(self.errors)}):")
            for err in self.errors:
                lines.append(f"  ❌ {err.field}: {err.message}")
                if err.suggestion:
                    lines.append(f"     💡 {err.suggestion}")

        if self.warnings:
            lines.append(f"\nWarnings ({len(self.warnings)}):")
            for warn in self.warnings:
                lines.append(f"  ⚠️  {warn.field}: {warn.message}")
                if warn.suggestion:
                    lines.append(f"     💡 {warn.suggestion}")

        return "\n".join(lines)


class SkillValidator:
    """
    Validates skill metadata against schema

    Usage:
        validator = SkillValidator()
        result = validator.validate_file("skills/implement/SKILL.md")

        if not result.valid:
            print(result)
            sys.exit(1)
    """

    # Valid enum values
    VALID_CATEGORIES = {"workflow", "utility", "research", "special", "orchestration"}
    VALID_COMPLEXITIES = {"basic", "standard", "enhanced", "advanced", "high"}
    VALID_ARG_TYPES = {"string", "enum", "int", "bool", "path"}
    VALID_INFER_SOURCES = {"user_query", "project_context", "git_history", "learning"}

    # Required fields
    REQUIRED_BASIC_FIELDS = {
        "name", "display_name", "description", "version",
        "category", "complexity"
    }

    REQUIRED_INTENT_FIELDS = {
        "intents": {"primary", "keywords", "patterns"}
    }

    REQUIRED_AUTO_TRIGGER_FIELDS = {
        "auto_trigger": {"enabled", "confidence_threshold", "confirm_before_execution"}
    }

    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def validate_file(self, file_path: str | Path) -> ValidationResult:
        """
        Validate skill file

        Args:
            file_path: Path to SKILL.md file

        Returns:
            ValidationResult with errors and warnings
        """
        self.errors = []
        self.warnings = []

        path = Path(file_path)

        if not path.exists():
            self.errors.append(ValidationError(
                field="file",
                message=f"File not found: {path}",
                severity="error"
            ))
            return ValidationResult(
                valid=False,
                errors=self.errors,
                warnings=self.warnings,
                skill_name=str(path)
            )

        # Parse frontmatter
        frontmatter = self._parse_frontmatter(path)

        if frontmatter is None:
            self.errors.append(ValidationError(
                field="frontmatter",
                message="Failed to parse YAML frontmatter",
                severity="error",
                suggestion="Check YAML syntax, ensure it starts with '---'"
            ))
            return ValidationResult(
                valid=False,
                errors=self.errors,
                warnings=self.warnings,
                skill_name=str(path)
            )

        # Validate schema
        self._validate_basic_info(frontmatter)
        self._validate_intents(frontmatter)
        self._validate_arguments(frontmatter)
        self._validate_auto_trigger(frontmatter)
        self._validate_dependencies(frontmatter)

        skill_name = frontmatter.get("name", str(path))

        return ValidationResult(
            valid=len(self.errors) == 0,
            errors=self.errors,
            warnings=self.warnings,
            skill_name=skill_name
        )

    def _parse_frontmatter(self, path: Path) -> Optional[Dict[str, Any]]:
        """Extract and parse YAML frontmatter"""
        try:
            content = path.read_text()

            # Find frontmatter block
            match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)

            if not match:
                return None

            frontmatter_text = match.group(1)
            return yaml.safe_load(frontmatter_text)

        except Exception as e:
            return None

    def _validate_basic_info(self, frontmatter: Dict[str, Any]):
        """Validate basic information fields"""

        # Check required fields
        for field in self.REQUIRED_BASIC_FIELDS:
            if field not in frontmatter:
                self.errors.append(ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing",
                    severity="error",
                    suggestion=f"Add '{field}:' to frontmatter"
                ))

        # Validate name format (kebab-case)
        if "name" in frontmatter:
            name = frontmatter["name"]
            if not re.match(r'^[a-z0-9]+(-[a-z0-9]+)*$', name):
                self.errors.append(ValidationError(
                    field="name",
                    message=f"Name '{name}' must be kebab-case",
                    severity="error",
                    suggestion="Use lowercase letters, numbers, and hyphens (e.g., 'my-skill')"
                ))

            if len(name) < 2 or len(name) > 30:
                self.errors.append(ValidationError(
                    field="name",
                    message=f"Name length must be 2-30 characters (got {len(name)})",
                    severity="error"
                ))

        # Validate version (semantic versioning)
        if "version" in frontmatter:
            version = frontmatter["version"]
            if not re.match(r'^\d+\.\d+\.\d+$', str(version)):
                self.errors.append(ValidationError(
                    field="version",
                    message=f"Version '{version}' must follow semantic versioning (X.Y.Z)",
                    severity="error",
                    suggestion="Use format like '1.0.0'"
                ))

        # Validate category
        if "category" in frontmatter:
            category = frontmatter["category"]
            if category not in self.VALID_CATEGORIES:
                self.errors.append(ValidationError(
                    field="category",
                    message=f"Invalid category '{category}'",
                    severity="error",
                    suggestion=f"Must be one of: {', '.join(self.VALID_CATEGORIES)}"
                ))

        # Validate complexity
        if "complexity" in frontmatter:
            complexity = frontmatter["complexity"]
            if complexity not in self.VALID_COMPLEXITIES:
                self.errors.append(ValidationError(
                    field="complexity",
                    message=f"Invalid complexity '{complexity}'",
                    severity="error",
                    suggestion=f"Must be one of: {', '.join(self.VALID_COMPLEXITIES)}"
                ))

        # Validate description length
        if "description" in frontmatter:
            desc = frontmatter["description"]
            if len(desc) > 100:
                self.warnings.append(ValidationError(
                    field="description",
                    message=f"Description is {len(desc)} chars (recommended <100)",
                    severity="warning",
                    suggestion="Keep description concise for better UX"
                ))

    def _validate_intents(self, frontmatter: Dict[str, Any]):
        """Validate intent detection metadata"""

        if "intents" not in frontmatter:
            self.errors.append(ValidationError(
                field="intents",
                message="Required section 'intents' is missing",
                severity="error",
                suggestion="Add 'intents:' with primary, keywords, patterns"
            ))
            return

        intents = frontmatter["intents"]

        # Check required intent fields
        for field in self.REQUIRED_INTENT_FIELDS["intents"]:
            if field not in intents:
                self.errors.append(ValidationError(
                    field=f"intents.{field}",
                    message=f"Required field 'intents.{field}' is missing",
                    severity="error"
                ))

        # Validate primary patterns
        if "primary" in intents:
            primary = intents["primary"]
            if not isinstance(primary, list) or len(primary) == 0:
                self.errors.append(ValidationError(
                    field="intents.primary",
                    message="Must be a non-empty array",
                    severity="error",
                    suggestion="Add at least one primary intent pattern"
                ))
            else:
                # Check for {param} placeholders
                for pattern in primary:
                    if "{" not in pattern:
                        self.warnings.append(ValidationError(
                            field="intents.primary",
                            message=f"Pattern '{pattern}' has no {{param}} placeholder",
                            severity="warning",
                            suggestion="Use {{param}} to mark extractable parts"
                        ))

        # Validate keywords
        if "keywords" in intents:
            keywords = intents["keywords"]
            if not isinstance(keywords, list) or len(keywords) < 2:
                self.errors.append(ValidationError(
                    field="intents.keywords",
                    message="Must have at least 2 keywords",
                    severity="error"
                ))

        # Validate regex patterns
        if "patterns" in intents:
            patterns = intents["patterns"]
            if not isinstance(patterns, list) or len(patterns) == 0:
                self.errors.append(ValidationError(
                    field="intents.patterns",
                    message="Must be a non-empty array",
                    severity="error"
                ))
            else:
                for pattern in patterns:
                    try:
                        re.compile(pattern)
                    except re.error as e:
                        self.errors.append(ValidationError(
                            field="intents.patterns",
                            message=f"Invalid regex '{pattern}': {e}",
                            severity="error"
                        ))

                    # Check for named groups
                    if "?P<" not in pattern:
                        self.warnings.append(ValidationError(
                            field="intents.patterns",
                            message=f"Pattern '{pattern}' has no named groups",
                            severity="warning",
                            suggestion="Use (?P<name>...) for argument extraction"
                        ))

    def _validate_arguments(self, frontmatter: Dict[str, Any]):
        """Validate argument schema"""

        if "arguments" not in frontmatter:
            # Arguments are optional
            return

        arguments = frontmatter["arguments"]

        if not isinstance(arguments, list):
            self.errors.append(ValidationError(
                field="arguments",
                message="Must be an array of argument objects",
                severity="error"
            ))
            return

        for i, arg in enumerate(arguments):
            if not isinstance(arg, dict):
                self.errors.append(ValidationError(
                    field=f"arguments[{i}]",
                    message="Must be an object",
                    severity="error"
                ))
                continue

            arg_name = arg.get("name", f"[{i}]")

            # Required argument fields
            required_arg_fields = {"name", "type", "required", "description", "infer_from"}

            for field in required_arg_fields:
                if field not in arg:
                    self.errors.append(ValidationError(
                        field=f"arguments.{arg_name}.{field}",
                        message=f"Required field '{field}' is missing",
                        severity="error"
                    ))

            # Validate argument name
            if "name" in arg:
                name = arg["name"]
                if not re.match(r'^[a-z_][a-z0-9_]*$', name):
                    self.errors.append(ValidationError(
                        field=f"arguments.{arg_name}.name",
                        message=f"Name '{name}' must be snake_case",
                        severity="error"
                    ))

            # Validate type
            if "type" in arg:
                arg_type = arg["type"]
                if arg_type not in self.VALID_ARG_TYPES:
                    self.errors.append(ValidationError(
                        field=f"arguments.{arg_name}.type",
                        message=f"Invalid type '{arg_type}'",
                        severity="error",
                        suggestion=f"Must be one of: {', '.join(self.VALID_ARG_TYPES)}"
                    ))

                # Enum type must have values
                if arg_type == "enum" and "values" not in arg:
                    self.errors.append(ValidationError(
                        field=f"arguments.{arg_name}.values",
                        message="Enum type requires 'values' field",
                        severity="error",
                        suggestion="Add 'values: [opt1, opt2, ...]'"
                    ))

            # Validate infer_from
            if "infer_from" in arg:
                source = arg["infer_from"]
                if source not in self.VALID_INFER_SOURCES:
                    self.errors.append(ValidationError(
                        field=f"arguments.{arg_name}.infer_from",
                        message=f"Invalid inference source '{source}'",
                        severity="error",
                        suggestion=f"Must be one of: {', '.join(self.VALID_INFER_SOURCES)}"
                    ))

            # Validate required field
            if "required" in arg:
                if not isinstance(arg["required"], bool):
                    self.errors.append(ValidationError(
                        field=f"arguments.{arg_name}.required",
                        message="Must be boolean (true/false)",
                        severity="error"
                    ))

                # Non-required should have default
                if not arg["required"] and "default" not in arg:
                    self.warnings.append(ValidationError(
                        field=f"arguments.{arg_name}.default",
                        message="Non-required argument should have a default value",
                        severity="warning"
                    ))

    def _validate_auto_trigger(self, frontmatter: Dict[str, Any]):
        """Validate auto-execution configuration"""

        if "auto_trigger" not in frontmatter:
            self.errors.append(ValidationError(
                field="auto_trigger",
                message="Required section 'auto_trigger' is missing",
                severity="error"
            ))
            return

        auto_trigger = frontmatter["auto_trigger"]

        # Check required fields
        for field in self.REQUIRED_AUTO_TRIGGER_FIELDS["auto_trigger"]:
            if field not in auto_trigger:
                self.errors.append(ValidationError(
                    field=f"auto_trigger.{field}",
                    message=f"Required field '{field}' is missing",
                    severity="error"
                ))

        # Validate enabled
        if "enabled" in auto_trigger:
            if not isinstance(auto_trigger["enabled"], bool):
                self.errors.append(ValidationError(
                    field="auto_trigger.enabled",
                    message="Must be boolean (true/false)",
                    severity="error"
                ))

        # Validate confidence_threshold
        if "confidence_threshold" in auto_trigger:
            threshold = auto_trigger["confidence_threshold"]
            if not isinstance(threshold, (int, float)):
                self.errors.append(ValidationError(
                    field="auto_trigger.confidence_threshold",
                    message="Must be a number",
                    severity="error"
                ))
            elif not (0.0 <= threshold <= 1.0):
                self.errors.append(ValidationError(
                    field="auto_trigger.confidence_threshold",
                    message=f"Must be between 0.0 and 1.0 (got {threshold})",
                    severity="error"
                ))
            elif threshold < 0.70:
                self.warnings.append(ValidationError(
                    field="auto_trigger.confidence_threshold",
                    message=f"Threshold {threshold} is very low (recommended ≥0.85)",
                    severity="warning"
                ))

        # Validate confirm_before_execution
        if "confirm_before_execution" in auto_trigger:
            if not isinstance(auto_trigger["confirm_before_execution"], bool):
                self.errors.append(ValidationError(
                    field="auto_trigger.confirm_before_execution",
                    message="Must be boolean (true/false)",
                    severity="error"
                ))
            elif not auto_trigger["confirm_before_execution"]:
                self.warnings.append(ValidationError(
                    field="auto_trigger.confirm_before_execution",
                    message="Auto-execution without confirmation is dangerous",
                    severity="warning",
                    suggestion="Consider setting to 'true' for safety"
                ))

    def _validate_dependencies(self, frontmatter: Dict[str, Any]):
        """Validate dependencies (optional fields)"""

        # These are all optional, just check format if present

        if "mcp_servers" in frontmatter:
            servers = frontmatter["mcp_servers"]
            if not isinstance(servers, list):
                self.errors.append(ValidationError(
                    field="mcp_servers",
                    message="Must be an array of server names",
                    severity="error"
                ))

        if "personas" in frontmatter:
            personas = frontmatter["personas"]
            if not isinstance(personas, list):
                self.errors.append(ValidationError(
                    field="personas",
                    message="Must be an array of persona names",
                    severity="error"
                ))

        if "requires_skills" in frontmatter:
            skills = frontmatter["requires_skills"]
            if not isinstance(skills, list):
                self.errors.append(ValidationError(
                    field="requires_skills",
                    message="Must be an array of skill names",
                    severity="error"
                ))

        if "optional_skills" in frontmatter:
            skills = frontmatter["optional_skills"]
            if not isinstance(skills, list):
                self.errors.append(ValidationError(
                    field="optional_skills",
                    message="Must be an array of skill names",
                    severity="error"
                ))


def validate_skill(file_path: str | Path) -> ValidationResult:
    """
    Convenience function to validate a skill file

    Args:
        file_path: Path to SKILL.md file

    Returns:
        ValidationResult
    """
    validator = SkillValidator()
    return validator.validate_file(file_path)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate skill metadata")
    parser.add_argument("files", nargs="+", help="Skill files to validate")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    args = parser.parse_args()

    all_valid = True

    for file_path in args.files:
        result = validate_skill(file_path)
        print(result)
        print()

        if not result.valid:
            all_valid = False
        elif args.strict and result.warnings:
            all_valid = False

    if not all_valid:
        print("❌ Validation failed")
        sys.exit(1)
    else:
        print("✅ All skills valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
