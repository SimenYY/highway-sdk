import socketserver
from highway_sdk.vendors.vms.fenghai.spec import Frame, What


class TCPFendhaiHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data = self.request.recv(1024)

        f = Frame.unpack(data)
        match f.what:
            # TODO: 现场获取报文
            case What.GET_ITEM.value:
                hex_str = "02 30 31 30 30 30 30 30 35 30 30 30 31 30 30 30 30 30 5C 66 73 32 34 32 34 5C 63 30 30 30 32 35 35 30 30 30 30 30 30 CB ED B5 C0 C2 B7 B6 CE 5C 6E BD F7 C9 F7 BC DD CA BB E7 4F 03 "
            case What.GET_BRIGHTNESS_AND_MODE.value:
                hex_str = "02 30 31 31 31 35 F4 74 03"
            case What.UPLOAD_FILE.value:
                hex_str = ""
            case What.DOWNLOAD_FILE.value:
                hex_str = "02 30 31 5B 70 6C 61 79 6C 69 73 74 5D 0D 0A 6E 77 69 6E 64 6F 77 73 3D 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 79 3D 30 0D 0A 77 69 6E 64 6F 77 73 30 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 30 5F 68 3D 33 30 30 0D 0A 69 74 65 6D 5F 6E 6F 3D 32 0D 0A 69 74 65 6D 30 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 38 0D 0A 69 74 65 6D 31 3D 33 30 30 2C 31 2C 30 2C 5C 42 30 30 39 0D 0A 77 69 6E 64 6F 77 73 31 5F 78 3D 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 79 3D 33 30 30 0D 0A 77 69 6E 64 6F 77 73 31 5F 77 3D 35 31 32 0D 0A 77 69 6E 64 6F 77 73 31 5F 68 3D 38 34 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 5F 6E 6F 3D 31 0D 0A 77 69 6E 64 6F 77 73 31 5F 69 74 65 6D 30 3D 35 30 30 2C 31 2C 30 2C 5C 66 73 33 32 33 32 5C 63 32 35 35 32 35 35 30 30 30 30 30 30 B8 DF CB D9 B9 AB C2 B7 20 D1 CF BD FB C4 E6 D0 D0 0D 0A 43 D8 03 "
            case What.PLAY_LIST.value:
                hex_str = ""
            case _:
                hex_str = "02 03"
        self.request.sendall(bytes.fromhex(hex_str))


class TCPSansiHander(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        return super().handle()


class TCPNovaHander(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        return super().handle()


class TCPXiankeHander(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        return super().handle()


class TCPDianmingHander(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        return super().handle()


class TCPJingxiaoHander(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        return super().handle()



