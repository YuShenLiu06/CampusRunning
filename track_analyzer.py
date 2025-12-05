#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轨迹分析器
分析提供的经纬度坐标，用于理解操场轨迹特征

作者: 猫娘幽浮喵
"""

import math
from typing import List, Tuple

class TrackAnalyzer:
    """轨迹分析器类"""
    
    def __init__(self):
        # 主人提供的操场经纬度坐标
        self.base_coordinates = [
            (106.6591413213796, 26.45129327365839),
            (106.65903260437665, 26.45160613825947),
            (106.65897824587523, 26.451793856595508),
            (106.65892647586247, 26.451993162220376),
            (106.65891639149515, 26.452180879961013),
            (106.65901475450505, 26.452278214935735),
            (106.65915453353261, 26.45238018483626),
            (106.65935643657872, 26.452410312215633),
            (106.65954280861615, 26.45237328086079),
            (106.6596256405976, 26.45232693091138),
            (106.65967741059592, 26.45218092841834),
            (106.65971623810833, 26.45203724329523),
            (106.65976024262193, 26.4518981929895),
            (106.65980936669962, 26.45171279227931),
            (106.65984819419236, 26.451585329168722),
            (106.6598947871995, 26.451420785621714),
            (106.65979901266735, 26.451334689893496),
            (106.659646872243, 26.451251259238074),
            (106.65946050020943, 26.451204908836818),
            (106.65930015181345, 26.451212730335623),
            (106.65912413379829, 26.451263715777763)
        ]
        
    def calculate_distance(self, point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """
        计算两点之间的距离（米）
        使用Haversine公式计算球面距离
        
        Args:
            point1: (经度, 纬度)
            point2: (经度, 纬度)
            
        Returns:
            距离（米）
        """
        # 地球半径（米）
        R = 6371000
        
        # 转换为弧度
        lon1, lat1 = math.radians(point1[0]), math.radians(point1[1])
        lon2, lat2 = math.radians(point2[0]), math.radians(point2[1])
        
        # Haversine公式
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    
    def calculate_total_distance(self, coordinates: List[Tuple[float, float]]) -> float:
        """
        计算轨迹总距离
        
        Args:
            coordinates: 坐标点列表
            
        Returns:
            总距离（米）
        """
        total_distance = 0
        for i in range(len(coordinates) - 1):
            total_distance += self.calculate_distance(coordinates[i], coordinates[i + 1])
        
        # 加上最后一点到第一点的距离（形成闭合环）
        total_distance += self.calculate_distance(coordinates[-1], coordinates[0])
        
        return total_distance
    
    def analyze_track(self) -> dict:
        """
        分析操场轨迹特征
        
        Returns:
            包含轨迹分析结果的字典
        """
        # 计算总距离
        total_distance = self.calculate_total_distance(self.base_coordinates)
        
        # 计算各段距离
        segment_distances = []
        for i in range(len(self.base_coordinates)):
            next_idx = (i + 1) % len(self.base_coordinates)
            segment_distance = self.calculate_distance(
                self.base_coordinates[i], 
                self.base_coordinates[next_idx]
            )
            segment_distances.append(segment_distance)
        
        # 计算中心点
        center_lon = sum(coord[0] for coord in self.base_coordinates) / len(self.base_coordinates)
        center_lat = sum(coord[1] for coord in self.base_coordinates) / len(self.base_coordinates)
        
        # 计算到中心点的平均距离（近似半径）
        avg_radius = sum(self.calculate_distance((center_lon, center_lat), coord) 
                        for coord in self.base_coordinates) / len(self.base_coordinates)
        
        # 判断是否为顺时针
        # 使用叉积判断轨迹方向
        clockwise = self.is_clockwise(self.base_coordinates)
        
        return {
            "total_distance_meters": total_distance,
            "total_distance_km": round(total_distance / 1000, 3),
            "segment_distances": segment_distances,
            "num_points": len(self.base_coordinates),
            "center": (center_lon, center_lat),
            "approximate_radius_meters": avg_radius,
            "is_clockwise": clockwise,
            "coordinates": self.base_coordinates
        }
    
    def is_clockwise(self, coordinates: List[Tuple[float, float]]) -> bool:
        """
        判断轨迹是否为顺时针方向
        
        Args:
            coordinates: 坐标点列表
            
        Returns:
            True表示顺时针，False表示逆时针
        """
        # 使用Shoelace公式计算多边形面积
        # 如果面积为正，则为逆时针；如果为负，则为顺时针
        area = 0
        n = len(coordinates)
        
        for i in range(n):
            j = (i + 1) % n
            area += coordinates[i][0] * coordinates[j][1]
            area -= coordinates[j][0] * coordinates[i][1]
        
        return area < 0
    
    def print_analysis(self):
        """打印轨迹分析结果"""
        analysis = self.analyze_track()
        
        print("=== 操场轨迹分析结果 ===")
        print(f"轨迹点数量: {analysis['num_points']}")
        print(f"总距离: {analysis['total_distance_meters']:.2f} 米 ({analysis['total_distance_km']} 公里)")
        print(f"近似半径: {analysis['approximate_radius_meters']:.2f} 米")
        print(f"中心点: ({analysis['center'][0]:.8f}, {analysis['center'][1]:.8f})")
        print(f"方向: {'顺时针' if analysis['is_clockwise'] else '逆时针'}")
        
        print("\n各段距离（米）:")
        for i, distance in enumerate(analysis['segment_distances']):
            print(f"  段 {i+1}: {distance:.2f} 米")
        
        print("\n原始坐标点:")
        for i, (lon, lat) in enumerate(analysis['coordinates']):
            print(f"  点 {i+1}: ({lon:.8f}, {lat:.8f})")


if __name__ == "__main__":
    analyzer = TrackAnalyzer()
    analyzer.print_analysis()