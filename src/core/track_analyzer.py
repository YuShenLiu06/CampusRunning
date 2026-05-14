#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轨迹分析器
分析提供的经纬度坐标，用于理解操场轨迹特征

作者: 猫娘幽浮喵
功能:
1. 使用 Haversine 公式计算球面距离
2. 分析轨迹总距离、分段距离、中心点等
3. 使用 Shoelace 公式判断轨迹方向
4. 返回结构化的 TrackAnalysis 数据
"""

import math
import logging
from typing import List

from src.core.models import GeoPoint, TrackAnalysis

logger = logging.getLogger(__name__)


class TrackAnalyzer:
    """轨迹分析器类

    接受一组 GeoPoint 坐标，提供轨迹距离计算、
    中心点计算和方向判断等分析功能。
    """

    def __init__(self, coordinates: List[GeoPoint]) -> None:
        """初始化轨迹分析器。

        Args:
            coordinates: 轨迹坐标点列表。
        """
        self.base_coordinates: List[GeoPoint] = coordinates
        logger.info(
            "轨迹分析器初始化: %d 个坐标点",
            len(self.base_coordinates)
        )

    def calculate_distance(self, point1: GeoPoint, point2: GeoPoint) -> float:
        """计算两点之间的球面距离（米），使用 Haversine 公式。

        Args:
            point1: 第一个坐标点。
            point2: 第二个坐标点。

        Returns:
            两点之间的距离（米）。
        """
        # 地球平均半径（米）
        R = 6371000

        # 转换为弧度
        lon1 = math.radians(point1.longitude)
        lat1 = math.radians(point1.latitude)
        lon2 = math.radians(point2.longitude)
        lat2 = math.radians(point2.latitude)

        # Haversine 公式
        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def calculate_total_distance(self, coordinates: List[GeoPoint]) -> float:
        """计算轨迹总距离（闭合环）。

        包括最后一点到第一点的距离。

        Args:
            coordinates: 坐标点列表。

        Returns:
            总距离（米）。
        """
        if len(coordinates) < 2:
            return 0.0

        total_distance = 0.0
        for i in range(len(coordinates) - 1):
            total_distance += self.calculate_distance(
                coordinates[i], coordinates[i + 1]
            )

        # 闭合环：最后一点到第一点
        total_distance += self.calculate_distance(
            coordinates[-1], coordinates[0]
        )

        return total_distance

    def analyze_track(self) -> TrackAnalysis:
        """分析轨迹特征，返回结构化分析结果。

        计算总距离、分段距离、中心点、近似半径和方向。

        Returns:
            TrackAnalysis 包含所有分析结果。
        """
        n = len(self.base_coordinates)
        if n == 0:
            logger.warning("轨迹分析: 坐标点为空")
            return TrackAnalysis(
                total_distance_meters=0.0,
                segment_distances=[],
                num_points=0,
                center=GeoPoint(longitude=0.0, latitude=0.0),
                approximate_radius_meters=0.0,
                is_clockwise=True,
            )

        # 计算总距离
        total_distance = self.calculate_total_distance(self.base_coordinates)

        # 计算各段距离
        segment_distances: List[float] = []
        for i in range(n):
            next_idx = (i + 1) % n
            segment_distances.append(
                self.calculate_distance(
                    self.base_coordinates[i], self.base_coordinates[next_idx]
                )
            )

        # 计算中心点
        center_lon = sum(p.longitude for p in self.base_coordinates) / n
        center_lat = sum(p.latitude for p in self.base_coordinates) / n
        center = GeoPoint(longitude=center_lon, latitude=center_lat)

        # 计算到中心点的平均距离（近似半径）
        avg_radius = (
            sum(
                self.calculate_distance(center, p)
                for p in self.base_coordinates
            )
            / n
        )

        # 判断轨迹方向
        clockwise = self._is_clockwise()

        logger.info(
            "轨迹分析完成: 总距离 %.2f 米, %d 个点, %s",
            total_distance,
            n,
            "顺时针" if clockwise else "逆时针",
        )

        return TrackAnalysis(
            total_distance_meters=total_distance,
            segment_distances=segment_distances,
            num_points=n,
            center=center,
            approximate_radius_meters=avg_radius,
            is_clockwise=clockwise,
        )

    def _is_clockwise(self) -> bool:
        """判断轨迹是否为顺时针方向。

        使用 Shoelace 公式计算多边形有符号面积：
        面积为负值表示顺时针方向。

        Returns:
            True 表示顺时针，False 表示逆时针。
        """
        area = 0.0
        n = len(self.base_coordinates)

        for i in range(n):
            j = (i + 1) % n
            area += (
                self.base_coordinates[i].longitude * self.base_coordinates[j].latitude
            )
            area -= (
                self.base_coordinates[j].longitude * self.base_coordinates[i].latitude
            )

        return area < 0
