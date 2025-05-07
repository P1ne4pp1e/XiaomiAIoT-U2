#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from devices_manager.e1 import E1DeviceManager
from devices_manager.s1 import S1DeviceManager


def e1_example_usage():
    """E1设备管理器使用示例"""
    # 创建E1设备管理器
    manager = E1DeviceManager()

    if not manager.led or not manager.tube:
        print("未找到所需设备")
        return

    # 循环显示效果
    try:
        index = 0
        while True:
            index += 1

            # 循环设置灯的颜色
            if index % 3 == 0:
                manager.set_led_color(60, 0, 0)  # 红色
            elif index % 3 == 1:
                manager.set_led_color(0, 60, 0)  # 绿色
            elif index % 3 == 2:
                manager.set_led_color(0, 0, 60)  # 蓝色

            # 循环设置数码管显示数字
            manager.display_tube_string(str(index % 10))

            time.sleep(1)
    except KeyboardInterrupt:
        print("程序被用户终止")
    finally:
        # 关闭设备
        manager.close()


def s1_example_usage():
    """S1设备管理器使用示例"""
    # 创建S1设备管理器
    manager = S1DeviceManager()

    if not manager.keypad:
        print("未找到S1按键板")
        return

    try:
        print("按键测试开始，请按下S1按键板上的按键...")
        last_key = 0

        while True:
            success, key = manager.get_key()

            if success:
                if key != 0 and key != last_key:
                    print(f"检测到按键 {key} 被按下")
                elif key == 0 and last_key != 0:
                    print("按键已释放")

                last_key = key

            time.sleep(0.5)  # 每0.5秒检测一次
    except KeyboardInterrupt:
        print("程序被用户终止")
    finally:
        # 关闭设备
        manager.close()


def e1_s1_combined_example():
    """E1和S1设备组合使用示例"""
    # 创建设备管理器
    e1_manager = E1DeviceManager()
    s1_manager = S1DeviceManager()

    if not e1_manager.led or not e1_manager.tube:
        print("未找到E1所需设备")
        return

    if not s1_manager.keypad:
        print("未找到S1按键板")
        return

    try:
        print("按键测试开始，请按下S1按键板上的按键...")
        last_key = 0

        while True:
            success, key = s1_manager.get_key()

            if success and key != last_key:
                if key == 0:
                    # 无按键按下，清除显示
                    e1_manager.set_led_color(0, 0, 0)
                    e1_manager.display_tube_string("")
                else:
                    # 显示按键号码
                    print(f"检测到按键 {key} 被按下")

                    # 根据按键设置不同的LED颜色
                    if key % 3 == 0:
                        e1_manager.set_led_color(255, 0, 0)  # 红色
                    elif key % 3 == 1:
                        e1_manager.set_led_color(0, 255, 0)  # 绿色
                    elif key % 3 == 2:
                        e1_manager.set_led_color(0, 0, 255)  # 蓝色

                    # 在数码管上显示按键号码
                    e1_manager.display_tube_string(str(key))

                last_key = key

            time.sleep(0.1)
    except KeyboardInterrupt:
        print("程序被用户终止")
    finally:
        # 关闭设备
        e1_manager.close()
        s1_manager.close()


if __name__ == "__main__":
    # 需要root权限运行
    if os.geteuid() != 0:
        print("此程序需要root权限才能访问I2C设备")
        print("请使用sudo运行")
        exit(1)

    # 选择要运行的示例
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "e1":
            e1_example_usage()
        elif sys.argv[1] == "s1":
            s1_example_usage()
        elif sys.argv[1] == "combined":
            e1_s1_combined_example()
        else:
            print("未知的参数，请使用 e1, s1 或 combined")
    else:
        # 默认运行E1示例
        e1_example_usage()