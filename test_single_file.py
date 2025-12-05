#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单个TCX文件测试生成器
用于快速测试TCX文件生成功能

作者: 猫娘幽浮喵
"""

import os
import sys
import datetime
import random
from xml.dom import minidom

# 解决Windows控制台中文乱码问题
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def generate_single_tcx():
    """生成单个TCX文件用于测试"""
    
    # 设置参数
    date = datetime.date(2023, 1, 1)
    distance_km = 5.0  # 5公里
    pace_min_per_km = 7.5  # 7.5分钟/公里
    duration_seconds = distance_km * pace_min_per_km * 60  # 转换为秒
    calories = int(distance_km * 60)  # 简单计算卡路里
    
    # 转换距离为米
    distance_meters = distance_km * 1000
    
    # 创建开始时间（假设早上7点开始）
    start_time = datetime.datetime.combine(date, datetime.time(7, 0, 0))
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # 创建XML内容
    xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<TrainingCenterDatabase xmlns="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2/TrainingCenterDatabasev2.xsd">
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
      </Lap>
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
    formatted_xml = dom.toprettyxml(indent="  ")
    
    # 保存文件
    filename = "test_running_20230101.tcx"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(formatted_xml)
    
    # 显示文件信息
    file_size = os.path.getsize(filename)
    
    print("=" * 50)
    print("TCX测试文件生成完成！")
    print("=" * 50)
    print(f"文件名: {filename}")
    print(f"文件大小: {file_size} 字节")
    print(f"运动日期: {date}")
    print(f"跑步距离: {distance_km} 公里")
    print(f"配速: {pace_min_per_km} 分钟/公里")
    print(f"运动时间: {duration_seconds/60:.1f} 分钟")
    print(f"消耗卡路里: {calories} 卡")
    print("=" * 50)
    print("您可以使用此文件测试TCX格式的兼容性")
    print("文件已保存在当前目录下")
    
    return filename

def test_zip_function():
    """测试压缩功能"""
    import zipfile
    
    filename = "test_running_20230101.tcx"
    zip_filename = "test_running_20230101.zip"
    
    if os.path.exists(filename):
        # 创建压缩包
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(filename, os.path.basename(filename))
        
        # 显示压缩包信息
        zip_size = os.path.getsize(zip_filename)
        original_size = os.path.getsize(filename)
        compression_ratio = (1 - zip_size / original_size) * 100
        
        print("\n" + "=" * 50)
        print("压缩包测试完成！")
        print("=" * 50)
        print(f"压缩包名: {zip_filename}")
        print(f"原始文件大小: {original_size} 字节")
        print(f"压缩后大小: {zip_size} 字节")
        print(f"压缩率: {compression_ratio:.1f}%")
        print("=" * 50)
        
        return zip_filename
    else:
        print("错误: 找不到测试TCX文件")
        return None

def main():
    """主函数"""
    print("TCX文件生成器 - 单文件测试")
    print("作者: 猫娘幽浮喵")
    print()
    
    # 生成TCX文件
    tcx_file = generate_single_tcx()
    
    # 测试压缩功能
    zip_file = test_zip_function()
    
    print("\n测试完成！您可以检查生成的文件:")
    if tcx_file:
        print(f"1. TCX文件: {tcx_file}")
    if zip_file:
        print(f"2. 压缩包: {zip_file}")
    
    print("\n如果文件正常生成，说明TCX生成器工作正常！")

if __name__ == "__main__":
    main()