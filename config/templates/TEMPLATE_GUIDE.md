# 模板创建指南

## 模板位置

模板文件存放在 `config/templates/` 目录下，每个模板是一个独立的 JSON 文件。

## 模板结构

```json
{
  "id": "模板唯一ID",
  "name": "模板显示名称",
  "description": "模板描述",
  "generation_config": {
    // 生成配置项
  }
}
```

## 配置参数说明

| 参数 | 类型 | 说明 |
|------|------|------|
| `min_pace` | float | 最快配速 (min/km)，越小越快 |
| `max_pace` | float | 最慢配速 (min/km)，越大越慢 |
| `start_hour_min` | int | 最早开始时间（小时） |
| `start_hour_max` | int | 最晚开始时间（小时） |
| `start_date` | string | 默认开始日期 (YYYY-MM-DD格式) |
| `end_date` | string | 默认结束日期 (YYYY-MM-DD格式) |
| `include_track` | bool | 是否包含轨迹点数据 |
| `apply_correction` | bool | 是否应用坐标修正 |
| `enable_pace_fluctuation` | bool | 是否启用配速波动 |
| `max_deviation_meters` | float | 坐标修正最大偏移（米） |
| `smooth_factor` | float | 轨迹平滑因子 (0.0-1.0) |
| `weekend_factor` | float | 周末跑步系数 |
| `rest_days_per_week` | int | 每周休息天数 |
| `min_daily_km` | float | 每日最低公里数 |
| `max_daily_km` | float | 每日最高公里数 |
| `calories_per_km` | float | 每公里消耗卡路里 |
| `points_per_km` | int | 每公里轨迹点数 |
| `create_zip` | bool | 是否创建ZIP压缩包 |

## 创建模板示例

### 1. 轻松跑模板

```json
{
  "id": "easy_run",
  "name": "轻松跑",
  "description": "轻松慢跑，适合恢复日",
  "generation_config": {
    "min_pace": 7.5,
    "max_pace": 9.0,
    "max_deviation_meters": 2.5,
    "smooth_factor": 0.4,
    "enable_pace_fluctuation": true
  }
}
```

### 2. 间歇跑模板

```json
{
  "id": "interval",
  "name": "间歇跑",
  "description": "高强度间歇训练",
  "generation_config": {
    "min_pace": 4.5,
    "max_pace": 5.5,
    "enable_pace_fluctuation": false,
    "max_deviation_meters": 1.0,
    "smooth_factor": 0.2
  }
}
```

### 3. 长距离跑模板

```json
{
  "id": "long_run",
  "name": "长距离跑",
  "description": "周末长距离训练",
  "generation_config": {
    "min_pace": 6.0,
    "max_pace": 7.5,
    "weekend_factor": 1.5,
    "enable_pace_fluctuation": true,
    "max_deviation_meters": 3.0,
    "smooth_factor": 0.5
  }
}
```

### 4. 训练周期模板（带日期）

```json
{
  "id": "spring_training",
  "name": "春季训练计划",
  "description": "3月1日至5月31日的春季训练",
  "generation_config": {
    "min_pace": 5.5,
    "max_pace": 7.0,
    "start_hour_min": 6,
    "start_hour_max": 8,
    "start_date": "2024-03-01",
    "end_date": "2024-05-31",
    "weekend_factor": 1.5,
    "enable_pace_fluctuation": true
  }
}
```

## 注意事项

1. **ID 唯一性**：每个模板的 `id` 必须唯一，不能与其他模板重复
2. **文件命名**：建议文件名与 `id` 保持一致，如 `easy_run.json`
3. **JSON 格式**：确保 JSON 格式正确，可使用在线 JSON 验证工具检查
4. **数值范围**：
   - `min_pace` 应小于 `max_pace`
   - `smooth_factor` 建议在 0.0-0.5 之间
   - `max_deviation_meters` 建议在 1.0-5.0 之间

## 使用模板

### 在Web界面中使用

1. **选择模板**：在"预设模板"下拉框中选择相应模板即可自动加载配置
2. **导入当前配置**：选择"导入当前配置"选项，可以将当前表单中的配置填充到模板选择中
3. **创建新模板**：点击"生成模板"按钮，可以将当前表单配置保存为新模板

### 通过API使用

```bash
# 获取模板列表
curl http://localhost:5000/api/templates

# 获取模板详情
curl http://localhost:5000/api/template/easy_run

# 创建新模板
curl -X POST http://localhost:5000/api/template \
  -H "Content-Type: application/json" \
  -d '{
    "name": "我的模板",
    "description": "自定义训练计划",
    "generation_config": {
      "min_pace": 6.0,
      "max_pace": 8.0
    }
  }'
```
