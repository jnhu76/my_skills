# Phenomenon Skill Pack

一个面向 **多轮分析 / 启发式提问 / 上下文压缩 / 状态保存** 的技能包。

它包含两类技能：

- `general/skill.md`：通用智囊版，适合社会现象、历史、组织、人际、决策、复杂问题分析
- `computing_debug/skill.md`：计算机 / agent / debug 专用版，适合程序异常、架构问题、性能分析、agent workflow 失败分析

同时包含一套 **Python 标准库实现** 的状态管理工具：

- `python/state_store.py`：SQLite 状态存储，管理案件 / 调试档案 / 轮次记录 / 假设 / 问题
- `python/question_engine.py`：启发式提问引擎，根据当前状态自动生成下一轮问题方向
- `python/context_compiler.py`：把完整状态压缩成可喂给 AI 的“下一轮上下文”
- `python/cli.py`：命令行入口，用于初始化、建案、写入轮次、生成上下文摘要

目标不是让 Python 代替分析，而是：

1. 用 `skill.md` 规范 AI 的分析方式
2. 用 Python 固化固定流程与状态保存
3. 用 SQLite + context compiler 防止长对话飘散

---

## 目录结构

```text
phenomenon_skill_pack/
├── README.md
├── general/
│   └── skill.md
├── computing_debug/
│   └── skill.md
├── shared/
│   └── templates/
│       ├── case_state_template.json
│       ├── debug_state_template.json
│       ├── case_file.md
│       └── debug_case_file.md
└── python/
    ├── cli.py
    ├── context_compiler.py
    ├── question_engine.py
    └── state_store.py
```

---

## 设计思路

### 1. AI 负责分析，Python 负责固定流程
适合交给 Python 的：
- 状态保存
- SQLite 归档
- 每轮快照
- 缺失字段检测
- 启发式问题模板选择
- 上下文编译

适合交给 AI 的：
- 解释现象
- 构造竞争性假设
- 发现矛盾机制
- 推断结构关系
- 生成阶段性结论

### 2. 每轮必须保存状态
不要把所有信息都寄托在模型上下文里。每轮对话后，都可以把已确认内容落进 SQLite，然后重新编译出下一轮摘要。

### 3. 先铺开，再收缩
整体节奏是：

- 收集现象
- 标记异常和矛盾
- 建时间线
- 建立竞争性假设
- 识别边界条件
- 输出有限结论

---

## 快速开始

### 1) 初始化数据库

```bash
python python/cli.py init --db ./cases.db
```

### 2) 创建一个通用案件

```bash
python python/cli.py create-case \
  --db ./cases.db \
  --title "组织内部沟通失灵" \
  --mode general \
  --problem "团队内部经常误解需求，返工很多，但大家都说流程没问题。"
```

### 3) 写入一轮信息

```bash
python python/cli.py add-round \
  --db ./cases.db \
  --case-id 1 \
  --facts "需求经常在开发中期变化；测试阶段才暴露目标偏差" \
  --interpretations "用户怀疑是产品经理表达不清" \
  --contradictions "流程文档存在，但执行中没人真正回看" \
  --unknowns "是谁在中途改目标；改动通过什么渠道传播"
```

### 4) 生成下一轮上下文摘要

```bash
python python/cli.py compile-context --db ./cases.db --case-id 1
```

### 5) 生成启发式下一轮问题

```bash
python python/cli.py next-questions --db ./cases.db --case-id 1
```

---

## 推荐工作流

### 通用问题分析
1. 让 AI 按 `general/skill.md` 接案
2. 每轮后把事实、矛盾、假设、未知信息写入 SQLite
3. 用 `compile-context` 生成压缩摘要
4. 下一轮只喂压缩摘要 + 新输入，避免上下文膨胀

### 计算机 / Agent / Debug 问题
1. 让 AI 按 `computing_debug/skill.md` 先定义症状和范围
2. 记录环境、时间线、变更、异常信号、竞争性假设
3. 用 `next-questions` 找最值得追问的验证点
4. 用 `compile-context` 编译下一轮摘要
5. 反复直到根因或最优实验设计足够清晰

---

## 为什么用 SQLite

因为它足够轻、稳定、可移植，且 Python 标准库自带 `sqlite3`。

这个场景里 SQLite 很合适：
- 多轮积累
- 结构化归档
- 查询某个 case 的状态
- 按时间回放轮次
- 后续可接分析脚本或 UI

---

## 为什么用 `functools.lru_cache`

`state_store.py` 里对某些只读查询做了缓存，适合：
- 同一 case 被频繁编译上下文
- 同一轮状态被频繁读取
- 降低 SQLite 重复查询成本

当写入发生时，相关缓存会被显式清理。

---

## 这套包最适合谁

- 想把“会问问题”固化成技能的人
- 想做多轮复杂分析，但又不想上下文漂移的人
- 想把 AI 从“随口发挥”变成“有档案的智囊”的人
- 想把 agent / debug 分析过程显式化、可回放化的人

---

## 后续可以扩展什么

- Web UI
- TUI 面板
- 自动生成 Mermaid 时间线 / 假设图
- 更细的 case schema
- 更强的规则引擎
- 针对某领域的专用 question pack

