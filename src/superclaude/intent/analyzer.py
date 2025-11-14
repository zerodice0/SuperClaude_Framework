"""
ContextAnalyzer - Analyzes project structure and environment.

The analyzer examines the current directory to determine project type,
file structure, git status, dependencies, and testing framework.
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

import tomli

from .models import (
    Dependencies,
    FileStructure,
    GitInfo,
    ProjectContext,
    TestingInfo,
)


class ContextAnalyzer:
    """Analyzes project structure, git history, and dependencies."""

    def __init__(self, root_dir: Optional[Path] = None):
        """
        Initialize analyzer.

        Args:
            root_dir: Project root directory (defaults to cwd)
        """
        self.root_dir = root_dir or Path.cwd()

    def analyze(self) -> ProjectContext:
        """
        Analyze project context.

        Returns:
            ProjectContext with all analyzed information
        """
        # Analyze components
        structure = self._analyze_structure()
        git_info = self._analyze_git()
        dependencies = self._analyze_dependencies()
        testing = self._detect_testing_framework()

        # Detect project type
        project_type = self._detect_project_type(dependencies, structure)

        # Determine active contexts
        active_contexts = self._determine_active_contexts(
            structure, git_info, dependencies
        )

        return ProjectContext(
            project_type=project_type,
            structure=structure,
            git_info=git_info,
            dependencies=dependencies,
            testing=testing,
            active_contexts=active_contexts,
            recent_skills=[],  # TODO: Load from learning data
        )

    def _analyze_structure(self) -> FileStructure:
        """Analyze project file structure."""
        source_dirs: List[Path] = []
        test_dirs: List[Path] = []
        config_files: List[Path] = []
        total_files = 0

        # Common source directory patterns
        source_patterns = [
            "src",
            "lib",
            "app",
            "source",
            "components",
            "modules",
        ]

        # Common test directory patterns
        test_patterns = ["tests", "test", "__tests__", "spec", "specs"]

        # Scan directory
        for item in self.root_dir.iterdir():
            if item.is_dir():
                # Check for source dirs
                if any(pattern in item.name.lower() for pattern in source_patterns):
                    source_dirs.append(item)

                # Check for test dirs
                if any(pattern in item.name.lower() for pattern in test_patterns):
                    test_dirs.append(item)

            elif item.is_file():
                total_files += 1

                # Check for config files
                if item.suffix in [".json", ".toml", ".yaml", ".yml", ".ini", ".cfg"]:
                    config_files.append(item)

        return FileStructure(
            root_dir=self.root_dir,
            source_dirs=source_dirs,
            test_dirs=test_dirs,
            config_files=config_files,
            total_files=total_files,
        )

    def _analyze_git(self) -> GitInfo:
        """Analyze git repository information."""
        git_dir = self.root_dir / ".git"
        if not git_dir.exists():
            return GitInfo(has_repo=False)

        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=2,
            )
            current_branch = result.stdout.strip() if result.returncode == 0 else ""

            # Get main branch (try master then main)
            main_branch = "master"
            result = subprocess.run(
                ["git", "rev-parse", "--verify", "main"],
                cwd=self.root_dir,
                capture_output=True,
                timeout=2,
            )
            if result.returncode == 0:
                main_branch = "main"

            # Get recent commits (last 5)
            result = subprocess.run(
                [
                    "git",
                    "log",
                    "-5",
                    "--pretty=format:%h|%s|%an|%ar",
                ],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=2,
            )

            recent_commits = []
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if line:
                        parts = line.split("|")
                        if len(parts) >= 4:
                            recent_commits.append(
                                {
                                    "hash": parts[0],
                                    "message": parts[1],
                                    "author": parts[2],
                                    "time": parts[3],
                                }
                            )

            # Get uncommitted changes count
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=2,
            )
            uncommitted_changes = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0

            # Get full status
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.root_dir,
                capture_output=True,
                text=True,
                timeout=2,
            )
            status = result.stdout.strip() if result.returncode == 0 else ""

            return GitInfo(
                has_repo=True,
                current_branch=current_branch,
                main_branch=main_branch,
                recent_commits=recent_commits,
                uncommitted_changes=uncommitted_changes,
                status=status,
            )

        except (subprocess.TimeoutExpired, FileNotFoundError):
            return GitInfo(has_repo=True)

    def _analyze_dependencies(self) -> Dependencies:
        """Analyze project dependencies."""
        # Check for package.json (npm/yarn)
        package_json = self.root_dir / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                return Dependencies(
                    package_manager="npm",
                    config_file=package_json,
                    dependencies=data.get("dependencies", {}),
                    dev_dependencies=data.get("devDependencies", {}),
                )
            except (json.JSONDecodeError, OSError):
                pass

        # Check for pyproject.toml (uv/poetry)
        pyproject_toml = self.root_dir / "pyproject.toml"
        if pyproject_toml.exists():
            try:
                with open(pyproject_toml, "rb") as f:
                    data = tomli.load(f)

                dependencies = {}
                dev_dependencies = {}

                # UV/PDM style
                if "project" in data and "dependencies" in data["project"]:
                    deps = data["project"]["dependencies"]
                    if isinstance(deps, list):
                        dependencies = {dep.split(">")[0].split("=")[0]: dep for dep in deps}

                # Poetry style
                if "tool" in data and "poetry" in data["tool"]:
                    poetry = data["tool"]["poetry"]
                    if "dependencies" in poetry:
                        dependencies = poetry["dependencies"]
                    if "dev-dependencies" in poetry:
                        dev_dependencies = poetry["dev-dependencies"]

                return Dependencies(
                    package_manager="uv",
                    config_file=pyproject_toml,
                    dependencies=dependencies,
                    dev_dependencies=dev_dependencies,
                )
            except (OSError, KeyError):
                pass

        # Check for requirements.txt (pip)
        requirements_txt = self.root_dir / "requirements.txt"
        if requirements_txt.exists():
            try:
                deps_text = requirements_txt.read_text()
                dependencies = {
                    line.split("==")[0].strip(): line.strip()
                    for line in deps_text.split("\n")
                    if line.strip() and not line.startswith("#")
                }
                return Dependencies(
                    package_manager="pip",
                    config_file=requirements_txt,
                    dependencies=dependencies,
                )
            except OSError:
                pass

        return Dependencies()

    def _detect_testing_framework(self) -> TestingInfo:
        """Detect testing framework and configuration."""
        test_dirs: List[Path] = []

        # Find test directories
        for pattern in ["tests", "test", "__tests__", "spec", "specs"]:
            test_dir = self.root_dir / pattern
            if test_dir.exists() and test_dir.is_dir():
                test_dirs.append(test_dir)

        # Detect Python testing frameworks
        pytest_ini = self.root_dir / "pytest.ini"
        if pytest_ini.exists():
            return TestingInfo(
                framework="pytest", test_dirs=test_dirs, config_file=pytest_ini
            )

        pyproject = self.root_dir / "pyproject.toml"
        if pyproject.exists():
            try:
                with open(pyproject, "rb") as f:
                    data = tomli.load(f)
                if "tool" in data and "pytest" in data["tool"]:
                    return TestingInfo(
                        framework="pytest", test_dirs=test_dirs, config_file=pyproject
                    )
            except (OSError, KeyError):
                pass

        # Detect JavaScript testing frameworks
        package_json = self.root_dir / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                dev_deps = data.get("devDependencies", {})

                if "vitest" in dev_deps:
                    return TestingInfo(
                        framework="vitest",
                        test_dirs=test_dirs,
                        config_file=package_json,
                    )
                elif "jest" in dev_deps:
                    return TestingInfo(
                        framework="jest", test_dirs=test_dirs, config_file=package_json
                    )
            except (json.JSONDecodeError, OSError):
                pass

        return TestingInfo(test_dirs=test_dirs)

    def _detect_project_type(
        self, dependencies: Dependencies, structure: FileStructure
    ) -> str:
        """Detect project type (python, typescript, javascript, mixed)."""
        has_python = False
        has_typescript = False
        has_javascript = False

        # Check config files
        if (self.root_dir / "pyproject.toml").exists():
            has_python = True
        if (self.root_dir / "tsconfig.json").exists():
            has_typescript = True
        if (self.root_dir / "package.json").exists():
            has_javascript = True

        # Check dependencies
        if dependencies.package_manager in ["uv", "pip", "poetry"]:
            has_python = True
        if dependencies.package_manager in ["npm", "yarn", "pnpm"]:
            has_javascript = True
            # Check for TypeScript in deps
            if any(
                "typescript" in dep.lower()
                for dep in dependencies.dependencies.keys()
            ) or any(
                "typescript" in dep.lower()
                for dep in dependencies.dev_dependencies.keys()
            ):
                has_typescript = True

        # Determine type
        if has_python and has_typescript:
            return "mixed"
        elif has_typescript:
            return "typescript"
        elif has_javascript:
            return "javascript"
        elif has_python:
            return "python"
        else:
            return "unknown"

    def _determine_active_contexts(
        self, structure: FileStructure, git_info: GitInfo, dependencies: Dependencies
    ) -> List[str]:
        """Determine currently active contexts for relevance boosting."""
        contexts: List[str] = []

        # Development phase contexts
        if git_info.uncommitted_changes > 0:
            contexts.append("development")
            contexts.append("uncommitted_changes")

        if git_info.current_branch and git_info.current_branch != git_info.main_branch:
            contexts.append("feature_branch")

        # Project structure contexts
        if structure.test_dirs:
            contexts.append("testing")

        # Dependency contexts
        if dependencies.config_file:
            contexts.append("dependencies")

        return contexts
