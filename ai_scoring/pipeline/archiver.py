import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import json
import logging

from ai_scoring.ai.client_factory import create_client
from ai_scoring.pipeline.retry import run_with_retry
from ai_scoring.utils.simple_yaml import load_yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KnowledgeArchiver:
    def __init__(self, provider_config_path: str = "ai_scoring/config/providers.yaml"):
        self.provider_config = load_yaml(provider_config_path)
        # 这里复用打分时的 client 配置，或者你可以专门为 archive 定义一个配置
        # 暂时我们只用 client.evaluate 来生成文本
        self.client = create_client(self.provider_config, {}) 
        self.output_dir = Path("knowledge_base")
        self.output_dir.mkdir(exist_ok=True)

    def archive_top_projects(self, score_file: str, top_n: int = 5) -> str:
        """
        读取评分文件，选取 Top N，生成深度报告并保存。
        返回生成报告的文件路径。
        """
        df = pd.read_excel(score_file)
        if "total_score" not in df.columns:
            raise ValueError("Invalid score file: missing 'total_score' column")
            
        # 排序并取 Top N
        top_df = df.sort_values(by="total_score", ascending=False).head(top_n)
        
        report_content = [
            f"# 🏆 Top {top_n} Finance Tech Archive",
            f"**Generated Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "---"
        ]
        
        for i, (idx, row) in enumerate(top_df.iterrows(), 1):
            print(f"Archiving [{i}/{top_n}]: {row.get('name')}...", flush=True)
            
            project_info = {
                "name": row.get("name"),
                "repo_url": row.get("repo_url"),
                "summary": row.get("summary"),
                "score": row.get("total_score"),
                "tags": row.get("tags"),
                "readme_excerpt": self._get_readme_excerpt(row) # 假设原始数据里可能有 readme，如果没有就为空
            }
            
            # 生成深度分析
            analysis = self._generate_analysis(project_info)
            
            report_content.append(f"## {i}. {project_info['name']} (Score: {project_info['score']})")
            report_content.append(f"- **URL**: {project_info['repo_url']}")
            report_content.append(f"- **Tags**: {project_info['tags']}")
            report_content.append("\n### 🧠 AI Deep Dive")
            report_content.append(analysis)
            report_content.append("\n---\n")
            
        # 保存文件
        filename = f"archive_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(report_content))
            
        print(f"Archive completed: {filepath}", flush=True)
        return str(filepath)

    def _get_readme_excerpt(self, row: pd.Series) -> str:
        # 这里是个 hack: 评分后的 Excel 可能没有 readme 列（为了减小体积通常不存）
        # 如果需要基于 Readme 生成部署指南，我们最好去 raw input 里找，或者重新抓取
        # 简化起见，这里先只用 summary，或者假设 Excel 里存了 reason_json 包含了一些信息
        return str(row.get("summary", ""))

    def _generate_analysis(self, info: Dict[str, Any]) -> str:
        prompt = f"""
        你是一位金融领域的资深技术架构师。
        请分析以下开源项目，并生成一份结构化的深度技术报告。
        **请务必使用中文回答**（代码片段和专有名词除外）。
        
        项目名称: {info['name']}
        URL: {info['repo_url']}
        描述: {info['summary']}
        
        请提供以下内容：
        1. **核心价值 (Why High Score)**: 解释为什么它在财务/会计自动化领域得分很高，解决了什么痛点？
        2. **关键特性 (Key Features)**: 列出它的核心功能点（Bullet points）。
        3. **部署与使用指南 (Deployment Guide)**: 基于常见的技术栈（Python/Node/Go等），给出一份简明的部署或使用步骤。
        
        要求：
        - 语言简洁、专业。
        - 格式为 Markdown。
        - **必须使用中文**。
        """
        
        try:
            # Use retry mechanism for stability
            return run_with_retry(
                lambda: self.client.evaluate(prompt),
                attempts=5,
                backoff_seconds=5.0
            )
        except Exception as e:
            return f"Error generating analysis: {str(e)}"

if __name__ == "__main__":
    # Test run
    archiver = KnowledgeArchiver()
    try:
        archiver.archive_top_projects("ai_scoring/output/tech_score_final.xlsx")
    except Exception as e:
        print(e)
