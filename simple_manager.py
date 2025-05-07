#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import fcntl
import struct

# I2C相关常量定义
I2C_SLAVE = 0x0703
I2C_SLAVE_FORCE = 0x0706

# PCA9685常量
LED_R = 0
LED_G = 1
LED_B = 2

LED0_ON_L = 0x6
LED0_ON_H = 0x7
LED0_OFF_L = 0x8
LED0_OFF_H = 0x9

PCA9685_MODE1 = 0x0

ALLLED_ON_L = 0xFA
ALLLED_ON_H = 0xFB
ALLLED_OFF_L = 0xFC
ALLLED_OFF_H = 0xFD

# HT16K33常量
HT16K33_STANDBY_MODE_DISABLE = 0x21
HT16K33_DISPLAY_ENABLE = 0x81
HT16K33_ROW_OUTPUT = 0xA0

# 地址定义
PCA9685_ADDRESS = [0x60, 0x61, 0x62, 0x63]
HT16K33_ADDRESS = [0x70, 0x71, 0x72, 0x73]

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


def i2c_write_cmd(fd, addr, cmd):
    try:
        fcntl.ioctl(fd, I2C_SLAVE_FORCE, addr)
        os.write(fd, bytes([cmd]))
        return True
    except:
        return False


def i2c_write_reg(fd, addr, reg, value):
    try:
        fcntl.ioctl(fd, I2C_SLAVE_FORCE, addr)
        os.write(fd, struct.pack('BB', reg, value))
        return True
    except:
        return False


def set_pwm(fd, addr, channel, on, off):
    return (i2c_write_reg(fd, addr, LED0_ON_L + 4 * channel, on & 0xFF) and
            i2c_write_reg(fd, addr, LED0_ON_H + 4 * channel, (on >> 8) & 0xFF) and
            i2c_write_reg(fd, addr, LED0_OFF_L + 4 * channel, off & 0xFF) and
            i2c_write_reg(fd, addr, LED0_OFF_H + 4 * channel, (off >> 8) & 0xFF))


def set_all_pwm(fd, addr, on, off):
    return (i2c_write_reg(fd, addr, ALLLED_ON_L, on & 0xFF) and
            i2c_write_reg(fd, addr, ALLLED_ON_H, (on >> 8) & 0xFF) and
            i2c_write_reg(fd, addr, ALLLED_OFF_L, off & 0xFF) and
            i2c_write_reg(fd, addr, ALLLED_OFF_H, (off >> 8) & 0xFF))


def ht16k33_clear(fd, addr):
    if not i2c_write_cmd(fd, addr, HT16K33_STANDBY_MODE_DISABLE):
        return False

    if not i2c_write_cmd(fd, addr, HT16K33_ROW_OUTPUT):
        return False

    for reg in range(0x02, 0x0A):
        if not i2c_write_reg(fd, addr, reg, 0x00):
            return False

    return i2c_write_cmd(fd, addr, HT16K33_DISPLAY_ENABLE)


def display_char(fd, addr, index, char):
    if index < 0 or index > 3 or char not in TUBE_CHARS:
        return False

    reg_base = 0x02 + index * 2
    value1 = TUBE_CHARS[char]['reg1']
    value2 = TUBE_CHARS[char]['reg2']

    return (i2c_write_reg(fd, addr, reg_base, value1) and
            i2c_write_reg(fd, addr, reg_base + 1, value2))


def display_string(fd, addr, text, align_right=True):
    if not ht16k33_clear(fd, addr):
        return False

    text = text[:4]

    if align_right:
        for i, char in enumerate(reversed(text)):
            if i >= 4:
                break
            if not display_char(fd, addr, i, char):
                return False
    else:
        for i, char in enumerate(text):
            if i >= 4:
                break
            if not display_char(fd, addr, i, char):
                return False

    return True


class SimpleE1Manager:
    """简化版E1设备管理器"""

    def __init__(self):
        self.led_fd = -1
        self.led_addr = 0
        self.tube_fd = -1
        self.tube_addr = 0

        self.scan_devices()

    def scan_devices(self):
        """扫描E1设备"""
        for i in range(6):
            dev_name = f"/dev/i2c-{i}"
            try:
                fd = os.open(dev_name, os.O_RDWR)
                if fd <= 0:
                    continue

                # 检测LED设备
                for addr in PCA9685_ADDRESS:
                    try:
                        fcntl.ioctl(fd, I2C_SLAVE_FORCE, addr)
                        os.read(fd, 1)  # 尝试读取一个字节
                        self.led_fd = fd
                        self.led_addr = addr
                        print(f"检测到LED设备: 总线={i}, 地址=0x{addr:02X}")

                        # 初始化LED
                        i2c_write_reg(fd, addr, PCA9685_MODE1, 0x00)
                        set_all_pwm(fd, addr, 0, 0)
                        break
                    except:
                        pass

                # 检测数码管设备
                for addr in HT16K33_ADDRESS:
                    try:
                        fcntl.ioctl(fd, I2C_SLAVE_FORCE, addr)
                        os.read(fd, 1)  # 尝试读取一个字节
                        self.tube_fd = fd
                        self.tube_addr = addr
                        print(f"检测到数码管设备: 总线={i}, 地址=0x{addr:02X}")

                        # 初始化数码管
                        ht16k33_clear(fd, addr)
                        break
                    except:
                        pass

                # 如果找到了设备，就不关闭fd
                if self.led_fd > 0 or self.tube_fd > 0:
                    if self.led_fd > 0 and self.tube_fd > 0:
                        break
                else:
                    os.close(fd)
            except:
                pass

        if self.led_fd <= 0:
            print("未找到LED设备")

        if self.tube_fd <= 0:
            print("未找到数码管设备")

    def set_led_color(self, red, green, blue):
        """设置LED颜色"""
        if self.led_fd <= 0 or self.led_addr == 0:
            print("未找到LED设备")
            return False

        red = max(0, min(255, red))
        green = max(0, min(255, green))
        blue = max(0, min(255, blue))

        on = 0x0f

        return (set_pwm(self.led_fd, self.led_addr, LED_R, on, on + red * 16) and
                set_pwm(self.led_fd, self.led_addr, LED_G, on, on + green * 16) and
                set_pwm(self.led_fd, self.led_addr, LED_B, on, on + blue * 16))

    def display_tube_string(self, text, align_right=True):
        """显示数码管字符串"""
        if self.tube_fd <= 0 or self.tube_addr == 0:
            print("未找到数码管设备")
            return False

        return display_string(self.tube_fd, self.tube_addr, text, align_right)

    def close(self):
        """关闭设备"""
        if self.led_fd > 0:
            try:
                os.close(self.led_fd)
            except:
                pass

        if self.tube_fd > 0 and self.tube_fd != self.led_fd:
            try:
                os.close(self.tube_fd)
            except:
                pass

        self.led_fd = -1
        self.led_addr = 0
        self.tube_fd = -1
        self.tube_addr = 0


# 示例使用
def simple_example():
    import time

    # 创建简化版E1设备管理器
    manager = SimpleE1Manager()

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
        manager.close()


if __name__ == "__main__":
    # 需要root权限运行
    if os.geteuid() != 0:
        print("此程序需要root权限才能访问I2C设备")
        print("请使用sudo运行")
        exit(1)

    simple_example()