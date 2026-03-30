#!/usr/bin/env python3
"""
GitHub AI 趋势捕手自动化脚本
功能：抓取 GitHub Trending Python/AI 项目 → Minimax AI 总结 → Discord Webhook 推送
"""

import requests
import json
import os
from datetime import datetime

# ============================================================
# 配置信息
# ============================================================

# Minimax API Key (从 Minimax 控制台获取)
# 在 GitHub Actions 中使用 secrets.MINIMAX_API_KEY
# 本地运行时从环境变量 MINIMAX_API_KEY 读取
MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "")

# Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1488096438721183908/DU0H3LzSSI1t1U_t-xFq_ojs8X6WL3FIe6-5tMe5A8H8d0vW_PzNESGD95bUgGWMTi1n"

# ============================================================
# 配置结束
# ============================================================


def get_github_trending_python():
    """抓取 GitHub Trending Python 项目"""
    url = "https://api.github.com/search/repositories"
    params = {
        "q": "language:python created:>=" + datetime.now().strftime("%Y-%m-%d"),
        "sort": "stars",
        "order": "desc",
        "per_page": 10
    }
    headers = {"Accept": "application/vnd.github.v3+json"}

    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json().get("items", [])
    except requests.RequestException as e:
        print(f"GitHub API 请求失败: {e}")
        return []


def summarize_with_minimax(projects):
    """调用 Minimax API 总结项目"""
    if not projects:
        return "今日暂无新增 Python AI 项目。"

    if not MINIMAX_API_KEY:
        return "Minimax API Key 未设置，请检查环境变量 MINIMAX_API_KEY"

    # 构建项目列表
    project_list = "\n".join([
        f"{i+1}. **{p['name']}** - star: {p['stargazers_count']} | author: {p['owner']['login']}\n"
        f"   desc: {p['description'] or '暂无描述'}\n"
        f"   url: {p['html_url']}"
        for i, p in enumerate(projects)
    ])

    prompt = f"""你是专业的 AI 技术资讯分析师。请分析以下今日 GitHub Trending Python/AI 项目：

{project_list}

请对每个项目用中文总结：
1. 核心亮点是什么？
2. 它使用了什么 AI/ML 技术？
3. 对普通 AI 玩家有什么具体帮助？

回复格式要求：
- 简洁有力，突出重点
- 用普通人能理解的语言解释技术
- 每个项目用 2-3 句话总结"""

    try:
        response = requests.post(
            "https://api.minimax.chat/v1/text/chatcompletion_v2",
            headers={
                "Authorization": f"Bearer {MINIMAX_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "MiniMax-Text-01",
                "max_tokens": 2048,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Minimax API 调用失败: {e}"


def send_to_discord(message):
    """通过 Discord Webhook 发送消息"""
    if DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        print("⚠️ Discord Webhook URL 未配置，跳过发送")
        return False

    try:
        payload = {
            "content": message,
            "username": "GitHub AI 趋势捕手"
        }
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=30)
        return response.status_code == 204
    except requests.RequestException as e:
        print(f"Discord 推送失败: {e}")
        return False


def main():
    print("=" * 50)
    print("[GitHub AI 趋势捕手启动]")
    print("=" * 50)

    # 1. 抓取数据
    print("\n[正在抓取 GitHub Trending Python/AI 项目...]")
    projects = get_github_trending_python()

    if not projects:
        print("[未能获取到项目数据]")
        return

    print(f"[成功获取 {len(projects)} 个项目]")

    # 2. AI 总结
    print("\n[正在调用 Minimax AI 进行总结...]")
    summary = summarize_with_minimax(projects)

    # 3. 构推发送内容
    today = datetime.now().strftime("%Y-%m-%d")
    discord_message = f"""**GitHub AI 趋势日报** | {today}

{summary}

---
数据来源: GitHub Trending"""

    # 4. 发送到 Discord
    print("\n[正在推送至 Discord...]")
    if send_to_discord(discord_message):
        print("[Discord 推送成功]")
    else:
        print("[Discord 推送失败，请检查 Webhook URL]")

    # 终端也显示结果
    print("\n" + "=" * 50)
    print("[Minimax AI 总结结果:]")
    print("=" * 50)
    print(summary)


if __name__ == "__main__":
    main()
