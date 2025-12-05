#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
校园跑步数据生成器 - 主程序
用于生成校园跑步数据的TCX格式文件

作者: 猫娘幽浮喵
功能:
1. 根据时间范围和每日公里数范围生成TCX文件
2. 根据时间和总公里数生成匹配数据的TCX文件
3. 配速、总公里数、跑步开始时间范围可自定义
"""

import os
import sys
import argparse
import datetime
from typing import List, Dict

# 解决Windows控制台中文乱码问题
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# 导入自定义模块
from src.tcx_generator import TCXGenerator
from src.data_planner import DataPlanner


def generate_by_daily_range(args):
    """根据每日公里数范围生成TCX文件"""
    print("=" * 60)
    print("根据每日公里数范围生成TCX文件")
    print("=" * 60)
    
    # 创建TCX生成器
    generator = TCXGenerator(apply_coordinate_correction=not args.no_correction)
    
    # 生成TCX文件
    tcx_files = generator.generate_tcx_files(
        start_date=args.start_date,
        end_date=args.end_date,
        min_km=args.min_km,
        max_km=args.max_km,
        min_pace=args.min_pace,
        max_pace=args.max_pace,
        start_hour_range=(args.start_hour_min, args.start_hour_max),
        output_dir=args.output_dir,
        include_track=not args.no_track
    )
    
    print(f"\n任务完成！")
    print(f"生成的TCX文件: {len(tcx_files)}个")
    print(f"输出目录: {args.output_dir}")
    print(f"包含轨迹: {'否' if args.no_track else '是'}")
    
    # 如果需要打包成压缩包
    if args.zip:
        zip_filename = f"tcx_files_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(args.output_dir, zip_filename)
        generator.create_zip_archive(tcx_files, zip_path)
        print(f"压缩包已创建: {zip_path}")
    
    return tcx_files


def generate_by_total_km(args):
    """根据总公里数生成匹配数据的TCX文件"""
    print("=" * 60)
    print("根据总公里数生成匹配数据的TCX文件")
    print("=" * 60)
    
    # 创建数据规划器
    planner = DataPlanner(apply_coordinate_correction=not args.no_correction)
    
    # 生成跑步计划
    plan = planner.generate_running_plan(
        start_date=args.start_date,
        end_date=args.end_date,
        total_km=args.total_km,
        min_daily_km=args.min_daily_km,
        max_daily_km=args.max_daily_km,
        weekend_factor=args.weekend_factor,
        rest_days_per_week=args.rest_days_per_week
    )
    
    # 打印计划摘要
    planner.print_plan_summary(plan)
    
    # 根据计划生成TCX文件
    tcx_files = planner.generate_tcx_from_plan(
        plan=plan,
        min_pace=args.min_pace,
        max_pace=args.max_pace,
        start_hour_range=(args.start_hour_min, args.start_hour_max),
        output_dir=args.output_dir,
        include_track=not args.no_track
    )
    
    print(f"\n任务完成！")
    print(f"生成的TCX文件: {len(tcx_files)}个")
    print(f"输出目录: {args.output_dir}")
    print(f"包含轨迹: {'否' if args.no_track else '是'}")
    
    # 如果需要打包成压缩包
    if args.zip:
        zip_filename = f"tcx_files_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(args.output_dir, zip_filename)
        generator = TCXGenerator(apply_coordinate_correction=not args.no_correction)
        generator.create_zip_archive(tcx_files, zip_path)
        print(f"压缩包已创建: {zip_path}")
    
    return tcx_files


def generate_single_file(args):
    """生成单个TCX文件"""
    print("=" * 60)
    print("生成单个TCX文件")
    print("=" * 60)
    
    # 创建TCX生成器
    generator = TCXGenerator(apply_coordinate_correction=not args.no_correction)
    
    # 解析日期
    date = datetime.datetime.strptime(args.date, "%Y-%m-%d").date()
    
    # 解析配速
    pace = None
    if args.pace:
        pace = float(args.pace)
    
    # 生成单个TCX文件
    tcx_file = generator.generate_single_tcx(
        date=date,
        distance_km=args.distance,
        pace_min_per_km=pace,
        start_hour=args.start_hour,
        output_dir=args.output_dir,
        include_track=not args.no_track
    )
    
    print(f"\n任务完成！")
    print(f"生成的TCX文件: {tcx_file}")
    print(f"输出目录: {args.output_dir}")
    print(f"包含轨迹: {'否' if args.no_track else '是'}")
    
    # 如果需要打包成压缩包
    if args.zip:
        zip_filename = f"tcx_files_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        zip_path = os.path.join(args.output_dir, zip_filename)
        generator.create_zip_archive([tcx_file], zip_path)
        print(f"压缩包已创建: {zip_path}")
    
    return [tcx_file]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='校园跑步数据生成器')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # 每日公里数范围生成命令
    daily_parser = subparsers.add_parser('daily', help='根据每日公里数范围生成TCX文件')
    daily_parser.add_argument('--start-date', required=True, help='开始日期 (YYYY-MM-DD)')
    daily_parser.add_argument('--end-date', required=True, help='结束日期 (YYYY-MM-DD)')
    daily_parser.add_argument('--min-km', type=float, required=True, help='最低公里数（周内基准）')
    daily_parser.add_argument('--max-km', type=float, required=True, help='最高公里数（周内基准）')
    daily_parser.add_argument('--min-pace', type=float, default=7.0, help='最快配速（分钟/公里） (默认: 7.0)')
    daily_parser.add_argument('--max-pace', type=float, default=8.0, help='最慢配速（分钟/公里） (默认: 8.0)')
    daily_parser.add_argument('--start-hour-min', type=int, default=6, help='最早开始时间（小时） (默认: 6)')
    daily_parser.add_argument('--start-hour-max', type=int, default=8, help='最晚开始时间（小时） (默认: 8)')
    daily_parser.add_argument('--output-dir', default='output', help='输出目录 (默认: output)')
    daily_parser.add_argument('--no-track', action='store_true', help='不生成轨迹点')
    daily_parser.add_argument('--no-correction', action='store_true', help='不应用坐标修正')
    daily_parser.add_argument('--zip', action='store_true', help='将生成的TCX文件打包成ZIP压缩包')
    
    # 总公里数生成命令
    total_parser = subparsers.add_parser('total', help='根据总公里数生成匹配数据的TCX文件')
    total_parser.add_argument('--start-date', required=True, help='开始日期 (YYYY-MM-DD)')
    total_parser.add_argument('--end-date', required=True, help='结束日期 (YYYY-MM-DD)')
    total_parser.add_argument('--total-km', type=float, required=True, help='总公里数')
    total_parser.add_argument('--min-daily-km', type=float, default=2.0, help='每日最低公里数 (默认: 2.0)')
    total_parser.add_argument('--max-daily-km', type=float, default=8.0, help='每日最高公里数 (默认: 8.0)')
    total_parser.add_argument('--weekend-factor', type=float, default=1.5, help='周末距离是周内的倍数 (默认: 1.5)')
    total_parser.add_argument('--rest-days-per-week', type=int, default=1, help='每周休息天数 (默认: 1)')
    total_parser.add_argument('--min-pace', type=float, default=7.0, help='最快配速（分钟/公里） (默认: 7.0)')
    total_parser.add_argument('--max-pace', type=float, default=8.0, help='最慢配速（分钟/公里） (默认: 8.0)')
    total_parser.add_argument('--start-hour-min', type=int, default=6, help='最早开始时间（小时） (默认: 6)')
    total_parser.add_argument('--start-hour-max', type=int, default=8, help='最晚开始时间（小时） (默认: 8)')
    total_parser.add_argument('--output-dir', default='output', help='输出目录 (默认: output)')
    total_parser.add_argument('--no-track', action='store_true', help='不生成轨迹点')
    total_parser.add_argument('--no-correction', action='store_true', help='不应用坐标修正')
    total_parser.add_argument('--zip', action='store_true', help='将生成的TCX文件打包成ZIP压缩包')
    
    # 单个文件生成命令
    single_parser = subparsers.add_parser('single', help='生成单个TCX文件')
    single_parser.add_argument('--date', required=True, help='日期 (YYYY-MM-DD)')
    single_parser.add_argument('--distance', type=float, required=True, help='距离（公里）')
    single_parser.add_argument('--pace', type=float, help='配速（分钟/公里），如果不指定则随机生成')
    single_parser.add_argument('--start-hour', type=int, default=7, help='开始时间（小时） (默认: 7)')
    single_parser.add_argument('--output-dir', default='output', help='输出目录 (默认: output)')
    single_parser.add_argument('--no-track', action='store_true', help='不生成轨迹点')
    single_parser.add_argument('--no-correction', action='store_true', help='不应用坐标修正')
    single_parser.add_argument('--zip', action='store_true', help='将生成的TCX文件打包成ZIP压缩包')
    
    args = parser.parse_args()
    
    # 根据命令执行相应功能
    if args.command == 'daily':
        generate_by_daily_range(args)
    elif args.command == 'total':
        generate_by_total_km(args)
    elif args.command == 'single':
        generate_single_file(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()