# AI Skill 财税技术评价评分（Excel 版）

本项目用于将爬虫抓取的技术信息输入 Excel，并通过 AI Skill 生成 0-100 的财税适配评分。

## 目录结构

```
/ai_scoring
  /config
    skill.md
    scoring.yaml
    providers.yaml
  /input
    tech_raw.xlsx
  /output
    tech_score.xlsx
    tech_score_failed.xlsx
  /prompts
    prompt_builder.py
  /ai
    base_client.py
    client_factory.py
    mock_client.py
  /pipeline
    scorer.py
    validator.py
    retry.py
  /utils
    excel_io.py
    rule_parser.py
  main.py
  requirements.txt
```

## 快速开始

1. 安装依赖

```
pip install -r requirements.txt
```

2. 准备输入文件

将爬虫输出写入 `input/tech_raw.xlsx`。字段建议如下：

```
tech_id | name | repo_url | readme | stars | forks | last_update | issues_open | language | keywords | summary
```

3. 执行评分

```
python main.py --input input/tech_raw.xlsx --output output/tech_score.xlsx
```

## 配置说明

- `config/skill.md`：财税技术评价专家规则（Prompt 约束源）
- `config/scoring.yaml`：评分维度与权重
- `config/providers.yaml`：AI 供应商配置（默认 mock，不调用外部 API）

## 注意

- 当前默认 `mock` provider，仅用于流程验证
- 真实接入国内 AI 服务时，请在 `providers.yaml` 中新增配置，并通过环境变量提供 API Key
