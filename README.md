# My Skills

个人技能收藏库。用于收集、整理和分享为 AI 编程助手设计的技能包（Skill Pack）。

每个技能包独立成目录，包含技能定义、模板和辅助工具，可直接加载到支持的 AI 编码工具中使用。

## 收录技能

| 技能包 | 适用领域 | 简介 |
| --- | --- | --- |
| [phenomenon_skill](./phenomenon_skill/) | 通用分析 / 计算机 Debug | 现象驱动分析技能 —— 通过逐步追问与收缩分析窗口，将模糊问题转化为结构化可分析的问题 |

---

## 技能详情

### Phenomenon Skill  — 现象驱动分析技能

核心理念：**先扩观察面，再缩分析窗**。不立刻下结论，而是通过 6 个阶段逐步逼近问题的真实结构。

#### 包含内容

| 文件 | 说明 |
| --- | --- |
| `general/skill.md` | 通用智囊版 —— 社会现象、组织问题、历史分析、决策分析等 |
| `computing_debug/skill.md` | 计算机 / Agent / Debug 专用版 —— 程序异常、性能问题、架构分析、agent workflow 失败分析等 |
| `python/` | Python 状态管理工具（SQLite 持久化 + 上下文编译 + 启发式提问引擎 + CLI） |
| `shared/templates/` | 案件档案模板与状态模板 |

#### 分析流程（6 阶段）

```text
现象展开 → 矛盾整理 → 分层拆解 → 机制假设 → 边界确认 → 有限结论
```

1. **现象展开** — 把用户的"结论句"翻译成"可观察现象"，区分事实、解释、情绪
2. **矛盾整理** — 找出互相冲突却同时存在的现象，矛盾是分析的入口
3. **分层拆解** — 从历史/结构/制度/文化/技术/环境多维度展开
4. **机制假设** — 构造 1~3 个"当前最强解释"，保持竞争性
5. **边界确认** — 明确结论在什么条件下成立、什么条件下不成立
6. **有限结论** — 给出分层、有限、可验证的结果，不装全知

#### 使用方式

##### 方式一：直接加载 skill.md

将对应的 `skill.md` 作为系统提示或技能文件加载到 AI 助手中即可。AI 会按照技能定义的流程和模板进行多轮分析。

- 通用分析 → 加载 `general/skill.md`
- 计算机 / Debug 问题 → 加载 `computing_debug/skill.md`

##### 方式二：配合 Python 工具使用

Python 工具用于固化状态保存和上下文管理，防止长对话失焦。零外部依赖，仅使用 Python 标准库。

```bash
# 初始化数据库
python3 phenomenon_skill/python/cli.py init --db ./cases.db

# 创建案件
python3 phenomenon_skill/python/cli.py create-case \
  --db ./cases.db \
  --title "组织内部沟通失灵" \
  --mode general \
  --problem "团队内部经常误解需求，返工很多，但大家都说流程没问题。"

# 写入一轮信息
python3 phenomenon_skill/python/cli.py add-round \
  --db ./cases.db \
  --case-id 1 \
  --facts "需求经常在开发中期变化；测试阶段才暴露目标偏差" \
  --contradictions "流程文档存在，但执行中没人真正回看" \
  --unknowns "是谁在中途改目标；改动通过什么渠道传播"

# 生成下一轮上下文摘要（喂给 AI，避免上下文膨胀）
python3 phenomenon_skill/python/cli.py compile-context --db ./cases.db --case-id 1

# 生成启发式下一轮问题
python3 phenomenon_skill/python/cli.py next-questions --db ./cases.db --case-id 1
```

推荐工作流：AI 按 `skill.md` 分析 → 每轮用 CLI 落盘状态 → 用 `compile-context` 编译摘要 → 下一轮只喂摘要 + 新输入。

---

## License

[MIT](./LICENSE)
