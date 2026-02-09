# 🚀 Finance Radar

**Mars Digital Innovation - 财税技术雷达系统**

一个集成了爬虫、AI 评分和知识库管理的财税技术评估平台。

## ✨ 核心功能

- 🕷️ **智能爬虫** - 自动抓取 GitHub/小红书等平台的技术项目
- 🤖 **AI 评分** - 基于智谱 AI 的财税适配性评分系统（0-100分）
- 📚 **知识库** - 自动归档 Top 5 项目，生成详细分析报告
- 📊 **可视化控制台** - Streamlit 驱动的 Mars 品牌风格界面

## 🎯 快速开始

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API Key
# 在 Streamlit Cloud Secrets 或环境变量中设置 ZHIPU_API_KEY

# 启动应用
streamlit run app.py
```

### 云端部署

详见 [DEPLOYMENT.md](DEPLOYMENT.md)

## 📁 项目结构

```
finance-radar/
├── app.py                      # 主应用入口
├── ai_scoring/                 # AI 评分模块
│   ├── config/                 # 配置文件
│   ├── pipeline/               # 评分流程
│   └── prompts/                # Prompt 构建
├── crawlers/                   # 爬虫模块
├── knowledge_base/             # 知识库归档
└── .streamlit/                 # Streamlit 配置
```

## 🔒 安全说明

- API Key 通过环境变量管理，不在代码中硬编码
- 建议使用私有仓库
- 可配置邮箱白名单限制访问

## 📊 技术栈

- **前端**: Streamlit
- **AI**: 智谱 AI (GLM-4)
- **爬虫**: Playwright
- **数据处理**: Pandas, OpenPyXL

## 📝 License

Internal use only - Mars Incorporated

---

**Powered by Mars Digital Innovation** 🌟
