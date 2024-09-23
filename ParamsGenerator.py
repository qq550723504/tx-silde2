import base64
import json
import pathlib
import random
import re
import string
import time
import uuid

import node_vm2
from loguru import logger as log

from encryptor import tea_encrypt

key = [[
    1448300889, 1245925737,
    1181042506, 1445935693,
    1052685, 1315863,
    0, 3
], [
    1746346815,
    1414750545,
    1330664231,
    1732797549,
    2960647,
    328986,
    0,
    2
], [
    1449345347,
    1449420127,
    1427652435,
    1500207464,
    592138,
    2763265,
    1,
    2
]]

DIR_PATH = pathlib.Path(__file__).parent


def generate_slide_trace(distance):
    trace = [
        [random.randint(-50, -10), random.randint(-50, -10), 0],
        [0, 0, 0]
    ]

    count = 30 + distance // 2

    t = random.randint(50, 100)
    lastX = 0
    lastY = 0
    lastYCount = 0

    for i in range(count):
        x = round(distance * (1 - pow(2, (-10 * i) / count)) if i != count else 1)

        t += random.randint(10, 20)

        if x == lastX:
            continue

        lastYCount += 1
        if lastYCount > random.randint(5, 10):
            lastYCount = 0
            lastY = random.randint(-2, 2)

        lastX = x
        trace.append([x, lastY, t])

    return trace


class TXSlideTDC:

    def __init__(self, js_text, x=None, sid='',
                 user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0',
                 uip=''):
        self.static_array = None
        self.temp_array = None
        self.uip = uip
        self.one_array = None
        self.empty_array = None
        self.numbers_array = None
        self.canvas_array = None
        self.sid = sid
        self.js_text = js_text
        self.user_agent = user_agent
        mouse_move_track = []
        if x is not None:
            track = generate_slide_trace(x - 65)[1:]
            for i in range(len(track)):
                if i == 0:
                    mouse_move_track.append(
                        [track[i][0] + 305, track[i][1] + 316, track[i][2] + random.randint(100, 1000)])
                else:
                    _last = track[i - 1]
                    t = [track[i][0] - _last[0], track[i][1] - _last[1], track[i][2] - _last[2]]
                    mouse_move_track.append(t)
            mouse_move_track = mouse_move_track[:59]
        mouse_move_track.append([1, 1, 12])
        self.mouse_move_track = mouse_move_track
        self.flag = True
        self.canvas_index = 0

    def init_array(self):
        self.temp_array = [[[0], [0, 3, 3, 4, 5, 1, 64], [116, 67, 104, 4, 7, 4, 10, 5, 25], [0, 2, 3, 4, 1, 64],
                            [66, 7, 60, 2, 60, 3, 60, 4, 60, 5, 60, 6, 47, 6, 10, 5, 25],
                            [66, 11, 60, 2, 60, 3, 60, 4, 60, 5, 60, 6, 60, 7, 60, 8, 60, 9, 60, 10, 37, 47, 10, 56, 66,
                             8, 60, 2],
                            [66, 6, 60, 2, 60, 3, 60, 4, 60, 5, 47, 3, 31, 67, 'exports', 31, 67, 'Object', 38, 0, 14,
                             31, 67, 'get', 37, 56, 66, 3, 60, 2, 31, 67, 'Array', 38, 0, 14, 25, 0, 59, 25],
                            [66, 6, 60, 2, 60, 3, 60, 4, 60, 5, 47, 3, 31, 67, 'exports', 31, 67, 'Object', 38, 0, 14,
                             31, 67, 'get', 37, 56, 66, 3, 60, 2, 31, 67, 'Array', 38, 0, 14, 25, 0, 59, 31],
                            [66, 7, 60, 2, 60, 3, 60, 4, 60, 5, 60, 6, 47, 6, 25, 0, 9, 64, 64, 47, 3, 31, 67,
                             'exports',
                             31, 67, 'Object', 38, 0, 14, 31, 67, 'get', 37, 56, 66, 4, 60, 2, 47, 3, 14, 18, 25, 1,
                             57],
                            [45, 6, 27, 2, 27, 3, 27, 4, 27, 5, 35, 3, 36, 66, 'exports', 36, 66, 'Object', 59, 0, 0,
                             36, 66, 'get', 1, 63, 45, 4, 27, 2, 27, 3, 35, 3, 36, 66]],
                           [[1], [0, 3, 3, 4, 5, 39, 47], [10, 104, 0, 46, 0, 1, 5, 61], [0, 2, 3, 4, 39, 47],
                            [28, 7, 5, 2, 5, 3, 5, 4, 5, 5, 5, 6, 66, 6, 1, 5, 61],
                            [28, 11, 5, 2, 5, 3, 5, 4, 5, 5, 5, 6, 5, 7, 5, 8, 5, 9, 5, 10, 41, 66, 10, 14],
                            [28, 6, 5, 2, 5, 3, 5, 4, 5, 5, 66, 3, 22, 10, 'exports', 22, 10, 'Object', 25, 0,
                             58, 22, 10, 'get', 41, 14, 28, 3, 5, 2, 22, 10, 'Array', 25, 0, 58, 61, 0, 27, 61],
                            [28, 6, 5, 2, 5, 3, 5, 4, 5, 5, 66, 3, 22, 10, 'exports', 22, 10, 'Object', 25, 0,
                             58, 22, 10, 'get', 41, 14, 28, 3, 5, 2, 22, 10, 'Array', 25, 0, 58, 61, 0, 27, 22],
                            [28, 7, 5, 2, 5, 3, 5, 4, 5, 5, 5, 6, 66, 6, 61, 0, 8, 47, 47, 66, 3, 22, 10,
                             'exports', 22, 10, 'Object', 25, 0, 58, 22, 10, 'get', 41, 14],
                            [45, 6, 27, 2, 27, 3, 27, 4, 27, 5, 35, 3, 36, 66, 'exports', 36, 66, 'Object', 59, 0, 0,
                             36, 66, 'get', 1, 63, 45, 4, 27, 2, 27, 3, 35, 3, 36, 66]],
                           [[2], [0, 3, 3, 4, 5, 22, 34],
                            [116, 66, 104, 41, 61, 41, 65, 5, 12], [0, 2, 3, 4, 22, 34],
                            [45, 7, 27, 2, 27, 3, 27, 4, 27, 5, 27, 6, 35, 6, 65, 5, 12],
                            [45, 11, 27, 2, 27, 3, 27, 4, 27, 5, 27, 6, 27, 7, 27, 8, 27, 9, 27, 10, 1, 35, 10, 63],
                            [45, 6, 27, 2, 27, 3, 27, 4, 27, 5, 35, 3, 36, 66, 'exports', 36, 66, 'Object', 59, 0, 0,
                             36, 66, 'get', 1, 63, 45,
                             3, 27, 2, 36, 66, 'Array', 59, 0, 0, 12, 0, 23, 12],
                            [45, 6, 27, 2, 27, 3, 27, 4, 27, 5, 35, 3, 36, 66, 'exports', 36, 66, 'Object', 59, 0, 0,
                             36, 66, 'get', 1, 63, 45,
                             3, 27, 2, 36, 66, 'Array', 59, 0, 0, 12, 0, 23, 36],
                            [45, 7, 27, 2, 27, 3, 27, 4, 27, 5, 27, 6, 35, 6, 12, 0, 37, 34, 34, 35, 3, 36, 66,
                             'exports', 36, 66, 'Object',
                             59, 0, 0, 36, 66, 'get', 1, 63, 45, 4, 27, 2, 35, 3, 0, 44, 12],
                            [45, 6, 27, 2, 27, 3, 27, 4, 27, 5, 35, 3, 36, 66, 'exports', 36, 66, 'Object', 59, 0, 0,
                             36, 66, 'get', 1, 63, 45, 4, 27, 2, 27, 3, 35, 3, 36, 66]]]

    def get_tdc(self):
        try:
            opcode_array = self.get_opcode_array(self.js_text)
            self.init_array()
            cd = self.get_cd(opcode_array)
            log.info('cd:{}', cd)
            plain_text = json.dumps({'cd': cd, 'sd': {
                "od": "C",
                "ft": "qf_7Pfn_H"
            }}, separators=(',', ':'))
            eks = re.search(r"window\.\D+ ?= ?('|\")(?P<eks>.+?)('|\")", self.js_text).group('eks')
            return {'collect': tea_encrypt(plain_text, key[self.static_array[0][0]]), 'eks': eks}
        except Exception as e:
            path = DIR_PATH.joinpath(f'error')
            path.mkdir(exist_ok=True, parents=True)
            with open(path.joinpath(f'{uuid.uuid4()}.js').as_posix(), 'w', encoding='utf-8') as f:
                f.write(self.js_text)
            raise e

    @staticmethod
    def get_opcode_array(js_text):
        array_text = '[' + re.search(r'\}\(\[(?P<text>.+?)\)\,', js_text).group('text')
        L = node_vm2.eval(array_text)
        s = L[0]
        x = L[1]
        G = []
        A = base64.b64decode(s)
        U = x.pop(0)
        C = x.pop(0)
        y = 0

        def qqq():
            nonlocal y, U, C
            while y == U:
                G.append(C)
                y += 1
                if not x:
                    break
                U = x.pop(0)
                C = x.pop(0)

        for M in range(len(A)):
            w = A[M]
            qqq()
            G.append(w)
            y += 1

        qqq()
        return G

    def is_test(self, array1, array2):
        array1 = array1[:len(array2)]
        return array1 == array2

    def get_method_opcode_array(self, _index, opcode_array, cache=None, _index_cache=None):
        if cache is None:
            cache = {}
        if _index_cache is None:
            _index_cache = []
        method_opcode = _index
        res = []
        while _index < len(opcode_array):
            _index = int(_index)
            opcode = opcode_array[int(_index)]
            res.append(opcode)
            _index += 1
            if opcode == 37:
                _index = opcode_array[_index]
                if _index in _index_cache:
                    # 进入循环
                    return res
                else:
                    _index_cache.append(_index)
                continue
            elif opcode == 0:
                temp = opcode_array[_index]
                _index += 1
                if temp > 100:
                    _index = temp
            elif opcode == 56:
                v = opcode_array[_index]
                if cache.get(v) is None:
                    cache[v] = []
                    array = self.get_method_opcode_array(v, opcode_array, cache, _index_cache)
                    cache[v] = array
                    res.extend(array)
                _index += 1
                r = opcode_array[_index]
                _index += 1
                f = opcode_array[_index]
                _index += 1
                _index += 2 * r
                _index += f
                _index = int(_index)
            elif opcode == 67:
                zz = []
                while opcode == 67:
                    zz.append(opcode_array[_index])
                    opcode = opcode_array[_index + 1]
                    _index += 2
                res.append(bytes(zz).decode())
            elif opcode in [47, 44, 60, 10, 38, 34, 11, 66, 36, 25, 52]:
                res.append(opcode_array[_index])
                _index += 1
            elif opcode in [33]:
                res.append(opcode_array[_index])
                res.append(opcode_array[_index + 1])
                _index += 2
            elif opcode == 54:
                break
        cache[method_opcode] = res
        return res

    def get_method_opcode_array2(self, _index, opcode_array, cache=None, _index_cache=None):
        if cache is None:
            cache = {}
        if _index_cache is None:
            _index_cache = []
        method_opcode = _index
        res = []
        while _index < len(opcode_array):
            _index = int(_index)
            opcode = opcode_array[int(_index)]
            res.append(opcode)
            _index += 1
            if opcode == 41:
                # res.extend(get_method_opcode_array(opcode_array[begin_index], opcode_array))
                _index = opcode_array[_index]
                if _index in _index_cache:
                    # 进入循环
                    return res
                else:
                    _index_cache.append(_index)
                continue
            elif opcode == 20:
                temp = opcode_array[_index]
                _index += 1
                if temp > 100:
                    _index = temp
            elif opcode == 14:
                v = opcode_array[_index]
                if cache.get(v) is None:
                    cache[v] = []
                    array = self.get_method_opcode_array2(v, opcode_array, cache, _index_cache)
                    cache[v] = array
                    res.extend(array)
                _index += 1
                r = opcode_array[_index]
                _index += 1
                f = opcode_array[_index]
                _index += 1
                _index += 2 * r
                _index += f
                _index = int(_index)
            elif opcode == 10:
                zz = []
                while opcode == 10:
                    zz.append(opcode_array[_index])
                    opcode = opcode_array[_index + 1]
                    _index += 2
                res.append(bytes(zz).decode())
            elif opcode in [66, 50, 5, 1, 25, 64, 4, 28, 23, 61, 2]:
                res.append(opcode_array[_index])
                _index += 1
            elif opcode in [13]:
                res.append(opcode_array[_index])
                res.append(opcode_array[_index + 1])
                _index += 2
            elif opcode == 57:
                break
        cache[method_opcode] = res
        return res

    def get_method_opcode_array3(self, _index, opcode_array, cache=None, _index_cache=None):
        if cache is None:
            cache = {}
        if _index_cache is None:
            _index_cache = []
        method_opcode = _index
        res = []
        while _index < len(opcode_array):
            _index = int(_index)
            opcode = opcode_array[int(_index)]
            res.append(opcode)
            _index += 1
            if opcode == 1:
                # res.extend(get_method_opcode_array(opcode_array[begin_index], opcode_array))
                _index = opcode_array[_index]
                if _index in _index_cache:
                    # 进入循环
                    return res
                else:
                    _index_cache.append(_index)
                continue
            elif opcode == 48:
                temp = opcode_array[_index]
                _index += 1
                if temp > 100:
                    _index = temp
            elif opcode == 63:
                v = opcode_array[_index]
                if cache.get(v) is None:
                    cache[v] = []
                    array = self.get_method_opcode_array3(v, opcode_array, cache, _index_cache)
                    cache[v] = array
                    res.extend(array)
                _index += 1
                r = opcode_array[_index]
                _index += 1
                f = opcode_array[_index]
                _index += 1
                _index += 2 * r
                _index += f
                _index = int(_index)
            elif opcode == 66:
                zz = []
                while opcode == 66:
                    zz.append(opcode_array[_index])
                    opcode = opcode_array[_index + 1]
                    _index += 2
                res.append(bytes(zz).decode())
            elif opcode in [35, 9, 27, 65, 59, 28, 49, 45, 68, 12, 13]:
                res.append(opcode_array[_index])
                _index += 1
            elif opcode in [21]:
                res.append(opcode_array[_index])
                res.append(opcode_array[_index + 1])
                _index += 2
            elif opcode == 32:
                break
        cache[method_opcode] = res
        return res

    function_list = [get_method_opcode_array, get_method_opcode_array2, get_method_opcode_array3]

    def get(self, static_array, array):
        if 'hardwareConcurrency' in array:
            return random.choice([8, 16, 24, 32, 4, 2, 1])
        elif 'languages' in array:
            return ['zh-CN', 'zh']
        elif '\\bsid=(\\d+)' in array:
            return self.sid
        elif 'href' in array:
            for i in array:
                if isinstance(i, str) and 'rand' in i:
                    return 'https://captcha.gtimg.com/1/template/drag_ele.html' + i
        elif 'availHeight' in array:
            return '1920-1080-1032-24-*-*-|-*'
        elif 'colorDepth' in array:
            return 24
        elif 'characterSet' in array or 'charset' in array:
            return 'UTF-8'
        elif 'screen' in array:
            if 'width' in array:
                return 1920
            elif 'height' in array:
                return 1080
        elif 'platform' in array:
            return 'Win32'
        elif 'touchmove' in array:
            return self.mouse_move_track
        elif 'WEBGL_debug_renderer_info' in array:
            return 'Google Inc. (NVIDIA)'
        elif 'alpha' in array:
            return []
        elif 'innerWidth' in array:
            return [360, 360]
        elif 'requestMIDIAccess' in array:
            return 1023
        elif '^\\d+:\\d+$' in array:
            return "time,time"
        elif 'RTCPeerConnection' in array:
            return self.uip
        elif 'TCaptchaReferrer' in array:
            # return 'https://007.qq.com/'
            return 'unknown'
        elif '?rand=' in array:
            return 'https://turing.captcha.qcloud.com/cap_union_new_show?rand=' + str(array[array.index('?rand=') + 2])
        elif '98k' in array:
            return '98k'
        elif 'getTimezoneOffset' in array:
            return '+08'
        elif 'ontouchstart' in array:
            return 2
        elif 'cookieEnabled' in array:
            return 1
        elif 'console' in array:
            return 0
        elif 'divdivdivppadiv' in array:
            return 0
        elif 'getComputedStyle' in array:
            return 1023
        elif 'random' in array or 'load' in array:
            return 0
        elif 'getCookie' in array:
            return 'cookie'
        elif "14px 'Arial'" in array or "canvas" in array:
            # return "GgoAAAANSUhEUgAAASwAAACWCAYAAAdYcZnC7u/EL/PH0ZK46nKuiid4BiG/8D0X2eD5sOjPUAAAAASUVORK5CYII="
            return f'GgoAAAANSUhEUgAAASwAAACWCAYAAA{"".join(random.choices(string.ascii_letters, k=56))}gg=='
        elif 'iframe' in array:
            return 'iframe'
        elif 'tCaptchaDyContent' in array:
            return [360, 360]
        elif 'userAgent' in array:
            return self.user_agent
        elif '[\\u0000-\\u0020]+' in array or '[\\u00ff-\\uffff]+' in array:
            return 'ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Laptop GPU Direct3D11 vs_5_0 ps_5_0, D3D11)'
        elif 'addEventListener' in array:
            return []
        elif 'getTime' in array:
            return int(time.time())
        elif 'href' in array:
            for g in array:
                if isinstance(g, str) and 'rand' in array:
                    return g
        else:
            if self.is_test(array, static_array[6]):
                return array[len(static_array[6])]
            elif self.is_test(array, static_array[7]):
                return ''
            elif self.is_test(array, static_array[8]):
                return 1
            elif self.is_test(array, static_array[5]):
                return 'canvas'
            elif self.is_test(array, static_array[9]):
                return 'document'
            else:
                return None

    def get_cd(self, a5):
        bb = []
        cc = []
        call_other = []
        self.static_array = []
        for array in self.temp_array:
            bb = []
            cc = []
            self.static_array = array
            opcode_array = array[1]
            signature = array[2]
            gg = array[3]
            call_other = array[4]
            a = len(opcode_array)
            b = len(signature)
            c = len(gg)
            for i in range(len(a5)):
                if a5[i:i + a] == opcode_array:
                    i_ = a5[i - 1]
                    bb.append(i_)
                if a5[i:i + b] == signature:
                    b_ = a5[i + b]
                    cc.append(b_)
                if a5[i:i + c] == gg:
                    if len(bb) > 5:
                        bb.insert(6, a5[i - 1])
            if len(cc) > 0:
                break
        res = []

        for i in cc:
            _index = bb[i]
            method_opcode_array = self.function_list[self.static_array[0][0]](self, _index=_index, opcode_array=a5)
            while self.is_call_other(method_opcode_array, call_other):
                method_opcode_array = self.function_list[self.static_array[0][0]](self, _index=bb[
                    method_opcode_array[len(call_other)]], opcode_array=a5)
            value = self.get(self.static_array, method_opcode_array)
            if value is None:
                value = 0
            if 'cookie' == value:
                res.append(random.randint(568321020, 668321020))
                res.append(int(time.time()) - 2000)
            elif 'canvas' == value:
                if 'Google Inc. (NVIDIA)' in res:
                    nv = random.choice(['3060', '3070', '3080', '3090', '4050', '4060', '4070', '4080', '4090'])
                    res.append("Google SwiftShader")
                    # res.append('ANGLE (NVIDIA, NVIDIA GeForce RTX ' + nv + ' Laptop GPU Direct3D11 vs_5_0 ps_5_0, D3D11)')
                else:
                    res.append('Google Inc.')
                    # res.append('Google Inc. (NVIDIA)')
            elif 'time,time' == value:
                res.append(1200298601)
                res.append(int(time.time()) - 1800)
            elif 'document' == value:
                res.append(2)
            else:
                res.append(value)
        return res

    def is_call_other(self, array, call_other):
        for i in range(0, len(call_other), 2):
            if array[i] != call_other[i]:
                return False
        return True
