from highway_sdk.core.protocol import TCPClientProtocol
from .spec import DianMingMsgBuilder

class VmsDianMingProtocl(TCPClientProtocol):
    """电明VMS协议实现"""
    
    def get_item(self):
        """读取当前显示内容
        """
        self.send(DianMingMsgBuilder.build_get_play_item())
    
    def get_play(self):
        """读取当前播放列表
        """
        pass