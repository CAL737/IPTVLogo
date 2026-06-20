import os
import re
import requests
import time

# ================= 配置区 =================
# Gitee 图床基础路径
GITEE_BASE_URL = "https://gitee.com/wyj484/iptvlogo/raw/main/img/"

# 双 EPG 链接
EPG_URL_1 = "http://epg.51zmt.top:8000/e2.xml.gz"
EPG_URL_2 = "http://epg.51zmt.top:8000/e.xml"
EPG_COMBINED = f'{EPG_URL_1},{EPG_URL_2}'

# ================= 中英文频道名映射表 =================
# 格式: "M3U中的中文频道名": "Gitee图片文件名(不含扩展名)"
# 你可以继续添加更多映射
CHANNEL_NAME_MAP = {
    # 广东台
    "广东卫视": "Guangdong Satellite TV",
    "广东珠江": "Guangdong Pearl River",
    "广东新闻": "Guangdong News",
    "广东体育": "Guangdong Sports",
    "广东公共": "Guangdong Public",
    "广东少儿": "Guangdong Children",
    "嘉佳卡通": "Qia Qia Cartoon",  # 你的音译
    "广东民生": "Guangdong Minsheng",
    "广东经济": "Guangdong Economy",
    "广东影视": "Guangdong Film",
    "广东4K": "Guangdong 4K",
    "大湾区卫视": "Greater Bay Area TV",
    "南方卫视": "Nanfang Satellite TV",
    "南方经济": "Nanfang Economy",
    "南方综艺": "Nanfang Variety",
    "南方影视": "Nanfang Film",
    "岭南戏曲": "Lingnan Opera",
    "现代教育": "Modern Education",
    
    # 香港台
    "翡翠台": "Jade",
    "明珠台": "Pearl",
    "J2": "J2",
    "TVB Plus": "TVB Plus",
    "无线新闻台": "TVB News",
    "无线财经台": "TVB Finance",
    "ViuTV": "ViuTV",
    "ViuTVsix": "ViuTVsix",
    "HOY TV": "HOY 77",
    "HOY资讯台": "HOY 78",
    "HKIBC": "HOY 76",
    "港台电视31": "RTHK TV 31",
    "港台电视32": "RTHK TV 32",
    "港台电视33": "RTHK TV 33",
    "港台电视34": "RTHK TV 34",
    "港台电视35": "RTHK TV 35",
}

# 分组关键字
GD_KEYWORDS = ["广东卫视", "广东珠江", "广东新闻", "广东体育", "广东公共", "广东少儿", "嘉佳卡通", "广东民生", "广东经济", "广东影视", "广东4K", "大湾区卫视", "南方卫视", "南方经济", "南方影视", "GDTV", "TVS"]
HK_KEYWORDS = ["翡翠", "明珠", "J2", "TVB Plus", "无线新闻", "无线财经", "ViuTV", "ViuTVsix", "HOY", "开电视", "港台电视", "RTHK", "TVB"]
# ===========================================

def get_gitee_logo_url(channel_name):
    """
    根据频道名，通过映射表找到英文文件名，然后构造并验证 Gitee 图片链接
    """
    # 1. 先在映射表中查找
    english_name = CHANNEL_NAME_MAP.get(channel_name)
    
    # 2. 如果映射表没有，尝试使用原名（以防万一）
    if not english_name:
        english_name = channel_name
    
    # 常见的图片后缀
    extensions = ['.png', '.jpg', '.ico', '.webp']
    
    # 尝试不同的文件名变体
    candidates = [english_name]
    
    # 添加去除空格的版本
    if " " in english_name:
        candidates.append(english_name.replace(" ", ""))
        candidates.append(english_name.replace(" ", "_"))
        candidates.append(english_name.replace(" ", "-"))
    
    # 遍历所有可能的文件名组合
    for name in candidates:
        for ext in extensions:
            file_url = f"{GITEE_BASE_URL}{name}{ext}"
            
            try:
                # 发送 HEAD 请求检查图片是否存在
                response = requests.head(file_url, timeout=2)
                if response.status_code == 200:
                    return file_url
            except:
                continue
                
    return None

def set_group_and_logo(line, group_name):
    """
    设置分组，并尝试替换 Logo
    """
    # 1. 设置分组
    if 'group-title=' in line:
        line = re.sub(r'group-title="[^"]*"', f'group-title="{group_name}"', line)
    else:
        line = re.sub(r',', f' group-title="{group_name}",', line, count=1)
        
    # 2. 提取频道名称 (逗号后面的部分)
    if ',' in line:
        channel_name = line.split(',')[-1].strip()
    else:
        return line, False
        
    # 3. 尝试获取 Gitee Logo
    logo_url = get_gitee_logo_url(channel_name)
    
    if logo_url:
        # 替换或插入 tvg-logo
        if 'tvg-logo=' in line:
            line = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{logo_url}"', line)
        else:
            line = re.sub(r',', f' tvg-logo="{logo_url}",', line, count=1)
        return line, True
    else:
        return line, False

def organize_iptv_gitee(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"❌ 错误: 找不到文件 '{input_file}'。")
        return

    print(f"🚀 开始整理，正在连接 Gitee 图床验证图片...")
    print(f"📋 已加载 {len(CHANNEL_NAME_MAP)} 个中英文频道映射关系")

    lines = []
    for encoding in ['utf-8', 'gbk', 'utf-8-sig']:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                lines = f.readlines()
            break
        except UnicodeDecodeError:
            continue

    extracted_lines = []
    keep_next = False
    logo_count = 0
    gd_count = 0
    hk_count = 0
    not_found_channels = []  # 记录未找到图片的频道
    
    # 逐行解析
    for i in range(1, len(lines)): 
        line = lines[i].strip()
        if not line: continue
            
        if line.startswith('#EXTINF:'):
            line_upper = line.upper()
            
            is_gd = any(kw.upper() in line_upper for kw in GD_KEYWORDS)
            is_hk = any(kw.upper() in line_upper for kw in HK_KEYWORDS)
            
            new_line = line
            replaced = False
            
            if is_gd:
                new_line, replaced = set_group_and_logo(line, "广东广播电视台")
                if replaced: 
                    logo_count += 1
                else:
                    # 记录未找到图片的频道
                    if ',' in line:
                        ch_name = line.split(',')[-1].strip()
                        if ch_name not in not_found_channels:
                            not_found_channels.append(ch_name)
                gd_count += 1
                extracted_lines.append(new_line)
                keep_next = True
                
            elif is_hk:
                new_line, replaced = set_group_and_logo(line, "香港免费地面波")
                if replaced: 
                    logo_count += 1
                else:
                    if ',' in line:
                        ch_name = line.split(',')[-1].strip()
                        if ch_name not in not_found_channels:
                            not_found_channels.append(ch_name)
                hk_count += 1
                extracted_lines.append(new_line)
                keep_next = True
            else:
                keep_next = False 
                
        elif keep_next:
            if not line.startswith('#'):
                extracted_lines.append(line)
                keep_next = False 
            else:
                extracted_lines.append(line) 

    total_count = gd_count + hk_count

    if total_count == 0:
        print("⚠️ 未找到任何匹配的频道。")
        return

    # 写入新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f'#EXTM3U x-tvg-url="{EPG_COMBINED}"\n')
        for line in extracted_lines:
            f.write(line + '\n')
            
    print(f"\n✅ 整理完成！")
    print(f"📺 共提取 {total_count} 个频道")
    print(f"   ├─ 广东广播电视台: {gd_count} 个")
    print(f"   └─ 香港免费地面波: {hk_count} 个")
    print(f"🖼️ 成功匹配并替换了 {logo_count} 个频道的台徽")
    
    if not_found_channels:
        print(f"\n⚠️ 以下 {len(not_found_channels)} 个频道未在 Gitee 找到对应图片:")
        for ch in not_found_channels[:10]:  # 只显示前10个
            print(f"   - {ch}")
        if len(not_found_channels) > 10:
            print(f"   ... 还有 {len(not_found_channels) - 10} 个")
        print(f"\n💡 建议: 请在 CHANNEL_NAME_MAP 中添加这些频道的映射关系")
    
    print(f"\n💾 已保存至: {output_file}")

if __name__ == "__main__":
    INPUT_FILE = "ipv4.m3u"               
    OUTPUT_FILE = "my_iptv_gitee_logo.m3u" 
    
    organize_iptv_gitee(INPUT_FILE, OUTPUT_FILE)