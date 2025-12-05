#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
计算TCX生成参数
用于计算达到指定总里程所需的min_km参数

作者: 猫娘幽浮喵
"""

import datetime
import sys

# 解决Windows控制台中文乱码问题
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

def calculate_parameters():
    """计算参数"""
    # 时间范围
    start_date = datetime.date(2025, 9, 1)
    end_date = datetime.date(2025, 11, 1)
    
    # 计算总天数和周末/周内天数
    total_days = (end_date - start_date).days + 1
    weekend_days = 0
    weekday_days = 0
    
    current = start_date
    while current <= end_date:
        if current.weekday() >= 5:  # 周末
            weekend_days += 1
        else:
            weekday_days += 1
        current += datetime.timedelta(days=1)
    
    # 目标总里程
    target_total_km = 140
    
    # 计算合适的min_km参数
    # 设周内每天跑x公里，周末每天跑1.5x公里
    # 总距离 = weekday_days * x + weekend_days * 1.5x = target_total_km
    # x = target_total_km / (weekday_days + weekend_days * 1.5)
    min_km = target_total_km / (weekday_days + weekend_days * 1.5)
    
    print("=" * 50)
    print("TCX生成参数计算结果")
    print("=" * 50)
    print(f"时间范围: {start_date} 至 {end_date}")
    print(f"总天数: {total_days} 天")
    print(f"周内天数: {weekday_days} 天")
    print(f"周末天数: {weekend_days} 天")
    print(f"目标总里程: {target_total_km} 公里")
    print()
    print(f"建议的min_km参数: {min_km:.2f}")
    print(f"预期周内距离: {min_km:.2f}-{min_km+2:.2f} 公里")
    print(f"预期周末距离: {min_km*1.5:.2f}-{(min_km+2)*1.5:.2f} 公里")
    print()
    
    # 生成命令
    print("推荐的生成命令:")
    print(f'python tcx_generator.py --start-date 2025-09-01 --end-date 2025-11-01 --min-km {min_km:.2f} --output-dir running_data_2025')
    print("=" * 50)
    
    return min_km

if __name__ == "__main__":
    calculate_parameters()