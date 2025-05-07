# I2C设备控制库技术文档

## 1. 简介

本文档详细介绍了I2C设备控制库的设计、实现和使用方法。该库提供了一套统一的接口，用于控制基于I2C总线的各种设备，特别是适用于E1开发板上的LED和数码管设备。库采用面向对象的设计方法，具有良好的可扩展性，便于后续添加更多I2C设备的支持。

## 2. 类层次结构

该库采用分层设计，主要包含以下几个类：

- `I2CBase`：I2C基础操作类，提供底层I2C总线操作
- `PCA9685`：PCA9685 PWM控制器，用于控制LED
- `HT16K33`：HT16K33 LED控制器，用于控制数码管
- `E1DeviceManager`：E1设备管理器，统一管理E1板上的设备

### 类关系图

```
I2CBase ◄─────┬─── PCA9685
              └─── HT16K33
                    
                    E1DeviceManager ───> I2CBase, PCA9685, HT16K33
```

## 3. 详细类说明

### 3.1 I2CBase 类

`I2CBase` 类提供了I2C总线的基本操作功能，包括打开/关闭设备、设置设备地址、读写数据等。

#### 主要方法

| 方法名 | 描述 |
|--------|------|
| `__init__(dev_path, address)` | 初始化I2C设备 |
| `open(dev_path)` | 打开I2C设备 |
| `close()` | 关闭I2C设备 |
| `set_address(address)` | 设置I2C设备地址 |
| `write_byte(data)` | 写入单个字节 |
| `read_byte()` | 读取单个字节 |
| `write_byte_data(reg, data)` | 写入单个字节到指定寄存器 |
| `read_byte_data(reg)` | 读取指定寄存器的单个字节 |
| `write_block_data(reg, data)` | 写入数据块到指定寄存器 |
| `read_block_data(reg, length)` | 读取指定寄存器的数据块 |

#### 使用示例

```python
# 创建I2C总线对象
i2c = I2CBase()

# 打开I2C设备
i2c.open("/dev/i2c-1")

# 设置设备地址
i2c.set_address(0x60)

# 写入数据到寄存器
i2c.write_byte_data(0x00, 0x01)

# 关闭设备
i2c.close()
```

### 3.2 PCA9685 类

`PCA9685` 类实现了对PCA9685 PWM控制器的操作，主要用于控制LED。

#### 主要属性

| 属性名 | 描述 |
|--------|------|
| `MODE1` | MODE1寄存器地址 |
| `LED0_ON_L` | LED0开始低字节寄存器地址 |
| `LED0_ON_H` | LED0开始高字节寄存器地址 |
| `LED0_OFF_L` | LED0结束低字节寄存器地址 |
| `LED0_OFF_H` | LED0结束高字节寄存器地址 |
| `ALLLED_ON_L` | 所有LED开始低字节寄存器地址 |
| `ALLLED_ON_H` | 所有LED开始高字节寄存器地址 |
| `ALLLED_OFF_L` | 所有LED结束低字节寄存器地址 |
| `ALLLED_OFF_H` | 所有LED结束高字节寄存器地址 |
| `POSSIBLE_ADDRESSES` | 可能的I2C地址列表 |

#### 主要方法

| 方法名 | 描述 |
|--------|------|
| `__init__(i2c, address)` | 初始化PCA9685 |
| `detect()` | 检测PCA9685是否存在 |
| `initialize()` | 初始化PCA9685 |
| `set_pwm(channel, on, off)` | 设置单个通道的PWM值 |
| `set_all_pwm(on, off)` | 设置所有通道的PWM值 |

#### 使用示例

```python
# 创建I2C总线对象
i2c = I2CBase("/dev/i2c-1")

# 创建PCA9685对象
pca = PCA9685(i2c, 0x60)

# 检测设备并初始化
if pca.detect() and pca.initialize():
    # 设置通道0的PWM值
    pca.set_pwm(0, 0, 2048)
```

### 3.3 HT16K33 类

`HT16K33` 类实现了对HT16K33 LED控制器的操作，主要用于控制数码管。

#### 主要属性

| 属性名 | 描述 |
|--------|------|
| `CMD_STANDBY_MODE_ENABLE` | 启用待机模式命令 |
| `CMD_STANDBY_MODE_DISABLE` | 禁用待机模式命令 |
| `CMD_DISPLAY_ENABLE` | 启用显示命令 |
| `CMD_DISPLAY_DISABLE` | 禁用显示命令 |
| `CMD_ROW_OUTPUT` | 行输出命令 |
| `POSSIBLE_ADDRESSES` | 可能的I2C地址列表 |
| `TUBE_CHARS` | 数码管字符映射表 |

#### 主要方法

| 方法名 | 描述 |
|--------|------|
| `__init__(i2c, address)` | 初始化HT16K33 |
| `detect()` | 检测HT16K33是否存在 |
| `initialize()` | 初始化HT16K33 |
| `clear()` | 清空显示内容 |
| `display_char_left(index, char)` | 在指定位置显示字符（从左侧开始计数） |
| `display_char_right(index, char)` | 在指定位置显示字符（从右侧开始计数） |
| `display_string(text, align_right)` | 显示字符串 |
| `read_key()` | 读取按键值 |

#### 使用示例

```python
# 创建I2C总线对象
i2c = I2CBase("/dev/i2c-1")

# 创建HT16K33对象
ht = HT16K33(i2c, 0x70)

# 检测设备并初始化
if ht.detect() and ht.initialize():
    # 显示字符串
    ht.display_string("1234")
```

### 3.4 E1DeviceManager 类

`E1DeviceManager` 类是E1设备管理器，用于统一管理E1板上的各种设备。

#### 主要属性

| 属性名 | 描述 |
|--------|------|
| `i2c` | I2C总线对象 |
| `led` | LED设备对象 |
| `tube` | 数码管设备对象 |

#### 主要方法

| 方法名 | 描述 |
|--------|------|
| `__init__()` | 初始化E1设备管理器 |
| `scan_devices()` | 扫描E1设备 |
| `set_led_color(red, green, blue)` | 设置LED颜色 |
| `display_tube_string(text, align_right)` | 设置数码管显示字符串 |
| `close()` | 关闭所有设备 |

#### 使用示例

```python
# 创建E1设备管理器
manager = E1DeviceManager()

# 设置LED颜色
manager.set_led_color(255, 0, 0)  # 红色

# 设置数码管显示
manager.display_tube_string("1234")

# 关闭设备
manager.close()
```

## 4. 常见应用场景

### 4.1 RGB LED控制

```python
def demo_rgb_led():
    manager = E1DeviceManager()
    
    try:
        # 循环显示不同颜色
        colors = [
            (255, 0, 0),    # 红色
            (0, 255, 0),    # 绿色
            (0, 0, 255),    # 蓝色
            (255, 255, 0),  # 黄色
            (255, 0, 255),  # 紫色
            (0, 255, 255),  # 青色
            (255, 255, 255) # 白色
        ]
        
        for color in colors:
            manager.set_led_color(*color)
            time.sleep(1)
    finally:
        manager.close()
```

### 4.2 数码管显示

```python
def demo_tube_display():
    manager = E1DeviceManager()
    
    try:
        # 显示数字
        for i in range(10):
            manager.display_tube_string(str(i))
            time.sleep(0.5)
        
        # 显示字母
        for c in "ABCDEF":
            manager.display_tube_string(c)
            time.sleep(0.5)
        
        # 显示字符串
        manager.display_tube_string("1234")
        time.sleep(1)
        
        # 左对齐显示
        manager.display_tube_string("5678", align_right=False)
        time.sleep(1)
    finally:
        manager.close()
```

### 4.3 计数器示例

```python
def demo_counter():
    manager = E1DeviceManager()
    
    try:
        for i in range(100):
            # 显示计数值
            manager.display_tube_string(f"{i:04d}")
            
            # 根据计数值设置LED颜色
            r = (i * 5) % 256
            g = (i * 3) % 256
            b = (i * 7) % 256
            manager.set_led_color(r, g, b)
            
            time.sleep(0.1)
    finally:
        manager.close()
```

## 5. 扩展指南

如需添加新的I2C设备支持，可按照以下步骤进行：

1. 创建新的设备类
2. 实现 `detect()` 和 `initialize()` 方法
3. 添加设备特有的功能方法
4. 在 `E1DeviceManager` 中添加对新设备的支持

### 示例：添加一个新的温度传感器设备

```python
class TemperatureSensor:
    """温度传感器设备"""
    
    # 可能的I2C地址
    POSSIBLE_ADDRESSES = [0x48, 0x49, 0x4A, 0x4B]
    
    # 寄存器定义
    REG_TEMP = 0x00
    REG_CONFIG = 0x01
    
    def __init__(self, i2c=None, address=None):
        """初始化温度传感器"""
        self.i2c = i2c
        self.address = address
        self.is_initialized = False
    
    def detect(self) -> bool:
        """检测设备是否存在"""
        if not self.i2c:
            print("总线未设置")
            return False
        
        # 如果已知地址，直接检测
        if self.address:
            if not self.i2c.set_address(self.address):
                return False
            
            try:
                success, _ = self.i2c.read_byte_data(self.REG_CONFIG)
                return success
            except:
                return False
        
        # 否则扫描可能的地址
        for addr in self.POSSIBLE_ADDRESSES:
            if not self.i2c.set_address(addr):
                continue
            
            try:
                success, _ = self.i2c.read_byte_data(self.REG_CONFIG)
                if success:
                    self.address = addr
                    print(f"检测到温度传感器: 0x{addr:02X}")
                    return True
            except:
                continue
        
        return False
    
    def initialize(self) -> bool:
        """初始化设备"""
        if not self.i2c or not self.address:
            print("总线或地址未设置")
            return False
        
        # 设置配置寄存器
        if not self.i2c.write_byte_data(self.REG_CONFIG, 0x60):
            return False
        
        self.is_initialized = True
        return True
    
    def read_temperature(self) -> Tuple[bool, float]:
        """读取温度值"""
        if not self.is_initialized:
            print("设备未初始化")
            return False, 0.0
        
        # 读取温度寄存器
        success, data = self.i2c.read_block_data(self.REG_TEMP, 2)
        if not success:
            return False, 0.0
        
        # 解析温度值
        temp = ((data[0] << 8) | data[1]) >> 4
        if temp & 0x800:
            temp = temp - 4096
        
        temp = temp * 0.0625  # 转换为摄氏度
        return True, temp
```

然后在 `E1DeviceManager` 中添加对温度传感器的支持：

```python
class ExtendedE1DeviceManager(E1DeviceManager):
    def __init__(self):
        """初始化扩展E1设备管理器"""
        super().__init__()
        self.temp_sensor = None
    
    def scan_devices(self):
        """扫描E1设备"""
        super().scan_devices()
        
        # 扫描温度传感器
        if self.i2c and self.i2c.fd > 0:
            sensor = TemperatureSensor(self.i2c)
            if sensor.detect() and sensor.initialize():
                self.temp_sensor = sensor
                print(f"初始化温度传感器: 地址=0x{sensor.address:02X}")
    
    def read_temperature(self):
        """读取温度值"""
        if not self.temp_sensor:
            print("未找到温度传感器")
            return False, 0.0
        
        return self.temp_sensor.read_temperature()
```

## 6. 安装与依赖

### 6.1 依赖项

- Python 3.6+
- 需要root权限访问I2C设备

### 6.2 安装说明

1. 确保I2C总线已启用
   ```bash
   sudo raspi-config
   # 选择 "Interfacing Options" -> "I2C" -> "Yes"
   ```

2. 将I2C设备控制库保存为Python模块
   ```bash
   # 创建目录结构
   mkdir -p i2c_lib
   mkdir -p devices_manager
   
   # 将库文件保存到模块目录
   # i2c_lib/i2c.py
   # i2c_lib/pca9685.py
   # i2c_lib/ht16k33.py
   # devices_manager/e1.py
   # main.py
   ```

3. 直接运行程序
   ```bash
   sudo python3 main.py
   ```

## 7. 故障排除

### 7.1 设备无法打开

- 检查I2C总线是否已启用
- 检查设备权限
- 尝试使用sudo运行程序

### 7.2 设备无法检测

- 检查设备连接是否正常
- 检查设备地址是否正确
- 确认使用的是正确的I2C总线（代码中使用了 /dev/i2c-5）

### 7.3 LED不亮

- 检查电源连接
- 确认PCA9685初始化成功
- 尝试设置更高的PWM值

### 7.4 数码管显示异常

- 检查电源连接
- 确认HT16K33初始化成功
- 尝试清空显示后再显示内容

## 8. 安全注意事项

- 使用root权限运行程序时需谨慎
- 避免频繁读写I2C设备，以防止损坏
- 避免长时间高亮度点亮LED，以防止过热
- 关闭程序前确保调用close()方法释放资源