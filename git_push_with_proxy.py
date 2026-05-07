#!/usr/bin/env python3
"""
自动检测代理端口并 git push
支持常见 VPN/代理软件的端口自动检测
"""

import subprocess
import socket
import sys
import os

# 常见代理端口（按优先级排序）
COMMON_PORTS = [10808, 7890, 1080, 10809, 8080, 1087, 7891, 7892]

def find_active_proxy():
    """检测当前可用的 SOCKS5 代理端口"""
    for port in COMMON_PORTS:
        try:
            # 尝试连接本地端口
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            s.close()
            if result == 0:
                # 端口有进程监听，验证是否是 SOCKS5（简单测试）
                print(f"发现活跃端口: 127.0.0.1:{port}")
                return port
        except Exception:
            pass
    return None

def git_push_with_proxy(repo_path, proxy_port):
    """使用指定代理端口进行 git push"""
    proxy_url = f"socks5h://127.0.0.1:{proxy_port}"

    # 临时设置代理（仅当前命令有效）
    env = os.environ.copy()
    env['ALL_PROXY'] = proxy_url
    env['HTTPS_PROXY'] = proxy_url
    env['HTTP_PROXY'] = proxy_url

    print(f"使用代理推送: {proxy_url}")
    print(f"仓库路径: {repo_path}")

    # git push
    result = subprocess.run(
        ['git', 'push', 'origin', 'main'],
        cwd=repo_path,
        env=env,
        capture_output=True,
        text=True
    )

    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    return result.returncode

def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    print("=" * 50)
    print("自动检测代理端口并 git push")
    print("=" * 50)

    # 1. 检测代理端口
    proxy_port = find_active_proxy()

    if proxy_port is None:
        print("未检测到活跃代理端口！")
        print("请确保 VPN/代理软件已启动")
        print(f"支持的端口: {COMMON_PORTS}")
        sys.exit(1)

    print(f"✅ 使用代理端口: {proxy_port}")

    # 2. 使用代理推送
    ret = git_push_with_proxy(repo_path, proxy_port)

    if ret == 0:
        print("✅ git push 成功！")
    else:
        print(f"❌ git push 失败，退出码: {ret}")
        sys.exit(ret)

if __name__ == '__main__':
    main()
