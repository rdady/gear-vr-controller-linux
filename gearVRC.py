import gatt
#import struct
import uinput
import signal
import math
import time
import numpy as np
import sys

manager = gatt.DeviceManager(adapter_name='hci0')

class AnyDevice(gatt.Device):
    def connect_succeeded(self):
        super().connect_succeeded()
        print("[%s] Connected" % (self.mac_address))

    def connect_failed(self, error):
        super().connect_failed(error)
        print("[%s] Connection failed: %s" % (self.mac_address, str(error)))

    def disconnect_succeeded(self):
        super().disconnect_succeeded()
        print("[%s] Disconnected" % (self.mac_address))

    def services_resolved(self):
        super().services_resolved()

        controller_data_service = next(
            s for s in self.services
            if s.uuid == '4f63756c-7573-2054-6872-65656d6f7465')
        
        controller_setup_data_characteristic = next(
            c for c in controller_data_service.characteristics
            if c.uuid == 'c8c51726-81bc-483b-a052-f7a14ea3d282')
        
        controller_data_characteristic = next(
            c for c in controller_data_service.characteristics
            if c.uuid == 'c8c51726-81bc-483b-a052-f7a14ea3d281')

        cmd = bytearray(b'\x01\x00')
        controller_setup_data_characteristic.write_value(cmd)

        self.__setup_characteristic = controller_setup_data_characteristic
        self.__sensor_characteristic = controller_data_characteristic
        self.__axisX = self.__axisY = 0;
        self.__device = uinput.Device([uinput.REL_X, uinput.REL_Y, uinput.BTN_LEFT, uinput.BTN_RIGHT, uinput.KEY_LEFTCTRL, uinput.KEY_LEFTALT, uinput.KEY_HOME, uinput.KEY_UP, uinput.KEY_DOWN, uinput.KEY_LEFT, uinput.KEY_RIGHT, uinput.KEY_VOLUMEUP, uinput.KEY_VOLUMEDOWN, uinput.KEY_KPPLUS, uinput.KEY_KPMINUS, uinput.KEY_PAGEUP, uinput.KEY_PAGEDOWN])
        self.__reset = self.__volbtn = self.__tchbtn = True
        
        self.__time = round(time.time()) + 10
        
        controller_data_characteristic.enable_notifications()
        
    def keepalive(self):
        # test time and each minute send a keepalive
        if (time.time() > self.__time):
            self.__time = round(time.time()) + 10
            cmd = bytearray(b'\x04\x00')
            for i in range(4):
                self.__setup_characteristic.write_value(cmd)

    def characteristic_value_updated(self, characteristic, value):
        if (characteristic == self.__sensor_characteristic):
            self.keepalive()
            int_values = [x for x in value]
            
            axisX = (((int_values[54] & 0xF) << 6) + ((int_values[55] & 0xFC) >> 2)) & 0x3FF;
            axisY = (((int_values[55] & 0x3) << 8) + ((int_values[56] & 0xFF) >> 0)) & 0x3FF;
            accelX = np.uint16((int_values[4] << 8) + int_values[5]) * 10000.0 * 9.80665 / 2048.0;
            accelY = np.uint16((int_values[6] << 8) + int_values[7]) * 10000.0 * 9.80665 / 2048.0;
            accelZ = np.uint16((int_values[8] << 8) + int_values[9]) * 10000.0 * 9.80665 / 2048.0;
            gyroX = np.uint16((int_values[10] << 8) + int_values[11]) * 10000.0 * 0.017453292 / 14.285;
            gyroY = np.uint16((int_values[12] << 8) + int_values[13]) * 10000.0 * 0.017453292 / 14.285;
            gyroZ = np.uint16((int_values[14] << 8) + int_values[15]) * 10000.0 * 0.017453292 / 14.285;
            magnetX = np.uint16((int_values[32] << 8) + int_values[33]) * 0.06;
            magnetY = np.uint16((int_values[34] << 8) + int_values[35]) * 0.06;
            magnetZ = np.uint16((int_values[36] << 8) + int_values[37]) * 0.06;
            
            triggerButton    = True if ((int_values[58] &  1) ==  1) else False
            homeButton       = True if ((int_values[58] &  2) ==  2) else False
            backButton       = True if ((int_values[58] &  4) ==  4) else False
            touchpadButton   = True if ((int_values[58] &  8) ==  8) else False
            volumeUpButton   = True if ((int_values[58] & 16) == 16) else False
            volumeDownButton = True if ((int_values[58] & 32) == 32) else False
            NoButton         = True if ((int_values[58] & 64) == 64) else False
            
            idelta = 30
            odelta = 15
            if (triggerButton == True):
                if (axisY < 158 and axisX < 158 + idelta and axisX > 158 - idelta):
                    self.__device.emit(uinput.KEY_UP, 1)
                if (axisY > 157 and axisX < 158 + idelta and axisX > 158 - idelta):
                    self.__device.emit(uinput.KEY_DOWN, 1)
                if (axisX < 158 and axisY < 158 + idelta and axisY > 158 - idelta):
                    self.__device.emit(uinput.KEY_LEFT, 1)
                if (axisX > 157 and axisY < 158 + idelta and axisY > 158 - idelta):
                    self.__device.emit(uinput.KEY_RIGHT, 1)
                if (axisX == 0 and axisY == 0):
                    self.__device.emit(uinput.KEY_UP, 0)
                    self.__device.emit(uinput.KEY_DOWN, 0)
                    self.__device.emit(uinput.KEY_LEFT, 0)
                    self.__device.emit(uinput.KEY_RIGHT, 0)
                return
            
            if (touchpadButton == True):
                if (axisX < 157 + idelta and axisX > 158 - idelta and axisY > 315 - odelta and self.__tchbtn == True):
                    self.__device.emit(uinput.KEY_PAGEDOWN, 1)
                    self.__device.emit(uinput.KEY_PAGEDOWN, 0)
                    self.__tchbtn = False
                    return
                elif (axisX < 157 + idelta and axisX > 158 - idelta and axisY < odelta and self.__tchbtn == True):
                    self.__device.emit(uinput.KEY_PAGEUP, 1)
                    self.__device.emit(uinput.KEY_PAGEUP, 0)
                    self.__tchbtn = False
                    return
                elif (axisX < 265 and axisX > 50 and axisY < 265 and axisY > 50 and self.__tchbtn == True):
                    self.__device.emit(uinput.BTN_LEFT, 1)
                    self.__tchbtn = False
                    # return is not feasable here
            else:
                self.__tchbtn = True
            
            if (homeButton == True and self.__volbtn == True):
                self.__device.emit(uinput.KEY_LEFTALT, 1)
                self.__device.emit(uinput.KEY_HOME, 1)
                self.__device.emit(uinput.KEY_HOME, 0)
                self.__device.emit(uinput.KEY_LEFTALT, 0)
                self.__volbtn = False
                return
                
            if (backButton == True and self.__volbtn == True):
                self.__device.emit(uinput.KEY_LEFTALT, 1)
                self.__device.emit(uinput.KEY_LEFT, 1)
                self.__device.emit(uinput.KEY_LEFT, 0)
                self.__device.emit(uinput.KEY_LEFTALT, 0)
                self.__volbtn = False
                return
                
            if (volumeDownButton == True and self.__volbtn == True):
                self.__device.emit(uinput.KEY_LEFTCTRL, 1, syn = False)
                self.__device.emit(uinput.KEY_KPMINUS, 1, syn = True)
                self.__device.emit(uinput.KEY_KPMINUS, 0, syn = False)
                self.__device.emit(uinput.KEY_LEFTCTRL, 0, syn = True)
                self.__volbtn = False
                return
                
            if (volumeUpButton == True and self.__volbtn == True):
                self.__volbtn = False
                self.__device.emit(uinput.KEY_LEFTCTRL, 1, syn = False)
                self.__device.emit(uinput.KEY_KPPLUS, 1, syn = True)
                time.sleep(0.05)
                self.__device.emit(uinput.KEY_KPPLUS, 0, syn = False)
                self.__device.emit(uinput.KEY_LEFTCTRL, 0, syn = True)
                return

            if (NoButton == True):
                self.__volbtn = True
                self.__tchbtn = True
                self.__device.emit(uinput.BTN_LEFT, 0)
                self.__device.emit(uinput.KEY_PAGEUP, 0)
                self.__device.emit(uinput.KEY_PAGEDOWN, 0)
                self.__device.emit(uinput.KEY_UP, 0)
                self.__device.emit(uinput.KEY_DOWN, 0)
                self.__device.emit(uinput.KEY_LEFT, 0)
                self.__device.emit(uinput.KEY_RIGHT, 0)

            if (axisX == 0 and axisY == 0):
                self.__reset = True
                return
            
            if (self.__reset == True):
                self.__reset = False
                self.__axisX = axisX
                self.__axisY = axisY
                return

            delta_X = axisX - self.__axisX
            delta_Y = axisY - self.__axisY
            delta_X = round(delta_X * 1.2)
            delta_Y = round(delta_Y * 1.2)
            
            incx = 0 if delta_X == 0 else round((0 - delta_X)/abs(delta_X))
            incy = 0 if delta_Y == 0 else round((0 - delta_Y)/abs(delta_Y))

            while (delta_X != 0 or delta_Y != 0):
                if (delta_X != 0):
                    self.__device.emit(uinput.REL_X, -incx, syn = True)
                    delta_X += incx
                if (delta_Y != 0):
                    self.__device.emit(uinput.REL_Y, -incy, syn = True)
                    delta_Y += incy

            self.__axisX = axisX
            self.__axisY = axisY

signal.signal(signal.SIGINT, lambda x,y: sys.exit(0))
print("Samsung Gear VR Controller mapper running ...")
print("Press Ctrl+C to terminate")

device = AnyDevice(mac_address='2C:BA:BA:25:6A:A1', manager=manager)
device.connect()

manager.run()

