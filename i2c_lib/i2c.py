#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import fcntl
import array
import struct
from abc import ABC, abstractmethod
from typing import *

class I2CBase:
    """I2C基础操作类，提供基本的I2C总线操作功能"""
    
    # I2C相关常量定义
    I2C_SLAVE = 0x0703
    I2C_SLAVE_FORCE = 0x0706
    I2C_SMBUS = 0x0720
    I2C_RDWR = 0x0707
    I2C_TIMEOUT = 0x0702
    I2C_RETRIES = 0x0701
    
    def __init__(self, dev_path: str = None, address: int = None):
        """
        初始化I2C设备
        
        Args:
            dev_path: I2C设备路径，如"/dev/i2c-1"
            address: I2C设备地址
        """
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
        """
        打开I2C设备
        
        Args:
            dev_path: I2C设备路径，如"/dev/i2c-1"
            
        Returns:
            bool: 是否成功打开设备
        """
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

    # 修改 set_address 方法
    def set_address(self, address: int) -> bool:
        """
        设置I2C设备地址

        Args:
            address: I2C设备地址

        Returns:
            bool: 是否成功设置地址
        """
        if self.fd <= 0:
            print("设备未打开")
            return False

        try:
            # 使用 I2C_SLAVE_FORCE 替代 I2C_SLAVE
            fcntl.ioctl(self.fd, self.I2C_SLAVE_FORCE, address)
            self.address = address
            return True
        except OSError as e:
            return False

    # 修改错误处理相关的方法
    def write_byte(self, data: int) -> bool:
        """
        写入单个字节到I2C设备

        Args:
            data: 要写入的字节

        Returns:
            bool: 是否成功写入
        """
        if self.fd <= 0:
            print("设备未打开")
            return False

        try:
            os.write(self.fd, bytes([data]))
            return True
        except OSError:
            return False

    def read_byte(self) -> Tuple[bool, int]:
        """
        从I2C设备读取单个字节

        Returns:
            Tuple[bool, int]: (是否成功, 读取的字节)
        """
        if self.fd <= 0:
            print("设备未打开")
            return False, 0

        try:
            result = os.read(self.fd, 1)
            return True, result[0]
        except OSError:
            return False, 0

    def write_byte_data(self, reg: int, data: int) -> bool:
        """
        写入单个字节数据到指定寄存器

        Args:
            reg: 寄存器地址
            data: 要写入的字节

        Returns:
            bool: 是否成功写入
        """
        if self.fd <= 0:
            print("设备未打开")
            return False

        try:
            msg = struct.pack('BB', reg, data)
            os.write(self.fd, msg)
            return True
        except OSError:
            return False

    def read_byte_data(self, reg: int) -> Tuple[bool, int]:
        """
        从指定寄存器读取单个字节数据

        Args:
            reg: 寄存器地址

        Returns:
            Tuple[bool, int]: (是否成功, 读取的字节)
        """
        if self.fd <= 0:
            print("设备未打开")
            return False, 0

        try:
            os.write(self.fd, bytes([reg]))
            result = os.read(self.fd, 1)
            return True, result[0]
        except OSError:
            return False, 0

    def write_block_data(self, reg: int, data: List[int]) -> bool:
        """
        写入数据块到指定寄存器

        Args:
            reg: 寄存器地址
            data: 要写入的数据列表

        Returns:
            bool: 是否成功写入
        """
        if self.fd <= 0:
            print("设备未打开")
            return False

        try:
            msg = bytes([reg]) + bytes(data)
            os.write(self.fd, msg)
            return True
        except OSError:
            return False

    def read_block_data(self, reg: int, length: int) -> Tuple[bool, List[int]]:
        """
        从指定寄存器读取数据块

        Args:
            reg: 寄存器地址
            length: 要读取的字节数

        Returns:
            Tuple[bool, List[int]]: (是否成功, 读取的数据列表)
        """
        if self.fd <= 0:
            print("设备未打开")
            return False, []

        try:
            os.write(self.fd, bytes([reg]))
            result = os.read(self.fd, length)
            return True, list(result)
        except OSError:
            return False, []
    
    @staticmethod
    def scan_devices(bus_num: int = 1, start_addr: int = 0x03, end_addr: int = 0x77) -> List[int]:
        """
        扫描I2C总线上的设备
        
        Args:
            bus_num: I2C总线号
            start_addr: 起始地址
            end_addr: 结束地址
            
        Returns:
            List[int]: 检测到的设备地址列表
        """
        found_devices = []
        dev_path = f"/dev/i2c-{bus_num}"
        
        try:
            fd = os.open(dev_path, os.O_RDWR)
            for addr in range(start_addr, end_addr + 1):
                try:
                    fcntl.ioctl(fd, I2CBase.I2C_SLAVE, addr)
                    os.read(fd, 1)  # 尝试读取一个字节
                    found_devices.append(addr)
                    print(f"检测到设备: 0x{addr:02X}")
                except:
                    pass  # 忽略错误，继续扫描
            os.close(fd)
        except OSError as e:
            print(f"无法扫描I2C总线 {bus_num}: {e}")
        
        return found_devices


class I2CDevice(ABC):
    """I2C设备抽象基类，所有具体的I2C设备类都应该继承此类"""
    
    def __init__(self, bus: I2CBase = None, address: int = None):
        """
        初始化I2C设备
        
        Args:
            bus: I2C总线对象
            address: I2C设备地址
        """
        self.bus = bus
        self.address = address
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化设备

        Returns:
            bool: 是否成功初始化
        """
        pass
    
    @abstractmethod
    def detect(self) -> bool:
        """
        检测设备是否存在
        
        Returns:
            bool: 设备是否存在
        """
        pass





