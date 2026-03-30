#!/usr/bin/env python3
"""
GitHub AI 趋势日报 - 本地自动化版本
功能：抓取数据 → Minimax AI 总结 → Discord 推送
"""

import requests
import json
import os
from datetime import datetime

# ==================== 配置区 ====================
# 请填写以下配置

# Minimax API Key
MINIMAX_API_KEY = "sk-cp-QTTayYt9MQ4eWs_2Ij4YwnJCcwTfwNDo6x8Gh_l4kdRzYO24s0Es3zmXeREOZu1sF4Fhoa2oVT8bsMS9Sg-78aRz2YE4RwuGyLkKPXv6VyxbYIGLxjdZFTk"

# Discord Webhook URL
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1488096438721183908/DU0H3LzSSI1t1U_t-xFq_ojs8X6WL3FIe6-5tMe5A8H8d0vW_PzNESGD95bUgGWMTi1n"

# ==================== 配置结束 ====================


def fetch_github_trending():
    """抓取 GitHub Trending Python 项目"""
    url = "https://api.github.com/search/repositories"
    params = {
        "q": "language:python created:>=" + datetime.now().strftime("%Y-%m-%d"),
        "sort": "stars",
        "order": "desc",
        "per_page": 5
    }
    headers = {"Accept": "application/vnd.github.v3+json"}

    print("[1/3] 正在抓取 GitHub Trending...")
    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    projects = response.json().get("items", [])

    # 保存到 JSON
    result = {
        "fetch_time": datetime.now().isoformat(),
        "count": len(projects),
        "projects": []
    }
    for p in projects:
        result["projects"].append({
            "name": p["full_name"],
            "description": p["description"] or "无描述",
            "stars": p["stargazers_count"],
            "url": p["html_url"]
        })

    with open("trending.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"    成功抓取 {len(projects)} 个项目")
    return result["projects"]


def summarize_with_minimax(projects):
    """调用 Minimax API 总结项目"""
    print("[2/3] 正在调用 Minimax AI 分析...")

    project_list = "\n".join([
        f"{i+1}. **{p['name']}** - {p['description']} (star: {p['stars']})"
        for i, p in enumerate(projects)
    ])

    prompt = f"""你是专业的 AI 技术分析师。请分析以下今日 GitHub Trending Python/AI 项目：

{project_list}

请对每个项目用中文总结：
1. 核心亮点是什么？
2. 对普通 AI 玩家有什么具体帮助？

格式要求：
- 简洁有力，突出重点
- 用普通人能理解的语言
- 每个项目 2-3 句话"""

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

    if response.status_code == 200:
        result = response.json()
        summary = result["choices"][0]["message"]["content"]
        print("    AI 总结完成")
        return summary
    else:
        print(f"    Minimax API 错误: {response.status_code}")
        print(f"    {response.text}")
        return None


def send_to_discord(summary):
    """推送 Discord"""
    print("[3/3] 正在推送 Discord...")

    today = datetime.now().strftime("%Y-%m-%d")
    message = f"**GitHub AI 趋势日报** | {today}\n\n{summary}\n\n---\n数据来源: GitHub Trending"

    payload = {"content": message, "username": "GitHub AI 趋势捕手"}
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

    if response.status_code == 204:
        print("    Discord 推送成功")
        return True
    else:
        print(f"    Discord 推送失败: {response.status_code}")
        return False


def main():
    print("=" * 50)
    print("[GitHub AI 趋势日报] 启动")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 50)

    try:
        # 1. 抓取数据
        projects = fetch_github_trending()

        if not projects:
            print("未获取到项目，退出")
            return

        # 2. AI 总结
        summary = summarize_with_minimax(projects)

        if summary:
            # 3. 推送 Discord
            send_to_discord(summary)
        else:
            print("AI 总结失败，跳过推送")

        print("\n[任务完成]")

    except Exception as e:
        print(f"\n[错误] {e}")


if __name__ == "__main__":
    main()
