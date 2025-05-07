from i2c_lib.i2c import I2CBase, I2CDevice

class PCA9685(I2CDevice):
    """PCA9685 PWM控制器"""

    # 寄存器定义
    MODE1 = 0x00
    LED0_ON_L = 0x06
    LED0_ON_H = 0x07
    LED0_OFF_L = 0x08
    LED0_OFF_H = 0x09
    ALLLED_ON_L = 0xFA
    ALLLED_ON_H = 0xFB
    ALLLED_OFF_L = 0xFC
    ALLLED_OFF_H = 0xFD

    # 可能的I2C地址
    POSSIBLE_ADDRESSES = [0x60, 0x61, 0x62, 0x63]

    def __init__(self, bus: I2CBase = None, address: int = None):
        """
        初始化PCA9685

        Args:
            bus: I2C总线对象
            address: PCA9685的I2C地址
        """
        super().__init__(bus, address)

    def initialize(self) -> bool:
        """
        初始化PCA9685

        Returns:
            bool: 是否成功初始化
        """
        if not self.bus or not self.address:
            print("总线或地址未设置")
            return False

        # 设置MODE1寄存器
        if not self.bus.write_byte_data(self.MODE1, 0x00):
            return False

        # 关闭所有LED
        self.set_all_pwm(0, 0)

        self.is_initialized = True
        return True

    def detect(self) -> bool:
        """
        检测PCA9685是否存在

        Returns:
            bool: 设备是否存在
        """
        if not self.bus:
            print("总线未设置")
            return False

        # 如果已知地址，直接检测
        if self.address:
            if not self.bus.set_address(self.address):
                return False

            success, value = self.bus.read_byte_data(self.MODE1)
            return success

        # 否则扫描可能的地址
        for addr in self.POSSIBLE_ADDRESSES:
            if not self.bus.set_address(addr):
                continue

            success, value = self.bus.read_byte_data(self.MODE1)
            if success:
                self.address = addr
                print(f"检测到PCA9685设备: 0x{addr:02X}")
                return True

        return False

    def set_pwm(self, channel: int, on: int, off: int) -> bool:
        """
        设置单个通道的PWM值

        Args:
            channel: 通道号 (0-15)
            on: 开始点 (0-4095)
            off: 结束点 (0-4095)

        Returns:
            bool: 是否成功设置
        """
        if not self.is_initialized:
            print("设备未初始化")
            return False

        if channel < 0 or channel > 15:
            print("通道号无效")
            return False

        on = max(0, min(4095, on))
        off = max(0, min(4095, off))

        # 设置PWM值
        return (self.bus.write_byte_data(self.LED0_ON_L + 4 * channel, on & 0xFF) and
                self.bus.write_byte_data(self.LED0_ON_H + 4 * channel, (on >> 8) & 0xFF) and
                self.bus.write_byte_data(self.LED0_OFF_L + 4 * channel, off & 0xFF) and
                self.bus.write_byte_data(self.LED0_OFF_H + 4 * channel, (off >> 8) & 0xFF))

    def set_all_pwm(self, on: int, off: int) -> bool:
        """
        设置所有通道的PWM值

        Args:
            on: 开始点 (0-4095)
            off: 结束点 (0-4095)

        Returns:
            bool: 是否成功设置
        """
        if not self.is_initialized:
            print("设备未初始化")
            return False

        on = max(0, min(4095, on))
        off = max(0, min(4095, off))

        # 设置所有通道的PWM值
        return (self.bus.write_byte_data(self.ALLLED_ON_L, on & 0xFF) and
                self.bus.write_byte_data(self.ALLLED_ON_H, (on >> 8) & 0xFF) and
                self.bus.write_byte_data(self.ALLLED_OFF_L, off & 0xFF) and
                self.bus.write_byte_data(self.ALLLED_OFF_H, (off >> 8) & 0xFF))