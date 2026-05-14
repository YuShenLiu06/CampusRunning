#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导出器基类

作者: 猫娘幽浮喵
功能: 定义导出器抽象接口，所有具体导出器继承此基类
"""

import os
from abc import ABC, abstractmethod
from src.core.models import ExportData


class BaseExporter(ABC):
    """抽象导出器

    所有格式导出器必须实现 export() 和 get_file_extension() 方法。
    """

    @abstractmethod
    def export(self, data: ExportData, output_path: str) -> str:
        """导出数据到文件

        Args:
            data: 导出数据
            output_path: 输出文件路径

        Returns:
            实际写入的文件路径
        """
        ...

    @abstractmethod
    def get_file_extension(self) -> str:
        """获取导出文件扩展名

        Returns:
            文件扩展名（含点号，如 ".tcx"）
        """
        ...

    def ensure_output_dir(self, output_path: str) -> None:
        """确保输出目录存在

        Args:
            output_path: 输出文件路径
        """
        directory = os.path.dirname(output_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
