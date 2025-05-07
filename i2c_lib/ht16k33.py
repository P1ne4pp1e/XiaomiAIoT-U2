from typing import *
from i2c_lib.i2c import I2CBase

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


    def read_key(self) -> Tuple[bool, int]:
        """
        读取按键值

        Returns:
            Tuple[bool, int]: (是否成功读取, 按键值)
        """
        if not self.is_initialized:
            print("设备未初始化")
            return False, 0

        # 读取按键数据
        success, values = self.bus.read_block_data(self.CMD_KEY_DATA_START, 6)
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
        else:
            return True, 0  # 没有按键按下

        return True, key