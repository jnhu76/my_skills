# 贡献指南

## Skill Pack 结构规范

一个 skill 至少要包含：

```
skill_name/
├── README.md           # 必需，说明用途、使用方式、目录结构
├── mainfest.json       # 必需，元数据与方法论
├── general/
│   └── skill.md        # 至少一个 skill.md
├── python/             # 可选，辅助工具脚本
├── shared/templates/   # 可选，共享模板
└── examples/           # 可选，使用示例
```

## Skill 命名规范

- 使用小写下划线命名：`phenomenon_skill`、`debug_workflow`
- 名称要表达方法或用途，不要过于口语化
- 示例：`phenomenon_skill`、`trace_analysis`、`hypothesis_mapper`

## 版本规范

- `0.x`：还在快速迭代，结构可能变化
- `1.0.0`：结构稳定，接口不变
- 遵循 [Semantic Versioning](https://semver.org/)

## mainfest.json 格式

```json
{
  "name": "skill_name",
  "version": "0.1.0",
  "description": "一句话描述",
  "modes": ["general"],
  "has_python_tools": false,
  "entrypoints": {
    "general": "general/skill.md"
  }
}
```

## 新增 Skill 流程

1. 创建目录，命名遵循上述规范
2. 至少包含 `README.md`、`mainfest.json` 和一个 `skill.md`
3. 如有辅助工具放入 `python/`
4. 更新根目录 `README.md` 中的技能表格
5. 提交
