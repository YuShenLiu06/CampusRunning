#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配速波动器
为跑步数据生成真实的配速波动

作者: 猫娘幽浮喵
功能:
1. 基于跑步阶段生成配速波动（热身/稳定/疲劳/冲刺）
2. 添加周期性和随机性波动以增强真实感
3. 调整配速曲线确保平均配速符合目标
"""

import logging
import math
import random
from typing import List, Optional

logger = logging.getLogger(__name__)


class PaceFluctuator:
    """配速波动器类

    根据跑步的四个阶段（热身、稳定、疲劳、冲刺）生成
    具有真实感的配速波动曲线，并通过正弦波叠加和高斯
    噪声增强自然感。
    """

    def __init__(
        self,
        base_pace_min_per_km: float,
        fluctuation_intensity: float = 0.15,
        random_seed: Optional[int] = None,
    ) -> None:
        """初始化配速波动器。

        Args:
            base_pace_min_per_km: 基础配速（分钟/公里）。
            fluctuation_intensity: 波动强度（0.0-1.0，默认0.15）。
            random_seed: 随机种子，用于可重现的结果。
        """
        self.base_pace: float = base_pace_min_per_km
        self.fluctuation_intensity: float = fluctuation_intensity

        if random_seed is not None:
            random.seed(random_seed)

        # 定义跑步阶段（起止进度百分比）
        self.phases = {
            'warmup': (0.0, 0.1),      # 0-10% 热身阶段
            'steady': (0.1, 0.7),      # 10-70% 稳定阶段
            'fatigue': (0.7, 0.9),     # 70-90% 疲劳阶段
            'final': (0.9, 1.0),       # 90-100% 最后阶段
        }

        logger.debug(
            "配速波动器初始化: 基础配速 %.2f 分钟/公里, 波动强度 %.2f",
            self.base_pace,
            self.fluctuation_intensity,
        )

    def generate_pace_profile(self, num_points: int) -> List[float]:
        """生成配速曲线。

        根据跑步阶段、周期性波动和随机噪声生成每个轨迹点
        的配速值，并通过调整因子确保平均配速接近目标。

        Args:
            num_points: 轨迹点数量。

        Returns:
            每个点的配速列表（分钟/公里）。
        """
        pace_profile: List[float] = []

        for i in range(num_points):
            # 计算当前点在跑步过程中的位置（0.0到1.0）
            progress = i / (num_points - 1) if num_points > 1 else 0.5

            # 根据阶段计算基础配速倍数
            phase_multiplier = self._get_phase_multiplier(progress)

            # 添加周期性波动
            periodic_factor = self._get_periodic_fluctuation(progress)

            # 添加随机噪声
            random_factor = self._get_random_fluctuation()

            # 计算最终配速
            pace = self.base_pace * phase_multiplier * (1 + periodic_factor + random_factor)
            pace_profile.append(pace)

        # 调整配速曲线，确保平均配速接近目标配速
        pace_profile = self._adjust_pace_profile(pace_profile)

        return pace_profile

    def _get_phase_multiplier(self, progress: float) -> float:
        """根据跑步进度获取阶段配速倍数。

        Args:
            progress: 跑步进度（0.0到1.0）。

        Returns:
            配速倍数。
        """
        # 热身阶段：配速较慢（比目标配速慢10-20%）
        if progress <= self.phases['warmup'][1]:
            # 从慢20%逐渐到慢10%
            return 1.2 - 0.1 * (progress / self.phases['warmup'][1])

        # 稳定阶段：配速接近目标（正负5%）
        elif progress <= self.phases['steady'][1]:
            # 在目标配速附近小幅波动
            steady_progress = (
                (progress - self.phases['steady'][0])
                / (self.phases['steady'][1] - self.phases['steady'][0])
            )
            return 1.0 + 0.05 * math.sin(steady_progress * math.pi * 4)

        # 疲劳阶段：配速逐渐减慢（比目标配速慢5-15%）
        elif progress <= self.phases['fatigue'][1]:
            # 从慢5%逐渐到慢15%
            fatigue_progress = (
                (progress - self.phases['fatigue'][0])
                / (self.phases['fatigue'][1] - self.phases['fatigue'][0])
            )
            return 1.05 + 0.1 * fatigue_progress

        # 最后阶段：可能冲刺或保持
        else:
            # 50%概率短暂冲刺，50%概率保持或略微减慢
            if random.random() < 0.5:
                # 短暂冲刺：配速接近目标
                final_progress = (
                    (progress - self.phases['final'][0])
                    / (self.phases['final'][1] - self.phases['final'][0])
                )
                return 1.05 - 0.1 * final_progress
            else:
                # 保持或略微减慢
                return 1.15

    def _get_periodic_fluctuation(self, progress: float) -> float:
        """获取周期性波动因子。

        使用多个正弦波叠加，模拟自然配速变化。

        Args:
            progress: 跑步进度（0.0到1.0）。

        Returns:
            周期性波动因子。
        """
        fluctuation = 0.0

        # 主波动周期（约每公里1-2次波动）
        fluctuation += 0.02 * math.sin(progress * math.pi * 8)

        # 次波动周期（更频繁的小幅波动）
        fluctuation += 0.01 * math.sin(progress * math.pi * 20)

        # 微小波动
        fluctuation += 0.005 * math.sin(progress * math.pi * 40)

        return fluctuation * self.fluctuation_intensity

    def _get_random_fluctuation(self) -> float:
        """获取随机波动因子。

        使用正态分布生成更自然的随机波动。

        Returns:
            随机波动因子。
        """
        return random.gauss(0, 0.02) * self.fluctuation_intensity

    def _adjust_pace_profile(self, pace_profile: List[float]) -> List[float]:
        """调整配速曲线，确保平均配速接近目标配速。

        通过线性缩放调整配速值，同时限制调整幅度以保持波动性。

        Args:
            pace_profile: 原始配速曲线。

        Returns:
            调整后的配速曲线。
        """
        if not pace_profile:
            return pace_profile

        # 计算当前平均配速
        current_avg_pace = sum(pace_profile) / len(pace_profile)

        # 计算调整因子
        adjustment_factor = self.base_pace / current_avg_pace

        # 限制调整幅度以保持波动性（最大调整10%）
        max_adjustment = 1.1
        adjustment_factor = max(
            1 / max_adjustment,
            min(max_adjustment, adjustment_factor),
        )

        # 应用调整
        adjusted_profile = [pace * adjustment_factor for pace in pace_profile]

        return adjusted_profile

    def generate_segment_times(
        self,
        pace_profile: List[float],
        segment_distances: List[float],
    ) -> List[float]:
        """根据配速曲线和分段距离计算每段的时间。

        Args:
            pace_profile: 配速曲线（分钟/公里）。
            segment_distances: 每段距离（公里）。

        Returns:
            每段的时间（秒）。

        Raises:
            ValueError: 当配速曲线和分段距离数量不匹配时。
        """
        if len(pace_profile) != len(segment_distances):
            raise ValueError(
                f"配速曲线和分段距离数量不匹配: "
                f"{len(pace_profile)} != {len(segment_distances)}"
            )

        segment_times: List[float] = []
        for pace, distance in zip(pace_profile, segment_distances):
            # 时间 = 配速 * 距离
            time_minutes = pace * distance
            segment_times.append(time_minutes * 60)  # 转换为秒

        return segment_times
