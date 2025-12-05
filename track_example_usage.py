#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轨迹功能使用示例
演示如何使用新的轨迹生成功能

作者: 猫娘幽浮喵
"""

import os
import datetime
from tcx_generator import TCXGenerator
from track_generator import TrackGenerator
from track_analyzer import TrackAnalyzer


def example_basic_track_generation():
    """示例1: 基本轨迹生成"""
    print("=== 示例1: 基本轨迹生成 ===")
    
    # 创建轨迹生成器
    generator = TrackGenerator()
    
    # 生成不同距离的轨迹
    distances = [1.0, 3.0, 5.0]  # 公里
    
    for distance in distances:
        track_points = generator.generate_smooth_track(distance)
        print(f"生成 {distance} 公里轨迹: {len(track_points)} 个点")
        
        # 显示前几个点
        print("  前3个点:")
        for i, point in enumerate(track_points[:3]):
            print(f"    点 {i+1}: ({point[0]:.8f}, {point[1]:.8f})")
    
    print()


def example_tcx_with_track():
    """示例2: 生成带轨迹的TCX文件"""
    print("=== 示例2: 生成带轨迹的TCX文件 ===")
    
    # 创建TCX生成器
    generator = TCXGenerator()
    
    # 创建输出目录
    output_dir = "track_example_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成单个带轨迹的TCX文件
    date = datetime.date(2025, 12, 5)
    distance_km = 3.0
    pace_min_per_km = 7.5
    duration_seconds = distance_km * pace_min_per_km * 60
    calories = int(distance_km * 60)
    
    # 生成带轨迹的TCX内容
    tcx_content = generator.create_tcx_content(
        date, distance_km, duration_seconds, calories, include_track=True
    )
    
    # 保存文件
    filename = f"running_with_track_{date.strftime('%Y%m%d')}.tcx"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(tcx_content)
    
    file_size = os.path.getsize(filepath)
    print(f"生成带轨迹的TCX文件: {filename}")
    print(f"文件大小: {file_size} 字节")
    
    # 检查轨迹点数量
    trackpoint_count = tcx_content.count("<Trackpoint>")
    print(f"轨迹点数量: {trackpoint_count}")
    print()


def example_batch_generation():
    """示例3: 批量生成带轨迹的TCX文件"""
    print("=== 示例3: 批量生成带轨迹的TCX文件 ===")
    
    # 创建TCX生成器
    generator = TCXGenerator()
    
    # 创建输出目录
    output_dir = "track_batch_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成一周的跑步数据
    tcx_files = generator.generate_tcx_files(
        start_date="2025-12-01",
        end_date="2025-12-07",
        min_km=3.0,
        output_dir=output_dir,
        include_track=True  # 包含轨迹点
    )
    
    print(f"生成了 {len(tcx_files)} 个带轨迹的TCX文件")
    
    # 显示文件信息
    for file_path in tcx_files:
        file_size = os.path.getsize(file_path)
        filename = os.path.basename(file_path)
        
        # 检查轨迹点数量
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            trackpoint_count = content.count("<Trackpoint>")
        
        print(f"{filename}: {file_size} 字节, {trackpoint_count} 个轨迹点")
    
    print()


def example_track_comparison():
    """示例4: 轨迹对比（带随机性 vs 不带随机性）"""
    print("=== 示例4: 轨迹对比（带随机性 vs 不带随机性） ===")
    
    # 创建轨迹生成器
    generator = TrackGenerator()
    
    # 生成相同距离的两种轨迹
    distance_km = 3.0
    
    # 带随机性的轨迹
    track_with_randomness = generator.generate_smooth_track(
        distance_km, enable_randomness=True
    )
    
    # 不带随机性的轨迹
    track_without_randomness = generator.generate_smooth_track(
        distance_km, enable_randomness=False
    )
    
    print(f"生成 {distance_km} 公里轨迹:")
    print(f"  带随机性: {len(track_with_randomness)} 个点")
    print(f"  不带随机性: {len(track_without_randomness)} 个点")
    
    # 比较前几个点
    print("\n前3个点对比:")
    for i in range(min(3, len(track_with_randomness), len(track_without_randomness))):
        with_rand = track_with_randomness[i]
        without_rand = track_without_randomness[i]
        
        # 计算偏差（米）
        deviation = generator.analyzer.calculate_distance(with_rand, without_rand)
        
        print(f"  点 {i+1}:")
        print(f"    带随机性: ({with_rand[0]:.8f}, {with_rand[1]:.8f})")
        print(f"    不带随机性: ({without_rand[0]:.8f}, {without_rand[1]:.8f})")
        print(f"    偏差: {deviation:.2f} 米")
    
    print()


def example_command_line_usage():
    """示例5: 命令行使用方法"""
    print("=== 示例5: 命令行使用方法 ===")
    
    print("生成带轨迹的TCX文件:")
    print("python tcx_generator.py --start-date 2025-12-01 --end-date 2025-12-07 --min-km 3.0 --output-dir track_cli_output")
    print()
    
    print("生成不带轨迹的TCX文件:")
    print("python tcx_generator.py --start-date 2025-12-01 --end-date 2025-12-07 --min-km 3.0 --output-dir track_cli_output --no-track")
    print()
    
    print("使用月度生成器（默认带轨迹）:")
    print("python monthly_generator.py")
    print()


def main():
    """主函数"""
    print("=" * 60)
    print("轨迹功能使用示例")
    print("=" * 60)
    print()
    
    try:
        example_basic_track_generation()
        example_tcx_with_track()
        example_batch_generation()
        example_track_comparison()
        example_command_line_usage()
        
        print("=" * 60)
        print("所有示例运行完成！")
        print("=" * 60)
        print()
        print("功能特性总结:")
        print("1. ✓ 轨迹生成为顺时针")
        print("2. ✓ 根据距离动态调整轨迹")
        print("3. ✓ 优化圆弧，使得其更加光滑")
        print("4. ✓ 轨迹需要浮动，有略微随机性，但不能偏离主要轨道")
        print()
        print("生成的文件保存在以下目录:")
        print("- track_example_output/: 单个带轨迹TCX文件示例")
        print("- track_batch_output/: 批量生成的带轨迹TCX文件")
        print("- test_track_output/: 测试文件")
        print("- test_batch_output/: 批量测试文件")
        
    except Exception as e:
        print(f"示例运行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()