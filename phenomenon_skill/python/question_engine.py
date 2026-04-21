#!/usr/bin/env python3
"""Heuristic next-question generator.

No LLM required. Uses missing-field and contradiction-driven prompts.
"""
from __future__ import annotations

from typing import List


def _append_unique(out: List[str], question: str) -> None:
    q = question.strip()
    if q and q not in out:
        out.append(q)


def next_questions(state: dict, limit: int = 5) -> List[str]:
    mode = state.get("mode", "general")
    out: List[str] = []

    # Shared heuristics
    if not state.get("timeline"):
        _append_unique(out, "这件事最早是从什么时候开始的？中间有没有明显的转折点？")
    if not state.get("actors") and mode == "general":
        _append_unique(out, "这里面有哪些关键角色或对象？谁直接受影响，谁在推动或阻碍事情发展？")
    if not state.get("contradictions"):
        _append_unique(out, "有没有一个最让你觉得不对劲、甚至和表面结论相反的细节？")
    if len(state.get("hypotheses", [])) < 2:
        _append_unique(out, "除了你现在最直觉的解释，还有没有第二种完全不同的解释路径？")
    if not state.get("unknowns"):
        _append_unique(out, "现在你最缺哪一条信息？如果补上它，问题会一下子清楚很多？")

    # General mode heuristics
    if mode == "general":
        if not state.get("facts"):
            _append_unique(out, "先把已经发生、可以确认的事实列出来：具体发生了什么？")
        if state.get("interpretations") and not state.get("facts"):
            _append_unique(out, "你刚才说的里面，哪些是事实，哪些是你自己的判断或怀疑？")
        if not state.get("emotions"):
            _append_unique(out, "这件事里你最强烈的感受是什么？这种感受是在哪个细节上被触发的？")
        if not state.get("actors"):
            _append_unique(out, "谁在这件事里看起来最关键，但你现在掌握的信息最少？")

    # Debug mode heuristics
    if mode == "computing_debug":
        if not state.get("scope"):
            _append_unique(out, "问题影响范围有多大？是单接口、单模块、单用户，还是全局？")
        if not state.get("environment"):
            _append_unique(out, "运行环境是什么？语言版本、OS、容器、依赖、部署环境分别是什么？")
        if not state.get("recent_changes"):
            _append_unique(out, "最近变了什么？代码、配置、依赖、部署方式、流量或数据分布有没有变化？")
        if not state.get("signals"):
            _append_unique(out, "现在最直接的可观察信号是什么？日志、metrics、trace、stack trace 哪个最异常？")
        if not state.get("scope") and not state.get("signals"):
            _append_unique(out, "这个问题是稳定复现、偶发，还是只在线上出现？")
        if not state.get("ruled_out"):
            _append_unique(out, "哪些可能性你已经排除了？依据是什么？")
        if not state.get("next_actions"):
            _append_unique(out, "如果只允许做一个最低成本的验证动作，你现在最想先验证什么？")

    return out[:limit]
