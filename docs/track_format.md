# 轨迹配置格式

## 轨迹定义文件

轨迹定义存储在 `config/tracks/` 目录下，JSON格式。

### 文件结构

```json
{
  "id": "track_id",
  "name": "轨迹名称",
  "description": "轨迹描述",
  "base_coordinates": [
    {"longitude": 106.6591, "latitude": 26.4513},
    {"longitude": 106.6590, "latitude": 26.4516},
    ...
  ],
  "coordinate_correction": {
    "current_center": {"longitude": 106.6594, "latitude": 26.4518},
    "target_center": {"longitude": 106.6630, "latitude": 26.4482}
  }
}
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `id` | string | 是 | 轨迹唯一标识符 |
| `name` | string | 是 | 轨迹显示名称 |
| `description` | string | 是 | 轨迹描述信息 |
| `base_coordinates` | array | 是 | 基础坐标点列表 |
| `coordinate_correction` | object | 否 | 坐标修正参数 |

### base_coordinates 格式

```json
{
  "longitude": 106.6591413213796,
  "latitude": 26.45129327365839
}
```

- `longitude`: 经度
- `latitude`: 纬度

### coordinate_correction 格式

```json
{
  "current_center": {"longitude": 106.6594, "latitude": 26.4518},
  "target_center": {"longitude": 106.6630, "latitude": 26.4482}
}
```

- `current_center`: 轨迹当前中心点坐标
- `target_center`: 目标中心点坐标
- 修正偏移量 = current_center - target_center

## 添加新轨迹

1. 在 `config/tracks/` 创建新 JSON 文件
2. 收集轨迹的 GPS 坐标点（顺时针方向）
3. 可选：配置坐标修正参数

### 示例：添加新操场

```json
{
  "id": "track_2",
  "name": "第二操场",
  "description": "田径场跑道",
  "base_coordinates": [
    {"longitude": 106.6600, "latitude": 26.4520},
    ...
  ]
}
```

使用新轨迹：
```bash
python main.py single --track track_2 --date 2025-01-01 --distance 5.0
```

## 坐标修正说明

GPS设备可能存在系统性偏移，坐标修正通过平移使显示位置更准确：

```
修正后坐标 = 原坐标 + (current_center - target_center)
```

偏移方向由 current_center 指向 target_center。

## 模板格式

预设模板存储在 `config/templates/` 目录下。

```json
{
  "id": "template_id",
  "name": "模板名称",
  "description": "模板描述",
  "generation_config": {
    "min_pace": 7.0,
    "max_pace": 8.0,
    "enable_pace_fluctuation": true
  }
}
```

可配置项参考 `GenerationConfig` 的所有字段。
