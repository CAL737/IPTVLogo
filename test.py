import urllib.request
import re
import sys

# 👇 在这里填入您的 M3U 链接或本地文件路径
M3U_SOURCE = "iptv.m3u"

# 检测超时时间（秒），建议设置较短以加快筛选速度
TIMEOUT = 5

def check_stream(url):
    """尝试请求流地址，返回是否可用"""
    try:
        req = urllib.request.Request(url, method='HEAD')
        req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Televizo/1.0)')
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status == 200
    except Exception:
        # HEAD 失败时降级为 GET 请求（部分服务器不支持 HEAD）
        try:
            req = urllib.request.Request(url, method='GET')
            req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Televizo/1.0)')
            req.add_header('Range', 'bytes=0-1023')  # 只请求前1KB，避免下载整个流
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return resp.status in (200, 206)
        except Exception:
            return False

def parse_and_check(source):
    """解析 M3U 并逐个检测"""
    # 读取内容（支持 URL 和本地文件）
    if source.startswith(('http://', 'https://')):
        print(f"⏳ 正在获取直播源: {source}")
        with urllib.request.urlopen(source, timeout=15) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
    else:
        print(f"📂 正在读取本地文件: {source}")
        with open(source, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

    lines = content.strip().splitlines()
    available_channels = []
    total = sum(1 for l in lines if l.strip().startswith('#EXTINF:'))
    checked = 0

    print(f"✅ 共发现 {total} 个频道，开始检测...\n")
    print("=" * 40)

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            # 提取逗号后的频道名
            match = re.search(r',(.+)$', line)
            channel_name = match.group(1).strip() if match else "未知频道"

            # 获取下一行的流地址
            stream_url = lines[i + 1].strip() if i + 1 < len(lines) else ""
            i += 2

            if not stream_url or stream_url.startswith('#'):
                continue

            checked += 1
            is_ok = check_stream(stream_url)

            if is_ok:
                print(f"  ✅ {channel_name}")
                available_channels.append(channel_name)
            # 不可用的频道静默跳过，保持终端整洁

            # 进度提示（每检测20个打印一次）
            if checked % 20 == 0:
                print(f"  --- 已检测 {checked}/{total} ---")
        else:
            i += 1

    print("=" * 40)
    print(f"\n🎉 检测完成！共 {checked} 个频道，其中 {len(available_channels)} 个可用：\n")
    for name in available_channels:
        print(name)

if __name__ == '__main__':
    # 支持命令行参数传入源地址
    source = sys.argv[1] if len(sys.argv) > 1 else M3U_SOURCE
    parse_and_check(source)