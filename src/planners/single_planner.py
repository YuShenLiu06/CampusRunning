#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单文件规划器

作者: 猫娘幽浮喵
功能: 生成单日跑步计划
"""

import datetime

from src.core.models import DailyPlan


class SinglePlanner:
    """单文件规划器

    用于生成单日跑步数据场景，直接将指定日期和距离包装为 DailyPlan。
    """

    def plan(self, date: datetime.date, distance_km: float) -> DailyPlan:
        """生成单日跑步计划

        Args:
            date: 运动日期
            distance_km: 跑步距离（公里）

        Returns:
            单日计划
        """
        return DailyPlan(date=date, distance_km=distance_km)
