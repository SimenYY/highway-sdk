from gettext import find
import socket
import threading
import time
from highway_sdk.driver.vms.nova.v3_11_5.spec import NovaPacket, NovaWhat
from highway_sdk.driver.vms.xianke.v1_4_2.spec import XianKeWhat, XianKePacket

# ==============================================================================
# TCP服务端mock基类
# ==============================================================================
class TCPServerMock:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8888,
        bufsize: int = 2**16,
        timeout: float = 1.0,
    ) -> None:
        self.host = host
        self.port = port
        self.bufsize = bufsize
        self.timeout = timeout
        self.sock = None
        self.thread = None
        self.is_running = False

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self.run, daemon=True)
            self.thread.start()
            time.sleep(0.1)

    def stop(self):
        if self.is_running:
            self.is_running = False
            if self.thread:
                self.thread.join(timeout=1.0)

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        print(f"TCP服务器启动成功，监听地址：{self.host}:{self.port}")
        try:
            while self.is_running:
                try:
                    self.sock.settimeout(self.timeout)
                    conn, addr = self.sock.accept()

                    threading.Thread(
                        target=self.handle_client,
                        args=(conn, addr),
                        daemon=True,
                    ).start()
                except socket.timeout:
                    continue
                except Exception as e:
                    print(e)
        except KeyboardInterrupt:
            print("TCP服务器正在关闭...")
        except Exception as e:
            print(f"TCP服务器错误：{e}")
        finally:
            self.sock.close()
            print("TCP服务器已关闭")

    def handle_client(self, conn: socket.socket, addr: tuple):
        pass


# ==============================================================================
# VMS 设备mock
# ==============================================================================
class VmsNovaMock_v3_11_5(TCPServerMock):
    def handle_client(self, conn: socket.socket, addr: tuple):
        try:
            while self.is_running:
                try:
                    data = conn.recv(self.bufsize)
                    if not data:
                        print(f"客户端 {addr} 已断开")
                        break
                    print(f"收到 {addr} 数据：{data.hex(' ')}")
                    p = NovaPacket.unpack(data)
                    match p.what:
                        case NovaWhat.SEND_FILE_NAME_REQ:
                            conn.send(bytes.fromhex("AA FF FF 12 01 CC A1 B4"))
                        case NovaWhat.SEND_FILE_CONTENT_REQ:
                            conn.send(bytes.fromhex("AA FF FF 14 01 00 01 CC 91 C4"))
                            conn.send(bytes.fromhex("AA FF FF F9 01 CC A6 94"))
                        case NovaWhat.PLAY_PLAYLIST_REQ:
                            conn.send(bytes.fromhex("AA FF FF 1C 01 CC BA A4"))
                        case NovaWhat.GET_NOW_PLAY_CONTENT_REQ:
                            conn.send(
                                bytes.fromhex(
                                    "AA FF FF 2E 01 01 01 5B 69 74 65 6D 31 5D 0A 70 61 72 61 6D 3D 31 30 30 2C 31 2C 31 2C 31 2C 30 2C 35 2C 31 2C 30 2C 31 0A 74 78 74 31 3D 31 30 2C 30 2C 33 2C 31 36 31 36 2C 31 2C 38 2C 30 2C E8 BD A6 E7 89 8C EF BC 9A E5 86 80 41 33 31 38 41 41 E5 A4 A7 E8 B4 A7 E8 BD A6 2C 31 39 32 2C 33 32 30 2C 30 0A 74 78 74 70 61 72 61 6D 31 3D 30 2C 30 CC 20 DF"
                                )
                            )
                        case NovaWhat.GET_NOW_PLAY_ALL_CONTENT_REQ:
                            conn.send(
                                bytes.fromhex(
                                    "AA FF FF 3B 01 5B 61 6C 6C 5D 0A 69 74 65 6D 73 3D 31 0A 5B 69 74 65 6D 31 5D 0A 70 61 72 61 6D 3D 31 30 30 2C 31 2C 31 2C 31 2C 30 2C 35 2C 31 2C 30 2C 31 0A 74 78 74 31 3D 31 30 2C 30 2C 33 2C 31 36 31 36 2C 31 2C 38 2C 30 2C E8 BD A6 E7 89 8C EF BC 9A E5 86 80 41 33 31 38 41 41 E5 A4 A7 E8 B4 A7 E8 BD A6 2C 31 39 32 2C 33 32 30 2C 30 0A 74 78 74 70 61 72 61 6D 31 3D 30 2C 30 CC D9 25"
                                )
                            )
                        case NovaWhat.GET_SCREEN_SIZE_REQ:
                            conn.send(bytes.fromhex("AA FF FF 83 A0 02 C0 01 CC 05 20"))
                        case NovaWhat.GET_NOW_BRIGHTNESS_REQ:
                            conn.send(bytes.fromhex("AA FF FF C3 02 FF CC 3A 2F"))
                except Exception as e:
                    print(e)
                    break
        finally:
            conn.close()
            print(f"已关闭与客户端 {addr} 的连接")
            

class VmsXiankeMock_v1_4_2(TCPServerMock):
    
    def handle_client(self, conn: socket.socket, addr: tuple):
        try:
            while self.is_running:
                try:
                    data = conn.recv(self.bufsize)
                    if not data:
                        print(f"客户端 {addr} 已断开")
                        break
                    print(f"收到 {addr} 数据：{data.hex(' ')}")
                    p = XianKePacket.unpack(data)
                    match p.what:
                        case XianKeWhat.UPLOAD_FILE:
                            conn.send(bytes.fromhex("02 32 30 30 30 01 B4 95 03"))
                        case XianKeWhat.DOWNLOAD_FILE:
                            conn.send(bytes.fromhex("02 32 31 30 30 01 30 31 32 6C 69 73 74 5C 30 30 30 2E 78 6B 6C 30 30 30 30 5B 4C 49 53 54 5D 0D 0A 49 74 65 6D 43 6F 75 6E 74 3D 30 30 32 0D 0A 49 74 65 6D 30 30 3D 32 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30 30 30 30 30 30 5C 46 73 33 32 5C 54 32 35 35 30 30 30 30 30 30 30 30 30 5C 42 30 30 30 30 30 30 30 30 30 30 30 30 5C 55 C9 EE DB DA CF D4 BF C6 BF C6 BC BC D3 D0 CF DE B9 AB CB BE 0D 0A 49 74 65 6D 30 31 3D 32 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30 30 30 30 30 30 5C 46 73 33 32 5C 54 30 30 30 32 35 35 30 30 30 30 30 30 5C 42 30 30 30 30 30 30 30 30 30 30 30 30 5C 55 C9 EE DB DA CF D4 BF C6 BF C6 BC BC D3 D0 CF DE B9 AB CB BE 0D 0A F2 52 03"))
                        case XianKeWhat.PLAY_LIST:
                            conn.send(bytes.fromhex("02 32 32 30 30 01 59 FD 03"))
                        case XianKeWhat.GET_NOW_PLAY_CONTENT:
                            conn.send(bytes.fromhex("02 32 34 30 30 01 34 2C 31 2C 30 2C 31 2C 31 2C 5C 43 30 30 30 30 30 30 5C 49 30 30 30 3D B0 03"))
                        case XianKeWhat.GET_NOW_PLAY_ALL_CONTENT:
                            conn.send(bytes.fromhex("02 32 33 30 30 01 30 30 30 2E 78 6B 6C 22 45 03"))
                        case XianKeWhat.GET_NOW_BRIGHTNESS:
                            conn.send(bytes.fromhex("02 30 35 30 30 01 31 30 30 30 30 30 30 30 30 10 40 03"))
                except Exception as e:
                    print(e)
                    break
        finally:
            conn.close()
            print(f"已关闭与客户端 {addr} 的连接")