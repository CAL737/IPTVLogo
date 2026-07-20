import re
import os

# ================= 配置区 =================
EPG_LIST_FILE = os.path.join(os.path.dirname(__file__), "epg_channel_list.txt")
M3U_INPUT_FILE = os.path.join(os.path.dirname(__file__), "iptv.m3u")
M3U_OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "iptv_fixed.m3u")

# 🔑 强制补全表：专门解决诊断出的9个"无ID"及名称不匹配问题
# 格式: { "M3U中的tvg-name": "正确的EPG_ID" }
FORCE_FIX = {
    "华丽翡翠台": "565",        # → 黃金翡翠台 (ID:565)
    "功夫台": "373",            # → 中国功夫 (ID:373)
    "娱乐新闻台": "娛樂新聞台",  # → EPG中为繁体名 (ID:娛樂新聞台)
    "ViuTV": "Viu 頻道",       # → EPG标准名 (ID:Viu 頻道)
    "TVBJ1": "TVBJ",           # → TVBJ (ID:TVBJ)
    "4K60PHLG-HEVC-EAC3测试": "測試頻道", # → 測試頻道 (ID:測試頻道)
    
    # 以下频道在EPG中确实不存在，设为None表示跳过不处理
    "ViuTVsix": None,
    "TVBDrama": None,
    "TVB1": None,
}

# 🔄 简繁/别名自动映射（仅当tvg-id缺失时触发）
NAME_ALIAS = {
    "娱乐新闻台": "娛樂新聞台",
    "无线新闻": "無綫新聞台",
    "凤凰中文": "鳳凰衛視中文台",
    "凤凰资讯": "鳳凰衛視資訊台",
    "凤凰香港": "鳳凰香港台",
}
# ==========================================

def load_epg_mapping():
    """解析固定宽度表格，返回 {display-name: epg_id}"""
    mapping = {}
    if not os.path.exists(EPG_LIST_FILE):
        print(f" 未找到: {EPG_LIST_FILE}")
        return mapping
        
    with open(EPG_LIST_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith('EPG ID') or stripped.startswith('-'):
                continue
            try:
                epg_id = line[:25].strip()
                channel_name = line[25:].strip()
                if epg_id and channel_name:
                    mapping[channel_name] = epg_id
            except IndexError:
                pass
                
    print(f"✅ 已加载 {len(mapping)} 个EPG频道映射")
    return mapping

def fix_m3u_ids(epg_map):
    fixed_count = 0
    id_added_count = 0
    unmatched = []

    with open(M3U_INPUT_FILE, 'r', encoding='utf-8') as fin, \
         open(M3U_OUTPUT_FILE, 'w', encoding='utf-8') as fout:
        
        for line_num, line in enumerate(fin, 1):
            if not line.startswith('#EXTINF'):
                fout.write(line)
                continue
                
            name_match = re.search(r'tvg-name="([^"]+)"', line)
            id_match = re.search(r'tvg-id="([^"]+)"', line)
            
            current_name = name_match.group(1) if name_match else ""
            current_id = id_match.group(1) if id_match else ""
            
            new_line = line
            needs_update = False
            
            # 1. 优先检查强制补全表
            if current_name in FORCE_FIX:
                target = FORCE_FIX[current_name]
                if target is not None:
                    # 如果target是ID则直接用；如果是名称则查map转ID
                    std_id = target if target in epg_map.values() else epg_map.get(target, target)
                    
                    if not current_id or current_id != std_id:
                        if not current_id:
                            insert_pos = line.find('tvg-name=')
                            if insert_pos > 0:
                                prefix = line[:insert_pos]
                                suffix = line[insert_pos:]
                                new_line = f'{prefix}tvg-id="{std_id}" {suffix}'
                                id_added_count += 1
                        else:
                            new_line = line.replace(f'tvg-id="{current_id}"', f'tvg-id="{std_id}"')
                        needs_update = True
                # target is None 时跳过
            
            # 2. 正常精确匹配
            elif current_name and current_name in epg_map:
                std_id = epg_map[current_name]
                if not current_id or current_id != std_id:
                    if not current_id:
                        insert_pos = line.find('tvg-name=')
                        if insert_pos > 0:
                            prefix = line[:insert_pos]
                            suffix = line[insert_pos:]
                            new_line = f'{prefix}tvg-id="{std_id}" {suffix}'
                            id_added_count += 1
                    else:
                        new_line = line.replace(f'tvg-id="{current_id}"', f'tvg-id="{std_id}"')
                    needs_update = True
                    
            # 3. 简繁别名兜底（仅当ID缺失时）
            elif current_name and not current_id and current_name in NAME_ALIAS:
                trad_name = NAME_ALIAS[current_name]
                if trad_name in epg_map:
                    std_id = epg_map[trad_name]
                    insert_pos = line.find('tvg-name=')
                    if insert_pos > 0:
                        prefix = line[:insert_pos]
                        suffix = line[insert_pos:]
                        new_line = f'{prefix}tvg-id="{std_id}" tvg-name="{trad_name}" {suffix.split(" ", 1)[-1]}'
                        id_added_count += 1
                        needs_update = True
            
            # 4. 记录未匹配项
            elif current_name and current_name not in epg_map and current_name not in FORCE_FIX:
                unmatched.append(current_name)
                
            if needs_update:
                fixed_count += 1
                
            fout.write(new_line)
            
    print(f"\n{'='*60}")
    print("🎉 修正完成！")
    print(f"   ✅ 成功修正/补全: {fixed_count} 个频道")
    print(f"   ➕ 新增 tvg-id: {id_added_count} 个")
    print(f"   💾 输出文件: {M3U_OUTPUT_FILE}")
    
    if unmatched:
        print(f"\n⚠️ 以下{len(unmatched)}个频道在EPG中未找到匹配:")
        for name in sorted(set(unmatched))[:20]:
            print(f"   - {name}")
        if len(unmatched) > 20:
            print(f"   ...还有 {len(unmatched)-20} 个")

if __name__ == '__main__':
    print("🚀 正在执行精准ID匹配修正...\n")
    mapping = load_epg_mapping()
    if mapping:
        fix_m3u_ids(mapping)
    else:
        print("❌ 未加载到任何映射，流程终止")