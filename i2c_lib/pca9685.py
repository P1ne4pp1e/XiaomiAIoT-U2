from i2c_lib.i2c import I2CBase

class PCA9685:
    """PCA9685 PWM控制器"""
    MODE1 = 0x00
    LED0_ON_L = 0x06
    LED0_ON_H = 0x07
    LED0_OFF_L = 0x08
    LED0_OFF_H = 0x09
    ALLLED_ON_L = 0xFA
    ALLLED_ON_H = 0xFB
    ALLLED_OFF_L = 0xFC
    ALLLED_OFF_H = 0xFD

    POSSIBLE_ADDRESSES = [0x60, 0x61, 0x62, 0x63]

    def __init__(self, i2c: I2CBase, address: int = None):
        """初始化PCA9685"""
        self.i2c = i2c
        self.address = address
        self.is_initialized = False

    def detect(self) -> bool:
        """检测PCA9685是否存在"""
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
                    print(f"检测到PCA9685设备: 0x{addr:02X}")
                    return True
            except:
                continue

        return False

    def initialize(self) -> bool:
        """初始化PCA9685"""
        if not self.i2c or not self.address:
            return False

        try:
            # 设置MODE1寄存器
            if not self.i2c.write_byte_data(self.MODE1, 0x00):
                return False

            # 关闭所有LED
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
            return (self.i2c.write_byte_data(self.LED0_ON_L + 4 * channel, on & 0xFF) and
                    self.i2c.write_byte_data(self.LED0_ON_H + 4 * channel, (on >> 8) & 0xFF) and
                    self.i2c.write_byte_data(self.LED0_OFF_L + 4 * channel, off & 0xFF) and
                    self.i2c.write_byte_data(self.LED0_OFF_H + 4 * channel, (off >> 8) & 0xFF))
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
            return (self.i2c.write_byte_data(self.ALLLED_ON_L, on & 0xFF) and
                    self.i2c.write_byte_data(self.ALLLED_ON_H, (on >> 8) & 0xFF) and
                    self.i2c.write_byte_data(self.ALLLED_OFF_L, off & 0xFF) and
                    self.i2c.write_byte_data(self.ALLLED_OFF_H, (off >> 8) & 0xFF))
        except:
            return False