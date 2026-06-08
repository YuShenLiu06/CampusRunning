#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""配置管理器

作者: 猫娘幽浮喵
功能: 加载和管理轨迹配置、默认设置等
"""

import json
import logging
import os
from typing import Optional

from src.core.models import (
    GeoPoint,
    CoordinateCorrection,
    TrackDefinition,
    GenerationConfig,
)

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器

    负责从 config/ 目录加载轨迹定义、默认设置等配置数据。
    """

    def __init__(self, config_dir: str) -> None:
        """初始化配置管理器

        Args:
            config_dir: 配置目录路径（通常为项目根目录下的 config/）
        """
        self._config_dir = config_dir
        self._tracks_dir = os.path.join(config_dir, "tracks")
        self._defaults_path = os.path.join(config_dir, "default_settings.json")

        logger.info("配置管理器初始化: %s", config_dir)

    def list_tracks(self) -> list[str]:
        """列出所有可用的轨迹ID

        Returns:
            轨迹ID列表
        """
        tracks = []
        if not os.path.isdir(self._tracks_dir):
            logger.warning("轨迹目录不存在: %s", self._tracks_dir)
            return tracks

        for filename in os.listdir(self._tracks_dir):
            if filename.endswith(".json"):
                tracks.append(filename[:-5])

        logger.info("发现 %d 条轨迹", len(tracks))
        return tracks

    def load_track(self, track_id: str) -> TrackDefinition:
        """加载轨迹定义

        Args:
            track_id: 轨迹ID

        Returns:
            轨迹定义对象

        Raises:
            FileNotFoundError: 轨迹文件不存在
        """
        filepath = os.path.join(self._tracks_dir, f"{track_id}.json")
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"轨迹文件不存在: {filepath}")

        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        # 解析基础坐标
        base_coords = [
            GeoPoint(longitude=p["longitude"], latitude=p["latitude"])
            for p in data["base_coordinates"]
        ]

        # 解析可选的坐标修正
        correction = None
        if "coordinate_correction" in data and data["coordinate_correction"]:
            cc = data["coordinate_correction"]
            correction = CoordinateCorrection(
                current_center=GeoPoint(
                    longitude=cc["current_center"]["longitude"],
                    latitude=cc["current_center"]["latitude"],
                ),
                target_center=GeoPoint(
                    longitude=cc["target_center"]["longitude"],
                    latitude=cc["target_center"]["latitude"],
                ),
            )

        track = TrackDefinition(
            id=data["id"],
            name=data["name"],
            description=data["description"],
            base_coordinates=base_coords,
            coordinate_correction=correction,
        )

        logger.info("加载轨迹: %s (%s)", track.name, track.id)
        return track

    def load_defaults(self) -> dict:
        """加载默认设置

        Returns:
            默认设置字典
        """
        if not os.path.isfile(self._defaults_path):
            logger.warning("默认设置文件不存在，使用内置默认值")
            return {}

        with open(self._defaults_path, "r", encoding="utf-8") as fh:
            defaults = json.load(fh)

        logger.info("默认设置已加载")
        return defaults

    def build_default_config(self, overrides: Optional[dict] = None) -> GenerationConfig:
        """根据默认设置构建生成配置

        Args:
            overrides: 覆盖项字典

        Returns:
            生成配置对象
        """
        defaults = self.load_defaults()
        params = {
            "track_id": defaults.get("default_track_id", "campus_default"),
            "min_pace": defaults.get("default_pace_range", [7.0, 8.0])[0],
            "max_pace": defaults.get("default_pace_range", [7.0, 8.0])[1],
            "start_time_min": defaults.get("default_start_time_range", ["06:00", "08:00"])[0],
            "start_time_max": defaults.get("default_start_time_range", ["06:00", "08:00"])[1],
            "weekend_factor": defaults.get("weekend_factor", 1.5),
            "rest_days_per_week": defaults.get("rest_days_per_week", 1),
            "points_per_km": defaults.get("points_per_km", 50),
            "max_deviation_meters": defaults.get("max_deviation_meters", 2.0),
            "smooth_factor": defaults.get("smooth_factor", 0.3),
            "calories_per_km": defaults.get("calories_per_km", 60.0),
            "min_daily_km": defaults.get("min_daily_km", 2.0),
            "max_daily_km": defaults.get("max_daily_km", 8.0),
        }

        if overrides:
            params.update(overrides)

        return GenerationConfig(**params)
