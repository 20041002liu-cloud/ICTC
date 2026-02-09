import time
import requests
import yaml
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GitHubSpider:
    BASE_URL = "https://api.github.com/search/repositories"
    
    # 强制排除词
    EXCLUDE_TERMS = [
        "game", "gaming", "unity", "unreal", "minecraft", "mods", 
        "hardware", "arduino", "firmware", "driver", "bios", 
        "music", "audio", "video", "player", "movie",
        "proxy", "vpn", "trojan", "hack", "cheat"
    ]

    def __init__(self, config_path: str = "crawlers/config/keywords.yaml"):
        self.config = self._load_config(config_path)
        self.seen_ids: Set[str] = set()
        
    def _load_config(self, path: str) -> Dict[str, Any]:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _get_headers(self) -> Dict[str, str]:
        return {"Accept": "application/vnd.github.v3+json"}

    def _build_query(self, keyword: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """构建单个查询参数"""
        days = strategy.get('days_back', 7)
        date_threshold = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        suffix_template = strategy.get('query_suffix', "")
        suffix = suffix_template.replace("{date}", date_threshold)
        
        kw_safe = f'"{keyword}"' if " " in keyword else keyword
        q = f"{kw_safe} {suffix}"
        
        return {
            "q": q,
            "sort": strategy.get('sort', 'stars'),
            "order": "desc",
            "per_page": 5 # 每次只抓前5个，然后挑最好的
        }

    def _is_relevant(self, item: Dict[str, Any]) -> bool:
        """简单的内容相关性检查"""
        text = (str(item.get('description', '')) + " " + str(item.get('name', ''))).lower()
        for term in self.EXCLUDE_TERMS:
            if term in text:
                return False
        return True

    def _fetch_readme(self, owner: str, repo: str, default_branch: str = "main") -> str:
        branches = [default_branch, "master"]
        for branch in branches:
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
            try:
                resp = requests.get(url, timeout=5)
                if resp.status_code == 200:
                    return resp.text[:5000]
            except Exception:
                continue
        return ""

    def run(self) -> List[Dict[str, Any]]:
        finance_kws = self.config.get('finance_keywords', [])
        strategies = self.config.get('github_search', {}).get('strategies', {})
        
        # 获取两种策略配置
        s_latest = strategies.get('latest_week')
        s_classic = strategies.get('classic_fallback')
        
        if not s_latest or not s_classic:
            logger.error("Missing strategies in config.yaml")
            return []

        all_results = []
        
        logger.info(f"Starting tiered crawl for {len(finance_kws)} keywords...")
        
        for i, kw in enumerate(finance_kws):
            logger.info(f"[{i+1}/{len(finance_kws)}] Processing keyword: {kw}")
            
            keyword_results = []
            
            # --- Tier 1: 最近一周 (0星也行) ---
            q_params = self._build_query(kw, s_latest)
            items_latest = self._execute_search(q_params)
            
            for item in items_latest:
                if self._process_item(item, kw, "latest_week", keyword_results):
                    if len(keyword_results) >= 2: break # 够了就停
            
            # --- Tier 2: 如果不够，用经典策略补齐 ---
            if len(keyword_results) < 2:
                needed = 2 - len(keyword_results)
                logger.info(f"  > Found {len(keyword_results)} latest items. Fetching {needed} more from fallback...")
                
                q_params = self._build_query(kw, s_classic)
                items_classic = self._execute_search(q_params)
                
                count = 0
                for item in items_classic:
                    if self._process_item(item, kw, "classic_fallback", keyword_results):
                        count += 1
                        if count >= needed: break
            
            all_results.extend(keyword_results)
            time.sleep(2) # 避免速率限制
            
        logger.info(f"Crawl finished. Found {len(all_results)} unique repos.")
        return all_results

    def _execute_search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            resp = requests.get(self.BASE_URL, headers=self._get_headers(), params=params, timeout=10)
            if resp.status_code == 403:
                logger.warning("Rate limit hit. Sleeping for 60s...")
                time.sleep(60)
                # Retry once
                resp = requests.get(self.BASE_URL, headers=self._get_headers(), params=params, timeout=10)
            
            if resp.status_code == 200:
                return resp.json().get("items", [])
        except Exception as e:
            logger.error(f"Request failed: {e}")
        return []

    def _process_item(self, item: Dict[str, Any], keyword: str, strategy: str, result_list: List[Dict[str, Any]]) -> bool:
        """处理单个项目：去重、过滤、格式化"""
        repo_id = str(item['id'])
        
        # 全局去重
        if repo_id in self.seen_ids:
            return False
            
        # 内容过滤
        if not self._is_relevant(item):
            return False
            
        # 记录
        self.seen_ids.add(repo_id)
        
        row = {
            "tech_id": f"GH_{repo_id}",
            "name": item['name'],
            "repo_url": item['html_url'],
            "stars": item['stargazers_count'],
            "forks": item['forks_count'],
            "issues_open": item['open_issues_count'],
            "language": item['language'],
            "last_update": item['pushed_at'],
            "summary": item['description'],
            "keywords": f"{keyword} ({strategy})",
            "readme": self._fetch_readme(item['owner']['login'], item['name'], item['default_branch'])
        }
        
        result_list.append(row)
        return True

if __name__ == "__main__":
    spider = GitHubSpider()
    data = spider.run()
    print(f"Got {len(data)} items")
