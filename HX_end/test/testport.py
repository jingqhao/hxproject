import time
import serial
from pymodbus.client import ModbusSerialClient

timings = {}
def timing(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        timings[func.__name__] = elapsed_time
        print(f"{func.__name__} 执行时间: {elapsed_time} 秒")
        return result
    return wrapper


@timing
def testport():
    com = ModbusSerialClient(method='rtu', port='COM8', baudrate=115200, parity='N', stopbits=1, bytesize=8)
    res = com.read_holding_registers(26000, 1, 1).registers[0]
    if res == 1:
        var = 26500
        for i in range(6):
            com.write_register(var, 100, 1)
            var += 2
        com.write_register(26400, 12, 1)
        com.write_register(26500, 12, 1)
    
    while True:
        res2 = com.read_holding_registers(26500, 1, 1).registers[0]
        if res2 == 12:
            break
    print("finish")

if __name__ == "__main__":
    testport()