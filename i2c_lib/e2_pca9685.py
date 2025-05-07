from typing import *
from i2c_lib.i2c import I2CBase


class E2PCA9685:
    """E2 PCA9685 PWM控制器，用于控制风扇转速"""

    # 寄存器地址定义
    MODE1 = 0x00
    SUBADR1 = 0x02
    SUBADR2 = 0x03
    SUBADR3 = 0x04
    PRESCALE = 0xFE

    # LED通道寄存器
    CH0_ON_L = 0x06
    CH0_ON_H = 0x07
    CH0_OFF_L = 0x08
    CH0_OFF_H = 0x09

    # 所有通道寄存器
    ALLCH_ON_L = 0xFA
    ALLCH_ON_H = 0xFB
    ALLCH_OFF_L = 0xFC
    ALLCH_OFF_H = 0xFD

    # 可能的I2C地址列表
    POSSIBLE_ADDRESSES = [0x64, 0x65, 0x66, 0x67]

    def __init__(self, i2c: I2CBase, address: int = None):
        """初始化E2 PCA9685控制器"""
        self.i2c = i2c
        self.address = address
        self.is_initialized = False

    def detect(self) -> bool:
        """检测E2 PCA9685设备是否存在"""
        if not self.i2c:
            print("I2C总线对象未初始化")
            return False

        # 如果已知地址，直接检测
        if self.address:
            print(f"尝试检测E2设备 (已知地址 0x{self.address:02X})...")
            if not self.i2c.set_address(self.address):
                print(f"设置I2C地址 0x{self.address:02X} 失败")
                return False

            try:
                success, _ = self.i2c.read_byte()
                if success:
                    print(f"在地址 0x{self.address:02X} 成功检测到E2设备")
                    return True
                else:
                    print(f"从地址 0x{self.address:02X} 读取数据失败")
                    return False
            except Exception as e:
                print(f"从地址 0x{self.address:02X} 读取数据时发生异常: {e}")
                return False

        # 否则扫描可能的地址
        print(f"扫描可能的E2设备地址...")
        for addr in self.POSSIBLE_ADDRESSES:
            print(f"尝试地址 0x{addr:02X}...")
            if not self.i2c.set_address(addr):
                print(f"设置I2C地址 0x{addr:02X} 失败")
                continue

            try:
                success, val = self.i2c.read_byte()
                if success:
                    self.address = addr
                    print(f"检测到E2 PCA9685设备: 0x{addr:02X}, 读取值: {val:02X}")
                    return True
                else:
                    print(f"从地址 0x{addr:02X} 读取数据失败")
            except Exception as e:
                print(f"从地址 0x{addr:02X} 读取数据时发生异常: {e}")
                continue

        print("未在任何可能的地址上检测到E2设备")
        return False

    def initialize(self) -> bool:
        """初始化E2 PCA9685"""
        if not self.i2c or not self.address:
            return False

        try:
            # 设置MODE1寄存器
            if not self.i2c.write_byte_data(self.MODE1, 0x00):
                return False

            # 关闭所有通道
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
            return (self.i2c.write_byte_data(self.CH0_ON_L + 4 * channel, on & 0xFF) and
                    self.i2c.write_byte_data(self.CH0_ON_H + 4 * channel, (on >> 8) & 0xFF) and
                    self.i2c.write_byte_data(self.CH0_OFF_L + 4 * channel, off & 0xFF) and
                    self.i2c.write_byte_data(self.CH0_OFF_H + 4 * channel, (off >> 8) & 0xFF))
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
            return (self.i2c.write_byte_data(self.ALLCH_ON_L, on & 0xFF) and
                    self.i2c.write_byte_data(self.ALLCH_ON_H, (on >> 8) & 0xFF) and
                    self.i2c.write_byte_data(self.ALLCH_OFF_L, off & 0xFF) and
                    self.i2c.write_byte_data(self.ALLCH_OFF_H, (off >> 8) & 0xFF))
        except:
            return False

    def set_fan_speed(self, speed_level: int) -> bool:
        """
        设置风扇转速

        Args:
            speed_level: 转速等级，取值范围[0,100]

        Returns:
            bool: 是否设置成功
        """
        if not self.is_initialized:
            return False

        try:
            # 限制转速范围
            speed_level = max(0, min(100, speed_level))

            # 计算PWM值
            on = 0
            off = on + int(0xFFF * speed_level / 100)

            # 设置PWM值到通道0
            return self.set_pwm(0, on, off)
        except:
            return False