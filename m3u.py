import os
import re

def set_group_title(line, group_name):
    """
    统一设置或修改 M3U 频道的分组名称 (group-title)
    """
    if 'group-title=' in line:
        # 1. 如果原文件已有分组，直接替换原有的值
        return re.sub(r'group-title="[^"]*"', f'group-title="{group_name}"', line)
    else:
        # 2. 如果原文件没有分组，在频道名称前的逗号处插入分组属性
        if ',' in line:
            return re.sub(r',', f' group-title="{group_name}",', line, count=1)
        else:
            # 3. 极端不规范格式：直接追加在行尾
            return f'{line} group-title="{group_name}"'

def extract_and_group_gd_channels(input_file, output_file, target_group="广东广播电视台"):
    # 广东台旗下频道关键字库
    keywords = [
        "广东卫视", "广东珠江", "广东新闻", "广东体育", "广东公共", 
        "广东少儿", "嘉佳卡通", "广东民生", "广东经济", "广东影视", 
        "广东4K", "广东超高清", "大湾区卫视", "南方卫视", "南方经济", 
        "南方综艺", "南方影视", "岭南戏曲", "现代教育", "广东国际", 
        "广东高尔夫", "广东移动", "GDTV", "TVS" 
    ]

    if not os.path.exists(input_file):
        print(f"❌ 错误: 找不到文件 '{input_file}'。")
        return

    # 读取文件并自动识别编码
    lines = []
    for encoding in ['utf-8', 'gbk', 'utf-8-sig']:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                lines = f.readlines()
            break
        except UnicodeDecodeError:
            continue
            
    if not lines:
        print("❌ 文件为空或无法读取。")
        return

    extracted_lines = []
    keep_next = False
    
    # 确保标准 M3U 头部
    if lines[0].strip().startswith('#EXTM3U'):
        extracted_lines.append(lines[0].strip())
        start_idx = 1
    else:
        extracted_lines.append('#EXTM3U')
        start_idx = 0

    # 逐行解析、匹配并修改分组
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
            
        if line.startswith('#EXTINF:'):
            line_upper = line.upper()
            # 检查是否匹配广东台频道
            if any(kw.upper() in line_upper for kw in keywords):
                # 🌟 核心修改：统一设置分组名称为 target_group
                modified_line = set_group_title(line, target_group)
                extracted_lines.append(modified_line)
                keep_next = True
            else:
                keep_next = False
        elif keep_next:
            if not line.startswith('#'):
                extracted_lines.append(line)
                keep_next = False 
            else:
                extracted_lines.append(line) 

    channel_count = sum(1 for line in extracted_lines if line.startswith('#EXTINF:'))

    if channel_count == 0:
        print("⚠️ 未找到任何广东台相关的频道。")
        return

    # 写入新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in extracted_lines:
            f.write(line + '\n')
            
    print(f"✅ 提取并分组完成！")
    print(f"📺 共提取 {channel_count} 个频道，已统一归入分组: 【{target_group}】")
    print(f"💾 已保存至: {output_file}")

if __name__ == "__main__":
    # ================= 配置区 =================
    INPUT_FILE = "guangdong_all.m3u"               
    OUTPUT_FILE = "guangdong_single_group.m3u" 
    GROUP_NAME = "广东广播电视台"          # 这里可以自定义你想要的分组名称
    # ==========================================
    
    extract_and_group_gd_channels(INPUT_FILE, OUTPUT_FILE, GROUP_NAME)