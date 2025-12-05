#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TCX生成器使用示例
演示如何使用TCXGenerator类生成跑步数据

作者: 猫娘幽浮喵
"""

from tcx_generator import TCXGenerator
import os

def main():
    """主函数 - 演示TCX生成器的使用"""
    
    print("=== TCX文件生成器使用示例 ===\n")
    
    # 创建生成器实例
    generator = TCXGenerator()
    
    # 示例1: 生成一周的跑步数据
    print("示例1: 生成一周的跑步数据")
    print("-" * 40)
    
    tcx_files = generator.generate_tcx_files(
        start_date="2023-01-01",
        end_date="2023-01-07",
        min_km=3.0,
        output_dir="example_output"
    )
    
    print(f"\n生成了 {len(tcx_files)} 个TCX文件\n")
    
    # 示例2: 创建压缩包
    print("示例2: 创建压缩包")
    print("-" * 40)
    
    zip_files = generator.create_zip_archives(
        file_list=tcx_files,
        max_size_mb=1,  # 设置为1MB以便演示多个压缩包
        output_dir="example_output"
    )
    
    print(f"\n创建了 {len(zip_files)} 个压缩包\n")
    
    # 示例3: 查看生成的文件
    print("示例3: 查看生成的文件")
    print("-" * 40)
    
    output_dir = "example_output"
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        for file in sorted(files):
            file_path = os.path.join(output_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"{file}: {file_size} bytes")
    
    print("\n=== 示例完成 ===")
    print(f"所有文件已保存到: {output_dir}")

if __name__ == "__main__":
    main()