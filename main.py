import os

from devices_manager.e1 import E1DeviceManager

# 示例：如何使用E1设备管理器
def example_usage():
    """E1设备管理器使用示例"""
    import time

    # 创建E1设备管理器
    manager = E1DeviceManager()

    # 扫描设备
    manager.scan_devices()

    # 获取设备
    led = manager.get_led()
    tube = manager.get_tube()

    if not led or not tube:
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
            manager.display_tube(index % 4, str(index % 10))

            # 等待1秒
            time.sleep(1)
    except KeyboardInterrupt:
        print("程序被用户终止")
    finally:
        # 关闭设备
        manager.close()


if __name__ == "__main__":
    # 需要root权限运行
    if os.geteuid() != 0:
        print("此程序需要root权限才能访问I2C设备")
        print("请使用sudo运行")
        exit(1)

    example_usage()