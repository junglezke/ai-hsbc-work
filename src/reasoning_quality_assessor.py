"""
推理质量评估器 - 专门评估生成的reasoning_trace质量
"""
import json
import re
from typing import Dict, List, Any, Tuple
from collections import Counter


class ReasoningQualityAssessor:
    """推理质量评估器"""
    
    def __init__(self):
        self.quality_frameworks = self._load_quality_frameworks()
        
    def _load_quality_frameworks(self) -> Dict[str, Dict[str, Any]]:
        """加载不同类型内容的质量评估框架"""
        return {
            'qa_function': {
                'min_length': 150,
                'required_elements': ['问题分析', '技术考察', '深度推理', '实践洞察'],
                'quality_indicators': [
                    '分析', '考虑', '评估', '推理', '因为', '所以',
                    '背景', '原因', '影响', '优势', '劣势', '方案',
                    '设计', '架构', '模式', '原则', '实践'
                ],
                'structure_patterns': ['1.', '2.', '3.', '首先', '其次', '最后', '步骤', '阶段']
            },
            'qa_class': {
                'min_length': 200,
                'required_elements': ['设计意图', '架构模式', '职责边界', '依赖关系', '扩展性', '最佳实践'],
                'quality_indicators': [
                    '设计', '架构', '模式', '职责', '耦合', '扩展',
                    '维护', '原则', '分析', '评估', '考虑'
                ],
                'structure_patterns': ['1.', '2.', '3.', '**', 'SOLID', '单一职责']
            },
            'qa_business': {
                'min_length': 180,
                'required_elements': ['业务背景', '规则逻辑', '业务价值', '影响范围', '异常情况', '优化建议'],
                'quality_indicators': [
                    '业务', '规则', '逻辑', '价值', '流程', '影响',
                    '异常', '处理', '优化', '建议', '分析'
                ],
                'structure_patterns': ['1.', '2.', '3.', '业务', '流程', '规则']
            },
            'qa_architecture': {
                'min_length': 220,
                'required_elements': ['架构模式', '设计原则', '可扩展性', '性能影响', '维护性', '演进策略'],
                'quality_indicators': [
                    '架构', '模式', '设计', '原则', '扩展', '性能',
                    '维护', '演进', '系统', 'SOLID', 'DRY', 'KISS'
                ],
                'structure_patterns': ['1.', '2.', '3.', 'SOLID', '水平扩展', '垂直扩展']
            },
            'design_enhancement': {
                'min_length': 400,
                'required_elements': ['现状分析', '问题识别', '方案对比', '技术选型', '风险评估', '实施策略', '成功标准'],
                'quality_indicators': [
                    '现状', '分析', '问题', '根因', '方案', '对比', '选择',
                    '技术', '风险', '评估', '实施', '策略', '标准', '考量',
                    '优势', '劣势', '缓解', '措施', '指标', '架构'
                ],
                'structure_patterns': ['1.', '2.', '3.', '**', '现状', '问题', '方案', '技术', '风险']
            }
        }
    
    def assess_reasoning_quality(self, content: Dict[str, Any], content_type: str) -> Dict[str, Any]:
        """评估单个内容的推理质量"""
        reasoning = content.get('reasoning_trace', '')
        framework = self.quality_frameworks.get(content_type, self.quality_frameworks['qa_function'])
        
        # 1. 长度评估
        length_score = min(len(reasoning) / framework['min_length'], 1.0)
        
        # 2. 质量指标评估
        quality_score = self._assess_quality_indicators(reasoning, framework['quality_indicators'])
        
        # 3. 结构化评估
        structure_score = self._assess_structure(reasoning, framework['structure_patterns'])
        
        # 4. 元素完整性评估
        completeness_score = self._assess_completeness(reasoning, framework['required_elements'])
        
        # 5. 逻辑连贯性评估
        coherence_score = self._assess_coherence(reasoning)
        
        # 综合得分
        overall_score = (
            length_score * 0.15 +
            quality_score * 0.25 +
            structure_score * 0.20 +
            completeness_score * 0.25 +
            coherence_score * 0.15
        )
        
        return {
            'overall_score': round(overall_score, 3),
            'length_score': round(length_score, 3),
            'quality_score': round(quality_score, 3),
            'structure_score': round(structure_score, 3),
            'completeness_score': round(completeness_score, 3),
            'coherence_score': round(coherence_score, 3),
            'reasoning_length': len(reasoning),
            'required_length': framework['min_length'],
            'passes_threshold': overall_score >= 0.7
        }
    
    def _assess_quality_indicators(self, reasoning: str, indicators: List[str]) -> float:
        """评估质量指标词汇的使用"""
        if not reasoning:
            return 0.0
        
        found_indicators = sum(1 for indicator in indicators if indicator in reasoning)
        return min(found_indicators / len(indicators), 1.0)
    
    def _assess_structure(self, reasoning: str, patterns: List[str]) -> float:
        """评估结构化程度"""
        if not reasoning:
            return 0.0
        
        structure_count = sum(1 for pattern in patterns if pattern in reasoning)
        return min(structure_count / 3, 1.0)  # 至少需要3个结构化元素
    
    def _assess_completeness(self, reasoning: str, required_elements: List[str]) -> float:
        """评估必要元素的完整性"""
        if not reasoning:
            return 0.0
        
        # 检查是否包含必要的分析元素
        element_count = 0
        for element in required_elements:
            # 使用更灵活的匹配策略
            if element in reasoning or any(word in reasoning for word in element.split()):
                element_count += 1
        
        return element_count / len(required_elements)
    
    def _assess_coherence(self, reasoning: str) -> float:
        """评估逻辑连贯性"""
        if not reasoning:
            return 0.0
        
        # 检查逻辑连接词
        logical_connectors = [
            '因为', '所以', '由于', '因此', '然而', '但是', '并且',
            '同时', '首先', '其次', '最后', '综上', '总结', '基于'
        ]
        
        connector_count = sum(1 for connector in logical_connectors if connector in reasoning)
        
        # 检查句子完整性（通过标点符号）
        sentences = len([s for s in re.split(r'[。！？.]', reasoning) if s.strip()])
        
        # 逻辑连贯性得分
        if sentences == 0:
            return 0.0
        
        connector_ratio = min(connector_count / max(sentences / 3, 1), 1.0)
        
        return connector_ratio
    
    def generate_quality_report(self, qa_pairs: List[Dict[str, Any]], 
                              design_proposals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成整体质量报告"""
        
        # 评估QA pairs
        qa_scores = []
        qa_type_scores = {}
        
        for qa in qa_pairs:
            element_type = qa.get('metadata', {}).get('element_type', 'function')
            content_type = f'qa_{element_type}'
            
            score_result = self.assess_reasoning_quality(qa, content_type)
            qa_scores.append(score_result)
            
            if content_type not in qa_type_scores:
                qa_type_scores[content_type] = []
            qa_type_scores[content_type].append(score_result['overall_score'])
        
        # 评估Design proposals
        design_scores = []
        for proposal in design_proposals:
            proposal_type = proposal.get('type', 'enhancement')
            content_type = f'design_{proposal_type}'
            
            score_result = self.assess_reasoning_quality(proposal, content_type)
            design_scores.append(score_result)
        
        # 统计分析
        overall_qa_score = sum(s['overall_score'] for s in qa_scores) / len(qa_scores) if qa_scores else 0
        overall_design_score = sum(s['overall_score'] for s in design_scores) / len(design_scores) if design_scores else 0
        
        # 质量等级分布
        qa_quality_distribution = self._get_quality_distribution([s['overall_score'] for s in qa_scores])
        design_quality_distribution = self._get_quality_distribution([s['overall_score'] for s in design_scores])
        
        # 不达标内容统计
        failing_qa_count = sum(1 for s in qa_scores if not s['passes_threshold'])
        failing_design_count = sum(1 for s in design_scores if not s['passes_threshold'])
        
        return {
            'overall_summary': {
                'total_qa_pairs': len(qa_pairs),
                'total_design_proposals': len(design_proposals),
                'overall_qa_score': round(overall_qa_score, 3),
                'overall_design_score': round(overall_design_score, 3),
                'combined_score': round((overall_qa_score + overall_design_score) / 2, 3)
            },
            'qa_analysis': {
                'average_score': round(overall_qa_score, 3),
                'quality_distribution': qa_quality_distribution,
                'failing_count': failing_qa_count,
                'failing_rate': round(failing_qa_count / len(qa_scores), 3) if qa_scores else 0,
                'type_breakdown': {k: round(sum(v) / len(v), 3) for k, v in qa_type_scores.items()}
            },
            'design_analysis': {
                'average_score': round(overall_design_score, 3),
                'quality_distribution': design_quality_distribution,
                'failing_count': failing_design_count,
                'failing_rate': round(failing_design_count / len(design_scores), 3) if design_scores else 0
            },
            'detailed_scores': {
                'qa_detailed': qa_scores,
                'design_detailed': design_scores
            },
            'recommendations': self._generate_recommendations(
                overall_qa_score, overall_design_score, 
                failing_qa_count, failing_design_count
            )
        }
    
    def _get_quality_distribution(self, scores: List[float]) -> Dict[str, int]:
        """获取质量等级分布"""
        if not scores:
            return {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        distribution = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
        
        for score in scores:
            if score >= 0.9:
                distribution['excellent'] += 1
            elif score >= 0.8:
                distribution['good'] += 1
            elif score >= 0.7:
                distribution['fair'] += 1
            else:
                distribution['poor'] += 1
        
        return distribution
    
    def _generate_recommendations(self, qa_score: float, design_score: float, 
                                failing_qa: int, failing_design: int) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if qa_score < 0.7:
            recommendations.append("QA推理质量偏低，建议优化prompt中的推理框架指导")
        
        if design_score < 0.7:
            recommendations.append("设计方案推理质量偏低，建议增强架构分析的深度要求")
        
        if failing_qa > 0:
            recommendations.append(f"有{failing_qa}个QA对的推理质量不达标，建议重新生成")
        
        if failing_design > 0:
            recommendations.append(f"有{failing_design}个设计方案的推理质量不达标，建议重新生成")
        
        if qa_score >= 0.8 and design_score >= 0.8:
            recommendations.append("推理质量整体良好，可考虑进一步提升复杂度和深度")
        
        return recommendations
    
    def save_quality_report(self, report: Dict[str, Any], output_path: str):
        """保存质量报告"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"推理质量报告已保存到: {output_path}")
