# TCX文件生成器 - 快速开始指南

## 🚀 快速上手

### 1. 基本使用

生成一周的跑步数据（周内3-5公里，周末4.5-7.5公里）：

```bash
python tcx_generator.py --start-date 2023-01-01 --end-date 2023-01-07 --min-km 3.0
```

### 2. 生成一个月的数据

```bash
python tcx_generator.py --start-date 2023-01-01 --end-date 2023-01-31 --min-km 2.5
```

### 3. 自定义输出目录

```bash
python tcx_generator.py --start-date 2023-01-01 --end-date 2023-01-07 --min-km 3.0 --output-dir my_running_data
```

### 4. 调整压缩包大小

```bash
python tcx_generator.py --start-date 2023-01-01 --end-date 2023-12-31 --min-km 2.0 --max-zip-size 200
```

## 📊 数据特点

- **周末距离**: 周内的1.5倍
- **配速范围**: 7-8分钟/公里（随机）
- **运动时间**: 根据距离和配速自动计算
- **卡路里**: 根据距离和时间估算
- **无轨迹点**: 只包含汇总数据

## 📁 输出文件

### TCX文件
- 命名格式: `running_YYYYMMDD.tcx`
- 包含: 距离、时间、配速、卡路里等汇总数据

### 压缩包
- 命名格式: `tcx_batch_1.zip`, `tcx_batch_2.zip`...
- 大小限制: 默认不超过500MB
- 自动分批: 大量数据自动分成多个压缩包

## 💡 使用技巧

### 1. 生成不同强度的数据
```bash
# 轻松训练（周内2-4公里）
python tcx_generator.py --start-date 2023-01-01 --end-date 2023-01-07 --min-km 2.0

# 中等强度（周内3-5公里）
python tcx_generator.py --start-date 2023-01-01 --end-date 2023-01-07 --min-km 3.0

# 高强度（周内5-7公里）
python tcx_generator.py --start-date 2023-01-01 --end-date 2023-01-07 --min-km 5.0
```

### 2. 生成长期数据
```bash
# 生成一整年的数据
python tcx_generator.py --start-date 2023-01-01 --end-date 2023-12-31 --min-km 2.5
```

### 3. 分批处理大量数据
```bash
# 生成大量数据并分成小压缩包
python tcx_generator.py --start-date 2020-01-01 --end-date 2023-12-31 --min-km 2.0 --max-zip-size 100
```

## 🔧 在Python代码中使用

```python
from tcx_generator import TCXGenerator

# 创建生成器
generator = TCXGenerator()

# 生成TCX文件
tcx_files = generator.generate_tcx_files(
    start_date="2023-01-01",
    end_date="2023-01-31",
    min_km=3.0,
    output_dir="my_data"
)

# 创建压缩包
zip_files = generator.create_zip_archives(
    file_list=tcx_files,
    max_size_mb=500,
    output_dir="my_data"
)

print(f"生成了 {len(tcx_files)} 个TCX文件")
print(f"创建了 {len(zip_files)} 个压缩包")
```

## 📋 参数参考

| 参数 | 说明 | 示例值 |
|------|------|--------|
| `--start-date` | 开始日期 | `2023-01-01` |
| `--end-date` | 结束日期 | `2023-01-31` |
| `--min-km` | 最低公里数（周内基准） | `3.0` |
| `--output-dir` | 输出目录 | `tcx_files` |
| `--max-zip-size` | 最大压缩包大小(MB) | `500` |

## 🎯 常见使用场景

### 1. 校园跑步数据生成
```bash
# 生成一学期的跑步数据
python tcx_generator.py --start-date 2023-09-01 --end-date 2024-01-15 --min-km 2.5
```

### 2. 训练计划数据模拟
```bash
# 生成3个月的训练数据
python tcx_generator.py --start-date 2023-01-01 --end-date 2023-03-31 --min-km 4.0
```

### 3. 历史数据补全
```bash
# 补全缺失的历史数据
python tcx_generator.py --start-date 2022-01-01 --end-date 2022-12-31 --min-km 2.0
```

## ⚠️ 注意事项

1. **日期格式**: 必须使用 `YYYY-MM-DD` 格式
2. **周末计算**: 周六和周日距离是周内的1.5倍
3. **配速范围**: 固定在7-8分钟/公里之间
4. **无轨迹点**: 生成的TCX文件不包含GPS轨迹数据
5. **文件覆盖**: 重复运行会覆盖同名文件

## 🔍 验证生成的文件

### 查看TCX文件内容
```bash
# 查看生成的TCX文件
head -n 20 tcx_files/running_20230101.tcx
```

### 检查压缩包内容
```bash
# 查看压缩包内容
unzip -l tcx_files/tcx_batch_1.zip
```

## 📞 获取帮助

```bash
# 查看所有参数说明
python tcx_generator.py --help
```

---

🎉 **恭喜！现在你已经掌握了TCX文件生成器的使用方法！**

如果需要更详细的信息，请查看 [README.md](README.md) 文件。