#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
月度TCX文件生成器
按月生成跑步数据，每月50-60公里

作者: 猫娘幽浮喵
"""

import os
import sys
import datetime
import random
from xml.dom import minidom
import zipfile
from typing import List, Tuple
from track_generator import TrackGenerator

# 解决Windows控制台中文乱码问题
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

class MonthlyTCXGenerator:
    """月度TCX文件生成器类"""
    
    def __init__(self):
        self.namespace = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
        self.xsi = "http://www.w3.org/2001/XMLSchema-instance"
        self.track_generator = TrackGenerator()
        
    def get_month_days(self, year: int, month: int) -> List[datetime.date]:
        """获取指定月份的所有日期"""
        start_date = datetime.date(year, month, 1)
        if month == 12:
            end_date = datetime.date(year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)
        
        dates = []
        current = start_date
        while current <= end_date:
            dates.append(current)
            current += datetime.timedelta(days=1)
        
        return dates
    
    def is_weekend(self, date: datetime.date) -> bool:
        """判断是否为周末"""
        return date.weekday() >= 5  # 5=周六, 6=周日
    
    def calculate_monthly_parameters(self, year: int, month: int, target_km: float) -> Tuple[float, int, int, int]:
        """
        计算月度参数
        
        Args:
            year: 年份
            month: 月份
            target_km: 目标公里数
            
        Returns:
            (min_km, running_days, weekday_running_days, weekend_running_days)
        """
        dates = self.get_month_days(year, month)
        weekend_days = sum(1 for d in dates if self.is_weekend(d))
        weekday_days = len(dates) - weekend_days
        
        # 假设每周跑5天，其中周内跑3天，周末跑2天
        # 计算实际跑步天数
        weekday_running_days = min(weekday_days, int(weekday_days * 3/5))
        weekend_running_days = min(weekend_days, int(weekend_days * 2/2))
        running_days = weekday_running_days + weekend_running_days
        
        # 设周内每天跑x公里，周末每天跑1.5x公里
        # 总距离 = weekday_running_days * x + weekend_running_days * 1.5x = target_km
        # x = target_km / (weekday_running_days + weekend_running_days * 1.5)
        if running_days > 0:
            min_km = target_km / (weekday_running_days + weekend_running_days * 1.5)
        else:
            min_km = 0
        
        return min_km, running_days, weekday_running_days, weekend_running_days
    
    def generate_monthly_data(self, year: int, month: int, target_km: float,
                           output_dir: str = "monthly_data", include_track: bool = True) -> List[str]:
        """
        生成月度数据
        
        Args:
            year: 年份
            month: 月份
            target_km: 目标公里数
            output_dir: 输出目录
            include_track: 是否包含轨迹点
            
        Returns:
            生成的文件路径列表
        """
        # 创建输出目录
        month_dir = os.path.join(output_dir, f"{year}_{month:02d}")
        os.makedirs(month_dir, exist_ok=True)
        
        # 计算参数
        min_km, running_days, weekday_running_days, weekend_running_days = self.calculate_monthly_parameters(year, month, target_km)
        
        # 获取月份所有日期
        dates = self.get_month_days(year, month)
        weekend_dates = [d for d in dates if self.is_weekend(d)]
        weekday_dates = [d for d in dates if not self.is_weekend(d)]
        
        # 分别选择周内和周末的跑步日期
        selected_weekday_dates = random.sample(weekday_dates, min(weekday_running_days, len(weekday_dates)))
        selected_weekend_dates = random.sample(weekend_dates, min(weekend_running_days, len(weekend_dates)))
        
        # 合并并排序
        running_dates = selected_weekday_dates + selected_weekend_dates
        running_dates.sort()
        
        generated_files = []
        total_distance = 0
        
        print(f"\n生成 {year}年{month}月 数据:")
        print(f"目标距离: {target_km} 公里")
        print(f"跑步天数: {running_days} 天")
        print(f"预计周内距离: {min_km:.2f}-{min_km+2:.2f} 公里")
        print(f"预计周末距离: {min_km*1.5:.2f}-{(min_km+2)*1.5:.2f} 公里")
        print("-" * 50)
        
        # 预先计算所有跑步距离，确保总距离接近目标
        weekday_distances = [round(random.uniform(min_km, min_km + 1.0), 2) for _ in range(len(selected_weekday_dates))]
        weekend_distances = [round(random.uniform(min_km * 1.5, min_km * 1.5 + 1.5), 2) for _ in range(len(selected_weekend_dates))]
        
        # 计算当前总距离
        current_total = sum(weekday_distances) + sum(weekend_distances)
        
        # 如果总距离与目标差距较大，按比例调整
        if current_total > 0:
            adjustment_factor = target_km / current_total
            weekday_distances = [round(d * adjustment_factor, 2) for d in weekday_distances]
            weekend_distances = [round(d * adjustment_factor, 2) for d in weekend_distances]
        
        # 创建日期到距离的映射
        distance_map = {}
        for i, date in enumerate(selected_weekday_dates):
            distance_map[date] = weekday_distances[i]
        for i, date in enumerate(selected_weekend_dates):
            distance_map[date] = weekend_distances[i]
        
        for date in running_dates:
            # 获取预先计算的距离
            distance = distance_map[date]
            pace = round(random.uniform(7.0, 8.0), 2)
            duration = round(distance * pace * 60, 0)
            calories = int(distance * 60 * (1 + (duration / 3600 - 0.5) * 0.1))
            
            total_distance += distance
            
            # 生成文件名
            filename = f"running_{date.strftime('%Y%m%d')}.tcx"
            filepath = os.path.join(month_dir, filename)
            
            # 创建TCX内容
            tcx_content = self.create_tcx_content(date, distance, duration, calories, include_track)
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(tcx_content)
            
            generated_files.append(filepath)
            
            # 打印进度
            weekend_flag = "（周末）" if self.is_weekend(date) else ""
            print(f"生成完成: {filename} - {distance}km, {pace}分钟/km, {duration/60:.1f}分钟{weekend_flag}")
        
        print(f"\n{year}年{month}月 完成:")
        print(f"实际总距离: {total_distance:.2f} 公里")
        print(f"目标距离: {target_km} 公里")
        print(f"差距: {total_distance - target_km:.2f} 公里")
        print(f"生成文件数: {len(generated_files)} 个")
        
        return generated_files
    
    def create_tcx_content(self, date: datetime.date, distance_km: float,
                          duration_seconds: float, calories: int,
                          include_track: bool = True) -> str:
        """创建TCX文件内容"""
        distance_meters = distance_km * 1000
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
    <Name>Monthly Running Data Generator</Name>
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
        
        dom = minidom.parseString(xml_content)
        return dom.toprettyxml(indent="  ")
    
    def create_monthly_zip(self, file_list: List[str], year: int, month: int, 
                         output_dir: str = "monthly_data") -> str:
        """创建月度压缩包"""
        month_dir = os.path.join(output_dir, f"{year}_{month:02d}")
        zip_filename = os.path.join(month_dir, f"running_{year}_{month:02d}.zip")
        
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in file_list:
                arcname = os.path.basename(file_path)
                zipf.write(file_path, arcname)
        
        zip_size = os.path.getsize(zip_filename) / (1024 * 1024)  # MB
        print(f"创建压缩包: {zip_filename} ({zip_size:.2f}MB, {len(file_list)}个文件)")
        
        return zip_filename

def main():
    """主函数"""
    generator = MonthlyTCXGenerator()
    
    # 生成9月、10月、11月数据
    months = [
        (2025, 9, random.uniform(50, 60)),  # 9月份不超过60公里
        (2025, 10, random.uniform(50, 70)),  # 10月份50-70公里
        (2025, 11, random.uniform(50, 70))   # 11月份50-70公里
    ]
    
    all_files = []
    all_zips = []
    
    print("=" * 60)
    print("月度TCX文件生成器")
    print("生成2025年9月、10月、11月跑步数据")
    print("9月目标: 50-60公里，10-11月目标: 50-70公里")
    print("=" * 60)
    
    for year, month, target_km in months:
        target_km = round(target_km, 1)
        
        # 生成月度数据
        files = generator.generate_monthly_data(year, month, target_km, include_track=True)
        all_files.extend(files)
        
        # 创建月度压缩包
        zip_file = generator.create_monthly_zip(files, year, month)
        all_zips.append(zip_file)
    
    print("\n" + "=" * 60)
    print("所有月份生成完成！")
    print(f"总文件数: {len(all_files)}")
    print(f"总压缩包数: {len(all_zips)}")
    print("=" * 60)

if __name__ == "__main__":
    main()