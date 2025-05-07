#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from devices_manager.e2 import E2DeviceManager


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

                # 尝试扫描常见地址
                potential_addrs = [0x64, 0x65, 0x66, 0x67]  # E2
                potential_addrs += [0x60, 0x61, 0x62, 0x63]  # PCA9685
                potential_addrs += [0x70, 0x71, 0x72, 0x73]  # HT16K33

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
                        pass  # 地址不存在，继续下一个

                os.close(fd)
            else:
                print(f"总线 {dev_name} 打开失败")
        except Exception as e:
            print(f"总线 {dev_name} 不存在或无法访问: {e}")

    print("==== I2C总线调试完成 ====\n")


def example_usage():
    """E2设备管理器使用示例"""
    print("\n===== E2风扇控制演示 =====")

    # 先运行I2C总线调试
    debug_i2c_bus()

    # 创建E2设备管理器
    print("创建E2设备管理器...")
    manager = E2DeviceManager()

    if not manager.fan:
        print("\n未找到E2风扇设备，请检查:")
        print("1. 设备是否已正确连接")
        print("2. I2C总线是否已启用")
        print("3. 设备地址是否正确")
        print("4. 是否使用了sudo权限运行程序")
        return

    print("\n成功找到E2风扇设备!")

    # 风扇转速演示
    try:
        # 定义几个转速等级
        speeds = [0, 20, 50, 90]

        # 循环展示不同转速
        print("\n开始风扇转速控制演示:")
        for i in range(12):  # 循环演示3轮
            speed = speeds[i % len(speeds)]
            print(f"\n[{i + 1}/12] 设置风扇转速为: {speed}%")

            # 设置风扇转速
            if manager.set_fan_speed(speed):
                print(f"✓ 风扇转速设置成功: {speed}%")
            else:
                print(f"✗ 风扇转速设置失败")

            # 等待3秒
            print(f"等待3秒...")
            time.sleep(3)

        print("\n演示完成!")

    except KeyboardInterrupt:
        print("\n程序被用户终止")
    finally:
        # 关闭设备前将风扇转速设为0
        print("\n正在关闭设备...")
        manager.set_fan_speed(0)
        print("风扇已停止")

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