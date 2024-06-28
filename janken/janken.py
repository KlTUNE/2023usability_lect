import numpy as np
import PySimpleGUI as sg
import time
import socket
import threading
from module.trac import hands_trac as ht
from time import sleep
import cv2

font = ("meiryo", 16)
size = (10, 6)
i = 0
cpu_num = -1

def judgment(your_num, cpu_num):
    if your_num == 0:
        if cpu_num == 0:
            result = "あいこ"
        elif cpu_num == 1:
            result = "あなたの勝ち"
        elif cpu_num == 2:
            result = "あなたの負け"

    elif your_num == 1:
        if cpu_num == 0:
            result = "あなたの負け"
        elif cpu_num == 1:
            result = "あいこ"
        elif cpu_num == 2:
            result = "あなたの勝ち"

    elif your_num == 2:
        if cpu_num == 0:
            result = "あなたの勝ち"
        elif cpu_num == 1:
            result = "あなたの負け"
        elif cpu_num == 2:
            result = "あいこ"

    return result

def make_janken():
    sg.theme("Default1")
    layout = [
        [sg.Button("スタート", key="start", font=font, size=size)],
    ]
    return sg.Window("ジャンケン", layout, finalize=True)


def make_result(your_num, cpu_num, result):
    sg.theme("Default1")
    l1 = [
        [
            sg.Text("あいて: ", font=font, size=(14, 2)),
            sg.Text("", key="CPU", font=font, size=(14, 2)),
        ]
    ]

    l2 = [
        [
            sg.Text("あなた: ", font=font, size=(14, 2)),
            sg.Text("", key="you", font=font, size=(14, 2)),
        ]
    ]

    if cpu_num == 1:
        l1 += [
            [
                sg.Image(filename="./hand/janken_choki.png", size=(300, 300)),
            ]
        ]
    elif cpu_num == 2:
        l1 += [
            [
                sg.Image(filename="./hand/janken_pa.png", size=(300, 300)),
            ]
        ]
    elif cpu_num == 0:
        l1 += [
            [
                sg.Image(filename="./hand/janken_gu.png", size=(300, 300)),
            ]
        ]
    if your_num == 1:
        l2 += [
            [
                sg.Image(filename="./hand/janken_choki.png", size=(300, 300)),
            ]
        ]
    elif your_num == 2:
        l2 += [
            [
                sg.Image(filename="./hand/janken_pa.png", size=(300, 300)),
            ]
        ]
    elif your_num == 0:
        l2 += [
            [
                sg.Image(filename="./hand/janken_gu.png", size=(300, 300)),
            ]
        ]
    layout = [
        [
            sg.Frame("", l1),
            sg.VerticalSeparator(),
            sg.Frame("", l2),
        ],
    ]
    layout += [
        [
            sg.Text(result, key="result", font=font, size=size),
            sg.Button("もう一度", key="again", font=font, size=size),
        ],
    ]
    return sg.Window("結果", layout, finalize=True)


def make_connection():
    sg.theme("Default1")
    layout = [
        [
            [
                sg.Text("IPアドレス", font=font, size=size),
                sg.InputText(key="IP", font=font, size=size),
            ],
            [
                sg.Button("接続", key="connect", font=font, size=size),
            ],
        ],
    ]
    return sg.Window("接続", layout, finalize=True)


def make_te():
    sg.theme("Default1")
    layout = [
        [
            [sg.Text("カメラに向かって出したい手を出していね", font=font, size=size)],
            [sg.Text(int(i), key="te", font=font, size=size)],
        ],
    ]
    return sg.Window("手", layout, finalize=True)

def Handler(sock):
    global cpu_num
    while True:
        try:
            cpu_num = int(sock.recv(4096).decode())
            print(cpu_num)
            print(type(cpu_num))
        except Exception as e:
            continue

window = make_connection()
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "172.0.0.1"
your_num = -1
cap = cv2.VideoCapture(0)

#10.1.57.169

while True:
    event, values = window.read(timeout=10)
    if event == sg.WINDOW_CLOSED:break

    if event == "connect":
        host = values["IP"] # values["IP"]にIPアドレスが入っている
        port = 55580
        if host != "":
            try:
                sock.connect((host, port))
                thread = threading.Thread(target = Handler, args= (sock,), daemon= True)
                thread.start()
                window.close()
                window = make_janken()
            except Exception as e:
                print(e)
                print("接続できませんでした")


    if event == "start":
        while your_num == -1:
            for i in range(5, 0, -1):  # ５秒間のカウントダウン
                print(i)
                window2 = make_te()
                time.sleep(1)
                window2.close()

            your_num = ht(cap)
        sock.send(str(your_num).encode("UTF-8"))
        while cpu_num == -1: print("待機中")
        # cpu_num = 0
        result = judgment(your_num, cpu_num)
        window.close()
        window = make_result(your_num, cpu_num, result)

        choice = {0: "グー", 1: "チョキ", 2: "パー"}
        window["CPU"].update(choice[cpu_num])
        window["you"].update(choice[your_num])


    if event == "again":  # もう一度ボタンが押されたら
        your_num = -1
        cpu_num = -1
        window.close()
        window = make_janken()


window.close()
