#!/usr/bin/env python3
"""
GitHub Trending 数据抓取脚本
功能：抓取今日最火的 5 个 Python 项目，保存到 trending.json
"""

import requests
import json
from datetime import datetime


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

    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json().get("items", [])


def save_to_json(projects, filename="trending.json"):
    """保存项目信息到 JSON 文件"""
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
            "forks": p["forks_count"],
            "language": p["language"],
            "url": p["html_url"],
            "author": p["owner"]["login"]
        })

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"已保存 {len(projects)} 个项目到 {filename}")


def main():
    print("=" * 50)
    print("[GitHub Trending 数据抓取]")
    print("=" * 50)

    print("\n[正在抓取 GitHub Trending Python 项目...]")
    projects = fetch_github_trending()

    if not projects:
        print("[未能获取到项目数据]")
        return

    print(f"[成功获取 {len(projects)} 个项目]")

    save_to_json(projects)

    print("\n[项目列表:]")
    for i, p in enumerate(projects, 1):
        print(f"  {i}. {p['full_name']} (star: {p['stargazers_count']})")


if __name__ == "__main__":
    main()
