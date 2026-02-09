import logging
import pandas as pd
import sys
import os
from pathlib import Path
from crawlers.github_spider import GitHubSpider
from crawlers.xhs_spider import XhsSpider

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def resolve_path(path: str) -> str:
    if getattr(sys, "frozen", False):
        # In frozen app, base dir is sys._MEIPASS
        basedir = sys._MEIPASS
    else:
        # In normal script, base dir is current file's dir
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

def main():
    # 1. 运行 GitHub 爬虫
    logger.info("Step 1: Running GitHub Crawler...")
    config_path = resolve_path("crawlers/config/keywords.yaml")
    gh_spider = GitHubSpider(config_path)
    gh_data = gh_spider.run()
    
    # 2. 运行小红书爬虫 (如果环境支持)
    logger.info("Step 2: Running Xiaohongshu Crawler...")
    xhs_spider = XhsSpider(config_path)
    xhs_data = xhs_spider.run()
    
    # 3. 合并数据
    all_data = gh_data + xhs_data
    logger.info(f"Total items collected: {len(all_data)}")
    
    if not all_data:
        logger.warning("No data found. Exiting.")
        return

    # 4. 保存到 ai_scoring 的输入目录
    output_dir = Path("ai_scoring/input")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "tech_raw.xlsx"
    
    df = pd.DataFrame(all_data)
    
    # 简单的去重 (基于 URL)
    if "repo_url" in df.columns:
        df.drop_duplicates(subset=["repo_url"], inplace=True)
        
    df.to_excel(output_path, index=False)
    logger.info(f"Saved crawler results to: {output_path}")
    logger.info("Now you can run the scoring pipeline: python ai_scoring/main.py")

if __name__ == "__main__":
    main()
