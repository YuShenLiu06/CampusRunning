#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模板管理器

作者: 猫娘幽浮喵
功能: 加载和管理跑步模板配置
"""

import json
import logging
import os
from typing import Optional

from src.config_manager import ConfigManager
from src.core.models import GenerationConfig

logger = logging.getLogger(__name__)


class TemplateManager:
    """模板管理器

    负责从 config/templates/ 目录加载模板，并提供模板应用功能。
    """

    def __init__(self, config_manager: ConfigManager) -> None:
        """初始化模板管理器

        Args:
            config_manager: 配置管理器实例
        """
        self._config_manager = config_manager
        self._templates_dir = os.path.join(
            config_manager._config_dir, "templates"
        )

        logger.info("模板管理器初始化: %s", self._templates_dir)

    def list_available(self) -> list[dict]:
        """列出所有可用模板

        Returns:
            模板信息列表，每项包含 id, name, description
        """
        templates = []

        if not os.path.isdir(self._templates_dir):
            logger.warning("模板目录不存在: %s", self._templates_dir)
            return templates

        for filename in os.listdir(self._templates_dir):
            if not filename.endswith(".json"):
                continue

            filepath = os.path.join(self._templates_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as fh:
                    data = json.load(fh)

                templates.append({
                    "id": data["id"],
                    "name": data["name"],
                    "description": data["description"],
                })
            except Exception as e:
                logger.error("加载模板 %s 失败: %s", filename, e)

        logger.info("发现 %d 个模板", len(templates))
        return templates

    def load_template(self, template_id: str) -> Optional[dict]:
        """加载模板配置

        Args:
            template_id: 模板ID

        Returns:
            模板数据字典，不存在时返回 None
        """
        filepath = os.path.join(self._templates_dir, f"{template_id}.json")
        if not os.path.isfile(filepath):
            logger.warning("模板不存在: %s", template_id)
            return None

        with open(filepath, "r", encoding="utf-8") as fh:
            data = json.load(fh)

        logger.info("加载模板: %s (%s)", data["name"], data["id"])
        return data

    def apply_template(
        self,
        template_id: Optional[str] = None,
        overrides: Optional[dict] = None,
    ) -> GenerationConfig:
        """应用模板并合并覆盖项，生成最终配置

        优先级：overrides > template > defaults

        Args:
            template_id: 模板ID（可选）
            overrides: 覆盖项字典（可选）

        Returns:
            最终的生成配置
        """
        # 从默认配置开始
        config_dict = self._config_manager.build_default_config()
        base_params = {
            "track_id": config_dict.track_id,
            "min_pace": config_dict.min_pace,
            "max_pace": config_dict.max_pace,
            "start_hour_min": config_dict.start_hour_min,
            "start_hour_max": config_dict.start_hour_max,
            "output_dir": config_dict.output_dir,
            "include_track": config_dict.include_track,
            "apply_correction": config_dict.apply_correction,
            "enable_pace_fluctuation": config_dict.enable_pace_fluctuation,
            "create_zip": config_dict.create_zip,
            "points_per_km": config_dict.points_per_km,
            "max_deviation_meters": config_dict.max_deviation_meters,
            "smooth_factor": config_dict.smooth_factor,
            "weekend_factor": config_dict.weekend_factor,
            "rest_days_per_week": config_dict.rest_days_per_week,
            "min_daily_km": config_dict.min_daily_km,
            "max_daily_km": config_dict.max_daily_km,
            "calories_per_km": config_dict.calories_per_km,
        }

        # 应用模板
        if template_id:
            template_data = self.load_template(template_id)
            if template_data and "generation_config" in template_data:
                gen_config = template_data["generation_config"]
                for key, value in gen_config.items():
                    if key in base_params:
                        base_params[key] = value
                logger.info("模板 %s 已应用", template_id)

        # 应用覆盖项
        if overrides:
            for key, value in overrides.items():
                if key in base_params:
                    base_params[key] = value
            logger.info("覆盖项已应用")

        return GenerationConfig(**base_params)
