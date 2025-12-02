from PySide6 import QtWidgets
from PySide6.QtWidgets import QMainWindow, QApplication
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtCore import QTime, QTimer
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression
from uv_led_controller import Controller
import os, json

try:
    controller_object = Controller()  
except Exception as e:
    print("unable to connect to the UV controller")

#contains cure step 1-5 information such as time and intensity
step_dictonary = {
    i: {"intensity": 0, "time":"00:00:00", "pos":0, "step": "STEP "+ str(i+1)}
    for i in range(0, 5)
}
#stores the current postion of cure step
pos_dictonary = {
    "pos": 0
}

# def func_ch_button(indicator):
#     if indicator.isChecked():
        
#         indicator.setChecked(False)
#     else:
        
#         indicator.setChecked(True)

#function for the intensity button (100%) that sets the current intensity to that buttons value
def func_setIntensity_button(intensity_control, intensity_button):
    intensity_value = intensity_button.text()
    intensity_value = intensity_value.strip("%")
    print(intensity_value)
    intensity_control.setValue(int(intensity_value))
    
#function for the save button that sets the intensity button setting the value base on the current intensity displayed
def func_saveIntensity_button(intensity_control, intensity_button):
    value = intensity_control.value()
    intensity_button.setText(str(value) + "%")

#function for the on/off button that turns on the UV controller
def func_uv_onOff_button(self, controller_object):
    intensity_control = self.intensity_control
    indicator = self.onOff_indicator

    controller_object.func_set_uv_intensity(intensity_control.value())

    uv_list = []

    if indicator.isChecked():
        print("Turning on the uv off")
        controller_object.func_uv_off()
        indicator.setChecked(False)
    else:
        print("Turning on the uv on... power set to", intensity_control.value())
        indicator.setChecked(True)

        uv_list = func_check_ch(self, uv_list)
        controller_object.func_uv_on(uv_list)

#function that returns a list that determines which uv heads need to be turned on
def func_check_ch(self, uv_list):
    if (self.ch1_button.isChecked() and self.ch2_button.isChecked() and self.ch3_button.isChecked() and self.ch4_button.isChecked()):
        uv_list.append(0)
    else:
        if self.ch1_button.isChecked():
            uv_list.append(1)
        if self.ch2_button.isChecked():
            uv_list.append(2)
        if self.ch3_button.isChecked():
            uv_list.append(3)
        if self.ch4_button.isChecked():
            uv_list.append(4)
    print(uv_list)
    
    return uv_list

#function that sets and displays the timer, as well I start the timer
def func_setTimer(self):
    entered_time = self.timer_input.text()

    print(entered_time)

    time_list = entered_time.split(":")

    func_set_time_display(self, time_list)
    
    start_timer(self)

#function that handles the time being displayed
def func_set_time_display(self, time_list):
    if(len(time_list) == 3):
        hours = time_list[0]
        min = time_list[1]
        sec = time_list[2]

    self.current_time = QTime(int(hours), int(min), int(sec))
    self.timer_display.setText(self.current_time.toString("hh:mm:ss"))

#function that runs the timer
def start_timer(self):
    # func_uv_onOff_button(self, controller_object)
    self.timer.start()

#function that updates the time and signals the next time if using uv step cure
def update_time(self):
    self.current_time = self.current_time.addSecs(-1)
    self.timer_display.setText(self.current_time.toString("hh:mm:ss"))
  
    if(self.current_time.toString("hh:mm:ss") == "00:00:00"):
        # func_uv_onOff_button(self, controller_object)
        self.timer.stop()
        if(self.step_indicator.isChecked()):
            func_next_step_control(self)

#function that continues the next step cure process
def func_next_step_control(self):
    if (pos_dictonary["pos"] > 4):
        print("Step Procedure Completed")
        self.step_indicator.setChecked(False)

        revert_color_change(self, pos_dictonary['pos'])
    else:
        if (step_dictonary[pos_dictonary["pos"]]["intensity"] == 0):
            print("Skipping Step Ending Early")
            self.step_indicator.setChecked(False)
        else:
            revert_color_change(self, pos_dictonary['pos'])

            self.step_display.setText(step_dictonary[pos_dictonary["pos"]]["step"])
            func_set_time_display(self, step_dictonary[pos_dictonary["pos"]]["time"])
            self.intensity_control.setValue(step_dictonary[pos_dictonary["pos"]]["intensity"])
            self.timer.start()

            color_change(self, pos_dictonary['pos']+1)

        pos_dictonary["pos"] += 1

#function that switches between gui mode to manual mode
def func_manual_mode(self):
    if(self.manual_box.isChecked()):
        print("Going Manual, Disabling GUI")
        controller_object.func_manual_control_enable()
    else:
        print("Going Program mode, enabling GUI") 
        controller_object.func_program_control_enable()

#function that begins the process of the step cure
def func_start_step_control(self):
    pos_dictonary["pos"] = 0
    self.step_indicator.setChecked(True)

    for i in range (5):
        step_num = i + 1
        intensity_widget = getattr(self, f"step{step_num}_intensity")
        time_widget = getattr(self, f"step{step_num}_time")
        step_dictonary[i]["intensity"] = int(intensity_widget.value())
        step_dictonary[i]["time"] = time_widget.text().split(":")

    pos_dictonary["pos"] += 1
    
    func_set_time_display(self, self.step1_time.text().split(":"))
    self.intensity_control.setValue(int(self.step1_intensity.value()))
    self.step_display.setText( step_dictonary[0]["step"])

    color_change(self, pos_dictonary['pos'])

    start_timer(self)  

def color_change(self, index):
    color_widget = getattr(self, f"step{index}_intensity")
    color_widget.setStyleSheet("background-color: rgb(181, 234, 170); color: rgb(0, 0, 0);")
    color_widget = getattr(self, f"step{index}_time")
    color_widget.setStyleSheet("background-color: rgb(181, 234, 170); color: rgb(0, 0, 0);")

def revert_color_change(self, index):
    orginal_style = self.intensity_control.styleSheet()
    orginal_style2 = self.timer_input.styleSheet()
    color_widget = getattr(self, f"step{index}_intensity")
    color_widget.setStyleSheet(orginal_style)
    color_widget = getattr(self, f"step{index}_time")
    color_widget.setStyleSheet(orginal_style2)


#function for the time combobox    
def func_time_comboBox(self): 
    current_index = self.time_comboBox.currentIndex()
    if(current_index == 0):
        self.timer_input.setText("00:03:00")
    elif(current_index == 1):
        self.timer_input.setText("00:05:00")
    elif(current_index == 2):
        self.timer_input.setText("00:20:00")

#function that opens the save_procedure json file
def func_open_json():
    with open("saved_procedure.json") as file:
        data = json.load(file)
    return data

#function that updates the cure process intensity and time based on which combo box is choosen
def func_step_comboBox(self):
    current_index = self.step_comboBox.currentIndex()

    if current_index == 0:
        self.save_procedure_button.show()
        self.save_procedure_input.show()
    else:
        data = func_open_json()

        self.save_procedure_button.hide()
        self.save_procedure_input.hide()
            
        self.step1_intensity.setValue(data[str(current_index)]["step_1_value"])
        self.step2_intensity.setValue(data[str(current_index)]["step_2_value"])
        self.step3_intensity.setValue(data[str(current_index)]["step_3_value"])
        self.step4_intensity.setValue(data[str(current_index)]["step_4_value"])
        self.step5_intensity.setValue(data[str(current_index)]["step_5_value"])
        self.step1_time.setText(data[str(current_index)]["step_1_time"])
        self.step2_time.setText(data[str(current_index)]["step_2_time"])
        self.step3_time.setText(data[str(current_index)]["step_3_time"])
        self.step4_time.setText(data[str(current_index)]["step_4_time"])
        self.step5_time.setText(data[str(current_index)]["step_5_time"])

#function that saves the procedure in the json file and adds it into the procedure combo box
def func_save_procedure(self):

    new_data = {
     str(self.step_comboBox.count()): {
        "procedure": self.save_procedure_input.text(),        
        "step_1_value": self.step1_intensity.value(), 
        "step_2_value": self.step2_intensity.value(), 
        "step_3_value": self.step3_intensity.value(), 
        "step_4_value": self.step4_intensity.value(), 
        "step_5_value": self.step5_intensity.value(), 
        "step_1_time": self.step1_time.text(), 
        "step_2_time": self.step2_time.text(), 
        "step_3_time": self.step3_time.text(), 
        "step_4_time": self.step4_time.text(), 
        "step_5_time": self.step5_time.text()
        }
    }

    self.step_comboBox.addItem(new_data[str(self.step_comboBox.count())]["procedure"])
   
    with open("saved_procedure.json", "r") as file:
        existing_data = json.load(file)
    
    existing_data.update(new_data)

    with open("saved_procedure.json", "w") as file:
        json.dump(existing_data, file, indent=4)

    
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):

        super().__init__()
        ui_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Controller_Design.ui") 

        loader = QUiLoader()
        file = QFile(ui_file_path)
        
        if not file.open(QIODevice.ReadOnly):
            print(f"Cannot open {ui_file_path}: {file.errorString()}")
            return
        self.ui = loader.load(file)
        file.close()
 
        # self.ch1_button.clicked.connect(lambda: func_ch_button(self.ch1_indicator))
        # self.ch2_button.clicked.connect(lambda: func_ch_button(self.ch2_indicator))
        # self.ch3_button.clicked.connect(lambda: func_ch_button(self.ch3_indicator))
        # self.ch4_button.clicked.connect(lambda: func_ch_button(self.ch4_indicator))

        self.ui.setIntensity1_button.clicked.connect(lambda: func_setIntensity_button(self.ui.intensity_control, self.ui.setIntensity1_button))
        self.ui.setIntensity2_button.clicked.connect(lambda: func_setIntensity_button(self.ui.intensity_control, self.ui.setIntensity2_button))
        self.ui.setIntensity3_button.clicked.connect(lambda: func_setIntensity_button(self.ui.intensity_control, self.ui.setIntensity3_button))
        self.ui.setIntensity4_button.clicked.connect(lambda: func_setIntensity_button(self.ui.intensity_control, self.ui.setIntensity4_button))

        self.ui.saveIntensity1_button.clicked.connect(lambda: func_saveIntensity_button(self.ui.intensity_control, self.ui.setIntensity1_button))
        self.ui.saveIntensity2_button.clicked.connect(lambda: func_saveIntensity_button(self.ui.intensity_control, self.ui.setIntensity2_button))
        self.ui.saveIntensity3_button.clicked.connect(lambda: func_saveIntensity_button(self.ui.intensity_control, self.ui.setIntensity3_button))
        self.ui.saveIntensity4_button.clicked.connect(lambda: func_saveIntensity_button(self.ui.intensity_control, self.ui.setIntensity4_button))

        self.ui.timer_input.setInputMask("00:00:00;_")
        self.ui.step1_time.setInputMask("00:00:00;_")
        self.ui.step2_time.setInputMask("00:00:00;_")
        self.ui.step3_time.setInputMask("00:00:00;_")
        self.ui.step4_time.setInputMask("00:00:00;_")
        self.ui.step5_time.setInputMask("00:00:00;_")

        time_regex = QRegularExpression("^(?:[01]\\d|2[0-3]):[0-5]\\d:[0-5]\\d$")
        time_validator = QRegularExpressionValidator(time_regex, self.ui.timer_input)

        self.ui.timer_input.setValidator(time_validator)
        self.ui.step1_time.setValidator(time_validator)
        self.ui.step2_time.setValidator(time_validator)
        self.ui.step3_time.setValidator(time_validator)
        self.ui.step4_time.setValidator(time_validator)
        self.ui.step5_time.setValidator(time_validator)
        
        self.ui.onOff_button.clicked.connect(lambda: func_uv_onOff_button(self.ui, controller_object))
        self.ui.confirmTimer_button.clicked.connect(lambda: func_setTimer(self.ui))

        self.ui.manual_box.clicked.connect(lambda: func_manual_mode(self.ui))
        self.ui.step_control_button.clicked.connect(lambda: func_start_step_control(self.ui))

        self.ui.time_comboBox.currentIndexChanged.connect(lambda: func_time_comboBox(self.ui))
        self.ui.step_comboBox.currentIndexChanged.connect(lambda: func_step_comboBox(self.ui))

        self.ui.save_procedure_button.clicked.connect(lambda: func_save_procedure(self.ui))
        self.ui.save_procedure_button.hide()
        self.ui.save_procedure_input.hide()

        data = func_open_json()

        for procedure_id, procedure in data.items():
            self.ui.step_comboBox.addItem(procedure["procedure"])
  
        self.ui.timer = QTimer(self.ui)
        self.ui.timer.setInterval(1000)  # 1 second
        self.ui.timer.timeout.connect(lambda: update_time(self.ui))

        self.setCentralWidget(self.ui)                  # ← This makes the GUI appear!
        self.setWindowTitle("UV LED Controller ♡")     # ← Pretty title for Mommy
        self.resize(1100, 750)                          # ← Nice big window
        
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())