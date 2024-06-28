import PySide6
from PySide6.QtWidgets import QPushButton, QApplication, QLabel, QWidget, QLineEdit
import os
import sys
import time
import schedule
import concurrent.futures as confu
import module.voice_power as vp
from pydub import AudioSegment
from pydub.playback import play
import threading
flag = True
alarm_flag = False
app_exit = False
target = "00:00"
test = 0


class Title(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

class Label1(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

class SetAlarm(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

class CanselAlarm(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

class InputTime(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("すくーむ")
        windowWidth = 1000
        windowHeight = 800
        self.resize(windowWidth, windowHeight)
        self.label()
        self.button()
        self.lineedit()

    def label(self):
        title = Title(self)
        title.setText("すくーむ")
        title.move(390, 30)

        self.label1 = Label1(self)
        self.label1.setText("アラームをセットする時間を入力してください")
        self.label1.move(100, 30)

    def button(self):
        set_button = SetAlarm(self)
        set_button.setText("アラームをセットする")
        set_button.move(200, 500)
        set_button.pressed.connect(lambda: self.change_color_pressed(set_button))
        set_button.released.connect(lambda: self.change_color_released(set_button))
        set_button.released.connect(self.start_alarm)

        stop_button = CanselAlarm(self)
        stop_button.setText("アラームを取り消す")
        stop_button.move(550, 500)
        stop_button.pressed.connect(lambda: self.change_color_pressed(stop_button))
        stop_button.released.connect(lambda: self.change_color_released(stop_button))
        stop_button.released.connect(self.stop_alarm)

    def lineedit(self):
        self.input_time = InputTime(self)
        self.input_time.setText(target)
        self.input_time.move(200, 200)
        self.input_time.resize(600, 250)
        self.input_time.returnPressed.connect(self.start_alarm)

    def change_color_pressed(self, button):
        button.setStyleSheet("background-color: rgb(200, 200, 200);")

    def change_color_released(self, button):
        button.setStyleSheet("background-color: rgb(210, 210, 210);")

    def start_alarm(self):
        global flag, alarm_flag, target
        target = self.input_time.text()
        self.label1.setText(target + "にアラームをセットしました")
        flag = True
        alarm_flag = True

    def stop_alarm(self):
        global flag, alarm_flag
        self.label1.setText("アラームをセットする時間を入力してください")
        vp.app_exit_func()
        flag = False
        alarm_flag = False


def alarm_multi():
    with confu.ThreadPoolExecutor() as executor:
        executor.map(start_sound, [1])
        executor.map(get_voice_power, [1])

def start_sound(x):
    global flag, app_exit, test
    sound = AudioSegment.from_file("./module/sound.wav")
    while flag == True and app_exit == False:
        play(sound)
        sound += 1
        test += 1

def get_voice_power(x):
    global flag, alarm_flag
    flag = vp.voice_power(10, "起きたよ")
    alarm_flag = False

def set_alarm ():
    global flag, alarm_flag, target, app_exit
    while app_exit == False:
        if alarm_flag == True:
            schedule.every().day.at(target).do(alarm_multi)

            while flag == True and app_exit == False:
                schedule.run_pending()
                time.sleep(1)

def main():
    global app_exit

    with open('./module/main.css', 'r') as f:
        css = f.read()

    thread = threading.Thread(target=set_alarm)
    thread.start()

    dirname = os.path.dirname(PySide6.__file__)
    plugin_path = os.path.join(dirname, 'plugins', 'pl^atforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setStyleSheet(css)
    window.show()

    if (not app.exec()):
        app_exit = True
        vp.app_exit_func()
        sys.exit()


if __name__ == "__main__":
    main()