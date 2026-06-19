import os
import re
from deep_translator import GoogleTranslator

def translate_text(text):
    """使用 Google 翻译将中文翻译成英文"""
    try:
        # 初始化翻译器：源语言自动检测，目标语言为英语
        translator = GoogleTranslator(source='auto', target='en')
        result = translator.translate(text)
        return result
    except Exception as e:
        print(f"翻译出错: {e}")
        return text

def clean_filename(name):
    """清理文件名中的非法字符，确保跨平台兼容"""
    # 替换 Windows/Linux/Mac 不允许的字符
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(invalid_chars, '_', name)
    # 去除首尾空格
    return cleaned.strip()

def translate_folder_contents(root_path, dry_run=True):
    """
    递归遍历文件夹并翻译文件名
    :param root_path: 根目录路径
    :param dry_run: 如果为 True，只打印预览不实际修改；False 则执行修改
    """
    if not os.path.exists(root_path):
        print("错误：路径不存在")
        return

    for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
        # 1. 先处理文件
        for filename in filenames:
            old_path = os.path.join(dirpath, filename)
            
            # 获取不带扩展名的部分和扩展名
            name, ext = os.path.splitext(filename)
            
            # 如果名字里包含中文字符才进行翻译
            if re.search(r'[\u4e00-\u9fff]', name):
                translated_name = translate_text(name)
                new_filename = f"{clean_filename(translated_name)}{ext}"
                new_path = os.path.join(dirpath, new_filename)
                
                if old_path != new_path:
                    if dry_run:
                        print(f"[预览] 文件: '{filename}' -> '{new_filename}'")
                    else:
                        try:
                            os.rename(old_path, new_path)
                            print(f"[成功] 文件: '{filename}' -> '{new_filename}'")
                        except Exception as e:
                            print(f"[失败] 文件: '{filename}', 原因: {e}")

        # 2. 再处理文件夹 (topdown=False 确保先处理完子文件夹里的内容)
        folder_name = os.path.basename(dirpath)
        parent_dir = os.path.dirname(dirpath)
        
        # 跳过根目录本身，且只翻译含中文的文件夹
        if dirpath != root_path and re.search(r'[\u4e00-\u9fff]', folder_name):
            translated_folder = translate_text(folder_name)
            new_folder_name = clean_filename(translated_folder)
            new_dirpath = os.path.join(parent_dir, new_folder_name)
            
            if dirpath != new_dirpath:
                if dry_run:
                    print(f"[预览] 文件夹: '{folder_name}' -> '{new_folder_name}'")
                else:
                    try:
                        os.rename(dirpath, new_dirpath)
                        print(f"[成功] 文件夹: '{folder_name}' -> '{new_folder_name}'")
                    except Exception as e:
                        print(f"[失败] 文件夹: '{folder_name}', 原因: {e}")

if __name__ == "__main__":
    # ⚠️ 请在这里修改你要处理的文件夹路径
    target_folder = r"C:\Users\jcfk1\Desktop\tvlogo1" 
    
    print("--- 开始扫描 ---")
    # 第一步：先设置为 dry_run=True 看看效果，确认没问题后再改为 False
    translate_folder_contents(target_folder, dry_run=False)
    
    # 确认无误后，取消下面这行的注释并再次运行
    #  translate_folder_contents(target_folder, dry_run=False)