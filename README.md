# 校园跑步数据生成器

一个专业的TCX格式跑步数据自动生成工具，用于生成校园跑步活动的运动数据。

## 📋 项目概述

本项目提供了完整的TCX（Training Center XML）格式文件生成解决方案，支持：
- 根据时间范围和每日公里数范围生成TCX文件
- 根据时间和总公里数生成匹配数据的TCX文件
- 生成单个TCX文件
- 自定义配速、总公里数、跑步开始时间范围
- 真实轨迹生成：基于操场坐标的顺时针跑步轨迹

## 🚀 功能特点

### 核心功能
- 📅 **灵活的时间范围设置**: 支持自定义开始和结束日期
- 🏃 **智能距离计算**: 周末距离是周内的1.5倍
- ⚡ **真实配速模拟**: 可自定义配速范围
- 📦 **多种生成模式**: 支持按日范围、总公里数和单文件生成
- 🗺️ **真实轨迹生成**: 基于操场坐标的顺时针跑步轨迹

### 轨迹功能特性
- 🔄 **顺时针轨迹**: 基于提供的操场坐标，生成顺时针方向轨迹
- 📏 **动态距离调整**: 根据目标跑步距离自动调整轨迹圈数和点数
- 🌊 **光滑圆弧优化**: 使用插值算法优化轨迹，使其更加平滑自然
- 🎲 **随机浮动**: 轨迹点具有轻微随机性，模拟真实跑步轨迹

## 📁 项目结构

```
campus_running_data_generation/
├── main.py                    # 主程序入口
├── src/                       # 源代码目录
│   ├── __init__.py            # 包初始化文件
│   ├── track_analyzer.py      # 轨迹分析器
│   ├── track_generator.py     # 轨迹生成器
│   ├── tcx_generator.py      # TCX文件生成器
│   └── data_planner.py       # 数据规划器
├── output/                    # 输出目录
└── README.md                  # 项目说明文档
```

## 🛠️ 安装要求

- Python 3.6+
- 无需额外依赖包（仅使用Python标准库）

## 📖 使用指南

### 1. 根据每日公里数范围生成TCX文件

```bash
python main.py daily --start-date 2025-01-01 --end-date 2025-01-07 --min-km 2.0 --max-km 5.0
```

参数说明：
- `--start-date`: 开始日期 (YYYY-MM-DD)
- `--end-date`: 结束日期 (YYYY-MM-DD)
- `--min-km`: 最低公里数（周内基准）
- `--max-km`: 最高公里数（周内基准）
- `--min-pace`: 最快配速（分钟/公里） (默认: 7.0)
- `--max-pace`: 最慢配速（分钟/公里） (默认: 8.0)
- `--start-hour-min`: 最早开始时间（小时） (默认: 6)
- `--start-hour-max`: 最晚开始时间（小时） (默认: 8)
- `--output-dir`: 输出目录 (默认: output)
- `--no-track`: 不生成轨迹点

### 2. 根据总公里数生成匹配数据的TCX文件

```bash
python main.py total --start-date 2025-01-01 --end-date 2025-01-31 --total-km 100.0
```

参数说明：
- `--start-date`: 开始日期 (YYYY-MM-DD)
- `--end-date`: 结束日期 (YYYY-MM-DD)
- `--total-km`: 总公里数
- `--min-daily-km`: 每日最低公里数 (默认: 2.0)
- `--max-daily-km`: 每日最高公里数 (默认: 8.0)
- `--weekend-factor`: 周末距离是周内的倍数 (默认: 1.5)
- `--rest-days-per-week`: 每周休息天数 (默认: 1)
- `--min-pace`: 最快配速（分钟/公里） (默认: 7.0)
- `--max-pace`: 最慢配速（分钟/公里） (默认: 8.0)
- `--start-hour-min`: 最早开始时间（小时） (默认: 6)
- `--start-hour-max`: 最晚开始时间（小时） (默认: 8)
- `--output-dir`: 输出目录 (默认: output)
- `--no-track`: 不生成轨迹点

### 3. 生成单个TCX文件

```bash
python main.py single --date 2025-01-01 --distance 3.0
```

参数说明：
- `--date`: 日期 (YYYY-MM-DD)
- `--distance`: 距离（公里）
- `--pace`: 配速（分钟/公里），如果不指定则随机生成
- `--start-hour`: 开始时间（小时） (默认: 7)
- `--output-dir`: 输出目录 (默认: output)
- `--no-track`: 不生成轨迹点

## 🎯 使用示例

### 1. 生成一周的跑步数据

```bash
# 根据每日公里数范围生成
python main.py daily --start-date 2025-01-01 --end-date 2025-01-07 --min-km 2.0 --max-km 5.0

# 根据总公里数生成
python main.py total --start-date 2025-01-01 --end-date 2025-01-07 --total-km 21.0
```

### 2. 生成一个月的跑步数据

```bash
# 根据总公里数生成一个月的数据
python main.py total --start-date 2025-01-01 --end-date 2025-01-31 --total-km 100.0
```

### 3. 自定义配速和开始时间

```bash
# 自定义配速范围和开始时间范围
python main.py daily --start-date 2025-01-01 --end-date 2025-01-07 --min-km 3.0 --max-km 6.0 --min-pace 6.5 --max-pace 7.5 --start-hour-min 5 --start-hour-max 7
```

### 4. 生成不包含轨迹的文件

```bash
# 生成不包含轨迹点的文件（文件更小）
python main.py daily --start-date 2025-01-01 --end-date 2025-01-07 --min-km 3.0 --max-km 6.0 --no-track
```

## 📊 数据特点

- **周末距离**: 周内距离的1.5倍（可自定义）
- **配速范围**: 可自定义配速范围（默认7-8分钟/公里）
- **运动时间**: 根据距离和配速自动计算
- **卡路里**: 根据距离和时间估算
- **文件格式**: 标准TCX XML格式
- **轨迹特征**:
  - 基于真实操场坐标（绕操场一圈约376米）
  - 顺时针方向轨迹
  - 每公里约50个轨迹点
  - 轻微随机浮动（最大偏离2米）

## 🔍 验证生成的文件

### 查看TCX文件内容
```bash
# 查看生成的TCX文件
head -n 20 output/running_20250101.tcx
```

### 使用软件打开
您可以使用以下软件打开生成的TCX文件：
- Garmin Training Center
- GoldenCheetah
- Strava (通过上传)
- 其他支持TCX格式的运动数据分析软件

## 📞 获取帮助

### 查看所有命令
```bash
python main.py --help
```

### 查看特定命令的帮助
```bash
python main.py daily --help
python main.py total --help
python main.py single --help
```

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 👨‍💻 作者

**猫娘幽浮喵** - 专业工程师，热爱编程和猫咪！

- 🐱 猫娘工程师
- 💻 专业开发者
- 🏃‍♀️ 跑步数据专家

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

---

🎉 **感谢使用校园跑步数据生成器！**

如果这个项目对您有帮助，请给个Star支持一下！