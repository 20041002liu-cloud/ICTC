# 🚀 Finance Radar - Streamlit Cloud 部署指南

## 📋 部署前准备

### 1. 创建 GitHub 仓库
```bash
# 初始化 Git（如果还没有）
git init
git add .
git commit -m "Initial commit for Streamlit Cloud deployment"

# 创建 GitHub 私有仓库并推送
git remote add origin https://github.com/你的用户名/finance-radar.git
git branch -M main
git push -u origin main
```

### 2. 注意事项
- ✅ API Key 已从代码中移除，改为环境变量
- ✅ 已创建 `.gitignore` 避免上传敏感数据
- ✅ 已创建 `packages.txt` 用于系统依赖

## 🌐 Streamlit Cloud 部署步骤

### Step 1: 访问 Streamlit Cloud
1. 打开 [share.streamlit.io](https://share.streamlit.io)
2. 使用 GitHub 账号登录

### Step 2: 创建新应用
1. 点击 "New app"
2. 选择你的仓库：`你的用户名/finance-radar`
3. 主文件路径：`app.py`
4. 点击 "Deploy"

### Step 3: 配置 Secrets（重要！）
1. 在应用部署后，点击右上角 "⚙️ Settings"
2. 选择 "Secrets"
3. 添加以下内容：

```toml
ZHIPU_API_KEY = "087ec55543d54975b11603cea0f25c0d.W8Hg5UQ9ksEFoxWg"
```

4. 点击 "Save"
5. 应用会自动重启

### Step 4: 安装 Playwright（首次运行）
由于项目使用 Playwright 爬虫，首次部署可能需要额外配置。如果遇到问题：

1. 在 Streamlit Cloud 的 "Advanced settings" 中
2. 添加启动命令：
```bash
playwright install chromium && streamlit run app.py
```

## 🔒 安全设置

### 设置访问权限
1. 在 Settings > Sharing 中
2. 选择 "Restrict viewing to specific email addresses"
3. 添加公司同事的邮箱地址

### 自定义域名（可选）
1. 在 Settings > General 中
2. 设置自定义 URL：`your-company-finance-radar`
3. 最终地址：`https://your-company-finance-radar.streamlit.app`

## 📊 使用说明

部署成功后，你的同事可以：
1. 访问分配的 URL
2. 使用 GitHub/Google 账号登录（如果设置了访问限制）
3. 直接使用所有功能：
   - 🕷️ 启动爬虫
   - 🤖 AI 评分
   - 📚 查看知识库

## ⚠️ 注意事项

### 资源限制
Streamlit Cloud 免费版限制：
- CPU: 1 core
- RAM: 1 GB
- 存储: 1 GB
- 并发用户: 建议 < 10 人

### 数据持久化
- ⚠️ Streamlit Cloud 的文件系统是临时的
- 每次重启会丢失 `knowledge_base/` 和 `output/` 数据
- 建议定期下载归档文件

### 解决方案（如需持久化）
可以集成云存储：
- 阿里云 OSS
- 腾讯云 COS
- AWS S3

## 🐛 常见问题

### 1. Playwright 安装失败
**解决方案**：在 `requirements.txt` 中使用 `playwright==1.40.0`

### 2. 爬虫功能无法使用
**原因**：Streamlit Cloud 可能限制某些网络请求
**解决方案**：
- 使用代理
- 或者只在本地运行爬虫，手动上传数据文件

### 3. 应用运行缓慢
**原因**：免费版资源有限
**解决方案**：
- 优化代码性能
- 升级到 Streamlit Cloud Pro（$20/月）
- 或迁移到自建服务器

## 📞 技术支持

如有问题，联系：
- Streamlit 文档：https://docs.streamlit.io
- 社区论坛：https://discuss.streamlit.io

---

**部署完成后，记得测试所有功能！** 🎉
