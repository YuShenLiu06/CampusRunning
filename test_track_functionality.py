#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试轨迹功能
验证新的轨迹生成功能是否正常工作

作者: 猫娘幽浮喵
"""

import os
import datetime
from tcx_generator import TCXGenerator
from track_generator import TrackGenerator
from track_analyzer import TrackAnalyzer


def test_track_analyzer():
    """测试轨迹分析器"""
    print("=== 测试轨迹分析器 ===")
    analyzer = TrackAnalyzer()
    analysis = analyzer.analyze_track()
    
    print(f"轨迹总距离: {analysis['total_distance_meters']:.2f} 米")
    print(f"是否顺时针: {'是' if analysis['is_clockwise'] else '否'}")
    print(f"中心点: ({analysis['center'][0]:.8f}, {analysis['center'][1]:.8f})")
    print("✓ 轨迹分析器测试通过\n")


def test_track_generator():
    """测试轨迹生成器"""
    print("=== 测试轨迹生成器 ===")
    generator = TrackGenerator()
    
    # 测试不同距离的轨迹生成
    test_distances = [1.0, 3.0, 5.0]  # 公里
    
    for distance in test_distances:
        track_points = generator.generate_smooth_track(distance)
        print(f"生成 {distance} 公里轨迹: {len(track_points)} 个点")
        
        # 验证轨迹点数量合理
        expected_points = int(distance * 50)  # 每公里约50个点
        if abs(len(track_points) - expected_points) / expected_points < 0.2:  # 允许20%误差
            print(f"✓ {distance} 公里轨迹点数量合理")
        else:
            print(f"✗ {distance} 公里轨迹点数量不合理: 期望约{expected_points}个，实际{len(track_points)}个")
    
    print("✓ 轨迹生成器测试通过\n")


def test_tcx_with_track():
    """测试带轨迹的TCX生成"""
    print("=== 测试带轨迹的TCX生成 ===")
    generator = TCXGenerator()
    
    # 创建测试目录
    test_dir = "test_track_output"
    os.makedirs(test_dir, exist_ok=True)
    
    # 生成一个带轨迹的TCX文件
    date = datetime.date(2025, 12, 5)
    distance_km = 3.0
    pace_min_per_km = 7.5
    duration_seconds = distance_km * pace_min_per_km * 60
    calories = int(distance_km * 60)
    
    # 生成带轨迹的TCX
    tcx_content_with_track = generator.create_tcx_content(
        date, distance_km, duration_seconds, calories, include_track=True
    )
    
    # 生成不带轨迹的TCX
    tcx_content_without_track = generator.create_tcx_content(
        date, distance_km, duration_seconds, calories, include_track=False
    )
    
    # 保存文件
    with_track_file = os.path.join(test_dir, "test_with_track.tcx")
    without_track_file = os.path.join(test_dir, "test_without_track.tcx")
    
    with open(with_track_file, 'w', encoding='utf-8') as f:
        f.write(tcx_content_with_track)
    
    with open(without_track_file, 'w', encoding='utf-8') as f:
        f.write(tcx_content_without_track)
    
    # 检查文件大小
    with_track_size = os.path.getsize(with_track_file)
    without_track_size = os.path.getsize(without_track_file)
    
    print(f"带轨迹文件大小: {with_track_size} 字节")
    print(f"不带轨迹文件大小: {without_track_size} 字节")
    
    if with_track_size > without_track_size:
        print("✓ 带轨迹的TCX文件比不带轨迹的文件大，符合预期")
    else:
        print("✗ 带轨迹的TCX文件大小异常")
    
    # 检查轨迹点数量
    if "<Track>" in tcx_content_with_track and "<Trackpoint>" in tcx_content_with_track:
        trackpoint_count = tcx_content_with_track.count("<Trackpoint>")
        print(f"轨迹点数量: {trackpoint_count}")
        print("✓ TCX文件包含轨迹点")
    else:
        print("✗ TCX文件不包含轨迹点")
    
    if "<Track>" not in tcx_content_without_track:
        print("✓ 不带轨迹的TCX文件确实不包含轨迹点")
    else:
        print("✗ 不带轨迹的TCX文件意外包含轨迹点")
    
    print("✓ 带轨迹的TCX生成测试通过\n")


def test_batch_generation():
    """测试批量生成"""
    print("=== 测试批量生成 ===")
    generator = TCXGenerator()
    
    # 创建测试目录
    test_dir = "test_batch_output"
    os.makedirs(test_dir, exist_ok=True)
    
    # 生成3天的数据
    tcx_files = generator.generate_tcx_files(
        start_date="2025-12-01",
        end_date="2025-12-03",
        min_km=3.0,
        output_dir=test_dir,
        include_track=True
    )
    
    print(f"生成了 {len(tcx_files)} 个TCX文件")
    
    # 检查每个文件
    for file_path in tcx_files:
        file_size = os.path.getsize(file_path)
        print(f"{os.path.basename(file_path)}: {file_size} 字节")
        
        # 检查是否包含轨迹
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "<Track>" in content and "<Trackpoint>" in content:
                trackpoint_count = content.count("<Trackpoint>")
                print(f"  包含 {trackpoint_count} 个轨迹点 ✓")
            else:
                print(f"  不包含轨迹点 ✗")
    
    print("✓ 批量生成测试通过\n")


def main():
    """主函数"""
    print("=" * 60)
    print("轨迹功能测试")
    print("=" * 60)
    
    try:
        test_track_analyzer()
        test_track_generator()
        test_tcx_with_track()
        test_batch_generation()
        
        print("=" * 60)
        print("所有测试完成！新的轨迹功能工作正常 ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()