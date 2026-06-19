import re
import os

# --- 配置区域 ---
INPUT_FILE = "iptv.m3u"  # 你的原始 m3u 文件名
OUTPUT_FILE = "updated_iptv_gitee.m3u"        # 输出的新 m3u 文件名
LOGO_BASE_URL = "https://gitee.com/wyj484/iptvlogo/raw/main/img/"

# 从 televionlogo.md 提取的频道名到图片文件名的映射
# 注意：这里使用的是 televionlogo.md 中的具体文件名
CHANNEL_LOGO_MAP = {
    "凤凰中文": "Phoenix TV Chinese Channel.png",
    "凤凰资讯": "Phoenix TV Information Channel.png",
    "凤凰香港": "Phoenix TV Hong Kong.png",
    "凤凰卫视": "Phoenix TV Chinese Channel.png",  # 映射到凤凰中文
    "翡翠台": "Jade.png",
    "明珠台": "Pearl.png",
    "TVB Plus": "TVB Plus.png",
    "无线新闻": "TVB News.png",
    "ViuTV": "viutv.png",
    "ViuTVsix": "ViuTVsix.png",
    "HOY TV": "HOY 77.png",  # 根据 televionlogo.md 使用 HOY 77
    "华丽翡翠台": "Jade.png",
}

def update_m3u_logos(input_path, output_path):
    if not os.path.exists(input_path):
        print(f"错误: 找不到文件 {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    updated_count = 0
    skipped_count = 0

    for line in lines:
        if line.startswith('#EXTINF'):
            # 提取 tvg-name
            name_match = re.search(r'tvg-name="(.*?)"', line)
            if name_match:
                channel_name = name_match.group(1)
                
                # 在映射表中查找
                if channel_name in CHANNEL_LOGO_MAP:
                    logo_filename = CHANNEL_LOGO_MAP[channel_name]
                    new_logo_url = f"{LOGO_BASE_URL}{logo_filename}"
                    
                    # 替换 tvg-logo 部分
                    # 使用正则替换整个 tvg-logo="..." 属性
                    new_line = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{new_logo_url}"', line)
                    new_lines.append(new_line)
                    updated_count += 1
                else:
                    # 如果没找到匹配，保留原样（或者你可以选择删除 tvg-logo）
                    new_lines.append(line)
                    skipped_count += 1
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"处理完成！")
    print(f"成功更新: {updated_count} 个频道")
    print(f"未匹配/跳过: {skipped_count} 个频道")
    print(f"输出文件: {output_path}")

if __name__ == "__main__":
    update_m3u_logos(INPUT_FILE, OUTPUT_FILE)