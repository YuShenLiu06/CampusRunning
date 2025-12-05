#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
坐标修正器
用于修正GCJ-02坐标数据的误差，通过平移消除误差
作者: 猫娘幽浮喵
"""

import math
from typing import Tuple, List


class CoordinateCorrector:
    """坐标修正器类"""
    
    def __init__(self):
        # 当前坐标中心点（从track_analyzer.py中的base_coordinates计算得出）
        self.current_center = (106.6594155297, 26.4517970862)
        
        # 软件中显示的中心点（目标位置）
        self.target_center = (106.66302911870878, 26.44820719269293)
        
        # 计算偏移量（需要向西北方向移动，即经度减小，纬度增加）
        # 当前坐标需要向西北移动，使得软件中显示的位置与实际位置一致
        
        # 当前中心点
        current_lon, current_lat = self.current_center
        # 目标中心点
        target_lon, target_lat = self.target_center
        
        # 计算偏移量（向西北方向移动）
        self.lon_offset = current_lon - target_lon  # 当前经度 - 目标经度（向西）
        self.lat_offset = current_lat - target_lat  # 当前纬度 - 目标纬度（向北）
        
        # 转换为米（用于理解）
        meters_per_degree_lat = 110540
        meters_per_degree_lon = 111320 * math.cos(math.radians(self.current_center[1]))
        
        lon_offset_meters = self.lon_offset * meters_per_degree_lon
        lat_offset_meters = self.lat_offset * meters_per_degree_lat
        
        # 计算总距离和方向
        total_distance = math.sqrt(lon_offset_meters**2 + lat_offset_meters**2)
        direction = math.atan2(lat_offset_meters, lon_offset_meters) * 180 / math.pi
        
        # 判断方向
        if direction >= 337.5 or direction < 22.5:
            dir_text = '东'
        elif 22.5 <= direction < 67.5:
            dir_text = '东北'
        elif 67.5 <= direction < 112.5:
            dir_text = '北'
        elif 112.5 <= direction < 157.5:
            dir_text = '西北'
        elif 157.5 <= direction < 202.5:
            dir_text = '西'
        elif 202.5 <= direction < 247.5:
            dir_text = '西南'
        elif 247.5 <= direction < 292.5:
            dir_text = '南'
        else:
            dir_text = '东南'
             
        print(f"坐标修正器初始化完成: 向{dir_text}方向偏移 {total_distance:.2f} 米")
    
    def correct_coordinate(self, lon: float, lat: float) -> Tuple[float, float]:
        """
        修正单个坐标点
        
        Args:
            lon: 原始经度
            lat: 原始纬度
            
        Returns:
            修正后的坐标 (经度, 纬度)
        """
        corrected_lon = lon + self.lon_offset
        corrected_lat = lat + self.lat_offset
        
        return (corrected_lon, corrected_lat)
    
    def correct_coordinates(self, coordinates: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """
        修正坐标列表
        
        Args:
            coordinates: 原始坐标列表 [(经度, 纬度), ...]
            
        Returns:
            修正后的坐标列表
        """
        corrected_coordinates = []
        
        for lon, lat in coordinates:
            corrected_lon, corrected_lat = self.correct_coordinate(lon, lat)
            corrected_coordinates.append((corrected_lon, corrected_lat))
        
        return corrected_coordinates
    
    def apply_inverse_correction(self, lon: float, lat: float) -> Tuple[float, float]:
        """
        应用反向修正（将修正后的坐标还原为原始坐标）
        
        Args:
            lon: 修正后的经度
            lat: 修正后的纬度
            
        Returns:
            原始坐标 (经度, 纬度)
        """
        original_lon = lon + self.lon_offset  # 反向操作（向西的反向是向东）
        original_lat = lat + self.lat_offset  # 反向操作（向北的反向是向南）
        
        return (original_lon, original_lat)