#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""每日范围规划器

作者: 猫娘幽浮喵
功能: 根据日期范围和每日最小/最大公里数生成跑步计划
"""

import datetime
import random
import logging

from src.core.models import DailyPlan, GenerationConfig

logger = logging.getLogger(__name__)


class DailyPlanner:
    """每日范围规划器

    为日期范围内的每一天生成跑步距离，周末距离按 weekend_factor 放大。
    """

    def __init__(self, config: GenerationConfig) -> None:
        """初始化规划器

        Args:
            config: 生成配置
        """
        self.config = config

    def plan(self, start_date: datetime.date, end_date: datetime.date,
             min_km: float, max_km: float) -> list[DailyPlan]:
        """生成每日跑步计划

        算法逻辑（来自 TCXGenerator）：
        1. 遍历日期范围内每一天
        2. 在 [min_km, max_km] 区间内随机生成基础距离
        3. 如果是周末（weekday >= 5），距离乘以 weekend_factor
        4. 保留两位小数

        Args:
            start_date: 开始日期
            end_date: 结束日期
            min_km: 最低公里数（周内基准）
            max_km: 最高公里数（周内基准）

        Returns:
            每日计划列表
        """
        plans: list[DailyPlan] = []
        current = start_date

        while current <= end_date:
            base_distance = random.uniform(min_km, max_km)

            if current.weekday() >= 5:  # 周末
                distance = base_distance * self.config.weekend_factor
            else:
                distance = base_distance

            plans.append(DailyPlan(date=current, distance_km=round(distance, 2)))
            current += datetime.timedelta(days=1)

        logger.info(
            "每日规划完成: %d天, 距离范围 %.1f-%.1fkm",
            len(plans), min_km, max_km
        )
        return plans
