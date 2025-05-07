#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from devices_manager.e2 import E2DeviceManager

def example_usage():
    """E2设备管理器使用示例"""
    # 创建E2设备管理器
    manager = E2DeviceManager()

    if not manager.fan:
        print("未找到风扇设备")
        return

    # 风扇转速演示
    try:
        # 定义几个转速等级
        speeds = [0, 20, 50, 90]
        
        # 循环展示不同转速
        for i in range(12):  # 循环演示3轮
            speed = speeds[i % len(speeds)]
            print(f"设置风扇转速为: {speed}%")
            
            # 设置风扇转速
            if manager.set_fan_speed(speed):
                print(f"风扇转速设置成功: {speed}%")
            else:
                print(f"风扇转速设置失败")
                
            # 等待3秒
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("程序被用户终止")
    finally:
        # 关闭设备前将风扇转速设为0
        manager.set_fan_speed(0)
        print("风扇已停止")
        
        # 关闭设备
        manager.close()
        print("设备已关闭")

if __name__ == "__main__":
    # 需要root权限运行
    if os.geteuid() != 0:
        print("此程序需要root权限才能访问I2C设备")
        print("请使用sudo运行")
        exit(1)

    example_usage()