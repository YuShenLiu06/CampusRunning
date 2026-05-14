#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""总公里数规划器

作者: 猫娘幽浮喵
功能: 根据日期范围和总公里数目标，智能分配每日跑步距离
"""

import datetime
import random
import logging

from src.core.models import DailyPlan, GenerationConfig, RunningPlan

logger = logging.getLogger(__name__)


class TotalKmPlanner:
    """总公里数规划器

    核心算法（来自 DataPlanner.generate_running_plan）：
    1. 分离工作日和周末
    2. 计算跑步天数（减去休息日）
    3. 设工作日距离为 x，周末为 weekend_factor * x
    4. x = total_km / (工作日数量 + 周末数量 * weekend_factor)
    5. 对每天添加 ±20% 随机浮动
    6. 随机选择休息日（每周 rest_days_per_week 天）
    7. 如果实际总距离偏差超过5%，用调整因子缩放
    8. 返回 RunningPlan
    """

    def __init__(self, config: GenerationConfig) -> None:
        """初始化规划器

        Args:
            config: 生成配置
        """
        self.config = config

    def plan(self, start_date: datetime.date, end_date: datetime.date,
             total_km: float) -> RunningPlan:
        """生成跑步计划

        Args:
            start_date: 开始日期
            end_date: 结束日期
            total_km: 总公里数

        Returns:
            跑步计划（包含每日计划列表）
        """
        min_daily_km = self.config.min_daily_km
        max_daily_km = self.config.max_daily_km
        weekend_factor = self.config.weekend_factor
        rest_days_per_week = self.config.rest_days_per_week

        # 生成日期范围
        dates: list[datetime.date] = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += datetime.timedelta(days=1)

        # 分类工作日和周末
        weekdays = [d for d in dates if d.weekday() < 5]
        weekends = [d for d in dates if d.weekday() >= 5]

        # 计算总天数和跑步天数
        total_days = len(dates)
        running_days = total_days - (total_days // 7) * rest_days_per_week

        # 计算平均每日距离
        avg_daily_km = total_km / running_days if running_days > 0 else 0

        # 计算工作日和周末的平均距离
        # 设工作日距离为 x，周末距离为 weekend_factor * x
        # 总距离 = 工作日数量 * x + 周末数量 * weekend_factor * x
        # x = 总距离 / (工作日数量 + 周末数量 * weekend_factor)
        if len(weekdays) + len(weekends) * weekend_factor > 0:
            weekday_avg = total_km / (len(weekdays) + len(weekends) * weekend_factor)
            weekend_avg = weekday_avg * weekend_factor
        else:
            weekday_avg = avg_daily_km
            weekend_avg = avg_daily_km * weekend_factor

        # 确保平均距离在合理范围内
        weekday_avg = max(min_daily_km, min(max_daily_km, weekday_avg))
        weekend_avg = max(min_daily_km, min(max_daily_km, weekend_avg))

        # 生成每日跑步计划（使用 dict[date] -> distance）
        daily_plan: dict[datetime.date, float] = {}

        # 为工作日分配距离（±20% 随机浮动）
        for date in weekdays:
            daily_distance = random.uniform(weekday_avg * 0.8, weekday_avg * 1.2)
            daily_distance = max(min_daily_km, min(max_daily_km, daily_distance))
            daily_plan[date] = round(daily_distance, 2)

        # 为周末分配距离（±20% 随机浮动）
        for date in weekends:
            daily_distance = random.uniform(weekend_avg * 0.8, weekend_avg * 1.2)
            daily_distance = max(min_daily_km, min(max_daily_km, daily_distance))
            daily_plan[date] = round(daily_distance, 2)

        # 随机选择休息日
        if rest_days_per_week > 0:
            weeks: dict[int, list[datetime.date]] = {}
            for date in dates:
                week_num = (date - start_date).days // 7
                if week_num not in weeks:
                    weeks[week_num] = []
                weeks[week_num].append(date)

            for week_dates in weeks.values():
                rest_days = random.sample(
                    week_dates,
                    min(rest_days_per_week, len(week_dates))
                )
                for rest_day in rest_days:
                    if rest_day in daily_plan:
                        del daily_plan[rest_day]

        # 计算实际总距离
        actual_total = sum(daily_plan.values())

        # 如果实际总距离与目标有较大差异（超过5%），进行调整
        if abs(actual_total - total_km) > total_km * 0.05:
            adjustment_factor = total_km / actual_total

            adjusted_plan: dict[datetime.date, float] = {}
            for date, distance in daily_plan.items():
                adjusted_plan[date] = round(distance * adjustment_factor, 2)
            daily_plan = adjusted_plan

        # 重新计算实际总距离
        actual_total = sum(daily_plan.values())

        # 将 dict 转换为 list[DailyPlan]
        daily_plan_list = [
            DailyPlan(date=date, distance_km=distance)
            for date, distance in daily_plan.items()
        ]

        logger.info(
            "总公里数规划完成: 目标 %.2fkm, 实际 %.2fkm, 跑步天数 %d/%d",
            total_km, actual_total, len(daily_plan_list), total_days
        )

        return RunningPlan(
            start_date=start_date,
            end_date=end_date,
            total_days=total_days,
            running_days=len(daily_plan_list),
            target_total_km=total_km,
            actual_total_km=round(actual_total, 2),
            weekday_avg_km=round(weekday_avg, 2),
            weekend_avg_km=round(weekend_avg, 2),
            daily_plans=daily_plan_list,
        )
