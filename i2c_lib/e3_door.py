from typing import *
from i2c_lib.i2c import I2CBase

class E3Door:
    """E3门/窗帘控制器"""
    
    # 可能的I2C地址列表
    POSSIBLE_ADDRESSES = [0x1C, 0x1D, 0x1E, 0x1F]
    
    # HR8833MTE寄存器地址
    HR8833MTE_REG = 0x03
    
    def __init__(self, i2c: I2CBase, address: int = None):
        """初始化E3门/窗帘控制器"""
        self.i2c = i2c
        self.address = address
        self.is_initialized = False
    
    def detect(self) -> bool:
        """
        检测E3门/窗帘控制器是否存在
        
        注意：从C++代码来看，这个功能可能无法正常工作，
        可能需要直接指定地址。
        """
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
                    print(f"检测到E3门/窗帘控制器: 0x{addr:02X}")
                    return True
            except:
                continue
        
        return False
    
    def initialize(self) -> bool:
        """
        初始化E3门/窗帘控制器
        
        将窗帘机归位为初始位置
        """
        if not self.i2c or not self.address:
            return False
        
        try:
            # 将窗帘位置设置为0
            if not self.i2c.write_byte_data(self.HR8833MTE_REG, 0):
                return False
            
            self.is_initialized = True
            return True
        except:
            return False
    
    def set_position(self, position: int) -> bool:
        """
        设置窗帘位置
        
        Args:
            position: 窗帘位置，取值范围[0, 100]
        
        Returns:
            bool: 是否设置成功
        """
        if not self.is_initialized:
            return False
        
        try:
            # 限制位置范围
            position = max(0, min(100, position))
            
            # 设置窗帘位置
            return self.i2c.write_byte_data(self.HR8833MTE_REG, position)
        except:
            return False
