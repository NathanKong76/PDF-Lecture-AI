with open(r'C:\Users\Kong\project\lecturer\app\services\pdf_processor.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 查找导入语句的位置
for i, line in enumerate(lines):
    if "from .logger import get_logger" in line:
        print(f"Found import at line {i+1}: {repr(line)}")
        # 查看下一行
        if i+1 < len(lines):
            print(f"Next line {i+2}: {repr(lines[i+1])}")
        # 查看下下行
        if i+2 < len(lines):
            print(f"Next line {i+3}: {repr(lines[i+2])}")
        break