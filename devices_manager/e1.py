from i2c_lib.i2c import I2CBase
from i2c_lib.ht16k33 import HT16K33
from i2c_lib.pca9685 import PCA9685

from typing import *

class E1DeviceManager:
    """E1设备管理器，用于统一管理E1板上的各种设备"""

    def __init__(self):
        """初始化E1设备管理器"""
        self.led = None
        self.tube = None
        self.i2c = None

        # 直接打开总线5（从测试结果看，设备在总线5上）
        self.i2c = I2CBase("/dev/i2c-5")

        # 扫描设备
        self.scan_devices()

    def scan_devices(self) -> None:
        """扫描E1设备"""
        if not self.i2c or self.i2c.fd <= 0:
            print("未找到I2C总线")
            return

        # 扫描LED设备
        led = PCA9685(self.i2c)
        if led.detect() and led.initialize():
            self.led = led
            print(f"初始化LED设备: 地址=0x{led.address:02X}")

        # 扫描数码管设备
        tube = HT16K33(self.i2c)
        if tube.detect() and tube.initialize():
            self.tube = tube
            print(f"初始化数码管设备: 地址=0x{tube.address:02X}")

    def set_led_color(self, red: int, green: int, blue: int) -> bool:
        """设置LED颜色"""
        if not self.led:
            print("未找到LED设备")
            return False

        try:
            # 限制颜色值范围
            red = max(0, min(255, red))
            green = max(0, min(255, green))
            blue = max(0, min(255, blue))

            # 设置LED颜色
            on = 0x0f
            return (self.led.set_pwm(0, on, on + red * 16) and  # R
                    self.led.set_pwm(1, on, on + green * 16) and  # G
                    self.led.set_pwm(2, on, on + blue * 16))  # B
        except:
            return False

    def display_tube_string(self, text: str, align_right: bool = True) -> bool:
        """设置数码管显示字符串"""
        if not self.tube:
            print("未找到数码管设备")
            return False

        try:
            # 显示字符串
            return self.tube.display_string(text, align_right)
        except:
            return False

    def close(self) -> None:
        """关闭所有设备"""
        if self.i2c:
            self.i2c.close()

        self.led = None
        self.tube = None
        self.i2c = None