import os
import sys
import socket
import runpy
import streamlit.web.cli as stcli

def resolve_path(path):
    if getattr(sys, "frozen", False):
        basedir = sys._MEIPASS
    else:
        basedir = os.path.dirname(__file__)
    return os.path.join(basedir, path)

def find_free_port(start_port=8501, max_tries=20):
    for port in range(start_port, start_port + max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return start_port  # 如果都失败，还是尝试默认端口

if __name__ == "__main__":
    # 0. Dispatcher for internal scripts (run_crawler, run_archiver, etc.)
    # This allows the frozen exe to run these scripts via subprocess
    if len(sys.argv) > 1:
        target_script = sys.argv[1]
        known_scripts = ["run_crawler.py", "run_archiver.py", "ai_scoring/main.py"]
        
        # Normalize slashes for comparison just in case
        target_normalized = target_script.replace("\\", "/")
        
        if target_normalized in known_scripts:
            script_path = resolve_path(target_script)
            
            # Ensure the script's directory is in sys.path so imports work
            script_dir = os.path.dirname(script_path)
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
            
            # Remove the executable name from argv, so argv[0] becomes the script name
            # Current argv: [exe_path, script_name, arg1, arg2...]
            # New argv: [script_name, arg1, arg2...]
            sys.argv.pop(0)
            
            print(f"Redirecting to internal script: {script_path}")
            try:
                # Use runpy to execute the script in the current process
                runpy.run_path(script_path, run_name="__main__")
            except Exception as e:
                print(f"Error running script {target_script}: {e}")
                import traceback
                traceback.print_exc()
            sys.exit(0)

    # 强制配置环境，解决打包后的路径和配置问题
    os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "false"
    
    # 查找可用端口
    port = find_free_port()
    print(f"Starting Finance Radar on port {port}...")
    
    # 获取 app.py 的真实路径
    app_path = resolve_path("app.py")
    
    # 模拟命令行参数
    sys.argv = [
        "streamlit",
        "run",
        app_path,
        "--server.address=localhost",
        f"--server.port={port}",
        "--global.developmentMode=false",
    ]
    
    sys.exit(stcli.main())
