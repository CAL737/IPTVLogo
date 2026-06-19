import re
import os

# --- 配置区域 ---
INPUT_M3U = "iptv.m3u"                      # 你的原始 m3u 文件名 (已更名)
OUTPUT_M3U = "iptv_with_logo_epg.m3u"       # 输出的新 m3u 文件名
LOGO_MD = "televionlogo.md"                 # 你的 logo 映射文件
EPG_URL = "http://epg.51zmt.top:8000/e2.xml.gz" # 你的 EPG 地址
LOGO_BASE_URL = "https://gitee.com/wyj484/onlyhktvlogo/raw/main/img/"

def parse_logo_mapping(md_file):
    """
    从 televionlogo.md 中解析 频道名 -> 图片文件名 的映射
    """
    mapping = {}
    if not os.path.exists(md_file):
        print(f"警告: 找不到 {md_file}，请确保文件在同一目录下。")
        return mapping

    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 正则表达式匹配表格中的 img src
    # 匹配格式: | 频道名 | <img src=".../filename.png" ... > |
    # 注意处理 src 属性中可能存在的空格
    pattern = r'\|\s*(.*?)\s*\|\s*<img\s+src\s*=\s*"[^"]*/([^/"]+\.png)"[^>]*>'
    
    matches = re.findall(pattern, content)
    for channel_name, filename in matches:
        clean_name = channel_name.strip()
        if clean_name and filename:
            # 清理文件名中可能存在的多余空格（虽然 URL 中通常保留，但为了匹配准确）
            mapping[clean_name] = filename
            
    print(f"✅ 从 {md_file} 成功加载 {len(mapping)} 个频道 Logo 映射。")
    return mapping

def update_m3u(input_file, output_file, logo_map, epg_url):
    """
    处理 M3U 文件：替换 Logo 并添加 EPG
    """
    if not os.path.exists(input_file):
        print(f"❌ 错误: 找不到输入文件 {input_file}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    updated_count = 0
    skipped_count = 0
    
    # 标记是否已处理头部
    header_processed = False

    for line in lines:
        stripped_line = line.strip()
        
        # 1. 处理头部 #EXTM3U
        if stripped_line.startswith('#EXTM3U') and not header_processed:
            # 构建新的头部，包含 EPG 信息
            # url-tvg 和 x-tvg-url 是为了兼容不同播放器
            new_header = f'#EXTM3U url-tvg="{epg_url}" x-tvg-url="{epg_url}"\n'
            new_lines.append(new_header)
            header_processed = True
            continue
        
        # 如果第一行不是 #EXTM3U 或者已经处理过，则按普通行处理
        if stripped_line.startswith('#EXTINF'):
            # 2. 处理频道条目
            # 提取 tvg-name
            name_match = re.search(r'tvg-name="(.*?)"', stripped_line)
            if name_match:
                channel_name = name_match.group(1)
                
                # 尝试匹配 Logo
                if channel_name in logo_map:
                    filename = logo_map[channel_name]
                    # 构建完整的 Gitee Raw 链接
                    new_logo_url = f"{LOGO_BASE_URL}{filename}"
                    
                    # 使用正则替换 tvg-logo 属性
                    # 如果原行没有 tvg-logo，这个正则会失败，所以先检查
                    if 'tvg-logo=' in stripped_line:
                        new_line = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{new_logo_url}"', stripped_line)
                    else:
                        # 如果没有 tvg-logo 属性，则插入它
                        # 通常在 tvg-name 之后插入
                        new_line = re.sub(r'(tvg-name="[^"]*")', rf'\1 tvg-logo="{new_logo_url}"', stripped_line)
                    
                    new_lines.append(new_line + '\n')
                    updated_count += 1
                else:
                    # 未匹配到 Logo，保持原样
                    new_lines.append(stripped_line + '\n')
                    skipped_count += 1
            else:
                # 没有 tvg-name 的行，保持原样
                new_lines.append(stripped_line + '\n')
        else:
            # 其他行（如播放地址 URL），直接保留
            new_lines.append(line)

    # 写入新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("-" * 40)
    print(f"🎉 处理完成！")
    print(f"📂 输出文件: {output_file}")
    print(f"🖼️ 成功更新 Logo: {updated_count} 个")
    print(f"⚠️ 未匹配 Logo (保持原样): {skipped_count} 个")
    print(f"📺 已封装 EPG: {epg_url}")
    print("-" * 40)

if __name__ == "__main__":
    print("🚀 开始处理 IPTV 源...")
    # 1. 获取 Logo 映射
    logo_mapping = parse_logo_mapping(LOGO_MD)
    
    # 2. 执行更新
    if logo_mapping:
        update_m3u(INPUT_M3U, OUTPUT_M3U, logo_mapping, EPG_URL)
    else:
        print("由于未能加载 Logo 映射，程序退出。请检查 televionlogo.md 是否存在且格式正确。")