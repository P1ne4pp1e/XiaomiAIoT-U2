# E2设备控制库技术文档

## 1. 简介

本文档详细介绍了E2设备控制库的设计、实现和使用方法。该库是对现有I2C设备控制库的扩展，提供了对E2板上风扇设备的支持。库采用与E1设备管理器相同的面向对象设计方法，保持了良好的一致性和可扩展性。

## 2. 类层次结构

E2设备控制库采用与E1设备控制库相同的分层设计，主要包含以下几个类：

- `I2CBase`：I2C基础操作类，提供底层I2C总线操作
- `E2PCA9685`：E2板上的PCA9685 PWM控制器，用于控制风扇
- `E2DeviceManager`：E2设备管理器，统一管理E2板上的设备

### 类关系图

```
I2CBase ◄───── E2PCA9685
               
E2DeviceManager ───> I2CBase, E2PCA9685
```

## 3. 详细类说明

### 3.1 E2PCA9685 类

`E2PCA9685` 类实现了对E2板上PCA9685 PWM控制器的操作，主要用于控制风扇转速。

#### 主要属性

| 属性名 | 描述 |
|--------|------|
| `MODE1` | MODE1寄存器地址 |
| `CH0_ON_L` | 通道0开始低字节寄存器地址 |
| `CH0_ON_H` | 通道0开始高字节寄存器地址 |
| `CH0_OFF_L` | 通道0结束低字节寄存器地址 |
| `CH0_OFF_H` | 通道0结束高字节寄存器地址 |
| `ALLCH_ON_L` | 所有通道开始低字节寄存器地址 |
| `ALLCH_ON_H` | 所有通道开始高字节寄存器地址 |
| `ALLCH_OFF_L` | 所有通道结束低字节寄存器地址 |
| `ALLCH_OFF_H` | 所有通道结束高字节寄存器地址 |
| `POSSIBLE_ADDRESSES` | 可能的I2C地址列表 |

#### 主要方法

| 方法名 | 描述 |
|--------|------|
| `__init__(i2c, address)` | 初始化E2PCA9685 |
| `detect()` | 检测E2PCA9685是否存在 |
| `initialize()` | 初始化E2PCA9685 |
| `set_pwm(channel, on, off)` | 设置单个通道的PWM值 |
| `set_all_pwm(on, off)` | 设置所有通道的PWM值 |
| `set_fan_speed(speed_level)` | 设置风扇转速，取值范围[0,100] |

#### 使用示例

```python
# 创建I2C总线对象
i2c = I2CBase("/dev/i2c-5")

# 创建E2PCA9685对象
e2_pca = E2PCA9685(i2c)

# 检测设备并初始化
if e2_pca.detect() and e2_pca.initialize():
    # 设置风扇转速
    e2_pca.set_fan_speed(50)  # 设置风扇转速为50%
```

### 3.2 E2DeviceManager 类

`E2DeviceManager` 类是E2设备管理器，用于统一管理E2板上的各种设备。

#### 主要属性

| 属性名 | 描述 |
|--------|------|
| `i2c` | I2C总线对象 |
| `fan` | 风扇设备对象 |

#### 主要方法

| 方法名 | 描述 |
|--------|------|
| `__init__()` | 初始化E2设备管理器 |
| `_scan_i2c_bus()` | 扫描可用的I2C总线 |
| `scan_devices()` | 扫描E2设备 |
| `set_fan_speed(speed_level)` | 设置风扇转速，取值范围[0,100] |
| `close()` | 关闭所有设备 |

#### 使用示例

```python
# 创建E2设备管理器
manager = E2DeviceManager()

# 设置风扇转速
manager.set_fan_speed(50)  # 设置风扇转速为50%

# 关闭设备
manager.close()
```

## 4. 常见应用场景

### 4.1 风扇控制

```python
def demo_fan_control():
    manager = E2DeviceManager()
    
    try:
        # 循环调整风扇转速
        speeds = [0, 20, 50, 90]
        for speed in speeds:
            print(f"设置风扇转速: {speed}%")
            manager.set_fan_speed(speed)
            time.sleep(3)
    finally:
        # 关闭前停止风扇
        manager.set_fan_speed(0)
        manager.close()
```

### 4.2 温度自动控制风扇

```python
def demo_auto_fan_control():
    import random  # 模拟温度传感器
    
    manager = E2DeviceManager()
    
    try:
        while True:
            # 模拟获取温度值（实际应用中应从传感器获取）
            temperature = random.uniform(20, 60)
            
            # 根据温度调整风扇转速
            if temperature < 30:
                speed = 0
            elif temperature < 40:
                speed = 20
            elif temperature < 50:
                speed = 50
            else:
                speed = 90
            
            print(f"当前温度: {temperature:.1f}°C, 设置风扇转速: {speed}%")
            manager.set_fan_speed(speed)
            
            time.sleep(2)
    finally:
        manager.set_fan_speed(0)
        manager.close()
```

## 5. 安装与依赖

### 5.1 依赖项

- Python 3.6+
- 需要root权限访问I2C设备

### 5.2 安装说明

1. 确保I2C总线已启用
   ```bash
   sudo raspi-config
   # 选择 "Interfacing Options" -> "I2C" -> "Yes"
   ```

2. 将E2设备控制库保存为Python模块
   ```bash
   # 创建目录结构
   mkdir -p i2c_lib
   mkdir -p devices_manager
   
   # 将库文件保存到模块目录
   # i2c_lib/__init__.py
   # i2c_lib/i2c.py
   # i2c_lib/e2_pca9685.py
   # devices_manager/__init__.py
   # devices_manager/e2.py
   # e2_example.py
   ```

3. 直接运行程序
   ```bash
   sudo python3 e2_example.py
   ```

## 6. 故障排除

### 6.1 设备无法打开

- 检查I2C总线是否已启用
- 检查设备权限
- 尝试使用sudo运行程序

### 6.2 设备无法检测

- 检查设备连接是否正常
- 检查设备地址是否正确
- 确认使用的是正确的I2C总线

### 6.3 风扇不转动

- 检查电源连接
- 确认E2PCA9685初始化成功
- 尝试设置更高的转速值

## 7. 扩展指南

如需添加更多E2设备的支持，可按照以下步骤进行：

1. 创建新的设备类
2. 实现 `detect()` 和 `initialize()` 方法
3. 添加设备特有的功能方法
4. 在 `E2DeviceManager` 中添加对新设备的支持

## 8. 与E1设备库的互操作

E2设备库和E1设备库可以并存，不会相互干扰。如果需要同时使用E1和E2设备，可以分别创建它们的设备管理器：

```python
from devices_manager.e1 import E1DeviceManager
from devices_manager.e2 import E2DeviceManager

# 创建E1设备管理器
e1_manager = E1DeviceManager()

# 创建E2设备管理器
e2_manager = E2DeviceManager()

# 同时使用E1和E2设备
e1_manager.set_led_color(255, 0, 0)  # 设置E1的LED为红色
e2_manager.set_fan_speed(50)        # 设置E2的风扇转速为50%

# 关闭所有设备
e1_manager.close()
e2_manager.close()
```

## 9. 安全注意事项

- 使用root权限运行程序时需谨慎
- 避免频繁读写I2C设备，以防止损坏
- 避免长时间高速运行风扇，以防止过热和损耗
- 关闭程序前确保调用close()方法释放资源