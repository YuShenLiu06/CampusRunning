# 校园跑步数据生成器

**版本 2.0.0** - 重构发布

Keep校园跑的终极方案，理论上支持所有支持导入tcx文件的运动软件

一个专业的TCX格式跑步数据自动生成工具，支持CLI和Web两种使用方式。

## 简述

作者深陷 gzu 校园跑侵扰，同时发现社区中大部分为基于虚拟定位的解决方案，不能满足我本身要求，故开发了这个工具并开源。

## 文件使用方法

见 [数据生成后使用指南](guied.md)

## 项目概述

本项目提供完整的TCX（Training Center XML）格式文件生成解决方案，支持：
- 根据时间范围和每日公里数范围生成TCX文件
- 根据时间和总公里数生成匹配数据的TCX文件
- 生成单个TCX文件
- 自定义配速、总公里数、跑步开始时间范围
- 真实轨迹生成：基于操场坐标的顺时针跑步轨迹

## 功能特点

### 核心功能
- 灵活的时间范围设置：支持自定义开始和结束日期
- 智能距离计算：周末距离是周内的1.5倍
- 真实配速模拟：可自定义配速范围，支持配速波动
- 多种生成模式：支持按日范围、总公里数和单文件生成
- 真实轨迹生成：基于操场坐标的顺时针跑步轨迹

### 扩展功能
- **多轨迹支持**：通过JSON配置文件定义多条轨迹
- **预设模板**：保存常用配置为模板，一键应用
- **Web界面**：浏览器可视化操作，无需记忆CLI参数
- **坐标修正**：修正GPS系统性偏移
- **配速波动**：4阶段真实配速模拟

## 项目结构

```
campus_running_data_generation/
├── main.py                      # CLI入口
├── app.py                      # Web应用入口
├── config/                      # 配置文件
│   ├── tracks/                 # 轨迹定义
│   │   └── campus_default.json
│   ├── templates/            # 预设模板
│   │   ├── easy_run.json
│   │   ├── long_run.json
│   │   └── interval.json
│   └── default_settings.json  # 默认设置
├── src/                       # 源代码
│   ├── core/                  # 核心模块
│   │   ├── __init__.py
│   │   ├── models.py         # 数据模型
│   │   ├── track_analyzer.py # 轨迹分析
│   │   ├── track_generator.py # 轨迹生成
│   │   ├── pace_fluctuator.py # 配速波动
│   │   ├── coordinate_corrector.py # 坐标修正
│   │   └── helpers.py        # 工具函数
│   ├── planners/            # 规划策略
│   │   ├── __init__.py
│   │   ├── daily_planner.py # 每日范围规划
│   │   ├── total_km_planner.py # 总公里数规划
│   │   └── single_planner.py # 单文件规划
│   ├── exporters/            # 导出格式
│   │   ├── __init__.py
│   │   ├── base.py          # 导出器基类
│   │   └── tcx_exporter.py  # TCX导出
│   ├── config_manager.py     # 配置管理
│   ├── template_manager.py   # 模板管理
│   └── generation_engine.py  # 生成引擎
├── web/                      # Web应用
│   ├── routes.py             # API路由
│   ├── templates/            # HTML模板
│   └── static/               # 静态资源
├── docs/                     # 文档
│   ├── architecture.md
│   ├── track_format.md
│   └── api_reference.md
└── output/                  # 生成文件输出
```

## 安装

```bash
# CLI版本（无需额外依赖）
python main.py --help

# Web界面（需要安装Flask）
pip install flask
python app.py
```

## 快速开始

### CLI模式

```bash
# 列出可用轨迹和模板
python main.py --list-tracks
python main.py --list-templates

# 每日范围生成
python main.py daily --start-date 2025-01-01 --end-date 2025-01-07 --min-km 2 --max-km 5

# 总公里数生成
python main.py total --start-date 2025-01-01 --end-date 2025-01-31 --total-km 100

# 单文件生成
python main.py single --date 2025-01-01 --distance 5.0

# 使用模板
python main.py daily --template easy_run --start-date 2025-01-01 --end-date 2025-01-07 --min-km 2 --max-km 5

# 指定轨迹
python main.py single --track campus_default --date 2025-01-01 --distance 5.0
```

### Web模式

```bash
pip install flask
python app.py
```

然后访问 http://127.0.0.1:5000

## 配置说明

### 添加新轨迹

在 `config/tracks/` 创建新JSON文件：

```json
{
  "id": "my_track",
  "name": "我的轨迹",
  "description": "操场跑道",
  "base_coordinates": [
    {"longitude": 106.6591, "latitude": 26.4513},
    {"longitude": 106.6590, "latitude": 26.4516}
  ],
  "coordinate_correction": {
    "current_center": {"longitude": 106.6594, "latitude": 26.4518},
    "target_center": {"longitude": 106.6630, "latitude": 26.4482}
  }
}
```

### 创建模板

模板用于保存和复用配置，支持多模式配置（每日范围/总公里数/单文件）。

**在Web界面中创建：**
1. 填写好表单配置
2. 点击"导出模板"按钮
3. 在弹出窗口中输入模板名称
4. 点击"导出"下载 JSON 文件

**在 config/templates/ 中创建：**
```json
{
  "id": "my_template",
  "name": "我的模板",
  "description": "日常训练",
  "track_id": "",
  "daily_config": {
    "min_pace": 6.5,
    "max_pace": 7.5,
    "min_km": 2.0,
    "max_km": 5.0,
    "enable_pace_fluctuation": true
  },
  "total_config": {
    "min_pace": 6.5,
    "max_pace": 7.5,
    "total_km": 50,
    "weekend_factor": 1.5,
    "min_daily_km": 2.0,
    "max_daily_km": 8.0,
    "rest_days_per_week": 1,
    "enable_pace_fluctuation": true
  }
}
```

详细说明请参考 [模板创建指南](config/templates/TEMPLATE_GUIDE.md)。

## 文档

- [架构说明](docs/architecture.md)
- [轨迹配置格式](docs/track_format.md)
- [API参考](docs/api_reference.md)

## 验证生成的文件

生成的文件可在以下软件中打开：
- Garmin Training Center
- GoldenCheetah
- Strava（上传）
- 其他支持TCX格式的运动数据分析软件

## 作者

YuShen

> 如果喜欢，那么点亮个start吧！✨，这对我很重要！如果有任何问题或建议，欢迎提交issue或PR！😊