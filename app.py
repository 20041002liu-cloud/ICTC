import streamlit as st
import pandas as pd
import subprocess
import os
import sys
import re
from pathlib import Path
from datetime import datetime

# --- Mars Branding & Config ---
st.set_page_config(
    page_title="Finance Radar",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Configuration ---
# API Key 从环境变量读取（Streamlit Cloud 部署时在 Secrets 中配置）
# API Key is read from environment variables (configure in Streamlit Cloud Secrets)
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")

# 默认使用的模型 (可以修改为 glm-4-plus, glm-4-flash 等)
DEFAULT_MODEL_NAME = "glm-4.7"

if ZHIPU_API_KEY:
    os.environ["ZHIPU_API_KEY"] = ZHIPU_API_KEY

# 覆盖配置文件中的模型设置
os.environ["ZHIPU_MODEL"] = DEFAULT_MODEL_NAME

# Mars Colors
COLORS = {
    "DeepBlue": "#0000A0",
    "ElectricBlue": "#0076C0",
    "BrightBlue": "#00D7B9",
    "Yellow": "#FFD100",
    "White": "#FFFFFF",
    "Black": "#000000",
    "DarkGray": "#333333"
}

# Custom CSS
st.markdown(f"""
    <style>
    .stApp {{
        background-color: {COLORS['DeepBlue']};
        color: {COLORS['White']};
    }}
    h1, h2, h3, h4, h5, h6 {{
        color: {COLORS['Yellow']} !important;
        font-family: 'Arial', sans-serif;
    }}
    /* Button Styling */
    .stButton > button {{
        background-color: {COLORS['Yellow']};
        color: {COLORS['DeepBlue']};
        border-radius: 8px;
        font-weight: bold;
        border: 2px solid {COLORS['Yellow']};
        padding: 0.5rem 1rem;
        transition: all 0.3s;
    }}
    .stButton > button:hover {{
        background-color: {COLORS['DeepBlue']};
        color: {COLORS['Yellow']};
        border: 2px solid {COLORS['Yellow']};
    }}
    
    /* Global Text Styling for Readability */
    .stCaption, div[data-testid="stCaptionContainer"] {{
        color: {COLORS['BrightBlue']} !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }}
    
    label, .stMarkdown p, .stMarkdown li {{
        color: {COLORS['White']} !important;
    }}
    
    /* Selectbox/Input labels */
    .stSelectbox label, .stTextInput label, .stNumberInput label, .stTextArea label {{
        color: {COLORS['Yellow']} !important;
        font-weight: bold !important;
    }}

    /* === DARK MODE OVERRIDES FOR INPUTS & EXPANDERS === */
    
    /* Expander (Details/Summary) */
    .stExpander {{
        background-color: {COLORS['DarkGray']} !important;
        border: 1px solid {COLORS['BrightBlue']} !important;
        border-radius: 5px;
    }}
    .stExpander > details > summary {{
        color: {COLORS['Yellow']} !important;
        background-color: {COLORS['DarkGray']} !important;
        border-radius: 5px;
    }}
    .stExpander > details > summary:hover {{
        color: {COLORS['BrightBlue']} !important;
    }}
    .stExpander > details[open] > summary {{
        border-bottom: 1px solid {COLORS['BrightBlue']} !important;
        border-bottom-left-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
    }}
    
    /* Input Fields Background (Selectbox, TextInput, etc.) */
    div[data-baseweb="select"] > div, 
    div[data-baseweb="input"] > div,
    div[data-baseweb="base-input"], 
    input.st-bd, textarea.st-bd {{
        background-color: {COLORS['DarkGray']} !important;
        color: {COLORS['White']} !important;
        border: 1px solid {COLORS['ElectricBlue']} !important;
    }}
    
    /* Input Text Color */
    input, textarea, .stSelectbox div[data-baseweb="select"] span {{
        color: {COLORS['White']} !important;
    }}
    
    /* Dropdown Menu Options */
    ul[data-baseweb="menu"] {{
        background-color: {COLORS['DarkGray']} !important;
    }}
    li[data-baseweb="option"] {{
        color: {COLORS['White']} !important;
    }}
    li[data-baseweb="option"]:hover, li[aria-selected="true"] {{
        background-color: {COLORS['ElectricBlue']} !important;
        color: {COLORS['Yellow']} !important;
    }}
    
    /* Multiselect Tag */
    span[data-baseweb="tag"] {{
        background-color: {COLORS['ElectricBlue']} !important;
    }}
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {{
        background-color: {COLORS['ElectricBlue']};
    }}
    
    /* Log Box Style */
    .log-card {{
        background-color: {COLORS['DarkGray']};
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid {COLORS['Yellow']};
        height: 500px;
        display: flex;
        flex-direction: column;
    }}
    .log-header {{
        color: {COLORS['Yellow']};
        font-weight: bold;
        margin-bottom: 10px;
        font-size: 1.1rem;
        border-bottom: 1px solid {COLORS['BrightBlue']};
        padding-bottom: 5px;
    }}
    .log-content {{
        background-color: {COLORS['Black']};
        color: #00FF00;
        font-family: 'Courier New', monospace;
        padding: 10px;
        border-radius: 5px;
        font-size: 0.8rem;
        flex-grow: 1;
        overflow-y: auto;
        border: 1px solid {COLORS['DeepBlue']};
    }}
    
    /* Radio Button Styling (Knowledge Base) */
    div[role="radiogroup"] * {{
        color: #FFFFFF !important;
        font-weight: bold !important;
    }}
    div[role="radiogroup"] label:hover {{
        color: #FFD100 !important;
    }}
        background-color: {COLORS['ElectricBlue']};
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid {COLORS['BrightBlue']};
    }}
    .tech-title {{
        color: {COLORS['Yellow']};
        font-weight: bold;
        font-size: 1.1rem;
    }}
    .tech-score {{
        float: right;
        color: {COLORS['White']};
        font-weight: bold;
        font-size: 1.2rem;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Log State ---
if 'logs' not in st.session_state:
    st.session_state.logs = []

import html

def log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    # Escape HTML characters to prevent breaking the layout
    safe_message = html.escape(message)
    st.session_state.logs.append(f"[{timestamp}] {safe_message}")

def render_logs(placeholder):
    if not placeholder: return
    # Show last 40 lines, reverse order to show newest at bottom (or just standard order)
    # Actually standard terminal is top-down, newest at bottom.
    # But for HTML div with overflow, we want it to scroll to bottom usually.
    # Here we just show text.
    log_content = "<br>".join(st.session_state.logs[-40:])
    placeholder.markdown(f"""
    <div class="log-card">
        <div class="log-header">📝 实时执行日志</div>
        <div class="log-content" id="log-container">
            {log_content}
            <script>
                var element = document.getElementById("log-container");
                element.scrollTop = element.scrollHeight;
            </script>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- Helper Functions ---
def parse_archive_file(file_path):
    """
    Parses an archive file and returns preamble and list of project line blocks.
    """
    if not os.path.exists(file_path):
        return [], []
        
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    preamble = []
    projects = []
    current_project_lines = []
    
    in_projects = False
    
    # Check for blacklist terms to avoid false positives on subheaders
    blacklist_terms = [
        "Why High Score", "Key Features", "Deployment Guide", "Technical Architecture", "AI Deep Dive",
        "核心价值", "关键特性", "部署与使用指南", "技术架构", "AI深度解析", "部署指南"
    ]
    
    for line in lines:
        # Match "## 1. Name"
        if re.match(r'^## \d+\. ', line):
            # Check if this is a subheader (false positive)
            is_blacklisted = False
            for term in blacklist_terms:
                if term in line:
                    is_blacklisted = True
                    break
            
            if is_blacklisted:
                if in_projects:
                    current_project_lines.append(line)
                else:
                    preamble.append(line)
            else:
                # Real new project start
                if current_project_lines:
                    projects.append(current_project_lines)
                current_project_lines = [line]
                in_projects = True
        else:
            if in_projects:
                current_project_lines.append(line)
            else:
                preamble.append(line)
                
    if current_project_lines:
        projects.append(current_project_lines)
        
    return preamble, projects

def save_archive_file(file_path, preamble, projects):
    """
    Saves the archive file, re-indexing projects.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(preamble)
        for idx, lines in enumerate(projects, 1):
            if not lines: continue
            # Update the index in the first line
            header = lines[0]
            # Regex to replace "## \d+." with "## {idx}."
            new_header = re.sub(r'^## \d+\.', f'## {idx}.', header)
            lines[0] = new_header
            f.writelines(lines)

def run_command(cmd_list, placeholder=None):
    try:
        log(f"Starting: {' '.join(cmd_list[:2])}...")
        if placeholder: render_logs(placeholder)
        
        # Force unbuffered output for Python subprocesses
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        
        process = subprocess.Popen(
            cmd_list,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=os.getcwd(),
            env=env
        )
        while True:
            # Read line by line
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                log(line.strip())
                if placeholder: render_logs(placeholder)
        
        if process.poll() == 0:
            log("Process finished successfully.")
        else:
            log("Process failed.")
        
        if placeholder: render_logs(placeholder)
        return process.poll() == 0
    except Exception as e:
        log(f"Error: {str(e)}")
        if placeholder: render_logs(placeholder)
        return False

# --- Navigation ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/15/Mars_Incorporated_Logo.svg", width=150)
    st.header("Mars Finance Radar")
    
    page = st.radio("导航 (Navigation)", ["🏠 控制台 (Console)", "🧠 知识库 (Knowledge Base)"], index=0)
    
    st.divider()
    st.subheader("⚙️ 设置 (Settings)") 
    
    # Safety Check: Warn if Key is not set
    if not os.getenv("ZHIPU_API_KEY"):
        st.error("⚠️ API Key 未配置！请在 Streamlit Cloud Secrets 中添加 ZHIPU_API_KEY。")

    # Model Selection (User can type any model name)
    st.caption("🤖 模型配置")
    current_model = os.environ.get("ZHIPU_MODEL", DEFAULT_MODEL_NAME)
    custom_model = st.text_input(
        "输入 AI 模型名称", 
        value=current_model,
        help="您可以输入任意智谱 AI 支持的模型名称，如 glm-4.7, glm-4-plus, glm-4-flash 等"
    )
    if custom_model:
        os.environ["ZHIPU_MODEL"] = custom_model
    
    st.caption(f"当前生效模型: **{os.environ.get('ZHIPU_MODEL')}**")

# ==========================================
# PAGE 1: CONSOLE (控制台)
# ==========================================
if "控制台" in page:
    st.title("🚀 控制中心 (Command Console)")
    st.markdown("---")

    main_col, log_col = st.columns([0.6, 0.4])

    # --- RIGHT COLUMN: Logs ---
    with log_col:
        log_placeholder = st.empty()
        # Always update logs at the end of run
        render_logs(log_placeholder)

    # --- LEFT COLUMN: Controls ---
    with main_col:
        st.subheader("🛠️ 任务执行 (Tasks)")
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("启动全网爬虫", use_container_width=True):
                with st.spinner("正在爬取..."):
                    if run_command([sys.executable, "run_crawler.py"], placeholder=log_placeholder):
                        st.success("爬取完成")
                        st.rerun()
        with c2:
            if st.button("启动 AI 评分", use_container_width=True):
                if not os.getenv("ZHIPU_API_KEY"):
                    st.error("请配置 API Key")
                else:
                    with st.spinner("正在评分..."):
                        cmd = [sys.executable, "ai_scoring/main.py", "--input", "ai_scoring/input/tech_raw.xlsx", "--output", "ai_scoring/output/tech_score_final.xlsx", "--providers", "ai_scoring/config/providers.yaml"]
                        if run_command(cmd, placeholder=log_placeholder):
                            st.success("评分完成")
                            st.rerun()
        with c3:
            if st.button("归档 Top 5", use_container_width=True):
                if not os.getenv("ZHIPU_API_KEY"):
                    st.error("请配置 API Key")
                else:
                    with st.spinner("正在归档..."):
                        cmd = [sys.executable, "run_archiver.py"]
                        if run_command(cmd, placeholder=log_placeholder):
                            st.success("归档完成")
                            st.rerun()

        st.divider()
        st.subheader("🏆 高分技术精选 (Top Rated)")
        output_file = Path("ai_scoring/output/tech_score_final.xlsx")
        
        if output_file.exists():
            try:
                df = pd.read_excel(output_file)
                if "total_score" in df.columns:
                    df = df.sort_values(by="total_score", ascending=False)
                
                for i, (index, row) in enumerate(df.head(4).iterrows()):
                    repo_link = row.get('repo_url', '#')
                    tags_html = ""
                    try:
                        tags = eval(row.get('tags', '[]')) if isinstance(row.get('tags'), str) else row.get('tags', [])
                        tags_html = " ".join([f"<span style='color:{COLORS['BrightBlue']};font-size:0.8rem'>#{t}</span>" for t in tags[:3]])
                    except: pass

                    st.markdown(f"""
                    <div class="tech-card">
                        <span class="tech-score">{row.get('total_score', 0):.1f}</span>
                        <div class="tech-title">
                            <a href="{repo_link}" target="_blank" style="color:{COLORS['Yellow']};text-decoration:none;">
                                {row.get('name', 'Unknown')}
                            </a>
                        </div>
                        <div>{tags_html}</div>
                        <div style="color:{COLORS['White']};font-size:0.9rem;margin-top:5px;">
                            {str(row.get('summary', ''))[:80]}...
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")
                
        st.divider()
        st.subheader("📊 数据透视 (Data Inspector)")
        t1, t2 = st.tabs(["评分结果", "原始数据"])
        with t1:
            if output_file.exists():
                if st.button("打开评分 Excel"): os.startfile(output_file.absolute())
                st.dataframe(pd.read_excel(output_file), use_container_width=True)
        with t2:
            raw_file = Path("ai_scoring/input/tech_raw.xlsx")
            if raw_file.exists():
                if st.button("打开原始 Excel"): os.startfile(raw_file.absolute())
                st.dataframe(pd.read_excel(raw_file), use_container_width=True)

# ==========================================
# PAGE 2: KNOWLEDGE BASE (知识库)
# ==========================================
elif "知识库" in page:
    st.title("🧠 知识库 (Knowledge Base)")
    
    # 扫描归档文件
    kb_dir = Path("knowledge_base")
    kb_dir.mkdir(exist_ok=True)
    archive_files = sorted(list(kb_dir.glob("*.md")), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not archive_files:
        st.info("暂无归档记录，请先在控制台生成报告。")
    else:
        # --- 管理功能 (折叠) ---
        with st.expander("🛠️ 内容管理 (Manage Content)", expanded=False):
            m1, m2 = st.tabs(["🗑️ 删除项目 (Delete Project)", "➕ 新建项目 (Add Project)"])
            
            # --- Tab 1: Delete Project ---
            with m1:
                st.caption("从归档文件中删除特定项目。")
                # Select file
                selected_file_name = st.selectbox("选择归档文件:", [f.name for f in archive_files], key="del_file_select")
                
                if selected_file_name:
                    target_file = kb_dir / selected_file_name
                    # Parse file
                    preamble, projects = parse_archive_file(target_file)
                    
                    # Extract project names for selection
                    project_names = []
                    for p_lines in projects:
                        if not p_lines: continue
                        # header is p_lines[0] like "## 1. Name (Score: 80)"
                        header = p_lines[0].strip()
                        # Clean up name
                        clean_name = re.sub(r'^## \d+\. ', '', header)
                        project_names.append(clean_name)
                    
                    projects_to_delete = st.multiselect("选择要删除的项目:", project_names)
                    
                    if st.button("🗑️ 确认删除选中项目", type="primary", key="btn_del_proj"):
                        if projects_to_delete:
                            # Filter out deleted projects
                            new_projects = []
                            deleted_count = 0
                            for p_lines in projects:
                                if not p_lines: continue
                                header = p_lines[0].strip()
                                clean_name = re.sub(r'^## \d+\. ', '', header)
                                if clean_name in projects_to_delete:
                                    deleted_count += 1
                                else:
                                    new_projects.append(p_lines)
                            
                            # Save back
                            save_archive_file(target_file, preamble, new_projects)
                            st.success(f"已删除 {deleted_count} 个项目！")
                            st.rerun()
                        else:
                            st.warning("请先选择项目。")

                st.divider()
                st.caption("或者删除整个归档文件:")
                files_to_delete = st.multiselect(
                    "选择要删除的文件:",
                    options=[f.name for f in archive_files],
                    key="del_whole_file"
                )
                if st.button("🗑️ 删除选中文件", type="secondary", key="btn_del_file"):
                    if files_to_delete:
                        for fname in files_to_delete:
                            try:
                                (kb_dir / fname).unlink(missing_ok=True)
                                st.toast(f"已删除: {fname}")
                            except Exception as e:
                                st.error(f"删除失败 {fname}: {e}")
                        
                        st.success("文件已删除")
                        st.rerun()

            # --- Tab 2: Add Project ---
            with m2:
                st.caption("手动添加新项目到最新的归档文件中。")
                latest_file = archive_files[0] if archive_files else None
                
                with st.form("add_project_form"):
                    new_name = st.text_input("项目名称 (Name)")
                    new_score = st.number_input("评分 (Score)", min_value=0.0, max_value=100.0, value=80.0)
                    new_url = st.text_input("项目链接 (URL)")
                    new_tags = st.text_input("标签 (Tags, 逗号分隔)", placeholder="DeFi, Python, AI")
                    new_desc = st.text_area("详细描述/AI分析 (Description)", height=200, placeholder="## 核心价值\n...\n## 关键特性\n...")
                    
                    submitted = st.form_submit_button("➕ 添加项目")
                    
                    if submitted:
                        if not new_name:
                            st.error("请输入项目名称")
                        else:
                            # Construct content
                            if not latest_file:
                                # Create new file if none exists
                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                latest_file = kb_dir / f"archive_{timestamp}.md"
                                with open(latest_file, "w", encoding="utf-8") as f:
                                    f.write(f"# 🏆 Top 5 Finance Tech Archive\n**Generated Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n---\n")
                            
                            # Prepare lines
                            header = f"## 999. {new_name} (Score: {new_score:.2f})\n"
                            meta = f"- **URL**: {new_url}\n- **Tags**: {new_tags}\n\n"
                            content = f"{new_desc}\n\n"
                            
                            new_block = [header, meta, content]
                            
                            # Read, append, save (to handle re-indexing)
                            preamble, projects = parse_archive_file(latest_file)
                            projects.append(new_block)
                            save_archive_file(latest_file, preamble, projects)
                            
                            st.success(f"已添加项目: {new_name}")
                            st.rerun()

        # 1. 聚合所有项目：遍历所有归档文件，提取项目
        all_projects = []
        for f_path in archive_files:
            try:
                with open(f_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 第一段通常是文件头
                file_date = f_path.stem.replace("archive_", "")
                
                # 更稳健的方式：手动根据行来解析
                lines = content.split('\n')
                current_project = {}
                project_buffer = []
                
                # 黑名单：如果标题包含这些词，就认为它不是项目名，而是子标题，跳过
                blacklist_terms = [
                    "Why High Score", "Key Features", "Deployment Guide", "Technical Architecture", "AI Deep Dive",
                    "核心价值", "关键特性", "部署与使用指南", "技术架构", "AI深度解析", "部署指南"
                ]

                for line in lines:
                    # 匹配 "## 1. Name"
                    if re.match(r'^## \d+\. ', line):
                        # 检查黑名单
                        is_blacklisted = False
                        for term in blacklist_terms:
                            if term in line:
                                is_blacklisted = True
                                break
                        
                        if is_blacklisted:
                            # 即使匹配了正则，如果包含黑名单词，也视为当前项目的内容，而不是新项目
                            if current_project:
                                project_buffer.append(line)
                            continue

                        # 如果已有正在处理的项目，先保存
                        if current_project:
                            current_project['content'] = "\n".join(project_buffer)
                            all_projects.append(current_project)
                            
                        # 开始新项目
                        project_buffer = [line] # 保留标题行以便渲染
                        title_text = line.replace("## ", "").strip() # "1. BitTax (Score: 82.35)"
                        
                        # 提取纯名
                        if ". " in title_text:
                            # 1. BitTax (Score...) -> BitTax
                            try:
                                name_part = title_text.split(". ", 1)[1]
                                name = name_part.split(" (Score")[0]
                            except:
                                name = title_text
                        else:
                            name = title_text
                            
                        current_project = {
                            "name": name,
                            "full_title": title_text,
                            "source_file": f_path.name,
                            "date": file_date
                        }
                    elif current_project:
                        # 只要在项目块内，就添加内容
                        project_buffer.append(line)
                        
                # 循环结束后，保存最后一个项目
                if current_project:
                    current_project['content'] = "\n".join(project_buffer)
                    all_projects.append(current_project)

            except Exception:
                continue
                
        # 2. 界面布局：左侧项目列表，右侧详情
        col_list, col_detail = st.columns([0.3, 0.7])
        
        with col_list:
            st.subheader("📂 项目列表 (Projects)")
            st.caption("按时间倒序排列")
            
            # 构造显示名称：ProjectName (Date)
            options_map = {f"{p['name']} [{p['date']}]": p for p in all_projects}
            
            selected_label = st.radio(
                "Select Project:",
                options=list(options_map.keys()),
                label_visibility="collapsed"
            )
            
        with col_detail:
            if selected_label:
                project = options_map[selected_label]
                
                # 渲染头部卡片
                st.markdown(f"""
                <div style="background-color:{COLORS['DarkGray']};padding:20px;border-radius:10px;border-left:5px solid {COLORS['Yellow']};margin-bottom:20px">
                    <h2 style="margin:0;color:{COLORS['Yellow']}">{project['full_title']}</h2>
                    <p style="margin-top:5px;color:{COLORS['BrightBlue']}">📅 归档来源: {project['source_file']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # 渲染 Markdown 正文 (去掉第一行标题)
                body = "\n".join(project['content'].split("\n")[1:])
                st.markdown(body)
            else:
                st.info("👈 请从左侧选择一个项目查看详情")

# Footer
st.markdown("---")
st.markdown(f"<div style='text-align: center; color: {COLORS['BrightBlue']}'>Powered by Mars Digital Innovation</div>", unsafe_allow_html=True)
