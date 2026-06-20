import os
import re

# ================= 配置区 =================
# Gitee 图床基础路径
GITEE_BASE_URL = "https://gitee.com/wyj484/iptvlogo/raw/main/img/"

# 双 EPG 链接
EPG_URL_1 = "http://epg.51zmt.top:8000/e2.xml.gz"
EPG_URL_2 = "http://epg.51zmt.top:8000/e.xml"
EPG_COMBINED = f'{EPG_URL_1},{EPG_URL_2}'

# ================= 中英文频道名映射表 =================
# 根据你实际的图片库和IPTV源建立的精准映射
CHANNEL_NAME_MAP = {
    # 凤凰卫视
    "凤凰中文": "Phoenix TV Chinese Channel",
    "凤凰资讯": "Phoenix TV Information Channel",
    "凤凰香港": "Phoenix TV Hong Kong",
    
    # 香港TVB
    "翡翠台": "Jade",
    "华丽翡翠台": "AstroJade",
    "明珠台": "Pearl",
    "TVB Plus": "TVB Plus",
    "无线新闻台": "TVB News",
    "无线新闻": "TVB News",
    
    # ViuTV
    "ViuTV": "viutv",
    "ViuTVsix": "ViuTVsix",
    
    # HOY TV (原奇妙电视/开电视)
    "HOY TV": "HOY 77",
    "HOY 77": "HOY 77",
    "HOY 76": "HOY 76",
    "HOY 78": "HOY 78",
    "开电视": "HOY 77",
    
    # 广东台
    "广东卫视": "Guangdong",
    "广东卫视4K": "Guangdong 4K UHD",
    "广东4K": "Guangdong 4K UHD",
    "广东珠江": "Guangdong Zhujiang",
    "珠江卫视": "Guangdong Zhujiang",
    "广东新闻": "Guangdong News",
    "广东体育": "Guangdong Sport",
    "广东公共": "Guangdong People",
    "广东少儿": "Guangdong Children",
    "嘉佳卡通": "Qia Qia Cartoon",
    "广东民生": "Guangdong House",
    "广东经济科教": "Guangdong Economic Science and Education",
    "广东影视": "Guangdong Movie",
    "大湾区卫视": "Greater Bay Area",
    "广东大湾区": "Greater Bay Area",
    "岭南戏曲": "Lingnan Opera",
    "广东国际": "Guangdong International",
    "广东移动": "Guangdong Mobile",
    "现代教育": "Guangdong Modern Education",
}

# 分组关键字
GD_KEYWORDS = ["广东卫视", "广东珠江", "广东新闻", "广东体育", "广东公共", "广东少儿", "嘉佳卡通", "广东民生", "广东经济科教", "广东影视", "广东4K", "大湾区卫视", "岭南戏曲", "广东国际", "广东移动", "现代教育"]
HK_KEYWORDS = ["翡翠", "明珠", "J2", "TVB Plus", "无线新闻", "ViuTV", "HOY", "开电视", "凤凰中文", "凤凰资讯", "凤凰香港"]
# ===========================================

def get_english_name(m3u_channel_name):
    """
    根据 M3U 中的频道名，通过映射表获取英文文件名
    支持精确匹配和模糊匹配
    """
    # 1. 精确匹配
    if m3u_channel_name in CHANNEL_NAME_MAP:
        return CHANNEL_NAME_MAP[m3u_channel_name]
    
    # 2. 模糊匹配 (M3U频道名包含映射表中的关键字)
    for cn_key, en_value in CHANNEL_NAME_MAP.items():
        if cn_key in m3u_channel_name:
            return en_value
            
    return None

def set_group_and_logo(line, group_name):
    """
    设置分组，并根据映射表直接拼接 Logo 链接
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
        
    # 3. 获取英文名并拼接 URL
    english_name = get_english_name(channel_name)
    
    if english_name:
        # 尝试多种图片后缀
        for ext in ['.png', '.jpg']:
            logo_url = f"{GITEE_BASE_URL}{english_name}{ext}"
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

    print(f"🚀 开始整理 IPTV 源...")
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
    not_found_channels = []  
    
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
            
    print(f"\n✅ 整理完成！(极速模式)")
    print(f"📺 共提取 {total_count} 个频道")
    print(f"   ├─ 广东广播电视台: {gd_count} 个")
    print(f"   └─ 香港免费地面波: {hk_count} 个")
    print(f"🖼️ 成功匹配并替换了 {logo_count} 个频道的台徽")
    
    if not_found_channels:
        print(f"\n⚠️ 以下 {len(not_found_channels)} 个频道未找到对应台徽:")
        for ch in not_found_channels:
            print(f"   - {ch}")
        print(f"\n💡 建议: 请在 CHANNEL_NAME_MAP 中补充映射关系")
    
    print(f"\n💾 已保存至: {output_file}")
    print(f"\n📝 提示: 生成的 M3U 文件已嵌入双 EPG 链接，台徽指向你的 Gitee 图床")

if __name__ == "__main__":
    INPUT_FILE = "iptv.m3u"               
    OUTPUT_FILE = "my_iptv_organized.m3u" 
    
    organize_iptv_gitee(INPUT_FILE, OUTPUT_FILE)