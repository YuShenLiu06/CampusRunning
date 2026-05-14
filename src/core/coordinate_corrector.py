#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
坐标修正器
用于修正GCJ-02坐标数据的误差，通过平移消除误差

作者: 猫娘幽浮喵
功能:
1. 接受 CoordinateCorrection 参数进行坐标修正
2. 支持 identity 模式（不修正）
3. 支持反向修正（将修正后的坐标还原为原始坐标）
"""

import logging
import math
from typing import Optional, List

from src.core.models import GeoPoint, CoordinateCorrection

logger = logging.getLogger(__name__)


class CoordinateCorrector:
    """坐标修正器类

    通过计算当前中心点与目标中心点之间的偏移量，
    对坐标进行平移修正以消除GCJ-02坐标系误差。

    当传入 None 时，进入 identity 模式，所有方法返回原始坐标。
    """

    def __init__(self, correction: Optional[CoordinateCorrection] = None) -> None:
        """初始化坐标修正器。

        Args:
            correction: 坐标修正参数，包含当前中心点和目标中心点。
                        传入 None 时进入 identity 模式（不进行修正）。
        """
        if correction is None:
            self._identity: bool = True
            self.lon_offset: float = 0.0
            self.lat_offset: float = 0.0
            logger.debug("坐标修正器初始化: identity 模式（不修正）")
            return

        self._identity = False

        # 计算偏移量（当前中心 - 目标中心）
        current = correction.current_center
        target = correction.target_center
        self.lon_offset = current.longitude - target.longitude
        self.lat_offset = current.latitude - target.latitude

        # 记录修正信息
        meters_per_degree_lat = 110540
        meters_per_degree_lon = 111320 * math.cos(math.radians(current.latitude))
        lon_meters = self.lon_offset * meters_per_degree_lon
        lat_meters = self.lat_offset * meters_per_degree_lat
        total = math.sqrt(lon_meters ** 2 + lat_meters ** 2)

        # 计算方向角度
        direction_deg = math.degrees(math.atan2(lat_meters, lon_meters))
        dir_text = self._direction_to_chinese(direction_deg)

        logger.info(
            "坐标修正器初始化: 向%s方向偏移 %.2f 米",
            dir_text, total
        )

    @staticmethod
    def _direction_to_chinese(direction_deg: float) -> str:
        """将角度转换为中文方向描述。

        Args:
            direction_deg: 方向角度（度），0 为东，90 为北。

        Returns:
            中文方向名称。
        """
        if direction_deg >= 337.5 or direction_deg < 22.5:
            return '东'
        elif 22.5 <= direction_deg < 67.5:
            return '东北'
        elif 67.5 <= direction_deg < 112.5:
            return '北'
        elif 112.5 <= direction_deg < 157.5:
            return '西北'
        elif 157.5 <= direction_deg < 202.5:
            return '西'
        elif 202.5 <= direction_deg < 247.5:
            return '西南'
        elif 247.5 <= direction_deg < 292.5:
            return '南'
        else:
            return '东南'

    def correct_coordinate(self, point: GeoPoint) -> GeoPoint:
        """修正单个坐标点。

        Args:
            point: 原始坐标点。

        Returns:
            修正后的坐标点。identity 模式下返回原始坐标。
        """
        if self._identity:
            return point
        return GeoPoint(
            longitude=point.longitude + self.lon_offset,
            latitude=point.latitude + self.lat_offset,
        )

    def correct_coordinates(self, coordinates: List[GeoPoint]) -> List[GeoPoint]:
        """修正坐标列表。

        Args:
            coordinates: 原始坐标点列表。

        Returns:
            修正后的坐标点列表。
        """
        return [self.correct_coordinate(p) for p in coordinates]

    def apply_inverse_correction(self, point: GeoPoint) -> GeoPoint:
        """应用反向修正（将修正后的坐标还原为原始坐标）。

        反向修正应该是减去偏移量。

        Args:
            point: 修正后的坐标点。

        Returns:
            原始坐标点。identity 模式下返回原始坐标。
        """
        if self._identity:
            return point
        return GeoPoint(
            longitude=point.longitude - self.lon_offset,
            latitude=point.latitude - self.lat_offset,
        )
