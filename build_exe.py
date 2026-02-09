import PyInstaller.__main__
import os
import shutil

# 清理旧构建
if os.path.exists("dist"):
    try:
        shutil.rmtree("dist")
    except Exception as e:
        print(f"Warning: Could not remove dist directory: {e}")

if os.path.exists("build"):
    try:
        shutil.rmtree("build")
    except Exception as e:
        print(f"Warning: Could not remove build directory: {e}")

print("Starting PyInstaller Build...")

PyInstaller.__main__.run([
    "run_app.py",
    "--name=FinanceRadar",
    "--onefile",
    "--clean",
    
    # 核心数据文件
    "--add-data=app.py;.",
    "--add-data=run_crawler.py;.",
    "--add-data=run_archiver.py;.",
    "--add-data=crawlers;crawlers",
    "--add-data=ai_scoring;ai_scoring",
    
    # 强制收集所有依赖库的元数据和隐式导入
    "--collect-all=streamlit",
    "--collect-all=altair",
    "--collect-all=pandas",
    "--collect-all=zhipuai",
    "--collect-all=playwright",
    
    # 排除大体积无关库
    "--exclude-module=matplotlib",
    "--exclude-module=tkinter",
    "--exclude-module=ipython",
    "--exclude-module=notebook",
    
    # Custom output directory
    "--distpath=dist_v2",
    "--workpath=build_v2",
])

print("\nBuild Complete! Look for 'FinanceRadar.exe' in the dist_v2/ folder.")
