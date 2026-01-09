from highway_sdk.vendors.vms.fenghai.parser import Parser, Frame


def test_paresr():
    assert len(Parser._parsers) > 0

    resp = "02 00 00 30 36 30 30 31 35 57 F9 03"
    frame = Frame.from_bytes(bytes.fromhex(resp))
    tags = Parser.parse(frame)
    print(tags)

    resp = "02 30 30 39 37 30 30 30 30 31 30 30 30 30 31 30 30 30 30 30 3C CB ED B5 C0 CA A9 B9 A4 D0 A1 D0 C4 0A BC DD CA BB 3E 00 F7 F6 03"
    frame = Frame.from_bytes(bytes.fromhex(resp))

    tags = Parser.parse(frame)
    print(tags)

    resp = "02 00 00 30 39 30 70 6C 61 79 2E 6C 73 74 2B 00 00 00 00 5B 70 6C 61 79 6C 69 73 74 5D 0D 0A 69 74 65 6D 5F 6E 6F 3D 31 0D 0A 69 74 65 6D 30 3D 31 30 30 30 2C 31 2C 30 2C 5C 43 30 30 30 30 30 37 5C 66 66 31 36 31 36 5C 63 32 35 35 30 30 30 30 30 30 30 30 30 CB ED B5 C0 CA A9 B9 A4 D0 A1 D0 C4 0A BC DD CA BB 0D 0A 60 90 03"
    frame = Frame.from_bytes(bytes.fromhex(resp))
    tags = Parser.parse(frame)
    print(tags)
