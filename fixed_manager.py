#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import fcntl
from typing import *

# I2C相关常量定义
I2C_SLAVE = 0x0703
I2C_SLAVE_FORCE = 0x0706


class I2CBase:
    """I2C基础操作类，提供基本的I2C总线操作功能"""

    def __init__(self, dev_path: str = None, address: int = None):
        """初始化I2C设备"""
        self.fd = -1
        self.address = address

        if dev_path:
            self.open(dev_path)
            if address is not None:
                self.set_address(address)

    def __del__(self):
        """析构函数，确保设备关闭"""
        self.close()

    def open(self, dev_path: str) -> bool:
        """打开I2C设备"""
        try:
            self.fd = os.open(dev_path, os.O_RDWR)
            return self.fd > 0
        except OSError as e:
            print(f"无法打开I2C设备 {dev_path}: {e}")
            return False

    def close(self) -> None:
        """关闭I2C设备"""
        if self.fd > 0:
            try:
                os.close(self.fd)
            except OSError:
                pass
            finally:
                self.fd = -1

    def set_address(self, address: int) -> bool:
        """设置I2C设备地址"""
        if self.fd <= 0:
            return False

        try:
            # 使用I2C_SLAVE_FORCE替代I2C_SLAVE
            fcntl.ioctl(self.fd, I2C_SLAVE_FORCE, address)
            self.address = address
            return True
        except OSError:
            return False

    def write_byte(self, data: int) -> bool:
        """写入单个字节到I2C设备"""
        if self.fd <= 0:
            return False

        try:
            os.write(self.fd, bytes([data]))
            return True
        except OSError:
            return False

    def read_byte(self) -> Tuple[bool, int]:
        """从I2C设备读取单个字节"""
        if self.fd <= 0:
            return False, 0

        try:
            result = os.read(self.fd, 1)
            return True, result[0]
        except OSError:
            return False, 0

    def write_byte_data(self, reg: int, data: int) -> bool:
        """写入单个字节数据到指定寄存器"""
        if self.fd <= 0:
            return False

        try:
            msg = bytes([reg, data])
            os.write(self.fd, msg)
            return True
        except OSError:
            return False

    def read_byte_data(self, reg: int) -> Tuple[bool, int]:
        """从指定寄存器读取单个字节数据"""
        if self.fd <= 0:
            return False, 0

        try:
            os.write(self.fd, bytes([reg]))
            result = os.read(self.fd, 1)
            return True, result[0]
        except OSError:
            return False, 0

    def write_block_data(self, reg: int, data: List[int]) -> bool:
        """写入数据块到指定寄存器"""
        if self.fd <= 0:
            return False

        try:
            msg = bytes([reg]) + bytes(data)
            os.write(self.fd, msg)
            return True
        except OSError:
            return False

    def read_block_data(self, reg: int, length: int) -> Tuple[bool, List[int]]:
        """从指定寄存器读取数据块"""
        if self.fd <= 0:
            return False, []

        try:
            os.write(self.fd, bytes([reg]))
            result = os.read(self.fd, length)
            return True, list(result)
        except OSError:
            return False, []


class PCA9685:
    """PCA9685 PWM控制器"""
    MODE1 = 0x00
    LED0_ON_L = 0x06
    LED0_ON_H = 0x07
    LED0_OFF_L = 0x08
    LED0_OFF_H = 0x09
    ALLLED_ON_L = 0xFA
    ALLLED_ON_H = 0xFB
    ALLLED_OFF_L = 0xFC
    ALLLED_OFF_H = 0xFD

    POSSIBLE_ADDRESSES = [0x60, 0x61, 0x62, 0x63]

    def __init__(self, i2c: I2CBase, address: int = None):
        """初始化PCA9685"""
        self.i2c = i2c
        self.address = address
        self.is_initialized = False

    def detect(self) -> bool:
        """检测PCA9685是否存在"""
        if not self.i2c:
            return False

        # 如果已知地址，直接检测
        if self.address:
            if not self.i2c.set_address(self.address):
                return False

            try:
                success, _ = self.i2c.read_byte()
                return success
            except:
                return False

        # 否则扫描可能的地址
        for addr in self.POSSIBLE_ADDRESSES:
            if not self.i2c.set_address(addr):
                continue

            try:
                success, _ = self.i2c.read_byte()
                if success:
                    self.address = addr
                    print(f"检测到PCA9685设备: 0x{addr:02X}")
                    return True
            except:
                continue

        return False

    def initialize(self) -> bool:
        """初始化PCA9685"""
        if not self.i2c or not self.address:
            return False

        try:
            # 设置MODE1寄存器
            if not self.i2c.write_byte_data(self.MODE1, 0x00):
                return False

            # 关闭所有LED
            if not self.set_all_pwm(0, 0):
                return False

            self.is_initialized = True
            return True
        except:
            return False

    def set_pwm(self, channel: int, on: int, off: int) -> bool:
        """设置单个通道的PWM值"""
        if not self.is_initialized:
            return False

        if channel < 0 or channel > 15:
            return False

        try:
            on = max(0, min(4095, on))
            off = max(0, min(4095, off))

            # 设置PWM值
            return (self.i2c.write_byte_data(self.LED0_ON_L + 4 * channel, on & 0xFF) and
                    self.i2c.write_byte_data(self.LED0_ON_H + 4 * channel, (on >> 8) & 0xFF) and
                    self.i2c.write_byte_data(self.LED0_OFF_L + 4 * channel, off & 0xFF) and
                    self.i2c.write_byte_data(self.LED0_OFF_H + 4 * channel, (off >> 8) & 0xFF))
        except:
            return False

    def set_all_pwm(self, on: int, off: int) -> bool:
        """设置所有通道的PWM值"""
        if not self.is_initialized and self.address is None:
            return False

        try:
            on = max(0, min(4095, on))
            off = max(0, min(4095, off))

            # 设置所有通道的PWM值
            return (self.i2c.write_byte_data(self.ALLLED_ON_L, on & 0xFF) and
                    self.i2c.write_byte_data(self.ALLLED_ON_H, (on >> 8) & 0xFF) and
                    self.i2c.write_byte_data(self.ALLLED_OFF_L, off & 0xFF) and
                    self.i2c.write_byte_data(self.ALLLED_OFF_H, (off >> 8) & 0xFF))
        except:
            return False


class HT16K33:
    """HT16K33 LED控制器"""
    CMD_STANDBY_MODE_ENABLE = 0x20
    CMD_STANDBY_MODE_DISABLE = 0x21
    CMD_DISPLAY_DISABLE = 0x80
    CMD_DISPLAY_ENABLE = 0x81
    CMD_ROW_OUTPUT = 0xA0

    POSSIBLE_ADDRESSES = [0x70, 0x71, 0x72, 0x73]

    # 数码管字符映射表
    TUBE_CHARS = {
        '0': {'reg1': 0xF8, 'reg2': 0x01},
        '1': {'reg1': 0x30, 'reg2': 0x00},
        '2': {'reg1': 0xD8, 'reg2': 0x02},
        '3': {'reg1': 0x78, 'reg2': 0x02},
        '4': {'reg1': 0x30, 'reg2': 0x03},
        '5': {'reg1': 0x68, 'reg2': 0x03},
        '6': {'reg1': 0xE8, 'reg2': 0x03},
        '7': {'reg1': 0x38, 'reg2': 0x00},
        '8': {'reg1': 0xF8, 'reg2': 0x03},
        '9': {'reg1': 0x78, 'reg2': 0x03},
        'A': {'reg1': 0xB8, 'reg2': 0x03},
        'B': {'reg1': 0xE0, 'reg2': 0x03},
        'C': {'reg1': 0xC8, 'reg2': 0x01},
        'D': {'reg1': 0xF0, 'reg2': 0x02},
        'E': {'reg1': 0xC8, 'reg2': 0x03},
        'F': {'reg1': 0x88, 'reg2': 0x03},
        '-': {'reg1': 0x00, 'reg2': 0x02},
        '_': {'reg1': 0x00, 'reg2': 0x00}
    }

    def __init__(self, i2c: I2CBase, address: int = None):
        """初始化HT16K33"""
        self.i2c = i2c
        self.address = address
        self.is_initialized = False

    def detect(self) -> bool:
        """检测HT16K33是否存在"""
        if not self.i2c:
            return False

        # 如果已知地址，直接检测
        if self.address:
            if not self.i2c.set_address(self.address):
                return False

            try:
                success, _ = self.i2c.read_byte()
                return success
            except:
                return False

        # 否则扫描可能的地址
        for addr in self.POSSIBLE_ADDRESSES:
            if not self.i2c.set_address(addr):
                continue

            try:
                success, _ = self.i2c.read_byte()
                if success:
                    self.address = addr
                    print(f"检测到HT16K33设备: 0x{addr:02X}")
                    return True
            except:
                continue

        return False

    def initialize(self) -> bool:
        """初始化HT16K33"""
        if not self.i2c or not self.address:
            return False

        try:
            # 唤醒设备
            if not self.i2c.write_byte(self.CMD_STANDBY_MODE_DISABLE):
                return False

            # 设置ROW输出
            if not self.i2c.write_byte(self.CMD_ROW_OUTPUT):
                return False

            # 清空显示内容
            if not self.clear():
                return False

            # 启用显示
            if not self.i2c.write_byte(self.CMD_DISPLAY_ENABLE):
                return False

            self.is_initialized = True
            return True
        except:
            return False

    def clear(self) -> bool:
        """清空显示内容"""
        try:
            # 清空所有寄存器
            for reg in range(0x02, 0x0A):
                if not self.i2c.write_byte_data(reg, 0x00):
                    return False

            return True
        except:
            return False

    def display_char_left(self, index: int, char: str) -> bool:
        """在指定位置显示字符（从左侧开始计数）"""
        if not self.is_initialized:
            return False

        if index < 0 or index > 3:
            return False

        if char not in self.TUBE_CHARS:
            return False

        try:
            # 计算寄存器地址
            reg_base = 0x02 + index * 2

            # 获取字符的寄存器值
            reg1_val = self.TUBE_CHARS[char]['reg1']
            reg2_val = self.TUBE_CHARS[char]['reg2']

            # 写入寄存器
            return (self.i2c.write_byte_data(reg_base, reg1_val) and
                    self.i2c.write_byte_data(reg_base + 1, reg2_val))
        except:
            return False

    def display_char_right(self, index: int, char: str) -> bool:
        """在指定位置显示字符（从右侧开始计数）"""
        if not self.is_initialized:
            return False

        if index < 0 or index > 3:
            return False

        if char not in self.TUBE_CHARS:
            return False

        try:
            # 计算寄存器地址
            reg_base = 0x08 - index * 2

            # 获取字符的寄存器值
            reg1_val = self.TUBE_CHARS[char]['reg1']
            reg2_val = self.TUBE_CHARS[char]['reg2']

            # 写入寄存器
            return (self.i2c.write_byte_data(reg_base, reg1_val) and
                    self.i2c.write_byte_data(reg_base + 1, reg2_val))
        except:
            return False

    def display_string(self, text: str, align_right: bool = True) -> bool:
        """显示字符串"""
        if not self.is_initialized:
            return False

        try:
            # 清空显示内容
            self.clear()

            # 限制字符串长度
            text = text[:4]

            # 显示字符串
            if align_right:
                for i, char in enumerate(reversed(text)):
                    if i >= 4:
                        break
                    if char not in self.TUBE_CHARS:
                        continue
                    if not self.display_char_right(i, char):
                        return False
            else:
                for i, char in enumerate(text):
                    if i >= 4:
                        break
                    if char not in self.TUBE_CHARS:
                        continue
                    if not self.display_char_left(i, char):
                        return False

            return True
        except:
            return False


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


# 示例：如何使用E1设备管理器
def example_usage():
    """E1设备管理器使用示例"""
    import time

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


if __name__ == "__main__":
    # 需要root权限运行
    if os.geteuid() != 0:
        print("此程序需要root权限才能访问I2C设备")
        print("请使用sudo运行")
        exit(1)

    example_usage()