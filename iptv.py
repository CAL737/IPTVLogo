#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 suxuang/myIPTV 提取"港澳代理"组中的指定频道
使用 fanmingming/live 台徽，并自动验证链接有效性（支持TVB前缀适配）
"""

import requests
import re
from pathlib import Path


# 台标基础URL
LOGO_BASE_URL = "https://raw.githubusercontent.com/fanmingming/live/main/tv"

# 频道名 -> 可能的文件名列表（按优先级排列）
# 脚本会依次尝试，直到找到第一个可访问的文件
LOGO_CANDIDATES = {
    '翡翠台':       ['TVB翡翠台.png', 'tvb-jade.png', '翡翠台.png'],
    '明珠台':       ['TVB明珠台.png', 'tvb-pearl.png', '明珠台.png'],
    'TVB Plus':     ['TVB Plus.png', 'tvb-plus.png', 'TVBPlus.png'],
    '无线新闻':     ['TVB无线新闻.png', 'tvb-news.png', '无线新闻台.png', '无线新闻.png'],
    'ViuTV':        ['ViuTV.png', 'viutv.png'],
    'HOY TV':       ['HOY TV.png', 'hoy-tv.png', 'HOYTV.png', '开电视.png'],
    '凤凰中文':     ['凤凰中文.png', 'phoenix-chinese.png', '凤凰卫视中文台.png'],
    '凤凰资讯':     ['凤凰资讯.png', 'phoenix-info.png', '凤凰卫视资讯台.png'],
    '凤凰香港':     ['凤凰香港.png', 'phoenix-hk.png', '凤凰卫视香港台.png'],
    '凤凰卫视':     ['凤凰卫视.png', 'phoenix-satellite.png'],
}


def download_m3u(url: str) -> str:
    """下载M3U文件内容"""
    print(f"正在下载 M3U 文件: {url}")
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    response.encoding = 'utf-8'
    print("✓ M3U 文件下载成功")
    return response.text


def parse_m3u(content: str) -> list[dict]:
    """解析M3U文件，返回频道列表"""
    channels = []
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            channel_info = {}
            logo_match = re.search(r'tvg-logo="([^"]*)"', line)
            if logo_match:
                channel_info['logo'] = logo_match.group(1)
            group_match = re.search(r'group-title="([^"]*)"', line)
            if group_match:
                channel_info['group'] = group_match.group(1)
            name_match = re.search(r'tvg-name="([^"]*)"', line)
            if name_match:
                channel_info['tvg_name'] = name_match.group(1)
            comma_index = line.rfind(',')
            if comma_index != -1:
                channel_info['name'] = line[comma_index + 1:].strip()
            if i + 1 < len(lines):
                url_line = lines[i + 1].strip()
                if url_line and not url_line.startswith('#'):
                    channel_info['url'] = url_line
            channels.append(channel_info)
            i += 2
        else:
            i += 1
    print(f"✓ 共解析到 {len(channels)} 个频道")
    return channels


def filter_channels(channels: list[dict]) -> list[dict]:
    """筛选目标频道"""
    target_keywords = {
        '翡翠台', '明珠台', 'TVB Plus', '无线新闻',
        'ViuTV', 'HOY TV',
        '凤凰中文', '凤凰资讯', '凤凰香港', '凤凰卫视'
    }
    filtered = []
    for channel in channels:
        if channel.get('group') != '港澳代理':
            continue
        channel_name = channel.get('name', '')
        tvg_name = channel.get('tvg_name', '')
        if any(kw in channel_name or kw in tvg_name for kw in target_keywords):
            filtered.append(channel)
    print(f"✓ 筛选出 {len(filtered)} 个目标频道")
    return filtered


def check_logo_exists(url: str) -> bool:
    """使用 HEAD 请求检查台标文件是否存在"""
    try:
        resp = requests.head(url, timeout=10, allow_redirects=True)
        return resp.status_code == 200
    except Exception:
        return False


def resolve_logo(channel_name: str, tvg_name: str) -> str:
    """
    按候选列表依次验证台标URL，返回第一个可访问的链接
    如果全部失败则返回空字符串
    """
    candidates = []
    for key, file_list in LOGO_CANDIDATES.items():
        if key in channel_name or key in tvg_name:
            candidates = file_list
            break

    if not candidates:
        print(f"  ⚠ [{channel_name}] 无候选台标文件名")
        return ""

    for filename in candidates:
        url = f"{LOGO_BASE_URL}/{filename}"
        if check_logo_exists(url):
            print(f"  ✓ [{channel_name}] -> {filename}")
            return url
        # 未命中时静默跳过，避免刷屏

    print(f"  ✗ [{channel_name}] 所有候选台标均不可用: {candidates}")
    return ""


def generate_m3u(channels: list[dict], output_file: str):
    """生成新的M3U文件"""
    m3u_content = "#EXTM3U\n"
    success_count = 0

    for channel in channels:
        channel_name = channel.get('name', '')
        tvg_name = channel.get('tvg_name', '')

        new_logo = resolve_logo(channel_name, tvg_name)
        final_logo = new_logo if new_logo else channel.get('logo', '')
        if new_logo:
            success_count += 1

        extinf = '#EXTINF:-1'
        if tvg_name:
            extinf += f' tvg-name="{tvg_name}"'
        if final_logo:
            extinf += f' tvg-logo="{final_logo}"'
        if 'group' in channel:
            extinf += f' group-title="{channel["group"]}"'
        extinf += f',{channel_name}'

        m3u_content += extinf + '\n'
        m3u_content += channel.get('url', '') + '\n'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(m3u_content)

    print(f"\n✓ 已生成 M3U 文件: {output_file}")
    print(f"✓ 共 {len(channels)} 个频道，其中 {success_count} 个台标验证通过")


def main():
    m3u_url = "https://gh-proxy.com/raw.githubusercontent.com/suxuang/myIPTV/main/ipv4.m3u"
    output_file = "filtered_iptv_fanmingming.m3u"

    print("=" * 60)
    print("IPTV 频道提取工具 (fanmingming/live 台标 + 在线验证)")
    print("=" * 60)

    try:
        m3u_content = download_m3u(m3u_url)
        channels = parse_m3u(m3u_content)
        filtered_channels = filter_channels(channels)

        if not filtered_channels:
            print("⚠ 未找到匹配的频道，请检查筛选条件")
            return

        print("\n正在逐一验证台标链接...")
        print("-" * 60)
        generate_m3u(filtered_channels, output_file)
        print("-" * 60)
        print("\n完成！可将 filtered_iptv_fanmingming.m3u 导入播放器")

    except requests.exceptions.RequestException as e:
        print(f"✗ 网络请求失败: {e}")
    except Exception as e:
        print(f"✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()