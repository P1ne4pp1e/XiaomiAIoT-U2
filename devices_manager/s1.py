#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import *
import os
import time
import fcntl
from i2c_lib.i2c import I2CBase


class S1KeyPad:
    """S1 按键板控制器，基于HT16K33芯片"""

    # 按键寄存器地址
    KEY_KS0 = 0x40
    KEY_REG_NUM = 6

    # HT16K33命令
    CMD_STANDBY_MODE_DISABLE = 0x21
    CMD_ROW_OUTPUT = 0xA0
    CMD_DISPLAY_ENABLE = 0x81

    # 可能的I2C地址列表
    POSSIBLE_ADDRESSES = [0x74, 0x75, 0x76, 0x77]

    def __init__(self, i2c: I2CBase = None, address: int = None):
        """初始化S1按键板"""
        self.i2c = i2c
        self.address = address
        self.is_initialized = False

    def detect(self) -> bool:
        """检测S1按键板是否存在"""
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
                    print(f"检测到S1按键板: 0x{addr:02X}")
                    return True
            except:
                continue

        return False

    def initialize(self) -> bool:
        """初始化S1按键板"""
        if not self.i2c or not self.address:
            return False

        try:
            # 唤醒设备
            if not self.i2c.write_byte(self.CMD_STANDBY_MODE_DISABLE):
                return False

            # 设置ROW输出
            if not self.i2c.write_byte(self.CMD_ROW_OUTPUT):
                return False

            # 清空所有寄存器 (参考C++代码里的 I2c_s1_key_init 函数)
            for reg in range(0x02, 0x0A):
                if not self.i2c.write_byte_data(reg, 0x00):
                    return False

            # 启用显示
            if not self.i2c.write_byte(self.CMD_DISPLAY_ENABLE):
                return False

            self.is_initialized = True
            return True
        except:
            return False

    def get_key(self) -> Tuple[bool, int]:
        """
        读取按键值

        Returns:
            Tuple[bool, int]: (是否成功读取, 按键值1-12，0表示无按键)
        """
        if not self.is_initialized:
            return False, 0

        try:
            # 读取按键寄存器
            success, values = self.i2c.read_block_data(self.KEY_KS0, self.KEY_REG_NUM)
            if not success:
                return False, 0

            # 解析按键值
            key = 0
            if values[0] & 0x01:
                key = 1
            elif values[2] & 0x01:
                key = 2
            elif values[4] & 0x01:
                key = 3
            elif values[0] & 0x02:
                key = 4
            elif values[2] & 0x02:
                key = 5
            elif values[4] & 0x02:
                key = 6
            elif values[0] & 0x04:
                key = 7
            elif values[2] & 0x04:
                key = 8
            elif values[4] & 0x04:
                key = 9
            elif values[0] & 0x08:
                key = 10
            elif values[2] & 0x08:
                key = 11
            elif values[4] & 0x08:
                key = 12

            return True, key
        except:
            return False, 0


class S1DeviceManager:
    """S1设备管理器，用于管理S1开发板上的设备"""

    def __init__(self):
        """初始化S1设备管理器"""
        self.keypad = None
        self.i2c = None

        # 扫描所有可能的I2C总线
        self.scan_i2c_bus()

    def scan_i2c_bus(self):
        """扫描所有可能的I2C总线，查找S1设备"""
        # 参考C++代码中的逻辑，扫描多个I2C总线
        for i in range(100):  # I2C_DEV_NUM in C++ code
            try:
                dev_name = f"/dev/i2c-{i}"
                i2c = I2CBase(dev_name)

                if i2c.fd <= 0:
                    continue

                # 尝试在此总线上检测S1设备
                keypad = S1KeyPad(i2c)
                if keypad.detect() and keypad.initialize():
                    self.keypad = keypad
                    self.i2c = i2c
                    print(f"找到S1按键板: 总线={i}, 地址=0x{keypad.address:02X}")
                    return True
                else:
                    i2c.close()
            except:
                pass

        print("未找到S1设备")
        return False

    def get_key(self) -> Tuple[bool, int]:
        """读取按键值"""
        if not self.keypad:
            print("未找到S1按键板")
            return False, 0

        return self.keypad.get_key()

    def close(self):
        """关闭所有设备"""
        if self.i2c:
            self.i2c.close()

        self.keypad = None
        self.i2c = None