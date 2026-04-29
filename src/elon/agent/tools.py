"""Tool registry for the Claude tool-use loop.

A tool is: name, JSON-schema input, async/sync handler taking (ctx, **kwargs).
The runner serializes handler return values to JSON for tool_result blocks.
"""

from __future__ import annotations

import inspect
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class AgentContext:
    tenant_id: str
    user_id: str | None = None
    extras: dict[str, Any] = field(default_factory=dict)


@dataclass
class Tool:
    name: str
    description: str
    input_schema: dict
    handler: Callable[..., Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def schema(self) -> list[dict]:
        return [
            {"name": t.name, "description": t.description, "input_schema": t.input_schema}
            for t in self._tools.values()
        ]

    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise KeyError(f"unknown tool: {name}")
        return self._tools[name]

    def call(self, name: str, ctx: AgentContext, args: dict) -> Any:
        tool = self.get(name)
        result = tool.handler(ctx=ctx, **args)
        if inspect.iscoroutine(result):
            raise RuntimeError(f"tool {name} returned a coroutine; use sync handlers in Phase 1")
        return result
