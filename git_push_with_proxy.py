#!/usr/bin/env python3
"""
自动推送代码到 GitHub 和 Gitee
- Gitee：国内直连，不需要代理
- GitHub：自动检测代理端口并推送
代理优先级：HTTP 代理(7890) > SOCKS5 代理(10808)，Windows Git 不支持 socks5h://
"""

import subprocess
import socket
import sys
import os

# HTTP 代理端口（Windows Git 原生支持，优先）
HTTP_PORTS = [7890, 7891, 7892, 8080]
# SOCKS5 代理端口（Windows Git 不支持 socks5h://，仅作兜底用 socks5://）
SOCKS_PORTS = [10808, 10809, 1080, 1087]

# Gitee 认证信息（从环境变量读取，不在代码中暴露）
GITEE_REPO = os.environ.get('GITEE_REPO', '')
GITEE_TOKEN = os.environ.get('GITEE_TOKEN', '')

# GitHub 认证信息（从环境变量读取）
GITHUB_REPO = os.environ.get('GITHUB_REPO', '')
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')


def find_active_proxy():
    """检测当前可用的代理端口，返回 (port, scheme)
    优先检测 HTTP 代理（Windows Git 原生支持），
    SOCKS5 仅作兜底（Windows 下用 socks5:// 而非 socks5h://）。
    """
    # 优先检测 HTTP 代理
    for port in HTTP_PORTS:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            s.close()
            if result == 0:
                return port, "http"
        except Exception:
            pass

    # 兜底：检测 SOCKS5 代理
    for port in SOCKS_PORTS:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex(('127.0.0.1', port))
            s.close()
            if result == 0:
                return port, "socks5"
        except Exception:
            pass

    return None, None


def run_git_push(repo_path, remote, branch='main', proxy_port=None, proxy_scheme=None):
    """执行 git push"""
    cmd = ['git', 'push', remote, branch]

    # 如果有代理，临时设置 git 配置
    if proxy_port and proxy_scheme:
        if proxy_scheme == "http":
            proxy_url = f"http://127.0.0.1:{proxy_port}"
        else:
            # Windows Git 不支持 socks5h://，用 socks5://
            proxy_url = f"socks5://127.0.0.1:{proxy_port}"
        print(f"  代理: {proxy_url}")
        # 临时设置代理（仅当前仓库）
        subprocess.run(
            ['git', 'config', 'http.proxy', proxy_url],
            cwd=repo_path,
            capture_output=True
        )
        subprocess.run(
            ['git', 'config', 'https.proxy', proxy_url],
            cwd=repo_path,
            capture_output=True
        )
    else:
        print(f"  代理: 无（直连）")
        # 清除代理配置
        subprocess.run(
            ['git', 'config', '--unset', 'http.proxy'],
            cwd=repo_path,
            capture_output=True
        )
        subprocess.run(
            ['git', 'config', '--unset', 'https.proxy'],
            cwd=repo_path,
            capture_output=True
        )

    print(f"  仓库: {remote}")
    print(f"  分支: {branch}")
    print("-" * 50)

    result = subprocess.run(
        cmd,
        cwd=repo_path,
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
    ret_gitee = run_git_push(repo_path, 'gitee', 'main', proxy_port=None, proxy_scheme=None)
    if ret_gitee == 0:
        print("  ✅ Gitee 推送成功！")
    else:
        print(f"  ❌ Gitee 推送失败（退出码: {ret_gitee}）")
    print()

    # 3. 检测代理并推送到 GitHub
    print("[3/4] 检测代理端口（用于 GitHub）...")
    proxy_port, proxy_scheme = find_active_proxy()

    if proxy_port:
        print(f"  ✅ 发现代理端口: 127.0.0.1:{proxy_port}（{proxy_scheme}）")
        print()
        print("[4/4] 推送到 GitHub（通过代理）...")
        ret_github = run_git_push(repo_path, 'origin', 'main', proxy_port=proxy_port, proxy_scheme=proxy_scheme)
        if ret_github == 0:
            print("  ✅ GitHub 推送成功！")
        else:
            print(f"  ❌ GitHub 推送失败（退出码: {ret_github}）")
    else:
        print("  ⚠️  未检测到代理端口，跳过 GitHub 推送")
        print("  （Gitee 已推送成功，GitHub 可在 VPN/代理开启后手动推送）")

    print()
    print("=" * 60)
    print("✅ 推送流程完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
