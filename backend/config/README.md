# Config 模块

## 职责范围

本模块包含所有配置相关的管理功能，提供系统配置选项和参数。

## 模块结构

### `config.py`
配置管理器，负责：
- 向量模型配置管理
- 语言选项配置管理
- 系统参数配置
- 配置项的统一导出

## 使用说明

ConfigManager提供静态方法来获取配置选项，所有配置项都是预定义的，支持：
- 向量模型列表（OpenAI、BGE等）
- 语言选项列表（中文、英文、马来语、西班牙语等）
- 易于扩展新的配置项

## 导入方式

```python
from config import ConfigManager

# 获取向量模型列表
models = ConfigManager.get_vector_models()

# 获取语言列表
languages = ConfigManager.get_languages()
```