#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""TCX格式导出器

作者: 猫娘幽浮喵
功能: 将 ExportData 导出为 Garmin TCX 格式文件
"""

import os
import zipfile
import logging
from xml.dom import minidom

from src.core.models import ExportData
from .base import BaseExporter

logger = logging.getLogger(__name__)


class TcxExporter(BaseExporter):
    """TCX格式导出器

    将跑步数据导出为 Garmin Training Center XML (TCX) 格式。
    保留与原始 TCXGenerator 完全一致的 XML 结构。
    """

    _NAMESPACE = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    _XSI = "http://www.w3.org/2001/XMLSchema-instance"

    def export(self, data: ExportData, output_path: str) -> str:
        """导出 ExportData 为 TCX 文件

        Args:
            data: 包含跑步数据的导出数据对象
            output_path: 输出文件路径

        Returns:
            实际写入的文件路径
        """
        self.ensure_output_dir(output_path)

        xml_content = self._build_tcx_xml(data)

        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(xml_content)

        logger.info("TCX文件已导出: %s (%.2fkm, %d秒, %d卡路里)",
                     output_path, data.distance_km,
                     int(data.duration_seconds), data.calories)
        return output_path

    def get_file_extension(self) -> str:
        """获取TCX文件扩展名

        Returns:
            ".tcx"
        """
        return ".tcx"

    @staticmethod
    def create_zip_archive(file_list: list[str], archive_path: str) -> str:
        """将文件列表打包成ZIP压缩包

        Args:
            file_list: 要打包的文件路径列表
            archive_path: 压缩包路径

        Returns:
            压缩包路径
        """
        logger.info("正在创建压缩包: %s", archive_path)

        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_list:
                filename = os.path.basename(file_path)
                zipf.write(file_path, filename)

        logger.info("压缩包创建完成: %s", archive_path)
        return archive_path

    def _build_tcx_xml(self, data: ExportData) -> str:
        """构建完整的TCX XML字符串

        XML结构与原始 TCXGenerator.create_tcx_content 保持完全一致：
        - TrainingCenterDatabase 根节点包含正确的 namespace 和 xsi:schemaLocation
        - Activity Sport="Running" 包含 Id、Lap
        - Lap 包含 TotalTimeSeconds、DistanceMeters、MaximumSpeed、Calories 等
        - 可选的 Track 节点包含 Trackpoint 序列
        - Author 节点包含应用信息

        Args:
            data: 导出数据

        Returns:
            格式化后的 TCX XML 字符串
        """
        distance_meters = data.distance_km * 1000
        start_time_str = data.start_time.strftime("%Y-%m-%dT%H:%M:%S")

        # 构建轨迹XML（如果有轨迹点）
        track_xml = self._build_track_xml(data.trackpoints)

        # 组装完整XML
        xml_content = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<TrainingCenterDatabase xmlns="{self._NAMESPACE}" '
            f'xmlns:xsi="{self._XSI}" '
            f'xsi:schemaLocation="{self._NAMESPACE} '
            f'{self._NAMESPACE}/TrainingCenterDatabasev2.xsd">\n'
            f'  <Activities>\n'
            f'    <Activity Sport="Running">\n'
            f'      <Id>{start_time_str}</Id>\n'
            f'      <Lap StartTime="{start_time_str}">\n'
            f'        <TotalTimeSeconds>{data.duration_seconds}</TotalTimeSeconds>\n'
            f'        <DistanceMeters>{distance_meters}</DistanceMeters>\n'
            f'        <MaximumSpeed>3.5</MaximumSpeed>\n'
            f'        <Calories>{data.calories}</Calories>\n'
            f'        <Intensity>Active</Intensity>\n'
            f'        <TriggerMethod>Manual</TriggerMethod>\n'
            f'{track_xml}'
            f'      </Lap>\n'
            f'    </Activity>\n'
            f'  </Activities>\n'
            f'  <Author xsi:type="Application_t">\n'
            f'    <Name>Campus Running Data Generator</Name>\n'
            f'    <Build>\n'
            f'      <Version>\n'
            f'        <VersionMajor>1</VersionMajor>\n'
            f'        <VersionMinor>0</VersionMinor>\n'
            f'        <BuildMajor>0</BuildMajor>\n'
            f'        <BuildMinor>0</BuildMinor>\n'
            f'      </Version>\n'
            f'    </Build>\n'
            f'    <LangID>zh</LangID>\n'
            f'    <PartNumber>000-00000-00</PartNumber>\n'
            f'  </Author>\n'
            f'</TrainingCenterDatabase>'
        )

        # 使用 minidom 美化XML格式
        dom = minidom.parseString(xml_content)
        return dom.toprettyxml(indent="  ")

    @staticmethod
    def _build_track_xml(trackpoints: list) -> str:
        """构建Track节点的XML字符串

        Trackpoint 格式：
        <Trackpoint>
          <Time>{time}</Time>
          <Position>
            <LatitudeDegrees>{latitude}</LatitudeDegrees>
            <LongitudeDegrees>{longitude}</LongitudeDegrees>
          </Position>
          <AltitudeMeters>{altitude}</AltitudeMeters>
          <DistanceMeters>{distance_meters}</DistanceMeters>
        </Trackpoint>

        Args:
            trackpoints: 轨迹点数据列表（可能为空）

        Returns:
            Track XML字符串，无轨迹点时返回空字符串
        """
        if not trackpoints:
            return ""

        lines = ["      <Track>"]
        for tp in trackpoints:
            lines.append(
                f"        <Trackpoint>\n"
                f"          <Time>{tp.time}</Time>\n"
                f"          <Position>\n"
                f"            <LatitudeDegrees>{tp.latitude}</LatitudeDegrees>\n"
                f"            <LongitudeDegrees>{tp.longitude}</LongitudeDegrees>\n"
                f"          </Position>\n"
                f"          <AltitudeMeters>{tp.altitude}</AltitudeMeters>\n"
                f"          <DistanceMeters>{tp.distance_meters}</DistanceMeters>\n"
                f"        </Trackpoint>"
            )
        lines.append("      </Track>")
        lines.append("")  # 尾部换行

        return "\n".join(lines)
