#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轨迹生成器
根据基础轨迹生成符合要求的跑步轨迹

作者: 猫娘幽浮喵
功能:
1. 轨迹生成为顺时针
2. 根据距离动态调整轨迹
3. 优化圆弧，使得其更加光滑
4. 轨迹需要浮动，有略微随机性，但不能偏离主要轨道
"""

import math
import random
import datetime
from typing import List, Tuple
from .track_analyzer import TrackAnalyzer
from .coordinate_corrector import CoordinateCorrector
from .pace_fluctuator import PaceFluctuator


class TrackGenerator:
    """轨迹生成器类"""
    
    def __init__(self, apply_correction: bool = True):
        self.analyzer = TrackAnalyzer()
        self.base_analysis = self.analyzer.analyze_track()
        
        # 基础参数
        self.base_track = self.base_analysis['coordinates']
        self.base_distance = self.base_analysis['total_distance_meters']
        self.center = self.base_analysis['center']
        self.is_clockwise = self.base_analysis['is_clockwise']
        
        # 随机性参数
        self.max_deviation = 2.0  # 最大偏离距离（米）
        self.smooth_factor = 0.3  # 光滑因子
        
        # 坐标修正器
        self.apply_correction = apply_correction
        if apply_correction:
            self.corrector = CoordinateCorrector()
            # 应用修正到基础轨迹
            self.base_track = self.corrector.correct_coordinates(self.base_track)
            # 更新中心点
            self.center = self.corrector.correct_coordinate(self.center[0], self.center[1])
            print("坐标修正已应用到基础轨迹")
        
        # 配速波动器（初始化为None，在需要时创建）
        self.pace_fluctuator = None
        
    def generate_smooth_track(self, target_distance_km: float, 
                             points_per_km: int = 50,
                             enable_randomness: bool = True) -> List[Tuple[float, float]]:
        """
        生成光滑的轨迹
        
        Args:
            target_distance_km: 目标距离（公里）
            points_per_km: 每公里的轨迹点数
            enable_randomness: 是否启用随机浮动
            
        Returns:
            轨迹点列表 [(经度, 纬度), ...]
        """
        # 计算需要的总圈数
        target_distance_m = target_distance_km * 1000
        total_laps = target_distance_m / self.base_distance
        
        # 计算每圈需要的点数
        points_per_lap = max(10, int(self.base_distance / 1000 * points_per_km))
        total_points = int(points_per_lap * total_laps)
        
        # 生成基础轨迹点
        base_points = self._generate_interpolated_track(points_per_lap)
        
        # 如果需要多圈，重复轨迹
        if total_laps > 1:
            full_laps = int(total_laps)
            remaining_lap_fraction = total_laps - full_laps
            
            # 完整圈
            track_points = []
            for _ in range(full_laps):
                track_points.extend(base_points)
            
            # 最后一部分圈
            if remaining_lap_fraction > 0:
                remaining_points = int(points_per_lap * remaining_lap_fraction)
                track_points.extend(base_points[:remaining_points])
        else:
            # 不足一圈的情况
            track_points = base_points[:total_points]
        
        # 应用随机浮动
        if enable_randomness:
            track_points = self._apply_randomness(track_points)
        
        # 光滑处理
        track_points = self._smooth_track(track_points)
        
        return track_points
    
    def _generate_interpolated_track(self, points_per_lap: int) -> List[Tuple[float, float]]:
        """
        生成插值轨迹点
        
        Args:
            points_per_lap: 每圈的点数
            
        Returns:
            插值后的轨迹点列表
        """
        # 确保轨迹是顺时针
        if not self.is_clockwise:
            base_track = list(reversed(self.base_track))
        else:
            base_track = self.base_track
        
        # 计算每段应该分配的点数
        segment_distances = []
        for i in range(len(base_track)):
            next_idx = (i + 1) % len(base_track)
            distance = self.analyzer.calculate_distance(
                base_track[i], base_track[next_idx]
            )
            segment_distances.append(distance)
        
        total_distance = sum(segment_distances)
        points = []
        
        # 为每段分配点数
        accumulated_distance = 0
        current_segment = 0
        segment_start_distance = 0
        
        for point_idx in range(points_per_lap):
            # 计算当前点应该在的总距离位置
            target_distance = (point_idx / points_per_lap) * total_distance
            
            # 找到当前点所在的段
            while current_segment < len(base_track) - 1 and \
                  target_distance > segment_start_distance + segment_distances[current_segment]:
                segment_start_distance += segment_distances[current_segment]
                current_segment += 1
            
            if current_segment >= len(base_track) - 1:
                current_segment = 0
                segment_start_distance = 0
            
            # 计算在当前段中的位置比例
            segment_progress = (target_distance - segment_start_distance) / segment_distances[current_segment]
            segment_progress = max(0, min(1, segment_progress))  # 确保在[0,1]范围内
            
            # 获取段的起点和终点
            start_point = base_track[current_segment]
            end_point = base_track[(current_segment + 1) % len(base_track)]
            
            # 线性插值
            lon = start_point[0] + (end_point[0] - start_point[0]) * segment_progress
            lat = start_point[1] + (end_point[1] - start_point[1]) * segment_progress
            
            points.append((lon, lat))
        
        return points
    
    def _apply_randomness(self, track_points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        应用随机浮动到轨迹点
        
        Args:
            track_points: 原始轨迹点
            
        Returns:
            应用随机浮动后的轨迹点
        """
        random_points = []
        
        for i, (lon, lat) in enumerate(track_points):
            # 计算到中心点的方向
            dx = lon - self.center[0]
            dy = lat - self.center[1]
            distance_to_center = math.sqrt(dx*dx + dy*dy)
            
            if distance_to_center > 0:
                # 归一化方向向量
                dx /= distance_to_center
                dy /= distance_to_center
                
                # 计算垂直方向（用于切向随机性）
                perp_dx = -dy
                perp_dy = dx
                
                # 径向随机偏移（向内或向外）
                radial_offset = random.uniform(-self.max_deviation, self.max_deviation)
                
                # 切向随机偏移（沿轨迹方向）
                tangential_offset = random.uniform(-self.max_deviation/2, self.max_deviation/2)
                
                # 转换为经纬度偏移
                # 1度经度约等于111320米 * cos(纬度)
                # 1度纬度约等于110540米
                meters_per_degree_lon = 111320 * math.cos(math.radians(lat))
                meters_per_degree_lat = 110540
                
                lon_offset = (dx * radial_offset + perp_dx * tangential_offset) / meters_per_degree_lon
                lat_offset = (dy * radial_offset + perp_dy * tangential_offset) / meters_per_degree_lat
                
                new_lon = lon + lon_offset
                new_lat = lat + lat_offset
                
                random_points.append((new_lon, new_lat))
            else:
                # 如果在中心点，只添加随机偏移
                meters_per_degree_lon = 111320 * math.cos(math.radians(lat))
                meters_per_degree_lat = 110540
                
                lon_offset = random.uniform(-self.max_deviation, self.max_deviation) / meters_per_degree_lon
                lat_offset = random.uniform(-self.max_deviation, self.max_deviation) / meters_per_degree_lat
                
                random_points.append((lon + lon_offset, lat + lat_offset))
        
        return random_points
    
    def _smooth_track(self, track_points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        光滑轨迹点
        
        Args:
            track_points: 原始轨迹点
            
        Returns:
            光滑后的轨迹点
        """
        if len(track_points) < 3:
            return track_points
        
        smoothed_points = []
        
        for i, (lon, lat) in enumerate(track_points):
            if i == 0 or i == len(track_points) - 1:
                # 保留起点和终点
                smoothed_points.append((lon, lat))
            else:
                # 对中间点应用加权平均
                prev_point = track_points[i-1]
                curr_point = track_points[i]
                next_point = track_points[i+1]
                
                # 计算加权平均
                weight_center = 1 - 2 * self.smooth_factor
                weight_neighbors = self.smooth_factor
                
                smoothed_lon = (weight_center * curr_point[0] + 
                              weight_neighbors * prev_point[0] + 
                              weight_neighbors * next_point[0])
                
                smoothed_lat = (weight_center * curr_point[1] + 
                              weight_neighbors * prev_point[1] + 
                              weight_neighbors * next_point[1])
                
                smoothed_points.append((smoothed_lon, smoothed_lat))
        
        return smoothed_points
    
    def generate_tcx_trackpoints(self, track_points: List[Tuple[float, float]],
                                start_time: datetime.datetime, duration_seconds: float,
                                base_pace_min_per_km: float = None,
                                enable_pace_fluctuation: bool = True) -> List[dict]:
        """
        生成TCX格式的轨迹点
        
        Args:
            track_points: 轨迹点列表
            start_time: 开始时间（datetime对象）
            duration_seconds: 总时长（秒）
            base_pace_min_per_km: 基础配速（分钟/公里），如果为None则使用均匀时间分布
            enable_pace_fluctuation: 是否启用配速波动
            
        Returns:
            TCX轨迹点字典列表
        """
        if not track_points:
            return []
        
        # 如果启用配速波动且提供了基础配速
        if enable_pace_fluctuation and base_pace_min_per_km is not None:
            # 创建配速波动器
            if self.pace_fluctuator is None or self.pace_fluctuator.base_pace != base_pace_min_per_km:
                self.pace_fluctuator = PaceFluctuator(base_pace_min_per_km)
            
            # 生成配速曲线
            pace_profile = self.pace_fluctuator.generate_pace_profile(len(track_points))
            
            # 计算每段距离
            segment_distances = []
            for i in range(len(track_points) - 1):
                distance = self.analyzer.calculate_distance(track_points[i], track_points[i + 1])
                segment_distances.append(distance / 1000)  # 转换为公里
            
            # 计算每段的时间
            segment_times = self.pace_fluctuator.generate_segment_times(pace_profile[:-1], segment_distances)
            
            # 生成轨迹点
            trackpoints = []
            current_time = start_time
            
            for i, (lon, lat) in enumerate(track_points):
                # 使用本地时间，不加Z后缀
                point_time_str = current_time.strftime("%Y-%m-%dT%H:%M:%S")
                
                # 计算海拔（模拟值，基于到中心的距离）
                distance_to_center = self.analyzer.calculate_distance(self.center, (lon, lat))
                altitude = 100 + (distance_to_center - self.base_analysis['approximate_radius_meters']) * 0.1
                
                # 计算累计距离
                if i == 0:
                    cumulative_distance = 0
                else:
                    # 使用实际计算的距离而不是线性插值
                    cumulative_distance = sum(self.analyzer.calculate_distance(
                        track_points[j], track_points[j+1]) for j in range(i))
                
                trackpoint = {
                    "time": point_time_str,
                    "latitude": lat,
                    "longitude": lon,
                    "altitude": altitude,
                    "distance_meters": cumulative_distance
                }
                
                trackpoints.append(trackpoint)
                
                # 更新当前时间（除了最后一个点）
                if i < len(track_points) - 1:
                    current_time += datetime.timedelta(seconds=segment_times[i])
            
            return trackpoints
        else:
            # 原有的均匀时间分布逻辑
            time_interval = duration_seconds / len(track_points)
            
            trackpoints = []
            
            for i, (lon, lat) in enumerate(track_points):
                # 计算当前点的时间
                point_time = start_time + datetime.timedelta(seconds=i * time_interval)
                # 使用本地时间，不加Z后缀
                point_time_str = point_time.strftime("%Y-%m-%dT%H:%M:%S")
                
                # 计算海拔（模拟值，基于到中心的距离）
                distance_to_center = self.analyzer.calculate_distance(self.center, (lon, lat))
                altitude = 100 + (distance_to_center - self.base_analysis['approximate_radius_meters']) * 0.1
                
                trackpoint = {
                    "time": point_time_str,
                    "latitude": lat,
                    "longitude": lon,
                    "altitude": altitude,
                    "distance_meters": i * (self.base_distance / len(track_points))
                }
                
                trackpoints.append(trackpoint)
            
            return trackpoints