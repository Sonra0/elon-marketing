"""Tool-use loop. Runs Claude with the registry until it stops calling tools."""

from __future__ import annotations

import json
from typing import Any

from elon.agent.tools import AgentContext, ToolRegistry
from elon.core.llm import call_claude
from elon.core.logging import get_logger

log = get_logger(__name__)

MAX_ITERATIONS = 8


def run_agent(
    *,
    ctx: AgentContext,
    system_blocks: list[dict],
    user_message: str,
    tools: ToolRegistry,
    model: str | None = None,
    max_tokens: int = 2048,
) -> tuple[str, list[dict]]:
    """Drive a tool-use conversation. Returns (final_text, transcript)."""
    messages: list[dict] = [{"role": "user", "content": user_message}]
    schema = tools.schema()

    for _ in range(MAX_ITERATIONS):
        resp = call_claude(
            tenant_id=ctx.tenant_id,
            system_blocks=system_blocks,
            messages=messages,
            tools=schema,
            model=model,
            max_tokens=max_tokens,
        )
        # Append assistant turn
        assistant_blocks: list[dict[str, Any]] = []
        tool_uses: list[Any] = []
        text_chunks: list[str] = []
        for blk in resp.content:
            if blk.type == "text":
                assistant_blocks.append({"type": "text", "text": blk.text})
                text_chunks.append(blk.text)
            elif blk.type == "tool_use":
                assistant_blocks.append(
                    {"type": "tool_use", "id": blk.id, "name": blk.name, "input": blk.input}
                )
                tool_uses.append(blk)
        messages.append({"role": "assistant", "content": assistant_blocks})

        if resp.stop_reason != "tool_use" or not tool_uses:
            return "\n".join(text_chunks), messages

        # Run all tool calls, return tool_results
        results = []
        for tu in tool_uses:
            try:
                out = tools.call(tu.name, ctx, dict(tu.input))
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "content": json.dumps(out, default=str),
                })
            except Exception as e:
                log.error("tool_error", tool=tu.name, error=str(e))
                results.append({
                    "type": "tool_result",
                    "tool_use_id": tu.id,
                    "is_error": True,
                    "content": f"error: {e}",
                })
        messages.append({"role": "user", "content": results})

    raise RuntimeError("agent exceeded max iterations without stopping")
