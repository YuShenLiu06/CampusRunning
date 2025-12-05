#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据规划器
根据时间和总公里数生成匹配的跑步数据

作者: 猫娘幽浮喵
功能:
1. 根据时间范围和总公里数，智能分配每日跑步距离
2. 考虑周末与周内的差异
3. 提供灵活的参数配置
"""

import datetime
import random
from typing import List, Dict, Tuple
from .tcx_generator import TCXGenerator


class DataPlanner:
    """数据规划器类"""
    
    def __init__(self, apply_coordinate_correction: bool = True):
        self.tcx_generator = TCXGenerator(apply_coordinate_correction=apply_coordinate_correction)
        
    def generate_running_plan(self, start_date: str, end_date: str, 
                           total_km: float, min_daily_km: float = 2.0,
                           max_daily_km: float = 8.0, 
                           weekend_factor: float = 1.5,
                           rest_days_per_week: int = 1) -> Dict:
        """
        生成跑步计划
        
        Args:
            start_date: 开始日期，格式：YYYY-MM-DD
            end_date: 结束日期，格式：YYYY-MM-DD
            total_km: 总公里数
            min_daily_km: 每日最低公里数
            max_daily_km: 每日最高公里数
            weekend_factor: 周末距离是周内的倍数
            rest_days_per_week: 每周休息天数
            
        Returns:
            包含跑步计划的字典
        """
        # 解析日期
        start = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        
        # 生成日期范围
        dates = []
        current = start
        while current <= end:
            dates.append(current)
            current += datetime.timedelta(days=1)
        
        # 分类工作日和周末
        weekdays = [d for d in dates if d.weekday() < 5]  # 0-4为工作日
        weekends = [d for d in dates if d.weekday() >= 5]  # 5-6为周末
        
        # 计算总天数和跑步天数
        total_days = len(dates)
        running_days = total_days - (total_days // 7) * rest_days_per_week
        
        # 计算平均每日距离
        avg_daily_km = total_km / running_days if running_days > 0 else 0
        
        # 计算工作日和周末的平均距离
        # 设工作日距离为x，周末距离为weekend_factor*x
        # 总距离 = 工作日数量 * x + 周末数量 * weekend_factor * x
        # x = 总距离 / (工作日数量 + 周末数量 * weekend_factor)
        if len(weekdays) + len(weekends) * weekend_factor > 0:
            weekday_avg = total_km / (len(weekdays) + len(weekends) * weekend_factor)
            weekend_avg = weekday_avg * weekend_factor
        else:
            weekday_avg = avg_daily_km
            weekend_avg = avg_daily_km * weekend_factor
        
        # 确保平均距离在合理范围内
        weekday_avg = max(min_daily_km, min(max_daily_km, weekday_avg))
        weekend_avg = max(min_daily_km, min(max_daily_km, weekend_avg))
        
        # 生成每日跑步计划
        daily_plan = {}
        
        # 为工作日分配距离
        for date in weekdays:
            # 添加随机浮动
            daily_distance = random.uniform(weekday_avg * 0.8, weekday_avg * 1.2)
            daily_distance = max(min_daily_km, min(max_daily_km, daily_distance))
            daily_plan[date] = round(daily_distance, 2)
        
        # 为周末分配距离
        for date in weekends:
            # 添加随机浮动
            daily_distance = random.uniform(weekend_avg * 0.8, weekend_avg * 1.2)
            daily_distance = max(min_daily_km, min(max_daily_km, daily_distance))
            daily_plan[date] = round(daily_distance, 2)
        
        # 随机选择休息日
        if rest_days_per_week > 0:
            weeks = {}
            for date in dates:
                week_num = (date - start).days // 7
                if week_num not in weeks:
                    weeks[week_num] = []
                weeks[week_num].append(date)
            
            for week_dates in weeks.values():
                # 随机选择休息日
                rest_days = random.sample(week_dates, min(rest_days_per_week, len(week_dates)))
                for rest_day in rest_days:
                    if rest_day in daily_plan:
                        del daily_plan[rest_day]
        
        # 计算实际总距离
        actual_total = sum(daily_plan.values())
        
        # 如果实际总距离与目标有较大差异，进行调整
        if abs(actual_total - total_km) > total_km * 0.05:  # 5%的容差
            # 计算调整因子
            adjustment_factor = total_km / actual_total
            
            # 调整每日距离
            for date in daily_plan:
                daily_plan[date] = round(daily_plan[date] * adjustment_factor, 2)
        
        # 重新计算实际总距离
        actual_total = sum(daily_plan.values())
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_days": total_days,
            "running_days": len(daily_plan),
            "target_total_km": total_km,
            "actual_total_km": round(actual_total, 2),
            "weekday_avg_km": round(weekday_avg, 2),
            "weekend_avg_km": round(weekend_avg, 2),
            "daily_plan": daily_plan
        }
    
    def generate_tcx_from_plan(self, plan: Dict, min_pace: float = 7.0, 
                             max_pace: float = 8.0, start_hour_range: Tuple[int, int] = (6, 8),
                             output_dir: str = "output", include_track: bool = True) -> List[str]:
        """
        根据计划生成TCX文件
        
        Args:
            plan: 跑步计划字典
            min_pace: 最快配速（分钟/公里）
            max_pace: 最慢配速（分钟/公里）
            start_hour_range: 开始时间范围（小时）
            output_dir: 输出目录
            include_track: 是否包含轨迹点
            
        Returns:
            生成的文件路径列表
        """
        # 创建输出目录
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        generated_files = []
        daily_plan = plan["daily_plan"]
        
        print(f"开始根据计划生成TCX文件，共{len(daily_plan)}天...")
        
        for date, distance in daily_plan.items():
            # 生成随机配速
            pace = round(random.uniform(min_pace, max_pace), 2)
            
            # 计算时长和卡路里
            duration = self.tcx_generator.calculate_duration(distance, pace)
            calories = self.tcx_generator.calculate_calories(distance, duration)
            
            # 生成随机开始时间
            start_time = self.tcx_generator.generate_start_time(date, start_hour_range)
            
            # 生成文件名
            filename = f"running_{date.strftime('%Y%m%d')}.tcx"
            filepath = os.path.join(output_dir, filename)
            
            # 创建TCX内容
            tcx_content = self.tcx_generator.create_tcx_content(
                date, distance, duration, calories, include_track, start_time
            )
            
            # 写入文件
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(tcx_content)
            
            generated_files.append(filepath)
            
            # 打印进度
            weekend_flag = "（周末）" if date.weekday() >= 5 else ""
            print(f"生成完成: {filename} - {distance}km, {pace}分钟/km, {duration/60:.1f}分钟{weekend_flag}")
        
        print(f"TCX文件生成完成，共{len(generated_files)}个文件")
        return generated_files
    
    def print_plan_summary(self, plan: Dict):
        """
        打印计划摘要
        
        Args:
            plan: 跑步计划字典
        """
        print("=" * 60)
        print("跑步计划摘要")
        print("=" * 60)
        print(f"时间范围: {plan['start_date']} 至 {plan['end_date']}")
        print(f"总天数: {plan['total_days']} 天")
        print(f"跑步天数: {plan['running_days']} 天")
        print(f"目标总距离: {plan['target_total_km']} 公里")
        print(f"实际总距离: {plan['actual_total_km']} 公里")
        print(f"工作日平均距离: {plan['weekday_avg_km']} 公里")
        print(f"周末平均距离: {plan['weekend_avg_km']} 公里")
        
        print("\n前10天跑步计划:")
        sorted_dates = sorted(plan["daily_plan"].keys())
        for i, date in enumerate(sorted_dates[:10]):
            distance = plan["daily_plan"][date]
            weekday = date.strftime("%A")
            weekend_flag = "（周末）" if date.weekday() >= 5 else ""
            print(f"  {date.strftime('%Y-%m-%d')} {weekday}: {distance}公里 {weekend_flag}")
        
        if len(sorted_dates) > 10:
            print(f"  ... 还有 {len(sorted_dates) - 10} 天")
        
        print("=" * 60)