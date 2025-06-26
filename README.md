# 智能训练数据生成系统

##  项目概述

本项目是一个基于AI的智能训练数据生成系统，专门为Qwen 2.5系列模型微调提供高质量训练数据。系统能够自动分析任何GitHub公开代码仓库，生成涵盖业务流程、规则问答和架构设计方案的训练数据集。

##  核心功能

### 场景1：智能问答对生成
- 自动分析代码仓库结构和业务逻辑
- 生成高质量问答对，包含完整推理过程
- 支持多种问题类型：最佳实践、使用方法、架构设计、业务逻辑
- 提供代码上下文和元数据

### 场景2：架构设计方案生成
- 基于现有代码架构生成设计方案
- 包含技术方案、实施步骤、收益分析
- 提供详细的推理trace和验收标准
- 支持增强、重构、新功能、迁移等方案类型

##  系统架构

```
智能训练数据生成系统
├── smart_defaults.py     # 自动计算合适的问答对数量
├── src/                     # 核心代码
│   ├── main.py             # 主程序入口
│   ├── code_analyzer.py    # 代码分析器
│   ├── qa_generator.py     # 问答生成器
│   └── design_generator.py # 设计生成器
├── output/                 # 输出示例
│   ├── analysis_report.json # 代码仓分析报告
│   ├── qa_pairs.json       # 问答对数据集
│   ├── design_proposals.json # 设计方案集
│   ├── training_dataset.jsonl # 标准训练格式
│   ├── comprehensive_report.json # 质量评估报告
│   └── design_document.md  # 详细设计文档
└── requirements.txt        # 依赖配置
```

##  快速开始

### 1. 环境配置
```bash
# 安装依赖
pip install -r requirements.txt

# 设置API密钥
export ANTHROPIC_API_KEY="your-api-key-here"
```

### 2. 基本使用
```bash
# 生成问答对和设计方案
python src/main.py --repo-path ./your-repo --num-qa-pairs 50 --num-design-proposals 10

# 使用在线GitHub仓库
python src/main.py --repo-path https://github.com/user/repo --num-qa-pairs 20 --num-design-proposals 5
```

### 3. 高级配置
```bash
# 自定义需求和详细输出
python src/main.py \
  --repo-path ./your-repo \
  --num-qa-pairs 100 \
  --num-design-proposals 20 \
  --requirements "API安全" "性能优化" "监控系统" \
  --output-dir ./custom-output \
  --verbose
```

##  质量评估体系

本系统提供5个维度的质量评估指标：

### 1. 数据多样性得分 (0-1)
- 基于信息论香农熵计算
- 评估问题类型、复杂度、视角的分布均匀性


### 2. 代码覆盖率得分 (0-1)
- 评估训练数据对代码库的覆盖广度，通常情况下与QA生成数量成正比
- 包含文件、函数、类的覆盖率


### 3. 推理质量得分 (0-1)
- 评估推理过程的逻辑性、相关性、深度
- 结合Chain-of-Thought评估框架


### 4. 元数据完整性得分 (0-1)
- 评估必要字段的完整程度
- 确保数据结构的规范性


### 5. 数据代表性得分 (0-1)
- 评估生成数据与实际代码库特征的一致性
- 验证技术栈、业务场景的匹配度


## 输出格式

### 问答对格式（qa_pairs.json）
```json
{
  "question": "如何在Flask应用中实现JWT认证？",
  "answer": "详细的实现步骤和最佳实践...",
  "code_context": "相关代码片段和上下文",
  "reasoning_trace": "详细的推理过程",
  "metadata": {
    "source_file": "src/auth.py",
    "question_type": "best_practices",
    "complexity_level": "intermediate",
    "perspective": "developer"
  }
}
```

### 设计方案格式（design_proposals.json）
```json
{
  "title": "API安全增强方案",
  "description": "详细的方案描述...",
  "technical_approach": "技术实现方案...",
  "implementation_steps": ["步骤1", "步骤2", "..."],
  "benefits": ["收益1", "收益2", "..."],
  "challenges_and_solutions": ["挑战及解决方案..."],
  "acceptance_criteria": ["验收标准..."],
  "reasoning_trace": "详细的分析推理过程..."
}
```

### 标准训练格式（training_dataset.jsonl）
```json
{"prompt": "问题内容", "completion": "回答内容", "metadata": {...}}
```

##  如何满足评判标准

### 1. 数据集场景覆盖和逻辑正确性 
- **场景1覆盖**：自动生成业务流程和规则问答对，包含完整推理过程
- **场景2覆盖**：基于代码架构生成设计方案，提供详细推理trace
- **逻辑正确性**：通过推理质量得分的逻辑结构完整性评估保证

### 2. 数据处理方法有效性和创新性 
- **创新方法**：
  - 基于信息论香农熵的多样性量化评估
  - 结合Chain-of-Thought的推理质量评估框架
  - 代码分析器+LLM增强的混合生成策略
- **有效性保证**：
  - 5维度质量评估体系确保数据质量
  - 自动化生成流程提高效率
  - 智能采样策略确保代表性

### 3. 系统架构完整性和可扩展性 
- **完整性**：
  - 模块化设计：CodeAnalyzer、QAGenerator、DesignGenerator
  - 完整的输入处理、数据生成、质量评估流程
  - 支持多种输出格式和配置选项
- **可扩展性**：
  - 插件化架构支持新语言和框架
  - 配置化管理支持自定义策略
  - 模板化生成支持个性化需求

### 4. 推理trace数据质量 
- **清晰度**：
  - 结构化推理过程：现状分析→问题识别→方案选择→实施策略
  - 技术选型理由和风险评估
  - 具体可执行的实施步骤
- **合规性**：
  - 推理质量得分专门评估reasoning_trace质量
  - 多维度评估：逻辑结构、内容相关性、深度分析
  - 自动化质量控制和阈值管理

##  技术特色

### 多样性与代表性平衡
- **代表性**：通过CodeAnalyzer提取真实代码特征
- **多样性**：通过Claude AI生成多角度、多类型内容
- **质量控制**：5维度评估体系确保数据质量

### 智能生成策略
- **自适应采样**：基于代码复杂度智能选择重要元素
- **多策略生成**：函数级、类级、业务规则级、架构级
- **质量优先**：质量不达标自动重新生成

### 企业级特性
- **批量处理**：支持大规模代码仓库处理
- **错误恢复**：智能错误处理和重试机制
- **扩展性**：模块化设计支持功能扩展

##  使用示例

### 示例1：分析Flask项目
```bash
python src/main.py \
  --repo-path https://github.com/pallets/flask \
  --num-qa-pairs 30 \
  --num-design-proposals 10 \
  --output-dir ./flask-analysis
```

### 示例2：自定义需求生成
```bash
python src/main.py \
  --repo-path ./my-project \
  --requirements "微服务架构" "容器化部署" "监控告警" \
  --num-qa-pairs 50 \
  --num-design-proposals 15
```

##  依赖要求

- Python 3.8+
- anthropic>=0.18.0
- pathlib
- typing-extensions>=4.0.0

##  贡献指南

1. Fork项目
2. 创建功能分支
3. 提交改动
4. 推送到分支
5. 创建Pull Request

##  许可证

本项目采用MIT许可证。

##  联系方式

如有问题或建议，请通过以下方式联系：
- 项目Issues
- 邮件咨询

---

**版本**: 1.0  
**更新日期**: 2025-06-26  
**维护者**: AI训练数据生成系统团队