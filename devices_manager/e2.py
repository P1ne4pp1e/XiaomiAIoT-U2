from typing import *
from i2c_lib.i2c import I2CBase
from i2c_lib.e2_pca9685 import E2PCA9685

class E2DeviceManager:
    """E2设备管理器，用于统一管理E2板上的风扇设备"""

    def __init__(self):
        """初始化E2设备管理器"""
        self.fan = None
        self.i2c = None

        # 扫描多个可能的总线
        self._scan_i2c_bus()
        
        # 扫描设备
        if self.i2c and self.i2c.fd > 0:
            self.scan_devices()

    def _scan_i2c_bus(self) -> None:
        """扫描可用的I2C总线"""
        for i in range(6):  # 尝试总线0-5
            dev_name = f"/dev/i2c-{i}"
            i2c = I2CBase(dev_name)
            
            if i2c.fd > 0:
                # 保存找到的有效总线
                self.i2c = i2c
                print(f"找到可用的I2C总线: {dev_name}")
                return
                
        print("未找到可用的I2C总线")

    def scan_devices(self) -> None:
        """扫描E2设备"""
        if not self.i2c or self.i2c.fd <= 0:
            print("未找到I2C总线")
            return

        # 扫描风扇设备
        fan = E2PCA9685(self.i2c)
        if fan.detect() and fan.initialize():
            self.fan = fan
            print(f"初始化E2风扇设备: 地址=0x{fan.address:02X}")

    def set_fan_speed(self, speed_level: int) -> bool:
        """
        设置风扇转速
        
        Args:
            speed_level: 转速等级，取值范围[0,100]
            
        Returns:
            bool: 是否设置成功
        """
        if not self.fan:
            print("未找到风扇设备")
            return False

        try:
            # 设置风扇转速
            return self.fan.set_fan_speed(speed_level)
        except Exception as e:
            print(f"设置风扇转速失败: {e}")
            return False

    def close(self) -> None:
        """关闭所有设备"""
        if self.i2c:
            self.i2c.close()

        self.fan = None
        self.i2c = None