#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import fcntl
import array
import struct
from abc import ABC, abstractmethod
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





