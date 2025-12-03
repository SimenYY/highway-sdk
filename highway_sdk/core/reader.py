from .protocol import STX, ETX

_DEFAULT_LIMIT = 2**16  # 64KB


class MessageReader:
    """报文读取器"""

    def __init__(self, limit: int = _DEFAULT_LIMIT):
        if limit < 0:
            raise ValueError("Limit cannot be <=0")

        self._limit = limit
        self._buffer = bytearray()

    def feed_data(self, data: bytes):
        if not data:
            return

        self._buffer.extend(data)

        if len(self._buffer) > 2 * self._limit:
            # 小包(1KB)应用场景下，几乎不会出现流量拥塞的情况
            # 一般设备状态数据都是可丢失的，但开发者也要感知到
            # 这个异常
            raise RuntimeError("Buffer is full")

    def iter_read_until(self, separator: bytes):
        """迭代获取报文，通过分隔符

        Args:
            separator (bytes): _description_

        Raises:
            ValueError: _description_
            RuntimeError: _description_

        Yields:
            _type_: _description_
        """
        seplen = len(separator)
        if seplen == 0:
            raise ValueError("Separator should be at least one-byte string")

        while True:
            buflen = len(self._buffer)
            if buflen < seplen:
                break

            isep = self._buffer.find(separator)
            if isep == -1:
                break

            if isep > self._limit:
                raise RuntimeError("Separator is found, but chunk is longer than limit")

            message = self._buffer[: isep + seplen]
            del self._buffer[: isep + seplen]
            yield bytes(message)

    def iter_read_between(self, stx: bytes = STX, etx: bytes = ETX):
        """迭代获取报文，通过起始符和结束符

        Args:
            stx (bytes): 起始符，默认为STX
            etx (bytes): 结束符，默认为ETX

        Raises:
            ValueError: 当stx或etx为空时抛出
            RuntimeError: 当找到的报文长度超过限制时抛出

        Yields:
            bytes: 完整的报文数据（包含stx和etx）
        """
        stx_len = len(stx)
        etx_len = len(etx)

        if stx_len == 0 or etx_len == 0:
            raise ValueError("STX and ETX should be at least one-byte string")

        while True:
            buflen = len(self._buffer)
            # 至少需要包含stx和etx才能构成一个完整报文
            if buflen < stx_len + etx_len:
                break

            # 查找起始符
            istart = self._buffer.find(stx)
            if istart == -1:
                # 没有找到起始符，清理缓冲区中无效数据
                break

            # 从起始符位置开始查找结束符
            iend = self._buffer.find(etx, istart + stx_len)
            if iend == -1:
                # 没有找到结束符，等待更多数据
                # 检查是否超出限制
                if buflen - istart > self._limit:
                    raise RuntimeError(
                        "End marker not found, but chunk is longer than limit"
                    )
                break

            # 计算完整报文的结束位置
            packet_end = iend + etx_len
            # 检查报文长度是否超出限制
            if packet_end - istart > self._limit:
                raise RuntimeError("Packet is longer than limit")

            # 提取完整报文
            message = self._buffer[istart:packet_end]
            # 删除已处理的数据
            del self._buffer[:packet_end]
            yield bytes(message)
