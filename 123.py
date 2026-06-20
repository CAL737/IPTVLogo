import os
import re

def extract_and_group_gd_channels(input_file, output_file, target_group="广东广播电视台"):
    # ... [前面的关键字列表和文件读取逻辑保持不变] ...
    
    # ================= 配置你的双 EPG 链接 =================
    EPG_URL_1 = "http://epg.51zmt.top:8000/e2.xml.gz"       # 替换为你的第一个 EPG 链接
    EPG_URL_2 = "http://epg.51zmt.top:8000/e.xml"               # 替换为你的第二个 EPG 链接
    # 将两个链接用逗号拼接
    EPG_COMBINED = f'{EPG_URL_1},{EPG_URL_2}'
    # =======================================================

    # ... [中间的频道提取逻辑保持不变] ...

    # 写入新文件
    with open(output_file, 'w', encoding='utf-8') as f:
        # 🌟 核心修改：写入带有双 EPG 链接的标准 M3U 头部
        f.write(f'#EXTM3U x-tvg-url="{EPG_COMBINED}"\n')
        
        # 写入提取出的频道内容（跳过原文件的第一行，因为我们已经重写了）
        for line in extracted_lines[1:]: 
            f.write(line + '\n')
            
    print(f"✅ 提取完成！已自动嵌入 2 个 EPG 链接。")
    print(f"💾 已保存至: {output_file}")