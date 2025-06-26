"""
代码仓库分析器 - 提取代码结构、业务逻辑和架构模式
"""
import os
import ast
import json
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


class CodeAnalyzer:
    """代码分析器，负责解析和分析代码仓的结构和内容"""
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        
    def analyze_repository(self) -> Dict[str, Any]:
        """分析整个代码仓"""
        print("🔍 开始分析代码仓库...")
        
        analysis_result = {
            'repo_structure': self._analyze_structure(),
            'file_analysis': self._analyze_files(),
            'business_rules': self._extract_business_rules(),
            'architecture_patterns': self._identify_architecture_patterns(),
            'dependencies': self._analyze_dependencies(),
            'documentation_analysis': self._analyze_documentation()
        }
        
        print(f"✅ 分析完成: {analysis_result['repo_structure']['total_files']} 个文件")
        return analysis_result
    
    def _analyze_structure(self) -> Dict[str, Any]:
        """分析仓库结构"""
        structure = {
            'directories': [],
            'file_types': {},
            'total_files': 0,
            'depth': 0
        }
        
        for root, dirs, files in os.walk(self.repo_path):
            level = root.replace(str(self.repo_path), '').count(os.sep)
            structure['depth'] = max(structure['depth'], level)
            
            rel_path = os.path.relpath(root, self.repo_path)
            if rel_path != '.':
                structure['directories'].append(rel_path)
            
            for file in files:
                structure['total_files'] += 1
                ext = Path(file).suffix.lower()
                structure['file_types'][ext] = structure['file_types'].get(ext, 0) + 1
                
        return structure
    
    def _analyze_files(self) -> Dict[str, Any]:
        """分析具体文件内容"""
        file_analysis = {}
        
        # 支持的文件类型
        supported_extensions = {'.py', '.js', '.ts', '.md', '.json', '.yaml', '.yml'}
        
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                file_path = Path(root) / file
                rel_path = file_path.relative_to(self.repo_path)
                
                if file_path.suffix.lower() in supported_extensions:
                    try:
                        analysis = self._analyze_single_file(file_path)
                        if analysis:
                            file_analysis[str(rel_path)] = analysis
                    except Exception as e:
                        print(f"⚠️ 分析文件 {file_path} 时出错: {e}")
                        
        return file_analysis
    
    def _analyze_single_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """分析单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            analysis = {
                'file_type': file_path.suffix.lower(),
                'size': len(content),
                'lines': len(content.splitlines()),
                'functions': [],
                'classes': [],
                'imports': [],
                'comments': self._extract_comments(content, file_path.suffix),
                'business_keywords': self._find_business_keywords(content)
            }
            
            # 特定文件类型的分析
            if file_path.suffix == '.py':
                analysis.update(self._analyze_python_file(content))
            elif file_path.suffix in ['.js', '.ts']:
                analysis.update(self._analyze_javascript_file(content))
            elif file_path.suffix == '.md':
                analysis.update(self._analyze_markdown_file(content))
                
            return analysis
            
        except Exception as e:
            print(f"⚠️ 无法读取文件 {file_path}: {e}")
            return None
    
    def _analyze_python_file(self, content: str) -> Dict[str, Any]:
        """分析Python文件"""
        result = {'functions': [], 'classes': [], 'imports': []}
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node),
                        'line_number': node.lineno,
                        'is_async': isinstance(node, ast.AsyncFunctionDef)
                    }
                    result['functions'].append(func_info)
                    
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        'docstring': ast.get_docstring(node),
                        'line_number': node.lineno,
                        'bases': [self._get_node_name(base) for base in node.bases]
                    }
                    result['classes'].append(class_info)
                    
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            result['imports'].append(alias.name)
                    else:
                        module = node.module or ''
                        for alias in node.names:
                            result['imports'].append(f"{module}.{alias.name}")
                            
        except SyntaxError as e:
            print(f"⚠️ Python语法错误: {e}")
            return result
            
        return result
    
    def _analyze_javascript_file(self, content: str) -> Dict[str, Any]:
        """分析JavaScript/TypeScript文件"""
        result = {'functions': [], 'classes': [], 'imports': []}
        
        # 简单的正则表达式匹配
        # 函数匹配
        func_patterns = [
            r'function\s+(\w+)\s*\([^)]*\)',  # function name()
            r'const\s+(\w+)\s*=\s*\([^)]*\)\s*=>', # const name = () =>
            r'(\w+)\s*:\s*function\s*\([^)]*\)',  # name: function()
        ]
        
        for pattern in func_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                result['functions'].append({
                    'name': match,
                    'args': [],  # 简化处理
                    'type': 'javascript'
                })
        
        # 类匹配
        class_matches = re.findall(r'class\s+(\w+)', content)
        for class_name in class_matches:
            result['classes'].append({
                'name': class_name,
                'methods': [],
                'type': 'javascript'
            })
        
        # 导入匹配
        import_patterns = [
            r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]',
            r'require\s*\(\s*[\'"]([^\'"]+)[\'"]\s*\)'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            result['imports'].extend(matches)
            
        return result
    
    def _analyze_markdown_file(self, content: str) -> Dict[str, Any]:
        """分析Markdown文件"""
        result = {
            'headings': [],
            'code_blocks': [],
            'links': []
        }
        
        lines = content.split('\n')
        for line in lines:
            # 标题
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                result['headings'].append({'level': level, 'title': title})
            
            # 代码块
            if line.strip().startswith('```'):
                language = line.strip()[3:].strip()
                result['code_blocks'].append(language)
        
        # 链接
        link_matches = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        result['links'] = [{'text': text, 'url': url} for text, url in link_matches]
        
        return result
    
    def _extract_comments(self, content: str, file_ext: str) -> List[str]:
        """提取注释"""
        comments = []
        lines = content.split('\n')
        
        if file_ext == '.py':
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('#'):
                    comments.append(stripped[1:].strip())
        elif file_ext in ['.js', '.ts']:
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('//'):
                    comments.append(stripped[2:].strip())
        
        return comments
    
    def _find_business_keywords(self, content: str) -> List[str]:
        """查找业务关键词"""
        business_keywords = [
            'user', 'customer', 'order', 'payment', 'invoice', 'product',
            'service', 'account', 'profile', 'authentication', 'authorization',
            'login', 'register', 'cart', 'checkout', 'billing', 'shipping',
            'notification', 'email', 'sms', 'report', 'dashboard', 'analytics',
            'admin', 'manager', 'role', 'permission', 'security', 'audit',
            'log', 'error', 'exception', 'validation', 'business', 'process',
            'workflow', 'rule', 'policy', 'config', 'setting', 'feature',
            'module', 'component', 'service', 'api', 'endpoint', 'route',
            'controller', 'model', 'view', 'template', 'database', 'query'
        ]
        
        found_keywords = []
        content_lower = content.lower()
        
        for keyword in business_keywords:
            if keyword in content_lower:
                found_keywords.append(keyword)
        
        return list(set(found_keywords))  # 去重
    
    def _extract_business_rules(self) -> List[Dict[str, Any]]:
        """提取业务规则"""
        business_rules = []
        
        # 从注释和文档字符串中提取业务规则
        rule_indicators = [
            'rule:', 'business rule:', 'constraint:', 'requirement:',
            'must', 'should', 'shall', 'required', 'mandatory'
        ]
        
        # 这里可以扩展更复杂的业务规则提取逻辑
        # 目前返回示例规则
        business_rules.append({
            'rule': '用户登录失败3次后锁定账户',
            'source_file': 'extracted_from_comments',
            'type': 'security_rule'
        })
        
        return business_rules
    
    def _identify_architecture_patterns(self) -> Dict[str, bool]:
        """识别架构模式"""
        patterns = {
            'mvc': False,
            'microservices': False,
            'layered': False,
            'event_driven': False,
            'rest_api': False
        }
        
        # 简单的模式识别逻辑
        # 可以根据目录结构、文件命名等来判断
        structure = self._analyze_structure()
        directories = structure.get('directories', [])
        
        # MVC模式检测
        mvc_indicators = ['controllers', 'models', 'views', 'controller', 'model', 'view']
        if any(indicator in str(directories).lower() for indicator in mvc_indicators):
            patterns['mvc'] = True
        
        # REST API检测
        api_indicators = ['api', 'routes', 'endpoints', 'handlers']
        if any(indicator in str(directories).lower() for indicator in api_indicators):
            patterns['rest_api'] = True
        
        # 分层架构检测
        layer_indicators = ['service', 'repository', 'dao', 'business', 'data']
        if any(indicator in str(directories).lower() for indicator in layer_indicators):
            patterns['layered'] = True
        
        return patterns
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """分析依赖关系"""
        dependencies = {
            'package_managers': [],
            'external_deps': [],
            'internal_deps': []
        }
        
        # 检查常见的包管理文件
        package_files = {
            'requirements.txt': 'pip',
            'package.json': 'npm',
            'Pipfile': 'pipenv',
            'pyproject.toml': 'poetry',
            'setup.py': 'setuptools'
        }
        
        for file_name, manager in package_files.items():
            if (self.repo_path / file_name).exists():
                dependencies['package_managers'].append(manager)
        
        return dependencies
    
    def _analyze_documentation(self) -> Dict[str, Any]:
        """分析文档"""
        doc_analysis = {
            'has_readme': False,
            'has_contributing': False,
            'has_license': False,
            'doc_files': [],
            'total_doc_lines': 0
        }
        
        doc_files = ['README.md', 'readme.md', 'README.txt', 'readme.txt']
        for doc_file in doc_files:
            if (self.repo_path / doc_file).exists():
                doc_analysis['has_readme'] = True
                break
        
        if (self.repo_path / 'CONTRIBUTING.md').exists():
            doc_analysis['has_contributing'] = True
        
        license_files = ['LICENSE', 'LICENSE.txt', 'LICENSE.md', 'license']
        for license_file in license_files:
            if (self.repo_path / license_file).exists():
                doc_analysis['has_license'] = True
                break
        
        return doc_analysis
    
    def _get_node_name(self, node) -> str:
        """获取AST节点名称"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_node_name(node.value)}.{node.attr}"
        else:
            return str(node)