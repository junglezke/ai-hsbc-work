"""
Claude集成的设计方案生成器 - 基于代码仓架构生成智能设计建议
"""
import json
import random
from typing import Dict, List, Any, Optional
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class DesignGenerator:
    """Claude驱动的设计方案生成器"""
    
    def __init__(self, claude_api_key: str):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("需要安装anthropic包: pip install anthropic")
        
        self.client = Anthropic(api_key=claude_api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.design_patterns = self._load_design_patterns()
        
    def _load_design_patterns(self) -> Dict[str, Dict[str, Any]]:
        """加载设计模式模板"""
        return {
            'mvc': {
                'name': 'Model-View-Controller',
                'description': '将应用逻辑分离为三个互联的组件',
                'benefits': ['关注点分离', '可维护性', '可测试性'],
                'use_cases': ['Web应用', '桌面应用', 'REST API']
            },
            'microservices': {
                'name': '微服务架构',
                'description': '将应用构建为松散耦合的服务集合',
                'benefits': ['可扩展性', '技术多样性', '独立部署'],
                'use_cases': ['大规模应用', '云原生应用', '高流量系统']
            },
            'layered': {
                'name': '分层架构',
                'description': '将代码组织为具有特定职责的水平层',
                'benefits': ['清晰分离', '模块化', '易于测试'],
                'use_cases': ['企业应用', '传统Web应用', '桌面软件']
            }
        }
    
    def generate_design_proposals(self, code_analysis: Dict[str, Any], 
                                requirements: List[str], num_proposals: int = 10) -> List[Dict[str, Any]]:
        """生成设计方案"""
        print(f"使用Claude生成 {num_proposals} 个设计方案...")
        
        proposals = []
        
        # 分析当前架构
        current_architecture = self._analyze_current_architecture(code_analysis)
        
        # 生成不同类型的设计方案
        generators = [
            self._generate_enhancement_proposals,
            self._generate_refactoring_proposals,
            self._generate_feature_proposals,
            self._generate_architecture_migration_proposals
        ]
        
        proposals_per_type = max(num_proposals // len(generators), 1)
        
        for generator in generators:
            try:
                new_proposals = generator(code_analysis, current_architecture, requirements, proposals_per_type)
                proposals.extend(new_proposals)
                if len(proposals) >= num_proposals:
                    break
            except Exception as e:
                print(f" 生成器 {generator.__name__} 出错: {e}")
        
        return proposals[:num_proposals]
    
    def _analyze_current_architecture(self, code_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """分析当前架构状态"""
        return {
            'detected_patterns': code_analysis.get('architecture_patterns', {}),
            'structure': code_analysis.get('repo_structure', {}),
            'technologies': self._detect_technologies(code_analysis),
            'complexity': self._assess_complexity(code_analysis),
            'strengths': self._identify_strengths(code_analysis),
            'weaknesses': self._identify_weaknesses(code_analysis)
        }
    
    def _detect_technologies(self, code_analysis: Dict[str, Any]) -> List[str]:
        """检测使用的技术栈"""
        technologies = []
        file_types = code_analysis.get('repo_structure', {}).get('file_types', {})
        
        if '.py' in file_types:
            technologies.append('Python')
        if '.js' in file_types or '.ts' in file_types:
            technologies.append('JavaScript/TypeScript')
        if '.java' in file_types:
            technologies.append('Java')
        if '.md' in file_types:
            technologies.append('Markdown Documentation')
        
        return technologies
    
    def _assess_complexity(self, code_analysis: Dict[str, Any]) -> str:
        """评估代码复杂度"""
        total_files = code_analysis.get('repo_structure', {}).get('total_files', 0)
        depth = code_analysis.get('repo_structure', {}).get('depth', 0)
        
        if total_files < 10 and depth < 3:
            return 'Low'
        elif total_files < 50 and depth < 5:
            return 'Medium'
        else:
            return 'High'
    
    def _identify_strengths(self, code_analysis: Dict[str, Any]) -> List[str]:
        """识别架构优势"""
        strengths = []
        doc_analysis = code_analysis.get('documentation_analysis', {})
        
        if doc_analysis.get('has_readme'):
            strengths.append('有完整的README文档')
        if doc_analysis.get('has_license'):
            strengths.append('有明确的许可证')
        
        patterns = code_analysis.get('architecture_patterns', {})
        if patterns.get('mvc'):
            strengths.append('使用MVC模式组织代码')
        if patterns.get('rest_api'):
            strengths.append('实现REST API设计')
        
        return strengths
    
    def _identify_weaknesses(self, code_analysis: Dict[str, Any]) -> List[str]:
        """识别架构劣势"""
        weaknesses = []
        doc_analysis = code_analysis.get('documentation_analysis', {})
        
        if not doc_analysis.get('has_readme'):
            weaknesses.append('缺少README文档')
        if not doc_analysis.get('has_contributing'):
            weaknesses.append('缺少贡献指南')
        
        structure = code_analysis.get('repo_structure', {})
        if structure.get('depth', 0) > 6:
            weaknesses.append('目录结构过深，可能表示复杂度过高')
        
        return weaknesses
    
    def _generate_enhancement_proposals(self, code_analysis: Dict[str, Any], 
                                      current_arch: Dict[str, Any], 
                                      requirements: List[str], num_proposals: int) -> List[Dict[str, Any]]:
        """生成增强建议"""
        proposals = []
        
        enhancement_areas = [
            '性能优化',
            '安全增强',
            '测试覆盖',
            '文档完善',
            '代码质量'
        ]
        
        for area in enhancement_areas[:num_proposals]:
            try:
                proposal = self._generate_claude_enhancement_proposal(area, current_arch, code_analysis)
                if proposal:
                    proposals.append(proposal)
            except Exception as e:
                print(f" 生成增强方案失败: {e}")
                continue
        
        return proposals
    
    def _generate_claude_enhancement_proposal(self, area: str, current_arch: Dict[str, Any], 
                                            code_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用Claude生成增强方案"""
        claude_prompt = f"""作为资深软件架构师和技术专家，请为以下代码仓库生成一个"{area}"的详细架构设计方案。这是为模型训练数据生成的，需要高质量的推理过程。

## 代码仓库分析:
- 架构复杂度: {current_arch.get('complexity', '未知')}
- 技术栈: {', '.join(current_arch.get('technologies', []))}
- 项目优势: {', '.join(current_arch.get('strengths', []))}
- 改进领域: {', '.join(current_arch.get('weaknesses', []))}
- 总文件数: {code_analysis.get('repo_structure', {}).get('total_files', 0)}
- 目录结构: {code_analysis.get('repo_structure', {}).get('directories', [])}
- 检测到的架构模式: {[k for k, v in code_analysis.get('architecture_patterns', {}).items() if v]}

## 业务功能分析:
- 核心类: {[cls['name'] for file_analysis in code_analysis.get('file_analysis', {}).values() for cls in file_analysis.get('classes', [])]}
- 主要功能: {[func['name'] for file_analysis in code_analysis.get('file_analysis', {}).values() for func in file_analysis.get('functions', [])]}

请生成一个全面、详细的{area}设计方案，要求:

1. **方案必须具体可实施**：提供详细的技术实现路径
2. **包含完整的推理trace**：解释为什么选择这种方案，分析过程，权衡考虑
3. **提供详细的实施步骤**：至少6-8个具体步骤，包含技术细节
4. **考虑业务影响**：分析对现有业务功能的影响
5. **包含技术选型理由**：解释技术选择的原因
6. **提供验收标准**：如何验证方案是否成功实施

JSON格式（请确保内容详尽）:
{{
    "title": "具体的方案标题（包含技术关键词）",
    "description": "详细描述方案的背景、目标、核心思路和预期效果（至少200字）",
    "technical_approach": "技术实现方案的详细说明（至少150字）",
    "implementation_steps": [
        "步骤1：具体的技术实施内容",
        "步骤2：详细的实现细节",
        "步骤3：配置和集成说明",
        "步骤4：测试和验证方案",
        "步骤5：部署和监控设置",
        "步骤6：文档和培训",
        "步骤7：性能优化和调优",
        "步骤8：维护和支持计划"
    ],
    "benefits": [
        "具体的技术收益",
        "业务价值的量化描述",
        "性能提升的具体指标",
        "可维护性改进",
        "扩展性增强"
    ],
    "challenges_and_solutions": [
        "挑战1及其解决方案",
        "挑战2及其解决方案",
        "挑战3及其解决方案"
    ],
    "acceptance_criteria": [
        "验收标准1：具体的可测量指标",
        "验收标准2：功能完整性检查",
        "验收标准3：性能基准测试"
    ],
    "estimated_effort": "Medium",
    "timeline": "预计实施时间和里程碑",
    "reasoning_trace": "系统性的分析推理过程，必须包含以下深度分析框架：\n\n**1. 现状深度分析**：详细评估当前系统的技术现状、性能瓶颈、架构限制\n\n**2. 问题根因识别**：深入分析问题的根本原因，而非表面现象\n\n**3. 方案对比评估**：比较多种可行方案，分析各自的优劣势\n\n**4. 技术选型推理**：详细解释为什么选择特定技术栈，包含技术成熟度、生态系统、团队技能等考量\n\n**5. 风险评估与缓解**：识别实施风险并提出具体的缓解措施\n\n**6. 实施策略制定**：制定详细的分阶段实施计划，考虑业务连续性\n\n**7. 成功标准定义**：明确可测量的成功指标和验收标准\n\n（要求至少400字，体现架构师的系统性思维和决策过程）"
}}"""

        try:
            print(f" 正在为 {area} 调用Claude API...")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": claude_prompt}]
            )
            
            content = response.content[0].text
            print(f" Claude返回内容: {content[:200]}...")
            
            # 清理和提取JSON
            content = self._extract_json_from_response(content)
            
            try:
                proposal_data = json.loads(content)
                
                proposal_result = {
                    'type': 'enhancement',
                    'title': proposal_data.get('title', f'{area}增强方案'),
                    'description': proposal_data.get('description', ''),
                    'technical_approach': proposal_data.get('technical_approach', ''),
                    'implementation_steps': proposal_data.get('implementation_steps', []),
                    'benefits': proposal_data.get('benefits', []),
                    'challenges_and_solutions': proposal_data.get('challenges_and_solutions', []),
                    'acceptance_criteria': proposal_data.get('acceptance_criteria', []),
                    'estimated_effort': proposal_data.get('estimated_effort', 'Medium'),
                    'timeline': proposal_data.get('timeline', ''),
                    'priority': 'High',
                    'reasoning_trace': proposal_data.get('reasoning_trace', ''),
                    'metadata': {
                        'enhancement_area': area,
                        'proposal_type': 'enhancement',
                        'complexity': current_arch.get('complexity', 'Medium'),
                        'generated_by': 'claude'
                    }
                }
                
                # 验证reasoning质量
                if not self._validate_design_reasoning_quality(proposal_result):
                    print(f" {area} 增强方案的reasoning质量不达标，跳过")
                    return None
                
                return proposal_result
            except json.JSONDecodeError as e:
                print(f" 增强方案的JSON解析错误: {e}")
                print(f" 问题内容: {content[:200] if content else 'None'}")
                return None
        except Exception as e:
            print(f" Claude增强方案生成失败: {e}")
            return None
    
    def _generate_refactoring_proposals(self, code_analysis: Dict[str, Any], 
                                      current_arch: Dict[str, Any], 
                                      requirements: List[str], num_proposals: int) -> List[Dict[str, Any]]:
        """生成重构建议"""
        proposals = []
        
        refactoring_types = [
            '服务抽取',
            '设计模式实现',
            '代码模块化',
            '关注点分离改进'
        ]
        
        for refactor_type in refactoring_types[:num_proposals]:
            try:
                proposal = self._generate_claude_refactoring_proposal(refactor_type, current_arch, code_analysis)
                if proposal:
                    proposals.append(proposal)
            except Exception as e:
                print(f" 生成重构方案失败: {e}")
                continue
        
        return proposals
    
    def _generate_claude_refactoring_proposal(self, refactor_type: str, current_arch: Dict[str, Any], 
                                            code_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用Claude生成重构方案"""
        claude_prompt = f"""作为软件重构专家，请为以下项目生成一个"{refactor_type}"的重构方案：

项目信息:
- 架构模式: {current_arch.get('detected_patterns', {})}
- 项目复杂度: {current_arch.get('complexity', '未知')}
- 技术栈: {', '.join(current_arch.get('technologies', []))}

请生成一个详细的{refactor_type}重构方案。

JSON格式:
{{
    "title": "重构方案标题",
    "description": "详细描述",
    "implementation_steps": ["步骤1", "步骤2"],
    "benefits": ["收益1", "收益2"],
    "risks": ["风险1", "风险2"],
    "estimated_effort": "Medium/High",
    "reasoning_trace": "重构分析过程"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": claude_prompt}]
            )
            
            content = response.content[0].text
            print(f" Claude返回内容: {content[:200]}...")
            
            # 清理和提取JSON
            content = self._extract_json_from_response(content)
            
            try:
                proposal_data = json.loads(content)
                
                return {
                    'type': 'refactoring',
                    'title': proposal_data.get('title', f'{refactor_type}重构'),
                    'description': proposal_data.get('description', ''),
                    'implementation_steps': proposal_data.get('implementation_steps', []),
                    'benefits': proposal_data.get('benefits', []),
                    'risks': proposal_data.get('risks', []),
                    'estimated_effort': proposal_data.get('estimated_effort', 'Medium'),
                    'priority': 'Medium',
                    'reasoning_trace': proposal_data.get('reasoning_trace', ''),
                    'metadata': {
                        'refactoring_type': refactor_type,
                        'proposal_type': 'refactoring',
                        'complexity': current_arch.get('complexity', 'Medium'),
                        'generated_by': 'claude'
                    }
                }
            except json.JSONDecodeError as e:
                print(f" 重构方案的JSON解析错误: {e}")
                print(f" 问题内容: {content[:200] if content else 'None'}")
                return None
        except Exception as e:
            print(f" Claude重构方案生成失败: {e}")
            return None
    
    def _generate_feature_proposals(self, code_analysis: Dict[str, Any], 
                                  current_arch: Dict[str, Any], 
                                  requirements: List[str], num_proposals: int) -> List[Dict[str, Any]]:
        """生成新功能建议"""
        proposals = []
        
        # 使用自定义需求或默认需求
        if not requirements:
            requirements = [
                '用户认证和授权系统',
                '实时数据处理',
                'API安全防护',
                '缓存和性能优化',
                '错误处理和日志系统'
            ]
        
        for requirement in requirements[:num_proposals]:
            try:
                proposal = self._generate_claude_feature_proposal(requirement, current_arch, code_analysis)
                if proposal:
                    proposals.append(proposal)
            except Exception as e:
                print(f" 生成功能方案失败: {e}")
                continue
        
        return proposals
    
    def _generate_claude_feature_proposal(self, requirement: str, current_arch: Dict[str, Any], 
                                        code_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用Claude生成功能方案"""
        claude_prompt = f"""作为产品架构师，请为以下项目设计"{requirement}"功能的实现方案：

项目背景:
- 当前架构: {current_arch.get('detected_patterns', {})}
- 技术栈: {', '.join(current_arch.get('technologies', []))}
- 项目规模: {code_analysis.get('repo_structure', {}).get('total_files', 0)} 个文件

需求: {requirement}

请提供详细的功能设计方案。

JSON格式:
{{
    "title": "功能方案标题",
    "description": "功能详细描述",
    "design_approach": "设计方法",
    "implementation_steps": ["实现步骤1", "实现步骤2"],
    "integration_points": ["集成点1", "集成点2"],
    "dependencies": ["依赖1", "依赖2"],
    "estimated_effort": "Medium/High",
    "reasoning_trace": "功能设计推理过程"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": claude_prompt}]
            )
            
            content = response.content[0].text
            print(f" Claude返回内容: {content[:200]}...")
            
            # 清理和提取JSON
            content = self._extract_json_from_response(content)
            
            try:
                proposal_data = json.loads(content)
                
                return {
                    'type': 'feature',
                    'title': proposal_data.get('title', f'实现{requirement}'),
                    'description': proposal_data.get('description', ''),
                    'design_approach': proposal_data.get('design_approach', ''),
                    'implementation_steps': proposal_data.get('implementation_steps', []),
                    'integration_points': proposal_data.get('integration_points', []),
                    'dependencies': proposal_data.get('dependencies', []),
                    'estimated_effort': proposal_data.get('estimated_effort', 'Medium'),
                    'priority': 'High',
                    'reasoning_trace': proposal_data.get('reasoning_trace', ''),
                    'metadata': {
                        'feature_requirement': requirement,
                        'proposal_type': 'feature',
                        'complexity': current_arch.get('complexity', 'Medium'),
                        'generated_by': 'claude'
                    }
                }
            except json.JSONDecodeError as e:
                print(f" 功能方案的JSON解析错误: {e}")
                print(f" 问题内容: {content[:200] if content else 'None'}")
                return None
        except Exception as e:
            print(f" Claude功能方案生成失败: {e}")
            return None
    
    def _generate_architecture_migration_proposals(self, code_analysis: Dict[str, Any], 
                                                 current_arch: Dict[str, Any], 
                                                 requirements: List[str], num_proposals: int) -> List[Dict[str, Any]]:
        """生成架构迁移建议"""
        proposals = []
        
        current_patterns = current_arch.get('detected_patterns', {})
        available_patterns = [pattern for pattern, detected in current_patterns.items() if not detected]
        
        for pattern in available_patterns[:num_proposals]:
            try:
                proposal = self._generate_claude_migration_proposal(pattern, current_arch, code_analysis)
                if proposal:
                    proposals.append(proposal)
            except Exception as e:
                print(f" 生成迁移方案失败: {e}")
                continue
        
        return proposals
    
    def _generate_claude_migration_proposal(self, target_pattern: str, current_arch: Dict[str, Any], 
                                          code_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用Claude生成架构迁移方案"""
        pattern_info = self.design_patterns.get(target_pattern, {})
        
        claude_prompt = f"""作为系统架构师，请为以下项目设计向"{pattern_info.get('name', target_pattern)}"架构迁移的方案：

当前状态:
- 项目复杂度: {current_arch.get('complexity', '未知')}
- 现有模式: {current_arch.get('detected_patterns', {})}
- 技术栈: {', '.join(current_arch.get('technologies', []))}

目标架构: {pattern_info.get('name', target_pattern)}
架构描述: {pattern_info.get('description', '')}

请提供详细的迁移方案。

JSON格式:
{{
    "title": "迁移方案标题",
    "description": "迁移描述",
    "migration_strategy": "迁移策略",
    "implementation_phases": ["阶段1", "阶段2"],
    "benefits": ["收益1", "收益2"],
    "challenges": ["挑战1", "挑战2"],
    "estimated_effort": "High",
    "reasoning_trace": "迁移分析过程"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": claude_prompt}]
            )
            
            content = response.content[0].text
            print(f" Claude返回内容: {content[:200]}...")
            
            # 清理和提取JSON
            content = self._extract_json_from_response(content)
            
            try:
                proposal_data = json.loads(content)
                
                return {
                    'type': 'architecture_migration',
                    'title': proposal_data.get('title', f'迁移到{pattern_info.get("name", target_pattern)}'),
                    'description': proposal_data.get('description', ''),
                    'target_architecture': pattern_info,
                    'migration_strategy': proposal_data.get('migration_strategy', ''),
                    'implementation_phases': proposal_data.get('implementation_phases', []),
                    'benefits': proposal_data.get('benefits', []),
                    'challenges': proposal_data.get('challenges', []),
                    'estimated_effort': 'High',
                    'priority': 'Low',
                    'reasoning_trace': proposal_data.get('reasoning_trace', ''),
                    'metadata': {
                        'target_pattern': target_pattern,
                        'proposal_type': 'architecture_migration',
                        'complexity': 'High',
                        'generated_by': 'claude'
                    }
                }
            except json.JSONDecodeError as e:
                print(f" 迁移方案的JSON解析错误: {e}")
                print(f" 问题内容: {content[:200] if content else 'None'}")
                return None
        except Exception as e:
            print(f" Claude迁移方案生成失败: {e}")
            return None
    
    def _extract_json_from_response(self, content: str) -> str:
        """从Claude响应中提取JSON"""
        # 尝试找到JSON开始和结束位置
        start_markers = ['{', '```json\n{', '```\n{']
        
        for start_marker in start_markers:
            start_pos = content.find(start_marker)
            if start_pos != -1:
                # 找到开始位置后，寻找对应的结束位置
                json_start = start_pos + (len(start_marker) - 1) if start_marker != '{' else start_pos
                
                # 尝试找到匹配的结束括号
                brace_count = 0
                for i, char in enumerate(content[json_start:], json_start):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_content = content[json_start:i+1]
                            # 清理控制字符
                            return self._clean_json_string(json_content)
        
        # 如果找不到完整的JSON，返回清理后的原内容
        return self._clean_json_string(content)
    
    def _clean_json_string(self, json_str: str) -> str:
        """清理JSON字符串中的控制字符"""
        import re
        # 移除所有控制字符（除了换行、制表符、回车）
        json_str = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', '', json_str)
        return json_str
    
    def _validate_design_reasoning_quality(self, proposal: Dict[str, Any]) -> bool:
        """验证设计方案reasoning_trace的质量"""
        reasoning = proposal.get('reasoning_trace', '')
        
        if len(reasoning) < 200:
            return False
        
        # 检查是否包含高质量的分析要素
        analysis_indicators = [
            '现状', '分析', '问题', '根因', '方案', '对比', '选择',
            '技术', '风险', '评估', '实施', '策略', '标准', '考量',
            '优势', '劣势', '缓解', '措施', '指标', '架构'
        ]
        
        indicator_count = sum(1 for indicator in analysis_indicators if indicator in reasoning)
        
        # 检查是否包含结构化的思维框架
        framework_elements = [
            '现状', '问题', '方案', '技术', '风险', '实施', '标准'
        ]
        
        framework_count = sum(1 for element in framework_elements if element in reasoning)
        
        return indicator_count >= 8 and framework_count >= 5 and len(reasoning) >= 200
    
    def save_design_proposals(self, proposals: List[Dict[str, Any]], output_path: str):
        """保存设计方案到文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(proposals, f, indent=2, ensure_ascii=False)
        print(f" 设计方案已保存到: {output_path}")
