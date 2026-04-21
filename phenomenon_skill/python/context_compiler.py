#!/usr/bin/env python3
"""Compile full state into compact markdown context for the next round."""
from __future__ import annotations

from typing import Iterable


def _bullets(items: Iterable[str], max_items: int = 6) -> str:
    trimmed = [x.strip() for x in items if x and x.strip()]
    if not trimmed:
        return "- （暂无）"
    return "\n".join(f"- {x}" for x in trimmed[:max_items])


def compile_context(state: dict) -> str:
    mode = state.get("mode", "general")
    lines: list[str] = []
    lines.append(f"# Compiled Context: {state.get('title', 'Untitled')} (case #{state.get('case_id')})")
    lines.append("")
    lines.append("## 核心问题")
    lines.append(f"- {state.get('problem', '')}")
    lines.append("")

    if mode == "general":
        sections = [
            ("已确认事实", state.get("facts", [])),
            ("用户的解释 / 推断", state.get("interpretations", [])),
            ("情绪与立场信号", state.get("emotions", [])),
            ("关键角色 / 对象", state.get("actors", [])),
            ("时间线", state.get("timeline", [])),
            ("异常点 / 矛盾点", state.get("contradictions", [])),
            ("当前假设", state.get("hypotheses", [])),
            ("未知但关键的信息", state.get("unknowns", [])),
        ]
    else:
        sections = [
            ("症状清单", state.get("facts", []) + state.get("signals", [])),
            ("影响范围", state.get("scope", [])),
            ("运行环境", state.get("environment", [])),
            ("最近变更", state.get("recent_changes", [])),
            ("时间线", state.get("timeline", [])),
            ("矛盾点 / 异常点", state.get("contradictions", [])),
            ("当前假设", state.get("hypotheses", [])),
            ("已排除项", state.get("ruled_out", [])),
            ("待确认的关键点", state.get("unknowns", [])),
            ("下一步动作", state.get("next_actions", [])),
        ]

    for title, items in sections:
        lines.append(f"## {title}")
        lines.append(_bullets(items))
        lines.append("")

    lines.append("## 使用规则")
    lines.append("- 先基于上面的状态继续推进，不要重新开题。")
    lines.append("- 优先追问最能缩小问题空间的 3~5 个问题。")
    lines.append("- 先更新事实、矛盾、假设，再给结论。")
    lines.append("- 保留竞争性解释，不要仓促结案。")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"
