#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCX文件自动生成器
用于生成校园跑步数据的TCX格式文件

作者: 猫娘幽浮喵
功能: 根据时间范围和最低公里数自动生成TCX文件
"""

import os
import random
import zipfile
import datetime
import sys
from xml.dom import minidom
from typing import List, Tuple, Dict
import argparse
from track_generator import TrackGenerator

# 解决Windows控制台中文乱码问题
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())


class TCXGenerator:
    """TCX文件生成器类"""
    
    def __init__(self):
        self.namespace = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
        self.xsi = "http://www.w3.org/2001/XMLSchema-instance"
        self.track_generator = TrackGenerator()
        
    def generate_date_range(self, start_date: str, end_date: str) -> List[datetime.date]:
        """
        生成日期范围内的所有日期
        
        Args:
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            
        Returns:
            日期列表
        """
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        
        date_list = []
        current = start
        while current <= end:
            date_list.append(current)
            current += datetime.timedelta(days=1)
            
        return date_list
    
    def is_weekend(self, date: datetime.date) -> bool:
        """判断是否为周末"""
        return date.weekday() >= 5  # 5=周六, 6=周日
    
    def calculate_daily_distance(self, min_km: float, date: datetime.date) -> float:
        """
        计算每日跑步距离
        周末是周内的1.5倍
        
        Args:
            min_km: 最低公里数（周内基准）
            date: 日期
            
        Returns:
            该日跑步距离（公里）
        """
        base_distance = random.uniform(min_km, min_km + 2.0)  # 基础距离随机浮动
        
        if self.is_weekend(date):
            # 周末距离是周内的1.5倍
            distance = base_distance * 1.5
        else:
            distance = base_distance
            
        # 保留两位小数
        return round(distance, 2)
    
    def generate_pace(self) -> float:
        """
        生成随机配速（分钟/公里）
        范围：7-8分钟/公里
        
        Returns:
            配速（分钟/公里）
        """
        return round(random.uniform(7.0, 8.0), 2)
    
    def calculate_duration(self, distance_km: float, pace_min_per_km: float) -> float:
        """
        根据距离和配速计算运动时间
        
        Args:
            distance_km: 距离（公里）
            pace_min_per_km: 配速（分钟/公里）
            
        Returns:
            运动时间（秒）
        """
        total_minutes = distance_km * pace_min_per_km
        return round(total_minutes * 60, 0)  # 转换为秒
    
    def calculate_calories(self, distance_km: float, duration_seconds: float) -> int:
        """
        估算消耗的卡路里
        简单计算：每公里约消耗60卡路里
        
        Args:
            distance_km: 距离（公里）
            duration_seconds: 运动时间（秒）
            
        Returns:
            卡路里数
        """
        base_calories = distance_km * 60
        # 根据时间微调（时间越长，消耗越多）
        time_factor = 1.0 + (duration_seconds / 3600 - 0.5) * 0.1
        return int(base_calories * time_factor)
    
    def create_tcx_content(self, date: datetime.date, distance_km: float,
                          duration_seconds: float, calories: int,
                          include_track: bool = True) -> str:
        """
        创建TCX文件内容（可选择是否包含轨迹点）
        
        Args:
            date: 运动日期
            distance_km: 距离（公里）
            duration_seconds: 运动时间（秒）
            calories: 卡路里
            include_track: 是否包含轨迹点
            
        Returns:
            TCX格式的XML字符串
        """
        # 转换距离为米
        distance_meters = distance_km * 1000
        
        # 创建开始时间（假设早上7点开始）
        start_time = datetime.datetime.combine(date, datetime.time(7, 0, 0))
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # 生成轨迹点
        track_xml = ""
        if include_track:
            # 生成轨迹点
            track_points = self.track_generator.generate_smooth_track(distance_km)
            tcx_trackpoints = self.track_generator.generate_tcx_trackpoints(
                track_points, start_time, duration_seconds
            )
            
            # 构建轨迹XML
            track_xml = "<Track>\n"
            for point in tcx_trackpoints:
                track_xml += f"""        <Trackpoint>
          <Time>{point['time']}</Time>
          <Position>
            <LatitudeDegrees>{point['latitude']}</LatitudeDegrees>
            <LongitudeDegrees>{point['longitude']}</LongitudeDegrees>
          </Position>
          <AltitudeMeters>{point['altitude']}</AltitudeMeters>
          <DistanceMeters>{point['distance_meters']}</DistanceMeters>
        </Trackpoint>
"""
            track_xml += "      </Track>\n"
        
        # 创建XML内容
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase xmlns="{self.namespace}" xmlns:xsi="{self.xsi}" xsi:schemaLocation="{self.namespace} {self.namespace}/TrainingCenterDatabasev2.xsd">
  <Activities>
    <Activity Sport="Running">
      <Id>{start_time_str}</Id>
      <Lap StartTime="{start_time_str}">
        <TotalTimeSeconds>{duration_seconds}</TotalTimeSeconds>
        <DistanceMeters>{distance_meters}</DistanceMeters>
        <MaximumSpeed>3.5</MaximumSpeed>
        <Calories>{calories}</Calories>
        <Intensity>Active</Intensity>
        <TriggerMethod>Manual</TriggerMethod>
        {track_xml}      </Lap>
    </Activity>
  </Activities>
  <Author xsi:type="Application_t">
    <Name>Campus Running Data Generator</Name>
    <Build>
      <Version>
        <VersionMajor>1</VersionMajor>
        <VersionMinor>0</VersionMinor>
        <BuildMajor>0</BuildMajor>
        <BuildMinor>0</BuildMinor>
      </Version>
    </Build>
    <LangID>zh</LangID>
    <PartNumber>000-00000-00</PartNumber>
  </Author>
</TrainingCenterDatabase>'''
        
        # 美化XML格式
        dom = minidom.parseString(xml_content)
        return dom.toprettyxml(indent="  ")
    
    def generate_tcx_files(self, start_date: str, end_date: str, min_km: float,
                          output_dir: str = "tcx_files", include_track: bool = True) -> List[str]:
        """
        生成TCX文件
        
        Args:
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            min_km: 最低公里数（周内基准）
            output_dir: 输出目录
            include_track: 是否包含轨迹点
            
        Returns:
            生成的文件路径列表
        """
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成日期范围
        dates = self.generate_date_range(start_date, end_date)
        generated_files = []
        
        print(f"开始生成TCX文件，共{len(dates)}天...")
        
        for date in dates:
            # 计算当日数据
            distance = self.calculate_daily_distance(min_km, date)
            pace = self.generate_pace()
            duration = self.calculate_duration(distance, pace)
            calories = self.calculate_calories(distance, duration)
            
            # 生成文件名
            filename = f"running_{date.strftime('%Y%m%d')}.tcx"
            filepath = os.path.join(output_dir, filename)
            
            # 创建TCX内容
            tcx_content = self.create_tcx_content(date, distance, duration, calories, include_track)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(tcx_content)
            
            generated_files.append(filepath)
            
            # 打印进度
            weekend_flag = "（周末）" if self.is_weekend(date) else ""
            print(f"生成完成: {filename} - {distance}km, {pace}分钟/km, {duration/60:.1f}分钟{weekend_flag}")
        
        print(f"TCX文件生成完成，共{len(generated_files)}个文件")
        return generated_files
    
    def create_zip_archives(self, file_list: List[str], max_size_mb: int = 500,
                           output_dir: str = "tcx_files") -> List[str]:
        """
        创建压缩包，每个不超过指定大小
        如果超过500MB，将超过的部分分到新的压缩包中
        
        Args:
            file_list: 要压缩的文件列表
            max_size_mb: 最大压缩包大小（MB）
            output_dir: 输出目录
            
        Returns:
            生成的压缩包路径列表
        """
        max_size_bytes = max_size_mb * 1024 * 1024
        zip_files = []
        
        # 按文件大小排序，先压缩大文件
        file_list.sort(key=lambda x: os.path.getsize(x), reverse=True)
        
        current_zip_files = []
        zip_index = 1
        
        for file_path in file_list:
            file_size = os.path.getsize(file_path)
            
            # 如果单个文件就超过限制，需要单独处理
            if file_size > max_size_bytes:
                # 先处理当前压缩包中的文件
                if current_zip_files:
                    zip_filename = os.path.join(output_dir, f"tcx_batch_{zip_index}.zip")
                    self._create_zip_file(current_zip_files, zip_filename)
                    zip_files.append(zip_filename)
                    zip_index += 1
                    current_zip_files = []
                
                # 单独压缩大文件
                zip_filename = os.path.join(output_dir, f"tcx_batch_{zip_index}.zip")
                self._create_zip_file([file_path], zip_filename)
                zip_files.append(zip_filename)
                zip_index += 1
                continue
            
            # 检查当前压缩包加上这个文件是否会超过限制
            # 预估压缩后大小（假设压缩率为50%）
            estimated_zip_size = self._estimate_zip_size(current_zip_files + [file_path])
            
            if estimated_zip_size > max_size_bytes and current_zip_files:
                # 创建当前压缩包
                zip_filename = os.path.join(output_dir, f"tcx_batch_{zip_index}.zip")
                self._create_zip_file(current_zip_files, zip_filename)
                zip_files.append(zip_filename)
                
                # 重置
                current_zip_files = []
                zip_index += 1
            
            current_zip_files.append(file_path)
        
        # 处理最后一个压缩包
        if current_zip_files:
            zip_filename = os.path.join(output_dir, f"tcx_batch_{zip_index}.zip")
            self._create_zip_file(current_zip_files, zip_filename)
            zip_files.append(zip_filename)
        
        print(f"压缩包创建完成，共{len(zip_files)}个压缩包")
        return zip_files
    
    def _estimate_zip_size(self, file_list: List[str]) -> int:
        """
        估算压缩后的文件大小
        使用简单的压缩率估算（假设50%压缩率）
        
        Args:
            file_list: 文件列表
            
        Returns:
            估算的压缩后大小（字节）
        """
        total_size = sum(os.path.getsize(f) for f in file_list)
        # 假设压缩率为50%，再加上一些额外的空间
        return int(total_size * 0.5 * 1.1)
    
    def _create_zip_file(self, file_list: List[str], zip_filename: str):
        """创建单个压缩文件"""
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_list:
                # 使用文件名作为压缩包内的路径
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)
        
        # 显示压缩包大小
        zip_size = os.path.getsize(zip_filename) / (1024 * 1024)  # MB
        print(f"创建压缩包: {zip_filename} ({zip_size:.2f}MB, {len(file_list)}个文件)")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='TCX文件自动生成器')
    parser.add_argument('--start-date', required=True, help='开始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', required=True, help='结束日期 (YYYY-MM-DD)')
    parser.add_argument('--min-km', type=float, required=True, help='最低公里数（周内基准）')
    parser.add_argument('--output-dir', default='tcx_files', help='输出目录 (默认: tcx_files)')
    parser.add_argument('--max-zip-size', type=int, default=500, help='最大压缩包大小(MB) (默认: 500)')
    parser.add_argument('--no-track', action='store_true', help='不生成轨迹点')
    
    args = parser.parse_args()
    
    # 创建生成器
    generator = TCXGenerator()
    
    # 生成TCX文件
    tcx_files = generator.generate_tcx_files(
        args.start_date,
        args.end_date,
        args.min_km,
        args.output_dir,
        not args.no_track  # 如果指定了--no-track，则不包含轨迹
    )
    
    # 创建压缩包
    zip_files = generator.create_zip_archives(
        tcx_files,
        args.max_zip_size,
        args.output_dir
    )
    
    print(f"\n任务完成！")
    print(f"生成的TCX文件: {len(tcx_files)}个")
    print(f"生成的压缩包: {len(zip_files)}个")
    print(f"输出目录: {args.output_dir}")
    print(f"包含轨迹: {'否' if args.no_track else '是'}")


if __name__ == "__main__":
    main()