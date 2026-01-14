from typing import Final

STX: Final[bytes] = b"\x02"

ETX: Final[bytes] = b"\x03"

ESC: Final[bytes] = b"\x1b"

LF: Final[bytes] = b"\n"

CR: Final[bytes] = b"\r"

CRLF: Final[bytes] = b"\r\n"

BUFSIZE: int = 2**16  # 64KB
