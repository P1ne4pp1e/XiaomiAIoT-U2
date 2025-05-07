from i2c_lib.i2c import I2CBase, I2CDevice
from i2c_lib.ht16k33 import HT16K33
from i2c_lib.pca9685 import PCA9685

from typing import *

class E1DeviceManager:
    """E1设备管理器，用于统一管理E1板上的各种设备"""

    def __init__(self, scan_buses: bool = True):
        """
        初始化E1设备管理器

        Args:
            scan_buses: 是否自动扫描I2C总线
        """
        self.buses = {}  # I2C总线字典，键为总线号，值为I2CBase对象
        self.led_devices = {}  # LED设备字典，键为设备地址，值为PCA9685对象
        self.tube_devices = {}  # 数码管设备字典，键为设备地址，值为HT16K33对象

        if scan_buses:
            self.scan_buses()

    def scan_buses(self, start_bus: int = 0, end_bus: int = 5) -> None:
        """
        扫描I2C总线

        Args:
            start_bus: 起始总线号
            end_bus: 结束总线号
        """
        for bus_num in range(start_bus, end_bus + 1):
            dev_path = f"/dev/i2c-{bus_num}"

            try:
                bus = I2CBase()
                if bus.open(dev_path):
                    self.buses[bus_num] = bus
                    print(f"发现I2C总线: {dev_path}")
            except Exception as e:
                print(f"无法打开I2C总线 {bus_num}: {e}")

    def scan_devices(self) -> None:
        """扫描E1设备"""
        if not self.buses:
            print("未找到I2C总线")
            return

        for bus_num, bus in self.buses.items():
            # 扫描LED设备
            for addr in PCA9685.POSSIBLE_ADDRESSES:
                led = PCA9685(bus, addr)
                if led.detect() and led.initialize():
                    self.led_devices[addr] = led
                    print(f"初始化LED设备: 总线={bus_num}, 地址=0x{addr:02X}")

            # 扫描数码管设备
            for addr in HT16K33.POSSIBLE_ADDRESSES:
                tube = HT16K33(bus, addr)
                if tube.detect() and tube.initialize():
                    self.tube_devices[addr] = tube
                    print(f"初始化数码管设备: 总线={bus_num}, 地址=0x{addr:02X}")

    def get_led(self, address: int = None) -> Optional[PCA9685]:
        """
        获取LED设备

        Args:
            address: LED设备地址，如果为None则返回第一个找到的设备

        Returns:
            Optional[PCA9685]: LED设备对象，如果未找到则返回None
        """
        if address is not None:
            return self.led_devices.get(address)

        # 返回第一个找到的设备
        return next(iter(self.led_devices.values())) if self.led_devices else None

    def get_tube(self, address: int = None) -> Optional[HT16K33]:
        """
        获取数码管设备

        Args:
            address: 数码管设备地址，如果为None则返回第一个找到的设备

        Returns:
            Optional[HT16K33]: 数码管设备对象，如果未找到则返回None
        """
        if address is not None:
            return self.tube_devices.get(address)

        # 返回第一个找到的设备
        return next(iter(self.tube_devices.values())) if self.tube_devices else None

    def set_led_color(self, red: int, green: int, blue: int, address: int = None) -> bool:
        """
        设置LED颜色

        Args:
            red: 红色分量 (0-255)
            green: 绿色分量 (0-255)
            blue: 蓝色分量 (0-255)
            address: LED设备地址，如果为None则使用第一个找到的设备

        Returns:
            bool: 是否成功设置
        """
        led = self.get_led(address)
        if not led:
            print("未找到LED设备")
            return False

        # 限制颜色值范围
        red = max(0, min(255, red))
        green = max(0, min(255, green))
        blue = max(0, min(255, blue))

        # 设置LED颜色
        on = 0x0f
        return (led.set_pwm(0, on, on + red * 16) and  # R
                led.set_pwm(1, on, on + green * 16) and  # G
                led.set_pwm(2, on, on + blue * 16))  # B

    def display_tube(self, index: int, char: str, address: int = None) -> bool:
        """
        设置数码管显示

        Args:
            index: 数码管索引 (0-3)
            char: 要显示的字符
            address: 数码管设备地址，如果为None则使用第一个找到的设备

        Returns:
            bool: 是否成功显示
        """
        tube = self.get_tube(address)
        if not tube:
            print("未找到数码管设备")
            return False

        # 初始化数码管
        tube.initialize()

        # 显示字符
        return tube.display_char_left(index, char)

    def display_tube_string(self, text: str, align_right: bool = True, address: int = None) -> bool:
        """
        设置数码管显示字符串

        Args:
            text: 要显示的字符串
            align_right: 是否右对齐
            address: 数码管设备地址，如果为None则使用第一个找到的设备

        Returns:
            bool: 是否成功显示
        """
        tube = self.get_tube(address)
        if not tube:
            print("未找到数码管设备")
            return False

        # 显示字符串
        return tube.display_string(text, align_right)

    def close(self) -> None:
        """关闭所有设备"""
        for bus in self.buses.values():
            bus.close()

        self.buses.clear()
        self.led_devices.clear()
        self.tube_devices.clear()