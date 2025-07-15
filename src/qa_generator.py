"""
Claude集成的问答对生成器 - 基于代码分析生成高质量训练数据
"""
import json
import random
from typing import Dict, List, Any, Optional, Tuple
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class QAGenerator:
    """Claude驱动的问答对生成器"""
    
    def __init__(self, claude_api_key: str):
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("需要安装anthropic包: pip install anthropic")
        
        self.client = Anthropic(api_key=claude_api_key)
        self.model = "claude-3-5-sonnet-20241022"
        self.question_templates = self._load_question_templates()
        
    def _load_question_templates(self) -> Dict[str, List[str]]:
        """加载问题模板以确保多样性"""
        return {
            'functionality': [
                "What does the {function_name} function do?",
                "How does {function_name} work?",
                "Explain the purpose of {function_name}",
                "What is the role of {function_name} in the system?",
                "Can you describe what {function_name} accomplishes?"
            ],
            'business_logic': [
                "What business rule is implemented in {code_context}?",
                "How does this code enforce business requirements?",
                "What business process does this code support?",
                "What are the business implications of this implementation?",
                "How does this code align with business needs?"
            ],
            'architecture': [
                "How does this code fit into the overall architecture?",
                "What architectural pattern is used here?",
                "How does this component interact with other parts?",
                "What are the architectural benefits of this approach?",
                "How does this design support system scalability?"
            ],
            'best_practices': [
                "What coding best practices are demonstrated here?",
                "How could this code be improved?",
                "What are potential issues with this implementation?",
                "What design patterns are used in this code?",
                "How does this code handle error cases?"
            ],
            'usage': [
                "How would you use {function_name}?",
                "What are the parameters for {function_name}?",
                "When should you call {function_name}?",
                "What does {function_name} return?",
                "How do you integrate {function_name} into a project?"
            ]
        }
    
    def generate_qa_pairs(self, code_analysis: Dict[str, Any], num_pairs: int = 50) -> List[Dict[str, Any]]:
        """生成问答对"""
        print(f"使用Claude生成 {num_pairs} 个问答对...")
        print(f"DEBUG: 开始执行generate_qa_pairs方法")
        
        qa_pairs = []
        
        # 从不同代码元素生成问答对
        generators = [
            self._generate_function_qa,
            self._generate_class_qa,
            self._generate_business_rule_qa,
            self._generate_architecture_qa,
        ]
        print(f"DEBUG: 已定义 {len(generators)} 个生成器")
        
        # 每个生成器分配更多数量，确保总数足够
        pairs_per_generator = max((num_pairs * 2) // len(generators), 2)
        print(f"每个生成器目标: {pairs_per_generator} 个QA")
        print(f"DEBUG: 计算完成，开始循环执行生成器")
        
        for generator in generators:
            try:
                pairs = generator(code_analysis, pairs_per_generator)
                if pairs:
                    qa_pairs.extend(pairs)
                    print(f"{generator.__name__} 生成了 {len(pairs)} 个QA")
                else:
                    print(f"{generator.__name__} 没有生成任何QA")
            except Exception as e:
                print(f"生成器 {generator.__name__} 出错: {e}")
                continue
        
        print(f"总共生成了 {len(qa_pairs)} 个QA，目标: {num_pairs}")
        
        # 确保多样性并保证数量
        qa_pairs = self._ensure_diversity(qa_pairs)
        
        # 如果数量不足，尝试从函数生成器补充
        if len(qa_pairs) < num_pairs:
            additional_needed = num_pairs - len(qa_pairs)
            print(f"数量不足，尝试补充 {additional_needed} 个QA")
            try:
                additional_pairs = self._generate_function_qa(code_analysis, additional_needed)
                qa_pairs.extend(additional_pairs)
            except Exception as e:
                print(f"补充生成失败: {e}")
        
        return qa_pairs[:num_pairs]
    
    def _generate_function_qa(self, code_analysis: Dict[str, Any], num_pairs: int) -> List[Dict[str, Any]]:
        """基于函数生成问答对"""
        qa_pairs = []
        file_analysis = code_analysis.get('file_analysis', {})
        
        # 收集所有函数
        all_functions = []
        for file_path, analysis in file_analysis.items():
            functions = analysis.get('functions', [])
            for func_info in functions:
                all_functions.append((file_path, func_info, analysis))
        
        if not all_functions:
            return qa_pairs
        
        # 随机选择函数
        selected_functions = random.sample(all_functions, min(len(all_functions), num_pairs))
        
        for file_path, func_info, analysis in selected_functions:
            try:
                qa_pair = self._generate_claude_qa_for_function(file_path, func_info, analysis)
                if qa_pair:
                    qa_pairs.append(qa_pair)
            except Exception as e:
                print(f"为函数 {func_info.get('name', 'unknown')} 生成QA时出错: {e}")
                continue
        
        return qa_pairs
    
    def _generate_claude_qa_for_function(self, file_path: str, func_info: Dict[str, Any], 
                                       file_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用Claude为函数生成问答对"""
        function_name = func_info.get('name', '')
        args = func_info.get('args', [])
        docstring = func_info.get('docstring', '')
        business_keywords = file_analysis.get('business_keywords', [])
        
        # 构建代码上下文
        context = f"""文件: {file_path}
函数: {function_name}({', '.join(args)})
文档: {docstring if docstring else '无文档'}
业务关键词: {', '.join(business_keywords) if business_keywords else '无'}"""

        # 选择问题类型和角度
        question_type = random.choice(list(self.question_templates.keys()))
        complexity_level = random.choice(['basic', 'intermediate', 'advanced'])
        perspective = random.choice(['developer', 'architect', 'business_analyst', 'user'])
        
        # 构建Claude提示词
        claude_prompt = f"""作为一位资深软件工程师和技术专家，请基于以下代码信息生成一个高质量的问答对，用于训练AI模型理解代码。

代码上下文:
{context}

要求:
1. 生成一个关于"{question_type}"的问题
2. 问题复杂度: {complexity_level}
3. 回答角度: {perspective}
4. 问题要具体、有针对性，体现深度思考
5. 答案要详细、准确，包含技术细节和实践经验
6. reasoning_trace必须包含完整的分析推理过程

## Reasoning Trace质量要求：
reasoning_trace必须遵循以下结构化推理框架：

**阶段1：问题理解与分解**
- 识别问题的核心要点
- 分析问题的技术背景和业务背景
- 确定需要考虑的关键因素

**阶段2：技术分析**
- 代码功能分析：具体做了什么
- 设计模式识别：使用了哪些模式
- 架构考量：在整体架构中的作用

**阶段3：深度推理**
- 因果关系分析：为什么这样设计
- 假设验证：如果采用其他方案会如何
- 权衡分析：优势与劣势的对比

**阶段4：实践考虑**
- 实际应用场景
- 潜在问题和解决方案
- 最佳实践建议

**示例格式**：
"1. 问题分析：[分析问题的核心要点和技术背景]
2. 技术考察：[详细分析代码的功能、模式、架构]
3. 深度推理：[解释设计原因、分析替代方案、评估优劣]
4. 实践洞察：[应用场景、潜在问题、最佳实践]"

请严格按照以下JSON格式回复，不要添加任何其他内容:
{{
    "question": "具体的问题（体现深度思考）",
    "answer": "详细的答案（包含技术细节和实践经验）",
    "reasoning_trace": "结构化的推理过程（至少150字，遵循上述4阶段框架）"
}}

注意：reasoning_trace必须具有逻辑连贯性，体现专家级的技术洞察力。只返回JSON，不要包含解释文字或markdown格式。"""

        try:
            print(f"正在为函数 {function_name} 调用Claude API...")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": claude_prompt
                    }
                ]
            )
            
            content = response.content[0].text
            print(f"Claude返回内容: {content[:200]}...")
            
            # 清理和提取JSON
            content = self._extract_json_from_response(content)
            
            # 尝试解析JSON
            try:
                qa_data = json.loads(content)
                
                qa_result = {
                    'question': qa_data.get('question', ''),
                    'answer': qa_data.get('answer', ''),
                    'code_context': context,
                    'reasoning_trace': qa_data.get('reasoning_trace', ''),
                    'metadata': {
                        'source_file': file_path,
                        'function_name': function_name,
                        'question_type': question_type,
                        'complexity_level': complexity_level,
                        'perspective': perspective,
                        'element_type': 'function',
                        'generated_by': 'claude'
                    }
                }
                
                # 验证reasoning质量
                if not self._validate_reasoning_quality(qa_result):
                    print(f"函数 {function_name} 的reasoning质量不达标，跳过")
                    return None
                
                return qa_result
            except json.JSONDecodeError:
                print(f"Claude返回的内容不是有效JSON: {content[:100]}...")
                return None
                
        except Exception as e:
            print(f"Claude API调用失败: {e}")
            return None
    
    def _generate_class_qa(self, code_analysis: Dict[str, Any], num_pairs: int) -> List[Dict[str, Any]]:
        """基于类生成问答对"""
        qa_pairs = []
        file_analysis = code_analysis.get('file_analysis', {})
        
        # 收集所有类
        all_classes = []
        for file_path, analysis in file_analysis.items():
            classes = analysis.get('classes', [])
            for class_info in classes:
                all_classes.append((file_path, class_info, analysis))
        
        if not all_classes:
            return qa_pairs
        
        selected_classes = random.sample(all_classes, min(len(all_classes), num_pairs))
        
        for file_path, class_info, analysis in selected_classes:
            try:
                qa_pair = self._generate_claude_qa_for_class(file_path, class_info, analysis)
                if qa_pair:
                    qa_pairs.append(qa_pair)
            except Exception as e:
                print(f"为类 {class_info.get('name', 'unknown')} 生成QA时出错: {e}")
                continue
        
        return qa_pairs
    
    def _generate_claude_qa_for_class(self, file_path: str, class_info: Dict[str, Any], 
                                    file_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """使用Claude为类生成问答对"""
        class_name = class_info.get('name', '')
        methods = class_info.get('methods', [])
        docstring = class_info.get('docstring', '')
        
        context = f"""文件: {file_path}
类: {class_name}
方法: {', '.join(methods) if methods else '无'}
文档: {docstring if docstring else '无文档'}"""

        claude_prompt = f"""作为资深软件架构师，请为以下类信息生成一个高质量的问答对，用于训练AI模型理解代码架构设计。

{context}

请生成一个关于类设计和架构的深度问题，以及专业的回答。

## Reasoning Trace质量要求：
必须包含结构化的架构分析推理：

**1. 设计意图分析**：解释该类的设计目的和在系统中的角色
**2. 架构模式识别**：分析使用的设计模式和架构原则
**3. 职责边界分析**：评估类的职责是否清晰，是否符合单一职责原则
**4. 依赖关系分析**：分析类与其他组件的耦合关系
**5. 扩展性评估**：评估类的可扩展性和可维护性
**6. 最佳实践对比**：与业界最佳实践进行对比分析

JSON格式:
{{
    "question": "关于类设计的深度架构问题",
    "answer": "详细的架构分析回答",
    "reasoning_trace": "结构化的架构推理过程（至少200字，体现架构师的专业洞察）"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": claude_prompt}]
            )
            
            content = response.content[0].text
            content = self._extract_json_from_response(content)
            
            try:
                qa_data = json.loads(content)
                
                return {
                    'question': qa_data.get('question', ''),
                    'answer': qa_data.get('answer', ''),
                    'code_context': context,
                    'reasoning_trace': qa_data.get('reasoning_trace', ''),
                    'metadata': {
                        'source_file': file_path,
                        'class_name': class_name,
                        'question_type': 'architecture',
                        'complexity_level': 'intermediate',
                        'perspective': 'architect',
                        'element_type': 'class',
                        'generated_by': 'claude'
                    }
                }
            except json.JSONDecodeError as e:
                print(f"类QA的JSON解析错误: {e}")
                print(f"问题内容: {content[:200] if content else 'None'}")
                return None
        except Exception as e:
            print(f"为类生成QA失败: {e}")
            return None
    
    def _generate_business_rule_qa(self, code_analysis: Dict[str, Any], num_pairs: int) -> List[Dict[str, Any]]:
        """基于业务规则生成问答对"""
        qa_pairs = []
        business_rules = code_analysis.get('business_rules', [])
        
        for rule_info in business_rules[:num_pairs]:
            try:
                qa_pair = self._generate_claude_qa_for_business_rule(rule_info)
                if qa_pair:
                    qa_pairs.append(qa_pair)
            except Exception as e:
                print(f"为业务规则生成QA时出错: {e}")
                continue
        
        return qa_pairs
    
    def _generate_claude_qa_for_business_rule(self, rule_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """为业务规则生成问答对"""
        rule = rule_info.get('rule', '')
        source_file = rule_info.get('source_file', '')
        
        claude_prompt = f"""作为资深业务分析师和技术专家，请基于以下业务规则生成高质量的问答对，用于训练AI模型理解业务逻辑。

业务规则: {rule}
来源: {source_file}

请生成一个深度的业务逻辑问题和专业回答。

## Reasoning Trace质量要求：
必须包含完整的业务分析推理：

**1. 业务背景分析**：解释该业务规则的背景和目的
**2. 规则逻辑分析**：详细分析规则的执行逻辑和条件
**3. 业务价值评估**：评估该规则对业务的价值和重要性
**4. 影响范围分析**：分析该规则对其他业务流程的影响
**5. 异常情况考虑**：分析可能的异常情况和处理方式
**6. 优化建议**：基于最佳实践提出改进建议

JSON格式:
{{
    "question": "深度的业务逻辑问题",
    "answer": "专业的业务分析回答",
    "reasoning_trace": "结构化的业务推理过程（至少180字，体现业务分析师的专业能力）"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                messages=[{"role": "user", "content": claude_prompt}]
            )
            
            content = response.content[0].text
            content = self._extract_json_from_response(content)
            
            try:
                qa_data = json.loads(content)
                
                return {
                    'question': qa_data.get('question', ''),
                    'answer': qa_data.get('answer', ''),
                    'code_context': f"业务规则: {rule}",
                    'reasoning_trace': qa_data.get('reasoning_trace', ''),
                    'metadata': {
                        'business_rule': rule,
                        'source_file': source_file,
                        'question_type': 'business_logic',
                        'complexity_level': 'intermediate',
                        'perspective': 'business_analyst',
                        'element_type': 'business_rule',
                        'generated_by': 'claude'
                    }
                }
            except json.JSONDecodeError as e:
                print(f"业务规则QA的JSON解析错误: {e}")
                print(f"问题内容: {content[:200] if content else 'None'}")
                return None
        except Exception as e:
            print(f"业务规则QA生成失败: {e}")
            return None
    
    def _generate_architecture_qa(self, code_analysis: Dict[str, Any], num_pairs: int) -> List[Dict[str, Any]]:
        """基于架构模式生成问答对"""
        qa_pairs = []
        architecture_patterns = code_analysis.get('architecture_patterns', {})
        
        detected_patterns = [pattern for pattern, is_present in architecture_patterns.items() if is_present]
        
        for pattern in detected_patterns[:num_pairs]:
            try:
                qa_pair = self._generate_claude_qa_for_architecture(pattern, code_analysis)
                if qa_pair:
                    qa_pairs.append(qa_pair)
            except Exception as e:
                print(f"为架构模式 {pattern} 生成QA时出错: {e}")
                continue
        
        return qa_pairs
    
    def _generate_claude_qa_for_architecture(self, pattern: str, code_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """为架构模式生成问答对"""
        repo_structure = code_analysis.get('repo_structure', {})
        
        claude_prompt = f"""作为系统架构师和技术领域专家，请基于以下项目信息生成高质量的架构问答对，用于训练AI模型理解系统架构设计。

检测到的架构模式: {pattern}
项目结构: {repo_structure}

请生成一个深度的架构设计问题和专业回答。

## Reasoning Trace质量要求：
必须包含系统性的架构分析推理：

**1. 架构模式识别**：深入分析当前架构模式的特征和适用性
**2. 设计原则评估**：评估架构是否符合SOLID、DRY、KISS等设计原则
**3. 可扩展性分析**：分析架构的水平扩展和垂直扩展能力
**4. 性能影响评估**：评估架构对系统性能的影响
**5. 维护性考量**：分析架构的可维护性和技术债务风险
**6. 演进策略**：提出架构演进和优化建议

JSON格式:
{{
    "question": "深度的架构设计问题",
    "answer": "专业的架构分析和设计建议",
    "reasoning_trace": "系统性的架构推理过程（至少220字，体现架构师的系统性思维）"
}}"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": claude_prompt}]
            )
            
            content = response.content[0].text
            content = self._extract_json_from_response(content)
            
            try:
                qa_data = json.loads(content)
                
                return {
                    'question': qa_data.get('question', ''),
                    'answer': qa_data.get('answer', ''),
                    'code_context': f"架构模式: {pattern}",
                    'reasoning_trace': qa_data.get('reasoning_trace', ''),
                    'metadata': {
                        'architecture_pattern': pattern,
                        'question_type': 'architecture',
                        'complexity_level': 'advanced',
                        'perspective': 'architect',
                        'element_type': 'architecture',
                        'generated_by': 'claude'
                    }
                }
            except json.JSONDecodeError as e:
                print(f"架构QA的JSON解析错误: {e}")
                print(f"问题内容: {content[:200] if content else 'None'}")
                return None
        except Exception as e:
            print(f"架构QA生成失败: {e}")
            return None
    
    def _validate_reasoning_quality(self, qa_pair: Dict[str, Any]) -> bool:
        """验证reasoning_trace的质量"""
        reasoning = qa_pair.get('reasoning_trace', '')
        
        if len(reasoning) < 100:
            return False
        
        # 检查是否包含结构化的分析步骤
        quality_indicators = [
            '分析', '考虑', '评估', '推理', '因为', '所以',
            '背景', '原因', '影响', '优势', '劣势', '方案',
            '设计', '架构', '模式', '原则', '实践'
        ]
        
        indicator_count = sum(1 for indicator in quality_indicators if indicator in reasoning)
        
        # 检查是否有逻辑结构（步骤1、步骤2等或数字编号）
        has_structure = any(pattern in reasoning for pattern in [
            '1.', '2.', '3.', '一、', '二、', '三、',
            '首先', '其次', '最后', '步骤', '阶段'
        ])
        
        return indicator_count >= 3 and has_structure and len(reasoning) >= 100
    
    def _ensure_diversity(self, qa_pairs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """确保问答对的多样性"""
        if not qa_pairs:
            return qa_pairs
        
        # 按问题类型分组
        by_type = {}
        for qa in qa_pairs:
            qtype = qa['metadata'].get('question_type', 'other')
            if qtype not in by_type:
                by_type[qtype] = []
            by_type[qtype].append(qa)
        
        # 平衡不同类型的数量
        balanced_pairs = []
        max_per_type = max(len(qa_pairs) // len(by_type), 1) if by_type else 1
        
        for qtype, pairs in by_type.items():
            selected = random.sample(pairs, min(len(pairs), max_per_type))
            balanced_pairs.extend(selected)
        
        return balanced_pairs
    
    def _extract_json_from_response(self, content: str) -> str:
        """从Claude响应中提取JSON"""
        # 尝试找到JSON开始和结束位置
        start_markers = ['{', '```json\n{', '```\n{']
        end_markers = ['}', '}\n```', '}```']
        
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
    
    def save_qa_pairs(self, qa_pairs: List[Dict[str, Any]], output_path: str):
        """保存问答对到文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(qa_pairs, f, indent=2, ensure_ascii=False)
        print(f"问答对已保存到: {output_path}")
