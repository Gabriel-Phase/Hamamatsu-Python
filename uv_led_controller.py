import time
from PyExpLabSys.drivers.hamamatsu import LCL1V5
import serial.tools.list_ports

def find_serial_port():
    print("Searching available ports")

    ports = serial.tools.list_ports.comports()

    if not ports:
        print("Unable to find any connection, makae sure your device is connected")
    for port in ports:
        print(f"Device - {port.device} Description - {port.description}")


class Controller:

    lc_l1v5 = None

    def __init__(self):
        find_serial_port()
        # connects to the conntroller through the port
        self.lc_l1v5 = LCL1V5(port='COM8')
        #sets the controller, so only the program can switch it on and off
        self.lc_l1v5.select_command_communication()        

    def func_set_uv_intensity(self, value):
        if value < 0:
            value = "000"
        elif value < 10:
            value = "00" + str(value)
        elif value < 100:
            value = "0" + str(value)
        else:
            value = "100"

        self.lc_l1v5.set_step_settings(0,(value,'001','001'),('01','01','01'))

    #WARNING!!!!! Turns on all channel and turns on the uv
    def func_uv_on(self, uv_selected):
        time.sleep(0.5)
        for i in uv_selected:
            self.lc_l1v5.switch_led_on(i)
            time.sleep(0.1)
  

    #turns all channel and uv

    def func_uv_off(self): 
        self.lc_l1v5.switch_led_off(0)

    #Allows user to interact with the controller physically
    def func_manual_control_enable(self):
        self.lc_l1v5.comm("CNT0")
    
    def func_program_control_enable(self):
        self.lc_l1v5.select_command_communication()
        
        
        
   