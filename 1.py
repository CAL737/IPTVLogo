import os
import re
import requests
import time

# ================= 配置区 =================
# 你的 Gitee 图床基础路径 (Raw 地址)
# 格式: https://gitee.com/用户名/项目名/raw/分支名/文件夹路径/
GITEE_BASE_URL = "https://gitee.com/wyj484/iptvlogo/raw/main/img/"

# 双 EPG 链接
EPG_URL_1 = "http://epg.51zmt.top:8000/e2.xml.gz"
EPG_URL_2 = "http://epg.51zmt.top:8000/e.xml"
EPG_COMBINED = f'{EPG_URL_1},{EPG_URL_2}'

# 分组关键字
GD_KEYWORDS = ["广东卫视", "广东珠江", "广东新闻", "广东体育", "广东公共", "广东少儿", "嘉佳卡通", "广东民生", "广东经济", "广东影视", "广东4K", "大湾区卫视", "南方卫视", "南方经济", "南方影视", "GDTV", "TVS"]
HK_KEYWORDS = ["翡翠", "明珠", "J2", "TVB Plus", "无线新闻", "无线财经", "ViuTV", "ViuTVsix", "HOY", "开电视", "港台电视", "RTHK", "TVB"]
# ===========================================

def get_gitee_logo_url(channel_name):
    """
    根据频道名，尝试构造并验证 Gitee 图片链接
    """
    # 1. 清理频道名，去除多余字符，提高匹配率
    # 例如："CCTV-1 高清" -> "CCTV1" 或 "CCTV-1"
    clean_name = channel_name.strip()
    
    # 常见的图片后缀
    extensions = ['.png', '.jpg', '.ico', '.webp']
    
    # 尝试匹配的逻辑：
    # 1. 直接匹配：频道名.png
    # 2. 去除空格匹配
    # 3. 去除"高清"、"HD"等后缀匹配
    
    candidates = [clean_name]
    if " " in clean_name:
        candidates.append(clean_name.replace(" ", ""))
    if "高清" in clean_name:
        candidates.append(clean_name.replace("高清", ""))
    if "HD" in clean_name.upper():
        candidates.append(re.sub(r'HD', '', clean_name, flags=re.IGNORECASE))
        
    # 遍历所有可能的文件名组合
    for name in candidates:
        for ext in extensions:
            # 构造完整 URL
            # 注意：URL中的中文需要 urlencode，但 requests.head 通常能处理，或者我们可以手动处理
            # 这里为了简单，直接拼接，如果报错再优化
            file_url = f"{GITEE_BASE_URL}{name}{ext}"
            
            try:
                # 发送 HEAD 请求检查图片是否存在 (超时设为 2 秒，防止脚本太慢)
                response = requests.head(file_url, timeout=2)
                if response.status_code == 200:
                    return file_url
            except:
                continue
                
    return None

def set_group_and_logo(line, group_name, img_dir_check=False):
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
        return line # 无法提取名称，跳过 Logo 替换
        
    # 3. 尝试获取 Gitee Logo
    logo_url = get_gitee_logo_url(channel_name)
    
    if logo_url:
        # 替换或插入 tvg-logo
        if 'tvg-logo=' in line:
            line = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{logo_url}"', line)
        else:
            line = re.sub(r',', f' tvg-logo="{logo_url}",', line, count=1)
        return line, True # 返回 True 表示替换成功
    else:
        # 如果没找到本地图床的图，可以选择保留原样，或者清空。
        # 这里选择保留原样（如果有的话），或者不做处理。
        return line, False

def organize_iptv_gitee(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"❌ 错误: 找不到文件 '{input_file}'。")
        return

    print(f"🚀 开始整理，正在连接 Gitee 图床验证图片...")

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
                if replaced: logo_count += 1
                gd_count += 1
                extracted_lines.append(new_line)
                keep_next = True
                
            elif is_hk:
                new_line, replaced = set_group_and_logo(line, "香港免费地面波")
                # 香港台也尝试换一下，如果有的话
                if replaced: logo_count += 1
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
            
    print(f"✅ 整理完成！")
    print(f"📺 共提取 {total_count} 个频道")
    print(f"   ├─ 广东广播电视台: {gd_count} 个")
    print(f"   └─ 香港免费地面波: {hk_count} 个")
    print(f"🖼️ 成功匹配并替换了 {logo_count} 个频道的台徽 (来源: Gitee)")
    print(f"💾 已保存至: {output_file}")
    print(f"\n💡 提示: 生成的 M3U 文件中的台徽链接指向你的 Gitee 仓库，请确保网络通畅。")

if __name__ == "__main__":
    INPUT_FILE = "ipv4.m3u"               
    OUTPUT_FILE = "my_iptv_gitee_logo.m3u" 
    
    organize_iptv_gitee(INPUT_FILE, OUTPUT_FILE)