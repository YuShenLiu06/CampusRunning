#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用工具函数

作者: 猫娘幽浮喵
功能: 提供配速、时长、卡路里、开始时间等计算工具
"""

import random
import datetime
import logging

logger = logging.getLogger(__name__)


def generate_pace(min_pace: float, max_pace: float) -> float:
    """生成随机配速（分钟/公里）

    Args:
        min_pace: 最快配速（分钟/公里）
        max_pace: 最慢配速（分钟/公里）

    Returns:
        配速（分钟/公里）
    """
    return round(random.uniform(min_pace, max_pace), 2)


def calculate_duration(distance_km: float, pace_min_per_km: float) -> float:
    """根据距离和配速计算运动时间

    Args:
        distance_km: 距离（公里）
        pace_min_per_km: 配速（分钟/公里）

    Returns:
        运动时间（秒）
    """
    total_minutes = distance_km * pace_min_per_km
    return round(total_minutes * 60, 0)


def calculate_calories(distance_km: float, duration_seconds: float,
                       calories_per_km: float = 60.0) -> int:
    """估算消耗的卡路里

    简单计算：每公里约消耗 calories_per_km 卡路里，根据时间微调

    Args:
        distance_km: 距离（公里）
        duration_seconds: 运动时间（秒）
        calories_per_km: 每公里基础消耗（默认60）

    Returns:
        卡路里数
    """
    base_calories = distance_km * calories_per_km
    time_factor = 1.0 + (duration_seconds / 3600 - 0.5) * 0.1
    return int(base_calories * time_factor)


def generate_start_time(date: datetime.date,
                        time_range: tuple[str, str] = ("06:00", "08:00")) -> datetime.datetime:
    """生成随机开始时间

    在指定的时间范围（精确到分钟）内随机生成一个开始时间。

    Args:
        date: 日期
        time_range: 开始时间范围（"HH:MM" 格式）

    Returns:
        随机开始时间
    """
    start_time = datetime.datetime.strptime(time_range[0], "%H:%M")
    end_time = datetime.datetime.strptime(time_range[1], "%H:%M")

    # 将时间转换为当天的分钟数以便随机
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute

    total_minutes = random.randint(start_minutes, end_minutes)
    hour = total_minutes // 60
    minute = total_minutes % 60
    second = random.randint(0, 59)

    return datetime.datetime.combine(date, datetime.time(hour, minute, second))
