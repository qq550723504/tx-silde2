import base64
from ctypes import c_int

key1 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="


def unsigned_right_shift(signed, i=0):
    shift = signed % 0x100000000
    return shift >> i


def custom_b64encode(data: str, custom_table=key1):
    # 将数据转换成二进制格式
    # data = data.encode('utf-8')
    # 计算数据的长度
    length = len(data)
    # 初始化编码结果
    result = ''
    # 循环处理数据
    for i in range(0, length, 3):
        # 取出3个字节数据
        chunk = data[i:i + 3]
        # 将3个字节数据转换成4个Base64编码字符
        ''
        if len(chunk) == 3:
            b64 = custom_table[(ord(chunk[0]) >> 2) & 0x3f] + custom_table[
                ((ord(chunk[0]) << 4) & 0x30) | ((ord(chunk[1]) >> 4) & 0x0f)] + custom_table[
                      ((ord(chunk[1]) << 2) & 0x3c) | ((ord(chunk[2]) >> 6) & 0x03)] + custom_table[
                      ord(chunk[2]) & 0x3f]
        elif len(chunk) == 2:
            b64 = custom_table[(ord(chunk[0]) >> 2) & 0x3f] + custom_table[
                ((ord(chunk[0]) << 4) & 0x30) | ((ord(chunk[1]) >> 4) & 0x0f)] + custom_table[
                      ((ord(chunk[1]) << 2) & 0x3c)] + '='
        else:
            b64 = custom_table[(ord(chunk[0]) >> 2) & 0x3f] + custom_table[((ord(chunk[0]) << 4) & 0x30)] + '=='
        # 将编码结果添加到总结果中
        result += b64
    return result

    # Base64解码函数


def custom_b64decode(data, custom_table=key1):
    # 计算数据的长度
    length = len(data)
    # 初始化解码结果
    result = ''
    # 循环处理数据
    for i in range(0, length, 4):
        # 取出4个Base64编码字符
        chunk = data[i:i + 4]
        # 将4个Base64编码字符转换成3个字节数据
        if chunk[3] == '=':
            if chunk[2] == '=':
                # 1字节数据
                b = custom_table.index(chunk[0]) << 2 | custom_table.index(chunk[1]) >> 4
                result += chr(b)
            else:
                # 2字节数据
                b1 = custom_table.index(chunk[0]) << 2 | custom_table.index(chunk[1]) >> 4
                b2 = ((custom_table.index(chunk[1]) << 4) & 0xf0) | ((custom_table.index(chunk[2]) >> 2) & 0x0f)
                result += chr(b1) + chr(b2)
        else:
            # 3字节数据
            b1 = custom_table.index(chunk[0]) << 2 | custom_table.index(chunk[1]) >> 4
            b2 = ((custom_table.index(chunk[1]) << 4) & 0xf0) | ((custom_table.index(chunk[2]) >> 2) & 0x0f)
            b3 = ((custom_table.index(chunk[2]) << 6) & 0xc0) | (custom_table.index(chunk[3]) & 0x3f)
            result += chr(b1) + chr(b2) + chr(b3)
    return result


def longs_to_str(longs):
    res = []
    for i in range(len(longs)):
        res.append(chr(c_int(unsigned_right_shift(longs[i]) & 0xff).value))
        res.append(chr(c_int(unsigned_right_shift(longs[i], 8) & 0xff).value))
        res.append(chr(c_int(unsigned_right_shift(longs[i], 16) & 0xff).value))
        res.append(chr(c_int(unsigned_right_shift(longs[i], 24) & 0xff).value))
    return ''.join(res)


def str_to_longs(s):
    length = len(s)
    longs = [0] * c_int((length + 3) >> 2).value
    for i in range(length):
        if isinstance(s, str):
            longs[i >> 2] |= c_int(ord(s[i]) << c_int((i % 4) << 3).value).value
        else:
            longs[i >> 2] |= c_int(s[i] << c_int((i % 4) << 3).value).value
    return longs


def encrypt_block(data, key):
    x, y = data
    delta, _sum = 0x9E3779B9, 0
    k = list(key)
    for i in range(32):
        if (_sum & 3) == k[6]:
            x += c_int((c_int(y << 4).value ^ unsigned_right_shift(y, 5)) + y).value ^ c_int(
                _sum + k[_sum & 3] + k[4]).value
        elif (_sum & 3) == k[7]:
            x += c_int((c_int(y << 4).value ^ unsigned_right_shift(y, 5)) + y).value ^ c_int(
                _sum + k[_sum & 3] + k[5]).value
        else:
            x += c_int((c_int(y << 4).value ^ unsigned_right_shift(y, 5)) + y).value ^ c_int(_sum + k[_sum & 3]).value
        _sum += delta
        if (c_int(_sum >> 11).value & 3) == k[6]:
            y += c_int(c_int(c_int(x << 4).value ^ unsigned_right_shift(x, 5)).value + x).value ^ c_int(
                _sum + k[(_sum >> 11) & 3] + k[4]).value
        elif (c_int(_sum >> 11).value & 3) == k[7]:
            y += c_int(c_int(c_int(x << 4).value ^ unsigned_right_shift(x, 5)).value + x).value ^ c_int(
                _sum + k[(_sum >> 11) & 3] + k[5]).value
        else:
            y += c_int(c_int(c_int(x << 4).value ^ unsigned_right_shift(x, 5)).value + x).value ^ c_int(
                _sum + k[(_sum >> 11) & 3]).value
    return [x, y]


def decrypt_block(data, key):
    x, y = data
    delta, _sum = 0x9E3779B9, 0x9E3779B9 * 32
    k = list(key)
    for i in range(32):
        if ((_sum >> 11) & 3) == k[6]:
            y -= c_int((c_int(x << 4).value ^ unsigned_right_shift(x, 5)) + x).value ^ c_int(
                _sum + k[(_sum >> 11) & 3] + k[4]).value
        elif ((_sum >> 11) & 3) == k[7]:
            y -= c_int(c_int(c_int(x << 4).value ^ unsigned_right_shift(x, 5)).value + x).value ^ c_int(
                _sum + k[c_int(_sum >> 11).value & 3] + k[5]).value
        else:
            y -= c_int(c_int(c_int(x << 4).value ^ unsigned_right_shift(x, 5)).value + x).value ^ c_int(
                _sum + k[c_int(_sum >> 11).value & 3]).value
        _sum -= delta
        if (_sum & 3) == k[6]:
            x -= c_int((c_int(y << 4).value ^ unsigned_right_shift(y, 5)) + y).value ^ c_int(
                _sum + k[_sum & 3] + k[4]).value
        elif (_sum & 3) == k[7]:
            x -= c_int((c_int(y << 4).value ^ unsigned_right_shift(y, 5)) + y).value ^ c_int(
                _sum + k[_sum & 3] + k[5]).value
        else:
            x -= c_int((c_int(y << 4).value ^ unsigned_right_shift(y, 5)) + y).value ^ c_int(_sum + k[_sum & 3]).value
    return [x, y]


def tea_encrypt(msg, key):
    msg_length = len(msg)
    if msg_length % 8 != 0:
        msg = msg + chr(0) * (8 - msg_length % 8)
    rounds = len(msg) >> 3
    final = ""
    for i in range(rounds):
        data = str_to_longs(msg[i * 8:i * 8 + 8])
        tmp = encrypt_block(data, key)
        final += longs_to_str(tmp)
    return custom_b64encode(final)


def tea_decrypt(msg, key):
    b64 = base64.b64decode(msg)
    rounds = len(b64) >> 3
    final = ""
    for i in range(rounds):
        data = str_to_longs(b64[i * 8:i * 8 + 8])
        tmp = decrypt_block(data, key)
        final += longs_to_str(tmp)
    return final.rstrip(chr(0))




