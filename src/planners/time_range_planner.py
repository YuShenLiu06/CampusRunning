#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""时间范围规划器

作者: 猫娘幽浮喵
功能: 根据精确的时间范围（开始时间到结束时间）生成跑步计划
"""

import datetime
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TimeRangePlan:
    """时间范围计划

    Attributes:
        start_datetime: 开始时间（完整日期时间）
        end_datetime: 结束时间（完整日期时间）
        duration_minutes: 持续分钟数
    """
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    duration_minutes: int


class TimeRangePlanner:
    """时间范围规划器

    根据开始时间和结束时间计算跑步距离，支持跨午夜场景。
    """

    def plan(
        self,
        start_dt: datetime.datetime,
        end_dt: datetime.datetime,
    ) -> TimeRangePlan:
        """生成时间范围计划

        算法：
        1. 如果结束时间 < 开始时间，说明跨午夜，加1天
        2. 计算持续时间（分钟）
        3. 返回 TimeRangePlan

        Args:
            start_dt: 开始时间（精确到分钟）
            end_dt: 结束时间（精确到分钟）

        Returns:
            时间范围计划

        Example:
            >>> planner = TimeRangePlanner()
            >>> plan = planner.plan(
            ...     datetime.datetime(2024, 1, 15, 6, 30),
            ...     datetime.datetime(2024, 1, 15, 7, 15)
            ... )
            >>> plan.duration_minutes
            45
        """
        # 跨午夜处理：如果结束时间早于开始时间，说明跨午夜
        adjusted_end = end_dt
        if end_dt <= start_dt:
            adjusted_end = end_dt + datetime.timedelta(days=1)
            logger.debug("检测到跨午夜操作，结束时间调整为: %s", adjusted_end)

        # 计算持续时间（秒）
        delta = adjusted_end - start_dt
        duration_minutes = int(delta.total_seconds() / 60)

        logger.info(
            "时间范围计划: %s → %s, 持续 %d 分钟",
            start_dt.strftime("%Y-%m-%d %H:%M"),
            adjusted_end.strftime("%Y-%m-%d %H:%M"),
            duration_minutes,
        )

        return TimeRangePlan(
            start_datetime=start_dt,
            end_datetime=adjusted_end,
            duration_minutes=duration_minutes,
        )