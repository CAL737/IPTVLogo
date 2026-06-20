import os

def extract_gd_channels(input_file, output_file):
    """
    从M3U文件中提取广东广播电视台旗下所有频道
    """
    # 1. 定义广东台旗下频道的关键字（包含中文名、4K频道、以及常见的英文/编号别名）
    keywords = [
        # 核心中文频道名
        "广东卫视", "广东珠江", "广东新闻", "广东体育", "广东公共", 
        "广东少儿", "嘉佳卡通", "广东民生", "广东经济", "广东影视", 
        "广东4K", "广东超高清", "大湾区卫视", "南方卫视", "南方经济", 
        "南方综艺", "南方影视", "岭南戏曲", "现代教育", "广东国际", 
        "广东高尔夫", "广东移动",
        # 英文及编号别名 (用于匹配 GDTV1, TVS2, GDTV-4K 等命名格式的源)
        "GDTV", "TVS" 
    ]

    # 2. 检查文件是否存在
    if not os.path.exists(input_file):
        print(f"❌ 错误: 找不到文件 '{input_file}'，请确保文件与脚本在同一目录下。")
        return

    # 3. 尝试读取文件，自动兼容不同的文本编码
    lines = []
    for encoding in ['utf-8', 'gbk', 'utf-8-sig']:
        try:
            with open(input_file, 'r', encoding=encoding) as f:
                lines = f.readlines()
            break
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"❌ 读取文件时发生错误: {e}")
            return
            
    if not lines:
        print("❌ 文件为空或无法读取。")
        return

    extracted_lines = []
    keep_next = False
    
    # 4. 确保输出文件有标准的 M3U 头部
    if lines[0].strip().startswith('#EXTM3U'):
        extracted_lines.append(lines[0].strip())
        start_idx = 1
    else:
        extracted_lines.append('#EXTM3U')
        start_idx = 0

    # 5. 逐行解析并提取目标频道
    for i in range(start_idx, len(lines)):
        line = lines[i].strip()
        if not line:
            continue
            
        # 如果是频道信息标签行 (#EXTINF)，检查是否包含关键字
        if line.startswith('#EXTINF:'):
            # 将行内容转为大写，以便同时匹配中英文和英文别名
            line_upper = line.upper()
            if any(kw.upper() in line_upper for kw in keywords):
                extracted_lines.append(line)
                keep_next = True
            else:
                keep_next = False
        elif keep_next:
            # 如果是 URL 行，或者是夹在中间的附加标签 (如 #EXTVLCOPT)
            if not line.startswith('#'):
                extracted_lines.append(line)
                keep_next = False  # URL行提取完毕后，重置状态
            else:
                extracted_lines.append(line) # 保留中间的附加标签

    # 6. 统计提取结果
    channel_count = sum(1 for line in extracted_lines if line.startswith('#EXTINF:'))

    if channel_count == 0:
        print("⚠️ 未找到任何广东台相关的频道。")
        return

    # 7. 写入新的 M3U 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in extracted_lines:
            f.write(line + '\n')
            
    print(f"✅ 提取完成！")
    print(f"📺 共提取到 {channel_count} 个广东广播电视台旗下的频道源。")
    print(f"💾 已保存至: {output_file}")
    print("\n💡 提示: 如果提取结果中混入了非省台的频道（如某些带'广东'字样的市县台），")
    print("   请在代码的 keywords 列表中移除 'GDTV' 或 'TVS' 等宽泛关键字，仅保留具体中文频道名。")

if __name__ == "__main__":
    # ================= 配置区 =================
    INPUT_FILE = "ipv4.m3u"               # 原始 M3U 文件名
    OUTPUT_FILE = "guangdong_all.m3u"     # 提取后保存的文件名
    # ==========================================
    
    extract_gd_channels(INPUT_FILE, OUTPUT_FILE)