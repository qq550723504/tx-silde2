import base64
import json
import math
import random
import re
import sys
import time
from hashlib import md5
from io import BytesIO
from urllib import parse
import ddddocr
import httpx
from PIL import Image
from loguru import logger as log

from ParamsGenerator import TXSlideTDC

user_agent = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
              'Chrome/128.0.0.0 Safari/537.36 Edg/128.0.0.0')
ua = base64.b64encode(user_agent.encode()).decode()


def cookie_to_dic(cookie):
    cookie_dic = {}
    for i in cookie.split('; '):
        cookie_dic[i.split('=')[0]] = i.split('=')[1]
    return cookie_dic


def params_to_dic(params: str):
    split = params.split("&")
    res = {}
    for i in split:
        i_split = i.split("=")
        res[i_split[0]] = i_split[1]
    return res


def level2_ocr(slide_content, background_content, crop=True):
    ocr = ddddocr.DdddOcr(show_ad=False)
    if crop:
        bytes_io = BytesIO(slide_content)
        img = Image.open(bytes_io)
        img = img.crop((140, 490, 260, 610))
        img_byte = BytesIO()
        img.save(img_byte, 'png')
        slide_content = img_byte.getvalue()
    match = ocr.slide_match(target_bytes=slide_content, background_bytes=background_content, simple_target=True)
    log.debug('识别结果:{}', match)
    return match['target'][0], match['target'][1]


class QQSlide2:

    def __init__(self, aid: int = 1, sid=None, uid=None, proxy=None):
        self.cookie = None
        self.rnd = None
        self.ans = None
        self.pow_answer = None
        self.collect = None
        self.eks = None
        self.tdc_js = None
        self.sess = None
        self.uid = uid
        self.sid = sid
        self.res = {
            "data": {

            }
        }
        self.aid = aid
        if proxy is not None:
            log.info("当前使用代理: " + proxy)
            proxies = {
                "all://": f"http://{proxy}",
            }
        else:
            proxies = None
        self.client = httpx.AsyncClient(proxies=proxies, timeout=10)

    async def cap_union_pre_handle(self):

        headers = {
            'Accept': '*/*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Referer': 'https://sso.weidian.com/login/index.php',
            'Sec-Fetch-Dest': 'script',
            'Sec-Fetch-Mode': 'no-cors',
            'Sec-Fetch-Site': 'same-site',
            'User-Agent': user_agent,
        }

        params = {
            'aid': self.aid,
            'protocol': 'https',
            'accver': '1',
            'showtype': 'popup',
            'ua': base64.b64encode(headers['User-Agent'].encode()).decode(),
            'noheader': '0',
            'fb': '1',
            'aged': '0',
            'enableAged': '0',
            'enableDarkMode': '0',
            # 'sid': self.sid,
            'grayscale': '1',
            'clientype': '2',
            'cap_cd': '',
            # 'uid': self.uid,
            'lang': 'zh-cn',
            'entry_url': 'https://sso.weidian.com/login/index.php',
            'elder_captcha': '0',
            'js': '/tcaptcha-frame.22125576.js',
            'login_appid': '',
            'wb': '1',
            'subsid': '7',
            'callback': '_aq_804718',
            'sess': '',
        }
        start = time.time()
        response = await self.client.get('https://turing.captcha.qcloud.com/cap_union_prehandle', params=params,
                                         headers=headers)
        response = response.text
        cap_pre_handle_res = json.loads(response.replace(f'{params["callback"]}(', '')[0:-1])
        log.debug('获取验证码预处理：{}', cap_pre_handle_res)
        self.sess = cap_pre_handle_res['sess']
        self.sid = cap_pre_handle_res['sid']
        log.debug("----------------预处理结束，耗时{}s--------------------", time.time() - start)
        return cap_pre_handle_res

    def get_collect(self, x=None):
        tdc = TXSlideTDC(self.tdc_js, sid=self.sid, x=x).get_tdc()
        self.collect = tdc['collect']
        self.eks = tdc['eks']
        return tdc

    @staticmethod
    def get_pow_answer(t):
        e = t["nonce"]
        r = t["target"]
        o = int(time.time() * 1000)
        f = 30000
        u = 0
        while True:
            if md5((e + str(u)).encode()).hexdigest() == r:
                break
            if (int(time.time() * 1000) - o) > f:
                break
            u += 1
        call = {
            'ans': u,
            'duration': int(time.time() * 1000) - o
        }
        return t['nonce'] + str(call['ans'])

    async def verif(self):
        headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # 'Cookie': self.cookie,
            'Origin': 'https://turing.captcha.qcloud.com',
            'Pragma': 'no-cache',
            'Referer': 'https://turing.captcha.qcloud.com/template/drag_ele.html',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': user_agent,
            'X-Requested-With': 'XMLHttpRequest',
        }

        data = {
            'collect': self.collect,
            'tlg': len(self.collect),
            'eks': self.eks,
            'sess': self.sess,
            'ans': json.dumps(self.ans, ensure_ascii=False),
            'pow_answer': self.pow_answer,
            'pow_calc_time': 41
        }

        response = await self.client.post('https://turing.captcha.qcloud.com/cap_union_new_verify', headers=headers,
                                          data=data)
        self.res['data'] = response.json()
        log.info('文字点选结果:{}', response.json())
        return self.res

    async def run(self):
        start = time.time()
        log.debug('----------------滑块验证开始------------------------')
        cap_pre_handle_res = await self.cap_union_pre_handle()
        subcapclass = int(cap_pre_handle_res['subcapclass'])
        log.info('subcapclass: {}', subcapclass)
        if subcapclass == 15:
            await self.slide2(cap_pre_handle_res)
        else:
            self.res = {"message": "这个类型的验证还解决不了", "data": ""}
            return
        log.info('----------------QQ滑块结束，耗时{}s--------------------', time.time() - start)
        return self.res

    async def slide2(self, cap_pre_handle_res):
        headers = {
            "User-Agent": user_agent,
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
                      "*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        }
        captcha_client = httpx.AsyncClient()
        url = "https://turing.captcha.qcloud.com/cap_union_new_show"
        params = {
            "aid": self.aid,
            "protocol": "https",
            "accver": "1",
            "showtype": "popup",
            "ua": base64.b64encode(headers['User-Agent'].encode()).decode(),
            "noheader": "1",
            "fb": "1",
            "aged": "0",
            "enableAged": "0",
            "enableDarkMode": "0",
            "grayscale": "1",
            "clientype": "2",
            "sess": self.sess,
            "fwidth": "0",
            "sid": self.sid,
            "wxLang": "",
            "tcScale": "1",
            "uid": self.uid,
            "cap_cd": "",
            "rnd": "233625",
            "prehandleLoadTime": "74",
            "createIframeStart": int(time.time() * 1000),
            "global": "0",
            "subsid": "2"
        }
        response = await self.client.get(url, headers=headers, params=params)
        self.rnd = math.floor(random.random() * 1000000)
        now = math.floor(time.time() * 1000)
        sid = cap_pre_handle_res["sid"]
        page_content = response.text
        nonce = re.search(r'nonce:"(?P<nonce>.*?)",', page_content).group('nonce')
        spt = re.search(r'spt:"(?P<spt>.*?)",', page_content).group('spt')
        sess = re.search(r'sess:"(?P<sess>.*?)"', page_content).group('sess')
        image = re.search(r'image=(?P<image>.*?)",', page_content).group('image')
        md5 = re.search(r'md5:"(?P<md5>.*?)"', page_content).group('md5')
        prefix = re.search(r'prefix:"(?P<prefix>.*?)"', page_content).group('prefix')
        self.pow_answer = self.get_pow_answer({"target": md5, "nonce": prefix})
        tdc_url = 'https://turing.captcha.qcloud.com/tdc.js?' + re.search(r'src="/tdc.js\?(?P<tdc>.*?)"',
                                                                          page_content).group(
            'tdc')
        log.debug('tdc.js地址：{}', tdc_url)
        self.tdc_js = (await self.client.get(tdc_url, headers=headers)).text
        log.debug('tdc_js_text:{}', self.tdc_js)
        bg_url = f'https://turing.captcha.qcloud.com/hycdn?index=1&image={image}?aid={self.aid}&sess={sess}&sid={sid}&img_index=1&subsid=3'
        log.debug('背景图片地址：{}', bg_url)
        slide_url = f'https://turing.captcha.qcloud.com/hycdn?index=2&image={image}?aid={self.aid}&sess={sess}&sid={sid}&img_index=2&subsid=4'
        log.debug('滑块图片地址：{}', slide_url)
        x, y = level2_ocr((await captcha_client.get(slide_url)).content, (await captcha_client.get(bg_url)).content,
                          False)
        tdc = self.get_collect(x)
        ans = f'{x},{int(spt)};'
        log.debug('ans--------:{}', ans)
        collect = tdc["collect"]
        log.debug('collect:{}', collect)
        self.cookie = None
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            # Requests sorts cookies= alphabetically
            # 'Cookie': self.cookie,
            'Pragma': 'no-cache',
            'Referer': 'https://open.captcha.qq.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': user_agent,
        }
        data = {
            "aid": self.aid,
            "protocol": "https",
            "accver": "1",
            "showtype": "popup",
            "ua": ua,
            "noheader": "1",
            "fb": "1",
            "aged": "0",
            "enableAged": "0",
            "enableDarkMode": "0",
            "grayscale": "1",
            "clientype": "2",
            "sess": sess,
            "fwidth": "0",
            "sid": sid,
            "wxLang": "",
            "tcScale": "1",
            "uid": "",
            "cap_cd": "",
            "rnd": self.rnd,
            "prehandleLoadTime": "508",
            "createIframeStart": now,
            "global": "0",
            "subsid": "5",
            "cdata": "0",
            "ans": ans,
            "vsig": "",
            "websig": "",
            "subcapclass": "",
            "pow_answer": self.pow_answer,
            "pow_calc_time": 1,
            "collect": collect,
            "tlg": len(collect),
            "fpinfo": "",
            "eks": {parse.unquote(tdc["eks"])},
            "nonce": nonce,
            "vlg": "0_0_1"
        }
        response = await self.client.post('https://turing.captcha.qcloud.com/cap_union_new_verify', headers=headers,
                                          data=data)
        self.res['data'] = response.json()
        await self.client.aclose()
        log.debug('res:{}', self.res)
        return self.res


async def get_ticket():
    try:
        log.remove()
        log.add(sys.stderr, level='INFO')

        proxy = httpx.get(
            'https://tps.kdlapi.com/api/gettps?secret_id=ovm4rxlthlcgq5i6ucp0&signature'
            '=4vr4abut9ezcbjg26yi1zysi8m7693s5&num=1').text
        res = QQSlide2(aid=2003473469, proxy=proxy)
        log.info('开始获取ticket')
        result = await res.run()
        log.info('获取ticket成功', result)
        return result
    except Exception as e:
        print(e)
