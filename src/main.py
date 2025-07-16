"""
智能训练数据生成系统 - 主程序
基于Claude AI为代码仓库生成高质量训练数据
"""
import os
import json
import math
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from code_analyzer import CodeAnalyzer
from qa_generator import QAGenerator
from design_generator import DesignGenerator
from reasoning_quality_assessor import ReasoningQualityAssessor


class TrainingDataGenerator:
    """智能训练数据生成系统主类"""
    
    def __init__(self, repo_path: str, output_dir: str, claude_api_key: str):
        self.repo_path = Path(repo_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化核心组件
        print("初始化Claude AI增强的训练数据生成系统...")
        self.analyzer = CodeAnalyzer(str(self.repo_path))
        self.qa_generator = QAGenerator(claude_api_key)
        self.design_generator = DesignGenerator(claude_api_key)
        self.quality_assessor = ReasoningQualityAssessor()
        
        self.analysis_result = None
        
    def run_full_pipeline(self, num_qa_pairs: int = 50, num_design_proposals: int = 10,
                         custom_requirements: Optional[List[str]] = None) -> Dict[str, str]:
        """运行完整的数据生成流水线"""
        print(" 启动智能训练数据生成流水线...")
        print(f" 分析仓库: {self.repo_path}")
        print(f" 目标: {num_qa_pairs} 个问答对, {num_design_proposals} 个设计方案")
        
        # Step 1: 代码仓分析
        print("\n Step 1: 分析代码仓库...")
        self.analysis_result = self._analyze_repository()
        
        # Step 2: 生成问答对
        print(f"\n❓ Step 2: 生成 {num_qa_pairs} 个问答对...")
        qa_output_path = self._generate_qa_pairs(num_qa_pairs)
        
        # Step 3: 生成设计方案
        print(f"\n Step 3: 生成 {num_design_proposals} 个设计方案...")
        design_output_path = self._generate_design_proposals(num_design_proposals, custom_requirements)
        
        # Step 4: 生成训练数据集
        print("\n Step 4: 创建标准训练数据集...")
        dataset_path = self._create_training_dataset(qa_output_path, design_output_path)
        
        # Step 5: 推理质量评估
        print("\n🔍 Step 5: 评估推理质量...")
        quality_report_path = self._assess_reasoning_quality(qa_output_path, design_output_path)
        
        # Step 6: 生成综合报告
        print("\nStep 6: 生成综合分析报告...")
        report_path = self._generate_comprehensive_report()
        
        print("\n训练数据生成完成!")
        
        return {
            'analysis_report': str(self.output_dir / 'analysis_report.json'),
            'qa_pairs': qa_output_path,
            'design_proposals': design_output_path,
            'training_dataset': dataset_path,
            'quality_report': quality_report_path,
            'comprehensive_report': report_path
        }
    
    def _analyze_repository(self) -> Dict[str, Any]:
        """分析代码仓"""
        analysis_result = self.analyzer.analyze_repository()
        
        # 保存分析结果
        output_path = self.output_dir / 'analysis_report.json'
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, ensure_ascii=False)
            
        print(f"    已分析 {analysis_result['repo_structure']['total_files']} 个文件")
        print(f"    目录深度: {analysis_result['repo_structure']['depth']}")
        detected_patterns = [k for k, v in analysis_result['architecture_patterns'].items() if v]
        if detected_patterns:
            print(f"   🔍 检测到架构模式: {', '.join(detected_patterns)}")
        
        return analysis_result
    
    def _generate_qa_pairs(self, num_pairs: int) -> str:
        """生成问答对"""
        qa_pairs = self.qa_generator.generate_qa_pairs(self.analysis_result, num_pairs)
        
        # 保存问答对
        output_path = str(self.output_dir / 'qa_pairs.json')
        self.qa_generator.save_qa_pairs(qa_pairs, output_path)
        
        # 生成统计信息
        stats = self._generate_qa_statistics(qa_pairs)
        print(f"    生成统计: {stats}")
        
        return output_path
    
    def _generate_design_proposals(self, num_proposals: int, 
                                 custom_requirements: Optional[List[str]] = None) -> str:
        """生成设计方案"""
        # 使用自定义需求或默认需求
        requirements = custom_requirements or [
            '用户身份验证和授权',
            '实时数据处理',
            'API安全防护和限流',
            '缓存和性能优化',
            '错误处理和日志系统',
            '数据库查询优化',
            '微服务架构迁移',
            '前端组件库建设',
            '自动化测试框架',
            '监控和告警系统'
        ]
        
        proposals = self.design_generator.generate_design_proposals(
            self.analysis_result, requirements, num_proposals
        )
        
        # 保存设计方案
        output_path = str(self.output_dir / 'design_proposals.json')
        self.design_generator.save_design_proposals(proposals, output_path)
        
        # 生成统计信息
        stats = self._generate_design_statistics(proposals)
        print(f"    生成统计: {stats}")
        
        return output_path
    
    def _assess_reasoning_quality(self, qa_path: str, design_path: str) -> str:
        """评估推理质量"""
        # 加载数据
        with open(qa_path, 'r', encoding='utf-8') as f:
            qa_pairs = json.load(f)
            
        with open(design_path, 'r', encoding='utf-8') as f:
            design_proposals = json.load(f)
        
        # 生成质量报告
        quality_report = self.quality_assessor.generate_quality_report(qa_pairs, design_proposals)
        
        # 保存质量报告
        output_path = str(self.output_dir / 'reasoning_quality_report.json')
        self.quality_assessor.save_quality_report(quality_report, output_path)
        
        # 打印质量摘要
        overall_summary = quality_report['overall_summary']
        print(f"    QA推理质量: {overall_summary['overall_qa_score']:.3f}")
        print(f"    设计推理质量: {overall_summary['overall_design_score']:.3f}")
        print(f"    综合推理质量: {overall_summary['combined_score']:.3f}")
        
        # 显示质量建议
        recommendations = quality_report.get('recommendations', [])
        if recommendations:
            print("    质量改进建议:")
            for rec in recommendations:
                print(f"      - {rec}")
        
        return output_path
    
    def _create_training_dataset(self, qa_path: str, design_path: str) -> str:
        """创建标准格式的训练数据集"""
        # 加载问答对和设计方案
        with open(qa_path, 'r', encoding='utf-8') as f:
            qa_pairs = json.load(f)
            
        with open(design_path, 'r', encoding='utf-8') as f:
            design_proposals = json.load(f)
        
        # 转换为标准训练格式
        training_data = []
        
        # 处理问答对
        for qa in qa_pairs:
            training_item = {
                'input': qa['question'],
                'output': qa['answer'],
                'context': qa['code_context'],
                'reasoning': qa['reasoning_trace'],
                'metadata': qa['metadata'],
                'type': 'qa_pair'
            }
            training_data.append(training_item)
        
        # 处理设计方案
        for proposal in design_proposals:
            training_item = {
                'input': f"请为以下需求设计解决方案: {proposal['title']}",
                'output': proposal['description'],
                'context': proposal.get('design_approach', ''),
                'reasoning': proposal['reasoning_trace'],
                'metadata': proposal['metadata'],
                'type': 'design_proposal'
            }
            training_data.append(training_item)
        
        # 保存训练数据集
        output_path = str(self.output_dir / 'training_dataset.jsonl')
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in training_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"   📦 创建了包含 {len(training_data)} 条记录的训练数据集")
        return output_path
    
    def _generate_comprehensive_report(self) -> str:
        """生成综合报告"""
        report = {
            'project_overview': {
                'repository_path': str(self.repo_path),
                'analysis_timestamp': datetime.now().isoformat(),
                'total_files': self.analysis_result['repo_structure']['total_files'],
                'file_types': self.analysis_result['repo_structure']['file_types'],
                'architecture_patterns': self.analysis_result['architecture_patterns'],
                'technologies': self._detect_technologies()
            },
            'data_generation_summary': {
                'qa_pairs_generated': len(self._load_qa_pairs()),
                'design_proposals_generated': len(self._load_design_proposals()),
                'total_training_items': len(self._load_qa_pairs()) + len(self._load_design_proposals())
            },
            'quality_metrics': self._calculate_quality_metrics(),
            'recommendations': self._generate_recommendations(),
            'next_steps': [
                "使用生成的training_dataset.jsonl训练您的模型",
                "根据项目特点调整问答对数量和设计方案数量",
                "考虑添加更多自定义需求以获得更针对性的设计方案",
                "定期更新训练数据以反映代码库的变化"
            ]
        }
        
        output_path = str(self.output_dir / 'comprehensive_report.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
            
        return output_path
    
    def _generate_qa_statistics(self, qa_pairs: List[Dict[str, Any]]) -> Dict[str, int]:
        """生成问答对统计信息"""
        stats = {}
        for qa in qa_pairs:
            qtype = qa['metadata'].get('question_type', 'unknown')
            stats[qtype] = stats.get(qtype, 0) + 1
        return stats
    
    def _generate_design_statistics(self, proposals: List[Dict[str, Any]]) -> Dict[str, int]:
        """生成设计方案统计信息"""
        stats = {}
        for proposal in proposals:
            ptype = proposal['metadata'].get('proposal_type', 'unknown')
            stats[ptype] = stats.get(ptype, 0) + 1
        return stats
    
    def _detect_technologies(self) -> List[str]:
        """检测技术栈"""
        technologies = []
        file_types = self.analysis_result['repo_structure']['file_types']
        
        if '.py' in file_types:
            technologies.append('Python')
        if '.js' in file_types or '.ts' in file_types:
            technologies.append('JavaScript/TypeScript')
        if '.java' in file_types:
            technologies.append('Java')
        if '.go' in file_types:
            technologies.append('Go')
        if '.rs' in file_types:
            technologies.append('Rust')
        
        return technologies
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        doc_analysis = self.analysis_result['documentation_analysis']
        if not doc_analysis.get('has_readme'):
            recommendations.append("建议添加README.md文档")
        if not doc_analysis.get('has_license'):
            recommendations.append("建议添加LICENSE文件")
        
        patterns = self.analysis_result['architecture_patterns']
        if not any(patterns.values()):
            recommendations.append("考虑采用更清晰的架构模式")
        
        return recommendations
    
    def _calculate_quality_metrics(self) -> Dict[str, float]:
        """计算实际的质量指标"""
        qa_pairs = self._load_qa_pairs()
        design_proposals = self._load_design_proposals()
        
        # 1. 数据多样性得分
        diversity_score = self._calculate_diversity_score(qa_pairs)
        
        # 2. 代码覆盖率得分  
        coverage_score = self._calculate_code_coverage_score(qa_pairs)
        
        # 3. 推理质量得分 (使用新的质量评估器)
        reasoning_score = self._calculate_enhanced_reasoning_quality_score(qa_pairs, design_proposals)
        
        # 4. 元数据完整性得分
        metadata_score = self._calculate_metadata_completeness(qa_pairs, design_proposals)
        
        # 5. 数据代表性得分
        representativeness_score = self._calculate_representativeness_score(qa_pairs, design_proposals)
        
        return {
            'data_diversity_score': diversity_score,
            'code_coverage_score': coverage_score,
            'reasoning_quality_score': reasoning_score,
            'metadata_completeness': metadata_score,
            'data_representativeness_score': representativeness_score,
            'metric_definitions': {
                'data_diversity_score': '基于香农熵的信息论指标，评估问题类型、复杂度、视角分布均匀性(0-1)',
                'code_coverage_score': '类似测试覆盖率概念，基于代码文件、函数、类的覆盖程度(0-1)',
                'reasoning_quality_score': '参考Chain-of-Thought评估框架，综合逻辑结构、内容相关性、深度分析(0-1)',
                'metadata_completeness': '基于数据质量评估标准，计算必要元数据字段完整程度(0-1)',
                'data_representativeness_score': '基于统计学代表性抽样原理，评估生成数据与目标代码库实际特征的一致性(0-1)'
            },
            'evaluation_methodology': {
                'diversity_method': 'Shannon Entropy (Information Theory)',
                'coverage_method': 'Code Coverage Analysis (Software Testing)',
                'reasoning_method': 'Custom Framework inspired by Chain-of-Thought Evaluation',
                'metadata_method': 'Data Quality Assessment Standards',
                'representativeness_method': 'Statistical Representativeness Analysis',
                'limitations': [
                    '推理质量评估为自定义方法，未经大规模验证',
                    '缺乏与标准基准数据集的对比',
                    '关键词匹配方法相对简单，不如语义理解准确',
                    '权重设置基于经验，缺乏理论依据'
                ],
                'future_improvements': [
                    '引入预训练语言模型进行语义相似度计算',
                    '与GSM8K、StrategyQA等标准数据集对比',
                    '使用人工评估验证自动化评估的准确性',
                    '基于大规模实验数据优化权重设置'
                ]
            }
        }
    
    def _calculate_diversity_score(self, qa_pairs: List[Dict]) -> float:
        """计算数据多样性得分"""
        if not qa_pairs:
            return 0.0
            
        # 统计不同维度的分布
        question_types = {}
        complexity_levels = {}
        perspectives = {}
        
        for qa in qa_pairs:
            metadata = qa.get('metadata', {})
            
            # 问题类型分布
            qtype = metadata.get('question_type', 'unknown')
            question_types[qtype] = question_types.get(qtype, 0) + 1
            
            # 复杂度分布
            complexity = metadata.get('complexity_level', 'unknown')
            complexity_levels[complexity] = complexity_levels.get(complexity, 0) + 1
            
            # 视角分布
            perspective = metadata.get('perspective', 'unknown')
            perspectives[perspective] = perspectives.get(perspective, 0) + 1
        
        # 计算香农熵作为多样性指标
        def shannon_entropy(distribution):
            total = sum(distribution.values())
            if total == 0:
                return 0
            entropy = 0
            for count in distribution.values():
                if count > 0:
                    p = count / total
                    entropy -= p * math.log2(p)
            return entropy
        
        # 理论最大熵（假设4种类型、3种复杂度、4种视角）
        max_entropy_types = math.log2(4)  # log2(4) ≈ 2.0
        max_entropy_complexity = math.log2(3)  # log2(3) ≈ 1.58
        max_entropy_perspective = math.log2(4)  # log2(4) ≈ 2.0
        
        # 实际熵
        actual_entropy_types = shannon_entropy(question_types)
        actual_entropy_complexity = shannon_entropy(complexity_levels)
        actual_entropy_perspective = shannon_entropy(perspectives)
        
        # 归一化得分（加权平均）
        diversity_score = (
            (actual_entropy_types / max_entropy_types) * 0.4 +
            (actual_entropy_complexity / max_entropy_complexity) * 0.3 +
            (actual_entropy_perspective / max_entropy_perspective) * 0.3
        )
        
        return round(min(diversity_score, 1.0), 3)
    
    def _calculate_code_coverage_score(self, qa_pairs: List[Dict]) -> float:
        """计算代码覆盖率得分"""
        if not qa_pairs:
            return 0.0
            
        # 统计被覆盖的代码元素
        covered_files = set()
        covered_functions = set()
        covered_classes = set()
        
        for qa in qa_pairs:
            metadata = qa.get('metadata', {})
            source_file = metadata.get('source_file', '')
            function_name = metadata.get('function_name', '')
            class_name = metadata.get('class_name', '')
            
            if source_file:
                covered_files.add(source_file)
            if function_name:
                covered_functions.add(f"{source_file}::{function_name}")
            if class_name:
                covered_classes.add(f"{source_file}::{class_name}")
        
        # 计算总的代码元素数量
        total_files = self.analysis_result['repo_structure']['total_files']
        total_functions = sum(len(analysis.get('functions', [])) 
                            for analysis in self.analysis_result['file_analysis'].values())
        total_classes = sum(len(analysis.get('classes', [])) 
                          for analysis in self.analysis_result['file_analysis'].values())
        
        # 计算覆盖率
        file_coverage = len(covered_files) / max(total_files, 1)
        function_coverage = len(covered_functions) / max(total_functions, 1)
        class_coverage = len(covered_classes) / max(total_classes, 1)
        
        # 加权平均覆盖率
        coverage_score = (file_coverage * 0.3 + function_coverage * 0.4 + class_coverage * 0.3)
        
        return round(min(coverage_score, 1.0), 3)
    
    def _calculate_enhanced_reasoning_quality_score(self, qa_pairs: List[Dict], design_proposals: List[Dict]) -> float:
        """使用新的质量评估器计算推理质量得分"""
        if not qa_pairs and not design_proposals:
            return 0.0
        
        # 使用新的质量评估器
        quality_report = self.quality_assessor.generate_quality_report(qa_pairs, design_proposals)
        combined_score = quality_report['overall_summary']['combined_score']
        
        # 返回0-1范围的分数
        return min(max(combined_score, 0.0), 1.0)
    
    def _calculate_reasoning_quality_score(self, qa_pairs: List[Dict], design_proposals: List[Dict]) -> float:
        """计算推理质量得分 - 基于逻辑结构和内容质量的综合评估"""
        total_items = len(qa_pairs) + len(design_proposals)
        if total_items == 0:
            return 0.0
            
        quality_scores = []
        
        # 评估QA的推理质量
        for qa in qa_pairs:
            reasoning = qa.get('reasoning_trace', '')
            answer = qa.get('answer', '')
            question = qa.get('question', '')
            
            score = self._evaluate_reasoning_quality(reasoning, answer, question, 'qa')
            quality_scores.append(score)
        
        # 评估设计方案的推理质量
        for proposal in design_proposals:
            reasoning = proposal.get('reasoning_trace', '')
            description = proposal.get('description', '')
            title = proposal.get('title', '')
            
            score = self._evaluate_reasoning_quality(reasoning, description, title, 'proposal')
            quality_scores.append(score)
        
        return round(sum(quality_scores) / len(quality_scores), 3)
    
    def _evaluate_reasoning_quality(self, reasoning: str, content: str, title: str, content_type: str) -> float:
        """评估单个推理内容的质量"""
        if not reasoning or not content:
            return 0.0
            
        # 1. 结构完整性评估 (40%)
        structure_score = self._evaluate_logical_structure(reasoning)
        
        # 2. 内容相关性评估 (30%)
        relevance_score = self._evaluate_content_relevance(reasoning, content, title)
        
        # 3. 深度和详细程度评估 (20%)
        depth_score = self._evaluate_reasoning_depth(reasoning, content_type)
        
        # 4. 语言质量评估 (10%)
        language_score = self._evaluate_language_quality(reasoning)
        
        # 优化权重分配，提高相关性和语言质量权重
        total_score = (
            structure_score * 0.25 +   # 降低结构要求权重
            relevance_score * 0.35 +   # 提高相关性权重
            depth_score * 0.25 +       # 适度降低深度要求
            language_score * 0.15      # 提高语言质量权重
        )
        
        return min(total_score, 1.0)
    
    def _evaluate_logical_structure(self, reasoning: str) -> float:
        """评估推理的逻辑结构"""
        score = 0.0
        reasoning_lower = reasoning.lower()
        
        # 检查是否有明确的分析步骤
        analysis_patterns = [
            '分析', '首先', '其次', '然后', '最后', '综合',
            '1)', '2)', '3)', '步骤', '过程', '阶段'
        ]
        has_steps = sum(1 for pattern in analysis_patterns if pattern in reasoning_lower)
        step_score = min(has_steps / 2, 1.0)  # 至少2个步骤标识得满分
        
        # 检查因果逻辑
        causal_patterns = ['因为', '所以', '因此', '由于', '导致', '结果', '原因']
        has_causality = sum(1 for pattern in causal_patterns if pattern in reasoning_lower)
        causal_score = min(has_causality / 1, 1.0)  # 至少1个因果关系得满分
        
        # 检查推理连接词
        reasoning_connectors = ['考虑到', '基于', '根据', '鉴于', '综合考虑', '权衡']
        has_connectors = sum(1 for connector in reasoning_connectors if connector in reasoning_lower)
        connector_score = min(has_connectors / 1, 1.0)  # 至少1个连接词得满分
        
        # 检查结论性语句
        conclusion_patterns = ['总结', '结论', '综上', '因此可以', '最终', '建议']
        has_conclusion = any(pattern in reasoning_lower for pattern in conclusion_patterns)
        conclusion_score = 1.0 if has_conclusion else 0.5
        
        # 加权计算结构得分 - 优化后的权重分配
        score = (step_score * 0.4 + causal_score * 0.2 + connector_score * 0.2 + conclusion_score * 0.2)
        
        return score
    
    def _evaluate_content_relevance(self, reasoning: str, content: str, title: str) -> float:
        """评估推理与内容的相关性"""
        # 提取关键词进行相关性分析
        def extract_keywords(text):
            # 简单的关键词提取（实际应用中可以使用更复杂的NLP方法）
            import re
            words = re.findall(r'\b[\u4e00-\u9fa5a-zA-Z]{2,}\b', text.lower())
            return set(words)
        
        reasoning_keywords = extract_keywords(reasoning)
        content_keywords = extract_keywords(content)
        title_keywords = extract_keywords(title)
        
        # 计算关键词重叠度
        if not reasoning_keywords:
            return 0.0
            
        content_overlap = len(reasoning_keywords & content_keywords) / len(reasoning_keywords)
        title_overlap = len(reasoning_keywords & title_keywords) / len(reasoning_keywords) if title_keywords else 0
        
        # 综合相关性得分
        relevance_score = content_overlap * 0.7 + title_overlap * 0.3
        
        return min(relevance_score, 1.0)
    
    def _evaluate_reasoning_depth(self, reasoning: str, content_type: str) -> float:
        """评估推理的深度和详细程度"""
        # 长度评估（合理范围内）
        min_length = 100 if content_type == 'qa' else 200  # 降低最低长度要求
        optimal_length = 250 if content_type == 'qa' else 400  # 降低最优长度要求
        
        length = len(reasoning)
        if length < min_length:
            length_score = length / min_length
        elif length <= optimal_length:
            length_score = 1.0
        else:
            # 超过最优长度后得分略微下降，避免冗长
            length_score = max(0.8, optimal_length / length)
        
        # 细节丰富度评估
        detail_indicators = [
            '具体', '详细', '例如', '比如', '包括', '涉及', '方面', '层面',
            '方法', '步骤', '流程', '机制', '策略', '方案', '实现', '技术'
        ]
        detail_count = sum(1 for indicator in detail_indicators if indicator in reasoning)
        detail_score = min(detail_count / 3, 1.0)  # 至少3个细节指标得满分
        
        # 深度思考指标
        depth_indicators = [
            '权衡', '对比', '优缺点', '风险', '挑战', '限制', '影响', '后果',
            '替代方案', '最佳实践', '经验', '教训', '原则', '标准'
        ]
        depth_count = sum(1 for indicator in depth_indicators if indicator in reasoning)
        depth_thinking_score = min(depth_count / 2, 1.0)  # 至少2个深度思考指标得满分
        
        # 综合深度得分
        depth_score = length_score * 0.4 + detail_score * 0.3 + depth_thinking_score * 0.3
        
        return depth_score
    
    def _evaluate_language_quality(self, reasoning: str) -> float:
        """评估语言质量和表达清晰度"""
        if not reasoning:
            return 0.0
            
        # 基本语言质量检查
        sentences = reasoning.split('。')
        valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        if not valid_sentences:
            return 0.0
        
        # 句子长度分布（避免过长或过短的句子）
        sentence_lengths = [len(s) for s in valid_sentences]
        avg_length = sum(sentence_lengths) / len(sentence_lengths)
        
        # 理想句子长度在20-60字之间
        if 20 <= avg_length <= 60:
            length_quality = 1.0
        elif avg_length < 20:
            length_quality = avg_length / 20
        else:
            length_quality = max(0.5, 60 / avg_length)
        
        # 表达清晰度（检查是否有清晰的表达）
        clarity_indicators = ['明确', '清楚', '显然', '可以看出', '表明', '说明', '证明']
        clarity_count = sum(1 for indicator in clarity_indicators if indicator in reasoning)
        clarity_score = min(clarity_count / 2, 1.0)
        
        # 专业性评估
        professional_terms = [
            '系统', '架构', '设计', '实现', '优化', '性能', '安全', '可维护',
            '扩展', '集成', '接口', '模块', '组件', '服务', '框架', '模式'
        ]
        professional_count = sum(1 for term in professional_terms if term in reasoning)
        professional_score = min(professional_count / 3, 1.0)
        
        # 综合语言质量得分
        language_score = length_quality * 0.4 + clarity_score * 0.3 + professional_score * 0.3
        
        return language_score
    
    def _calculate_metadata_completeness(self, qa_pairs: List[Dict], design_proposals: List[Dict]) -> float:
        """计算元数据完整性得分"""
        total_items = len(qa_pairs) + len(design_proposals)
        if total_items == 0:
            return 0.0
            
        completeness_scores = []
        
        # QA必要字段
        qa_required_fields = ['source_file', 'question_type', 'complexity_level', 'perspective', 'element_type']
        
        for qa in qa_pairs:
            metadata = qa.get('metadata', {})
            present_fields = sum(1 for field in qa_required_fields if metadata.get(field))
            completeness = present_fields / len(qa_required_fields)
            completeness_scores.append(completeness)
        
        # 设计方案必要字段  
        proposal_required_fields = ['proposal_type', 'complexity', 'generated_by']
        
        for proposal in design_proposals:
            metadata = proposal.get('metadata', {})
            present_fields = sum(1 for field in proposal_required_fields if metadata.get(field))
            completeness = present_fields / len(proposal_required_fields)
            completeness_scores.append(completeness)
        
        return round(sum(completeness_scores) / len(completeness_scores), 3)
    
    def _calculate_representativeness_score(self, qa_pairs: List[Dict], design_proposals: List[Dict]) -> float:
        """计算数据代表性得分"""
        total_items = len(qa_pairs) + len(design_proposals)
        if total_items == 0:
            return 0.0
            
        scores = []
        
        # 1. 技术栈一致性评估 (权重30%)
        tech_score = self._evaluate_tech_stack_consistency(qa_pairs, design_proposals)
        scores.append(tech_score * 0.3)
        
        # 2. 业务场景相关性评估 (权重25%)  
        business_score = self._evaluate_business_relevance(qa_pairs, design_proposals)
        scores.append(business_score * 0.25)
        
        # 3. 代码上下文准确性评估 (权重25%)
        context_score = self._evaluate_code_context_accuracy(qa_pairs)
        scores.append(context_score * 0.25)
        
        # 4. 架构模式匹配度评估 (权重20%)
        arch_score = self._evaluate_architecture_consistency(design_proposals)
        scores.append(arch_score * 0.2)
        
        return round(sum(scores), 3)
    
    def _evaluate_tech_stack_consistency(self, qa_pairs: List[Dict], design_proposals: List[Dict]) -> float:
        """评估技术栈一致性"""
        # 获取实际技术栈
        actual_tech_stack = set()
        for file_analysis in self.analysis_result['file_analysis'].values():
            imports = file_analysis.get('imports', [])
            for imp in imports:
                # 提取主要技术栈
                if 'flask' in imp.lower():
                    actual_tech_stack.add('Flask')
                elif 'jwt' in imp.lower():
                    actual_tech_stack.add('JWT')  
                elif 'redis' in imp.lower():
                    actual_tech_stack.add('Redis')
                elif 'hashlib' in imp.lower():
                    actual_tech_stack.add('bcrypt/hashlib')
        
        # 评估问答对中技术栈的匹配度
        matched_items = 0
        total_items = len(qa_pairs) + len(design_proposals)
        
        for qa in qa_pairs:
            answer = qa.get('answer', '').lower()
            context = qa.get('code_context', '').lower()
            
            # 检查是否包含实际技术栈相关内容
            if any(tech.lower() in answer or tech.lower() in context 
                   for tech in actual_tech_stack):
                matched_items += 1
        
        # 评估设计方案中技术栈的匹配度
        for proposal in design_proposals:
            description = proposal.get('description', '').lower()
            if any(tech.lower() in description for tech in actual_tech_stack):
                matched_items += 1
                
        return matched_items / max(total_items, 1)
    
    def _evaluate_business_relevance(self, qa_pairs: List[Dict], design_proposals: List[Dict]) -> float:
        """评估业务场景相关性"""
        # 获取实际业务关键词
        actual_keywords = set()
        for file_analysis in self.analysis_result['file_analysis'].values():
            keywords = file_analysis.get('business_keywords', [])
            actual_keywords.update(keywords)
        
        matched_items = 0
        total_items = len(qa_pairs) + len(design_proposals)
        
        # 评估问答对业务相关性
        for qa in qa_pairs:
            context = qa.get('code_context', '').lower()
            reasoning = qa.get('reasoning_trace', '').lower()
            
            # 检查是否包含实际业务关键词
            keywords_found = sum(1 for keyword in actual_keywords 
                               if keyword.lower() in context or keyword.lower() in reasoning)
            if keywords_found >= 2:  # 至少包含2个业务关键词
                matched_items += 1
        
        # 评估设计方案业务相关性  
        for proposal in design_proposals:
            description = proposal.get('description', '').lower()
            reasoning = proposal.get('reasoning_trace', '').lower()
            
            keywords_found = sum(1 for keyword in actual_keywords
                               if keyword.lower() in description or keyword.lower() in reasoning)
            if keywords_found >= 2:
                matched_items += 1
                
        return matched_items / max(total_items, 1)
    
    def _evaluate_code_context_accuracy(self, qa_pairs: List[Dict]) -> float:
        """评估代码上下文准确性"""
        accurate_items = 0
        
        for qa in qa_pairs:
            metadata = qa.get('metadata', {})
            source_file = metadata.get('source_file', '')
            function_name = metadata.get('function_name', '')
            
            # 检查引用的文件是否存在于分析结果中
            if source_file and source_file in self.analysis_result['file_analysis']:
                file_analysis = self.analysis_result['file_analysis'][source_file]
                
                # 检查引用的函数是否存在
                if function_name:
                    functions = file_analysis.get('functions', [])
                    function_names = [f.get('name') for f in functions]
                    if function_name in function_names:
                        accurate_items += 1
                else:
                    # 没有具体函数名但文件存在，算部分准确
                    accurate_items += 0.5
                    
        return accurate_items / max(len(qa_pairs), 1)
    
    def _evaluate_architecture_consistency(self, design_proposals: List[Dict]) -> float:
        """评估架构模式匹配度"""
        if not design_proposals:
            return 1.0
            
        # 获取实际架构模式
        actual_patterns = [k for k, v in self.analysis_result['architecture_patterns'].items() if v]
        
        consistent_proposals = 0
        for proposal in design_proposals:
            description = proposal.get('description', '').lower()
            reasoning = proposal.get('reasoning_trace', '').lower()
            
            # 检查设计方案是否符合现有架构模式
            if any(pattern.lower() in description or pattern.lower() in reasoning 
                   for pattern in actual_patterns):
                consistent_proposals += 1
            
        return consistent_proposals / len(design_proposals)
    
    def _load_qa_pairs(self) -> List[Dict[str, Any]]:
        """加载问答对"""
        try:
            with open(self.output_dir / 'qa_pairs.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    
    def _load_design_proposals(self) -> List[Dict[str, Any]]:
        """加载设计方案"""
        try:
            with open(self.output_dir / 'design_proposals.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Claude AI驱动的智能训练数据生成系统')
    parser.add_argument('--repo-path', required=True, help='要分析的代码仓库路径')
    parser.add_argument('--output-dir', default='./output', help='输出目录 (默认: ./output)')
    parser.add_argument('--num-qa-pairs', type=int, default=50, help='生成问答对数量 (默认: 50)')
    parser.add_argument('--num-design-proposals', type=int, default=10, help='生成设计方案数量 (默认: 10)')
    parser.add_argument('--claude-api-key', help='Claude API密钥 (也可使用环境变量 ANTHROPIC_API_KEY)')
    parser.add_argument('--requirements', nargs='+', help='自定义需求列表')
    
    args = parser.parse_args()
    
    # 获取Claude API密钥
    claude_api_key = claude_api_key
    if not claude_api_key:
        print(" 错误: 需要提供Claude API密钥")
        print(" 方法1: --claude-api-key 'your-api-key'")
        print(" 方法2: export ANTHROPIC_API_KEY='your-api-key'")
        return
    
    # 验证仓库路径
    if not Path(args.repo_path).exists():
        print(f" 错误: 仓库路径不存在: {args.repo_path}")
        return
    
    try:
        # 创建生成器
        generator = TrainingDataGenerator(
            repo_path=args.repo_path,
            output_dir=args.output_dir,
            claude_api_key=claude_api_key
        )
        
        # 运行生成流水线
        results = generator.run_full_pipeline(
            num_qa_pairs=args.num_qa_pairs,
            num_design_proposals=args.num_design_proposals,
            custom_requirements=args.requirements
        )
        
        print("\n 生成完成!")
        print("\n 生成的文件:")
        for file_type, file_path in results.items():
            if Path(file_path).exists():
                file_size = Path(file_path).stat().st_size
                print(f"    {file_type}: {file_path} ({file_size:,} bytes)")
        
        print(f"\n 主要文件: {results['training_dataset']}")
        print(" 这个文件包含了用于模型训练的标准格式数据")
        
    except Exception as e:
        print(f" 系统运行出错: {e}")
        print(" 请检查API密钥是否正确，网络连接是否正常")


if __name__ == "__main__":
    main()
