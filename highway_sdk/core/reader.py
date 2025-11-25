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
