#!/usr/bin/env python3
"""
自动推送代码到 GitHub 和 Gitee
- Gitee：国内直连，不需要代理
- GitHub：自动检测代理端口并推送
"""

import subprocess
import socket
import sys
import os

# 常见代理端口
COMMON_PORTS = [10808, 7890, 1080, 10809, 8080, 1087, 7891, 7892]

# Gitee 认证信息
GITEE_REPO = "https://yolo-yo:693a5bedc99c60a9b783bb225fc4038c@gitee.com/yolo-yo/cninfo-board.git"
GITHUB_REPO = "https://Yolo-Yolo-MAx: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@github.com/Yolo-Yolo-MAx/cninfo-board.git"

def find_active_proxy():
    """检测当前可用的 SOCKS5 代理端口"""
    for port in COMMON_PORTS:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            s.close()
            if result == 0:
                return port
        except Exception:
            pass
    return None

def run_git_push(repo_path, remote, branch='main', proxy_port=None):
    """执行 git push"""
    cmd = ['git', 'push', remote, branch]
    
    env = os.environ.copy()
    if proxy_port:
        proxy_url = f"socks5h://127.0.0.1:{proxy_port}"
        env['ALL_PROXY'] = proxy_url
        env['HTTPS_PROXY'] = proxy_url
        env['HTTP_PROXY'] = proxy_url
        print(f"  代理: {proxy_url}")
    else:
        # 清除代理环境变量
        env['ALL_PROXY'] = ''
        env['HTTPS_PROXY'] = ''
        env['HTTP_PROXY'] = ''
        print(f"  代理: 无（直连）")
    
    print(f"  仓库: {remote}")
    print(f"  分支: {branch}")
    print("-" * 50)
    
    result = subprocess.run(
        cmd,
        cwd=repo_path,
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print(f"  STDOUT: {result.stdout[:200]}")
    if result.stderr:
        print(f"  STDERR: {result.stderr[:200]}")
    
    return result.returncode

def main():
    repo_path = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    
    print("=" * 60)
    print("自动推送代码到 GitHub + Gitee")
    print("=" * 60)
    print(f"仓库路径: {repo_path}")
    print()
    
    # 1. 先 commit 本地变更
    print("[1/4] 检查本地变更...")
    status_result = subprocess.run(
        ['git', 'status', '--porcelain'],
        cwd=repo_path,
        capture_output=True,
        text=True
    )
    
    if status_result.stdout.strip():
        print("  发现本地变更，正在提交...")
        subprocess.run(['git', 'add', '.'], cwd=repo_path)
        subprocess.run(
            ['git', 'commit', '-m', 'chore: 自动更新公告数据'],
            cwd=repo_path,
            capture_output=True
        )
        print("  ✅ 已提交本地变更")
    else:
        print("  无本地变更")
    print()
    
    # 2. 推送到 Gitee（直连，不需要代理）
    print("[2/4] 推送到 Gitee（国内直连）...")
    ret_gitee = run_git_push(repo_path, 'gitee', 'main', proxy_port=None)
    if ret_gitee == 0:
        print("  ✅ Gitee 推送成功！")
    else:
        print(f"  ❌ Gitee 推送失败（退出码: {ret_gitee}）")
    print()
    
    # 3. 检测代理并推送到 GitHub
    print("[3/4] 检测代理端口（用于 GitHub）...")
    proxy_port = find_active_proxy()
    
    if proxy_port:
        print(f"  ✅ 发现代理端口: 127.0.0.1:{proxy_port}")
        print()
        print("[4/4] 推送到 GitHub（通过代理）...")
        ret_github = run_git_push(repo_path, 'origin', 'main', proxy_port=proxy_port)
        if ret_github == 0:
            print("  ✅ GitHub 推送成功！")
        else:
            print(f"  ❌ GitHub 推送失败（退出码: {ret_github}）")
    else:
        print("  ⚠️  未检测到代理端口，跳过 GitHub 推送")
        print("  （Gitee 已推送成功，GitHub 可在 VPN 开启后手动推送）")
    
    print()
    print("=" * 60)
    print("✅ 推送流程完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
