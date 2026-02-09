import sys
import os
from pathlib import Path

# 确保项目根目录在 sys.path 中
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

from ai_scoring.pipeline.archiver import KnowledgeArchiver

def main():
    try:
        archiver = KnowledgeArchiver()
        report_path = archiver.archive_top_projects("ai_scoring/output/tech_score_final.xlsx")
        print(f"SUCCESS: {report_path}") # 输出成功路径供 app.py 捕获
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
