"""Schema definition and loading for envguard."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


VALID_TYPES = {"string", "integer", "float", "boolean", "url", "email"}


@dataclass
class VariableSchema:
    name: str
    required: bool = True
    type: str = "string"
    pattern: Optional[str] = None
    allowed_values: list[str] = field(default_factory=list)
    description: str = ""
    default: Optional[Any] = None

    def __post_init__(self):
        if self.type not in VALID_TYPES:
            raise ValueError(
                f"Invalid type '{self.type}' for variable '{self.name}'. "
                f"Must be one of: {', '.join(sorted(VALID_TYPES))}"
            )


@dataclass
class EnvSchema:
    variables: list[VariableSchema] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "EnvSchema":
        variables = [
            VariableSchema(
                name=name,
                required=meta.get("required", True),
                type=meta.get("type", "string"),
                pattern=meta.get("pattern"),
                allowed_values=meta.get("allowed_values", []),
                description=meta.get("description", ""),
                default=meta.get("default"),
            )
            for name, meta in data.get("variables", {}).items()
        ]
        return cls(variables=variables)

    @classmethod
    def load(cls, path: str | Path) -> "EnvSchema":
        schema_path = Path(path)
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
        with schema_path.open() as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Schema file '{schema_path}' contains invalid JSON: {e}"
                ) from e
        return cls.from_dict(data)

    def get_variable(self, name: str) -> Optional[VariableSchema]:
        """Return the VariableSchema for the given variable name, or None if not found."""
        for variable in self.variables:
            if variable.name == name:
                return variable
        return None
