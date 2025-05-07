#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from devices_manager.e3 import E3DeviceManager


def debug_i2c_bus():
    """调试I2C总线"""
    print("\n==== I2C总线调试信息 ====")

    # 尝试打开所有可能的I2C总线
    for i in range(10):  # 尝试总线0-9
        dev_name = f"/dev/i2c-{i}"
        try:
            fd = os.open(dev_name, os.O_RDWR)
            if fd > 0:
                print(f"总线 {dev_name} 打开成功，文件描述符: {fd}")

                # 尝试扫描E3设备可能的地址
                potential_addrs = [0x1C, 0x1D, 0x1E, 0x1F]  # E3设备可能的地址

                print(f"  在总线 {dev_name} 上扫描设备...")
                for addr in potential_addrs:
                    try:
                        # 尝试设置地址
                        import fcntl
                        I2C_SLAVE_FORCE = 0x0706
                        fcntl.ioctl(fd, I2C_SLAVE_FORCE, addr)

                        # 尝试读取一个字节
                        data = os.read(fd, 1)
                        print(f"  地址 0x{addr:02X} 读取成功: {data.hex() if data else 'None'}")
                    except Exception as e:
                        print(f"  地址 0x{addr:02X} 读取失败: {e}")

                os.close(fd)
            else:
                print(f"总线 {dev_name} 打开失败")
        except Exception as e:
            print(f"总线 {dev_name} 不存在或无法访问: {e}")

    print("==== I2C总线调试完成 ====\n")


def example_usage():
    """E3设备管理器使用示例"""
    print("\n===== E3门/窗帘控制演示 =====")

    # 先运行I2C总线调试
    debug_i2c_bus()

    # 创建E3设备管理器
    print("创建E3设备管理器...")
    manager = E3DeviceManager()

    if not manager.door:
        print("\n未找到E3门/窗帘设备，请检查:")
        print("1. 设备是否已正确连接")
        print("2. I2C总线是否已启用")
        print("3. 设备地址是否正确")
        print("4. 是否使用了sudo权限运行程序")
        return

    print("\n成功找到E3门/窗帘设备!")

    # 窗帘位置控制演示
    try:
        # 定义几个位置等级
        positions = [0, 25, 50, 75, 100, 0]

        # 循环展示不同位置
        print("\n开始门/窗帘位置控制演示:")
        for i, position in enumerate(positions):
            print(f"\n[{i + 1}/{len(positions)}] 设置门/窗帘位置为: {position}%")

            # 设置门/窗帘位置
            if manager.set_door_position(position):
                print(f"✓ 门/窗帘位置设置成功: {position}%")
            else:
                print(f"✗ 门/窗帘位置设置失败")

            # 等待5秒
            print(f"等待5秒...")
            time.sleep(5)

        print("\n演示完成!")

    except KeyboardInterrupt:
        print("\n程序被用户终止")
    finally:
        # 关闭设备前将门/窗帘位置设为0
        print("\n正在关闭设备...")
        manager.set_door_position(0)
        print("门/窗帘已复位")

        # 关闭设备
        manager.close()
        print("设备已关闭")
        print("===== 演示结束 =====\n")


if __name__ == "__main__":
    # 需要root权限运行
    if os.geteuid() != 0:
        print("此程序需要root权限才能访问I2C设备")
        print("请使用sudo运行")
        exit(1)

    example_usage()
