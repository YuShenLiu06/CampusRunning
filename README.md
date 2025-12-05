# 校园跑步数据生成器

一个专业的TCX格式跑步数据自动生成工具，用于生成校园跑步活动的运动数据。

## 📋 项目概述

本项目提供了完整的TCX（Training Center XML）格式文件生成解决方案，支持：
- 按时间范围生成跑步数据
- 月度数据生成
- 周末/周内差异化距离设置
- 自动压缩打包
- **🆕 真实轨迹生成：基于操场坐标的顺时针跑步轨迹**
- 智能轨迹点生成：根据距离动态调整轨迹密度
- 轨迹随机浮动：模拟真实跑步轨迹，包含轻微随机偏移

## 🚀 功能特点

### 核心功能
- 📅 **灵活的时间范围设置**: 支持自定义开始和结束日期
- 🏃 **智能距离计算**: 周末距离是周内的1.5倍
- ⚡ **真实配速模拟**: 7-8分钟/公里随机生成
- 📦 **自动压缩打包**: 每个压缩包不超过500MB
- 🗺️ **真实轨迹生成**: 基于操场坐标的顺时针跑步轨迹

### 轨迹功能特性
- 🔄 **顺时针轨迹**: 基于提供的操场坐标，生成顺时针方向轨迹
- 📏 **动态距离调整**: 根据目标跑步距离自动调整轨迹圈数和点数
- 🌊 **光滑圆弧优化**: 使用插值算法优化轨迹，使其更加平滑自然
- 🎲 **随机浮动**: 轨迹点具有轻微随机性，模拟真实跑步轨迹

### 特色功能
- 🌐 **中文支持**: 完美解决Windows控制台中文乱码问题
- 📊 **月度生成器**: 按月生成50-65公里范围的跑步数据
- 🎯 **精确控制**: 支持目标总里程的精确分配
- 🔧 **参数计算**: 自动计算最优的生成参数

## 📁 项目文件结构

```
campus_running_data_generation/
├── README.md                    # 项目说明文档
├── QUICKSTART.md                # 快速开始指南
├── tcx_generator.py            # 主要TCX生成器（已集成轨迹功能）
├── monthly_generator.py         # 月度数据生成器（已集成轨迹功能）
├── track_generator.py          # 轨迹生成器核心模块 🆕
├── track_analyzer.py           # 轨迹分析器，分析操场坐标特征 🆕
├── calculate_params.py          # 参数计算工具
├── example_usage.py            # 基础使用示例
├── track_example_usage.py       # 轨迹功能使用示例 🆕
├── test_track_functionality.py # 轨迹功能测试脚本 🆕
├── test_single_file.py         # 单文件测试工具
├── monthly_data/              # 月度数据输出目录
│   ├── 2025_09/             # 9月数据
│   ├── 2025_10/             # 10月数据
│   └── 2025_11/             # 11月数据
├── running_data_2025/         # 其他生成数据
└── example_output/            # 示例输出
```

## 🛠️ 安装要求

- Python 3.6+
- 无需额外依赖包（仅使用Python标准库）

## 📖 使用指南

### 1. 基本TCX生成

生成指定时间范围的跑步数据：

```bash
# 生成带轨迹的TCX文件（默认）
python tcx_generator.py --start-date 2025-01-01 --end-date 2025-01-31 --min-km 3.0

# 生成不带轨迹的TCX文件
python tcx_generator.py --start-date 2025-01-01 --end-date 2025-01-31 --min-km 3.0 --no-track
```

### 2. 月度数据生成

按月生成50-65公里范围的跑步数据：

```bash
python monthly_generator.py
```

### 3. 参数计算

计算达到目标总里程所需的最优参数：

```bash
python calculate_params.py
```

### 4. 快速测试

生成单个测试文件验证功能：

```bash
python test_single_file.py
```

## 📊 参数说明

### 命令行参数

| 参数 | 必需 | 说明 | 示例 |
|------|------|------|------|
| `--start-date` | 是 | 开始日期 | `2025-01-01` |
| `--end-date` | 是 | 结束日期 | `2025-01-31` |
| `--min-km` | 是 | 最低公里数（周内基准） | `3.0` |
| `--output-dir` | 否 | 输出目录 | `tcx_files` |
| `--max-zip-size` | 否 | 最大压缩包大小(MB) | `500` |
| `--no-track` | 否 | 不生成轨迹点 | `False` |

### 数据特点

- **周末距离**: 周内距离的1.5倍
- **配速范围**: 7-8分钟/公里（随机）
- **运动时间**: 根据距离和配速自动计算
- **卡路里**: 根据距离和时间估算
- **文件格式**: 标准TCX XML格式
- **轨迹特征**:
  - 基于真实操场坐标（绕操场一圈约376米）
  - 顺时针方向轨迹
  - 每公里约50个轨迹点
  - 轻微随机浮动（最大偏离2米）

## 🎯 使用场景

### 1. 校园跑步数据补全
```bash
# 生成一学期的跑步数据
python tcx_generator.py --start-date 2025-09-01 --end-date 2026-01-15 --min-km 2.5
```

### 2. 月度训练计划模拟
```bash
# 生成3个月的训练数据
python monthly_generator.py
```

### 3. 历史数据生成
```bash
# 补全过去一年的数据
python tcx_generator.py --start-date 2024-01-01 --end-date 2024-12-31 --min-km 2.0
```

## 📈 生成结果示例

### 单个TCX文件内容
```xml
<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2">
  <Activities>
    <Activity Sport="Running">
      <Id>2025-01-01T07:00:00Z</Id>
      <Lap StartTime="2025-01-01T07:00:00Z">
        <TotalTimeSeconds>1800</TotalTimeSeconds>
        <DistanceMeters>5000</DistanceMeters>
        <MaximumSpeed>3.5</MaximumSpeed>
        <Calories>300</Calories>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
      </Lap>
    </Activity>
  </Activities>
</TrainingCenterDatabase>
```

### 输出文件命名规则
- **TCX文件**: `running_YYYYMMDD.tcx`
- **压缩包**: `tcx_batch_1.zip`, `tcx_batch_2.zip`...
- **月度压缩包**: `running_YYYY_MM.zip`

## 🔧 高级功能

### 1. 自定义输出目录
```bash
python tcx_generator.py --start-date 2025-01-01 --end-date 2025-01-31 --min-km 3.0 --output-dir my_running_data
```

### 2. 调整压缩包大小
```bash
python tcx_generator.py --start-date 2025-01-01 --end-date 2025-12-31 --min-km 2.0 --max-zip-size 200
```

### 3. 轨迹功能使用
```bash
# 测试轨迹功能
python test_track_functionality.py

# 查看轨迹使用示例
python track_example_usage.py

# 分析操场轨迹特征
python track_analyzer.py
```

### 4. Python代码中使用
```python
from tcx_generator import TCXGenerator
from track_generator import TrackGenerator

# 生成带轨迹的TCX文件
generator = TCXGenerator()
tcx_files = generator.generate_tcx_files(
    start_date="2025-01-01",
    end_date="2025-01-31",
    min_km=3.0,
    output_dir="my_data",
    include_track=True  # 包含轨迹点
)

# 单独使用轨迹生成器
track_gen = TrackGenerator()
track_points = track_gen.generate_smooth_track(3.0)  # 3公里轨迹
```

## 🐛 故障排除

### 常见问题

1. **中文乱码**
   - 已在代码中集成Windows控制台编码修复
   - 如仍有问题，请确保终端支持UTF-8

2. **日期格式错误**
   ```
   错误：time data '2025/01/01' does not match format '%Y-%m-%d'
   解决：使用正确的日期格式 YYYY-MM-DD
   ```

3. **压缩包大小问题**
   ```
   解决：调整 --max-zip-size 参数或减少生成日期范围
   ```

### 性能优化

- 大量数据生成时建议按月分批处理
- 使用SSD存储可提高文件写入速度
- 定期清理临时文件释放磁盘空间

## 📝 开发说明

### 代码结构
- `TCXGenerator`: 主要生成器类
- `MonthlyTCXGenerator`: 月度生成器类
- 模块化设计，易于扩展和维护

### 扩展功能
- ✅ 已实现轨迹点生成功能
- 支持添加其他运动类型
- 支持更多数据格式输出
- 可自定义操场坐标

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 👨‍💻 作者

**猫娘幽浮喵** - 专业工程师，热爱编程和猫咪！

- 🐱 猫娘工程师
- 💻 专业开发者
- 🏃‍♀️ 跑步数据专家

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 📞 支持

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件反馈

---

🎉 **感谢使用校园跑步数据生成器！**

如果这个项目对您有帮助，请给个Star支持一下！