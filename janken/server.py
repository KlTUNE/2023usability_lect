import socket;
import threading

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# 接続待ちするサーバのホスト名とポート番号を指定
host = "0.0.0.0"
port = 55580
argument = (host, port)
sock.bind(argument)
# 2 ユーザまで接続を許可
sock.listen(2)
clients = []

# 接続済みクライアントは読み込みおよび書き込みを繰り返す
def loop_handler(connection, address):
    while True:
        try:
            #クライアント側から受信する
            res = connection.recv(4096)
            for value in clients:
                if value[1][0] == address[0] and value[1][1] == address[1] :
                    print(res.decode())
                else:
                    value[0].send(res)
        except Exception as e:
            print(e)


while True:
    try:
        # 接続要求を受信
        print("接続待ち状態")
        conn, addr = sock.accept()

        clients.append((conn, addr))
        # スレッド作成
        thread = threading.Thread(target=loop_handler, args=(conn, addr), daemon=True)
        # スレッドスタート
        thread.start()

    except KeyboardInterrupt:
        sock.close()
        break