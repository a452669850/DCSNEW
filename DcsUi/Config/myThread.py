import struct


def double2wordarray(data):
    """
    double -> 16bit * 4
    little-end
    """
    return struct.unpack('<HHHH', struct.pack('<d', data))


def wordarray2double(data):
    assert isinstance(data, (tuple, list))
    return struct.unpack('<d', struct.pack('<HHHH', *data))[0]
