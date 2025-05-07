from typing import *
from i2c_lib.i2c import I2CBase
from i2c_lib.e3_door import E3Door


class E3DeviceManager:
    """E3设备管理器，用于统一管理E3板上的窗帘/门设备"""

    def __init__(self):
        """初始化E3设备管理器"""
        self.door = None
        self.i2c = None

        # 扫描多个可能的总线
        self._scan_i2c_bus()

        # 如果没有找到设备，尝试使用固定地址
        if self.door is None and self.i2c is not None and self.i2c.fd > 0:
            self._use_fixed_address()

    def _scan_i2c_bus(self) -> None:
        """扫描可用的I2C总线，查找E3设备"""
        available_buses = []

        # 首先列出所有可用的I2C总线
        for i in range(6):  # 尝试总线0-5
            dev_name = f"/dev/i2c-{i}"
            i2c = I2CBase(dev_name)

            if i2c.fd > 0:
                available_buses.append((i, i2c))
                print(f"找到可用的I2C总线: {dev_name}")

        if not available_buses:
            print("未找到可用的I2C总线")
            return

        # 首先尝试总线5（根据C++代码，直接使用总线5）
        for bus_num, i2c in available_buses:
            if bus_num == 5:
                self.i2c = i2c
                door = E3Door(i2c)
                if door.detect():
                    self.door = door
                    print(f"在总线 /dev/i2c-5 上找到E3门/窗帘设备: 地址=0x{door.address:02X}")

                    # 初始化设备
                    if door.initialize():
                        print(f"E3门/窗帘设备初始化成功")
                    else:
                        print(f"E3门/窗帘设备初始化失败")
                    return
                break

        # 如果总线5上没有找到，尝试其他总线
        for bus_num, i2c in available_buses:
            if bus_num == 5:  # 已经检查过了
                continue
                
            door = E3Door(i2c)
            if door.detect():
                self.i2c = i2c
                self.door = door
                print(f"在总线 /dev/i2c-{bus_num} 上找到E3门/窗帘设备: 地址=0x{door.address:02X}")

                # 初始化设备
                if door.initialize():
                    print(f"E3门/窗帘设备初始化成功")
                else:
                    print(f"E3门/窗帘设备初始化失败")
                return
            else:
                i2c.close()

        # 如果没有找到设备，保留总线5的连接（如果存在）
        for bus_num, i2c in available_buses:
            if bus_num == 5:
                self.i2c = i2c
                print("在总线5上未检测到E3设备，将尝试使用固定地址")
                return
            
        print("在所有可用总线上均未找到E3门/窗帘设备")

    def _use_fixed_address(self) -> None:
        """
        使用固定地址初始化E3设备
        
        从C++代码可以看出，E3设备可能无法通过detect函数检测到，
        需要直接使用一个固定地址
        """
        if not self.i2c or self.i2c.fd <= 0:
            print("未找到I2C总线")
            return

        # 使用固定地址0x1C（根据C++代码中的固定地址）
        fixed_addr = 0x1C
        print(f"尝试使用固定地址0x{fixed_addr:02X}初始化E3设备...")
        
        if self.i2c.set_address(fixed_addr):
            door = E3Door(self.i2c, fixed_addr)
            
            # 初始化设备
            if door.initialize():
                self.door = door
                print(f"使用固定地址0x{fixed_addr:02X}初始化E3门/窗帘设备成功")
            else:
                print(f"使用固定地址0x{fixed_addr:02X}初始化E3门/窗帘设备失败")

    def set_door_position(self, position: int) -> bool:
        """
        设置窗帘/门位置
        
        Args:
            position: 位置值，取值范围[0,100]
        
        Returns:
            bool: 是否设置成功
        """
        if not self.door:
            print("未找到E3门/窗帘设备")
            return False

        try:
            # 设置窗帘/门位置
            return self.door.set_position(position)
        except Exception as e:
            print(f"设置窗帘/门位置失败: {e}")
            return False

    def close(self) -> None:
        """关闭所有设备"""
        if self.i2c:
            self.i2c.close()

        self.door = None
        self.i2c = None
