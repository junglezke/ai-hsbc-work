#!/usr/bin/env python3
"""
智能默认值计算器
为现有系统提供基于项目规模的智能默认QA数量建议
"""
import json
from pathlib import Path
from typing import Dict, Tuple

def calculate_smart_defaults(repo_path: str) -> Tuple[int, str]:
    """
    基于代码仓库快速分析计算智能默认QA数量
    
    Returns:
        (recommended_qa_count, justification)
    """
    repo_path = Path(repo_path)
    
    # 快速统计项目规模
    total_files = 0
    python_files = 0
    estimated_functions = 0
    
    for file_path in repo_path.rglob("*"):
        if file_path.is_file() and not any(skip in str(file_path) for skip in ['.git', '__pycache__', '.pyc', 'node_modules']):
            total_files += 1
            
            if file_path.suffix == '.py':
                python_files += 1
                # 粗略估算函数数量（每个Python文件平均5-10个函数）
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # 统计def和class关键字
                        estimated_functions += content.count('\ndef ') + content.count('\nclass ') + content.count('def ') + content.count('class ')
                except:
                    estimated_functions += 7  # 默认估算
    
    # 基于项目规模计算建议
    if total_files <= 10 and estimated_functions <= 30:
        # 微小项目
        recommended_qa = max(estimated_functions, 20)
        project_type = "微小项目"
        
    elif total_files <= 50 and estimated_functions <= 150:
        # 小型项目
        recommended_qa = max(int(estimated_functions * 0.8), 30)
        project_type = "小型项目"
        
    elif total_files <= 150 and estimated_functions <= 500:
        # 中型项目
        recommended_qa = max(int(estimated_functions * 0.5), 80)
        project_type = "中型项目"
        
    else:
        # 大型项目
        recommended_qa = max(int(estimated_functions * 0.3), 150)
        project_type = "大型项目"
    
    # 生成说明
    justification = f"""
🔍 项目分析:
• 文件总数: {total_files}
• Python文件: {python_files}  
• 估算函数/类: {estimated_functions}
• 项目类型: {project_type}

💡 建议QA数量: {recommended_qa}
• 可实现约60-80%的有效覆盖率
• 平衡质量与生成效率
• 建议使用: --num-qa-pairs {recommended_qa}
    """.strip()
    
    return recommended_qa, justification

def main():
    """命令行工具：快速获取项目的智能默认值"""
    import sys
    
    if len(sys.argv) != 2:
        print("用法: python smart_defaults.py <repo_path>")
        print("示例: python smart_defaults.py ../flask-main")
        return
    
    repo_path = sys.argv[1]
    
    if not Path(repo_path).exists():
        print(f"❌ 路径不存在: {repo_path}")
        return
    
    recommended_qa, justification = calculate_smart_defaults(repo_path)
    
    print("=" * 50)
    print("🧠 智能默认值建议")
    print("=" * 50)
    print(justification)
    print("=" * 50)
    print(f"🚀 推荐命令:")
    print(f"python main.py --repo-path {repo_path} --num-qa-pairs {recommended_qa}")

if __name__ == "__main__":
    main()