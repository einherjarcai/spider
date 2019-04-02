"""
 @Time          :   2019-04-02 14:51
 @Author        :   einherjar
 @File          :   baidu_translation.py
 @Description   :   调用百度翻译API
"""
import requests
import json
import re
import execjs
import sys


class BaiduTranslation(object):
    def __init__(self, content):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
            'Cookie': 'BIDUPSID=E9B058D087F0C0FDD3A0C88A93681FCE; PSTM=1536569393; BDUSS=zFYV1NpRVRmSDhEVWg2Y3pjS2t5RFdXWGFoa0NIeFROdnozdWRkWU1MZHB2T3RiQVFBQUFBJCQAAAAAAAAAAAEAAADnj6yvtdK~y83GtuA5NQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAGkvxFtpL8RbM; MCITY=-%3A; BAIDUID=0A5182736E61ACA3D7442FC0DDE62F01:FG=1; BDSFRCVID=bV4sJeCCxG3J_p59aEDMQwqW21UdQvfiKQYI3J; H_BDCLCKID_SF=JRA8oK05JIvhDRTvhCcjh-FSMgTBKI62aKDsKp7g-hcqEIL4LPRbQR0pjnOJBnOfQmTH2DQma4OkHUbSj4Qoj-6QbfvLBTolLeJMXJRttq5nhMJm257JDMP0qJ7jttTy523ibR6vQpnNqxtuj6tWj6j0DNR22Pc22-oKWnTXbRu_Hn7zeUjoDbtpbtbmhU-eyJni_C3m5tnnHlQPQJosbR8h5qLDLROg0R7ZVDD5fCtbMDLr-Pvo5t3H5MoX5-QXbPo2WbC35tooDtOv5J5jbjus5p62-KCHtbP8_KL8tD8MbD0Cq6K5j5cWjG4OexneWDTm5-nTtK3VjP_63-jS3pby0M5O2-rLJaKtbM8baU85OCFlD5thD63BeaRKeJQX2COXsJ6VHJOoDDkRjMR5y4LdLp7xJhT00bFf0bRmL-TdO56CbMFMjl4JyM7EtMCeWJLe_KDaJItWbP5kMtn_qttjMfbWetTbHD7yWCv5Wt55OR5JLn7nDpIX0a-fK-7wK66L0lo_2hO1MljhW55SMfJyyGCHt6tjtnAj_Iv55RTWjJuk-4r_bnIJMqJ-2tvtK4o2WbCQJhu28pcNLTDKjbIHLfcaqlkLBK5f-l5-Bt0B8prhjpO1j4_eKG8OttQL3b63blrSt-5J8h5jDh3qb6ksD-RC5JTwJjvy0hvcLR6cShnq5fjrDRLbXU6BK5vPbNcZ0l8K3l02VKO_e6t5jjJLDGtsKbQKaDQ036rh-6rjDnCr2MnOXUI8LNDH2x4HXKTBVlv8LKJbSq54X6rCbbk80RO7ttoAKa535hTR3UjAEf5lqf7nDUL1Db3DW6vMtg3tsRngfInoepvo0tcc3MkF5tjdJJQOBKQB0KnGbUQkeq8CQft205tpeGLfq6tOfnksL6rJbPoEq5rnhPF3-l53KP6-3MJO3b7ZM-tafRjpsh6h5nQRD6_AbbQqKtciLG5AohFLK-oj-D_mD5AB3J; BDORZ=B490B5EBF6F3CD402E515D22BCDA1598; H_PS_PSSID=28312_1456_21125_28132_28266_22160; delPer=0; PSINO=2; BDRCVFR[feWj1Vr5u3D]=I67x6TjHwwYf0; locale=zh; from_lang_often=%5B%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%2C%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%5D; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1547433565; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1547433565; to_lang_often=%5B%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%2C%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%5D',
            'Host': 'fanyi.baidu.com',
            'Origin': 'https: // fanyi.baidu.com',
            'Referer': 'https: // fanyi.baidu.com /?aldtype = 16047'
        }
        self.detect_url = 'https://fanyi.baidu.com/langdetect'
        self.trans_url = 'https://fanyi.baidu.com/v2transapi'
        self.ori_url = 'https://fanyi.baidu.com/'
        self.content = content
        self.session = requests.Session()
        self.token = ''
        self.gtk = ''

    def get_token_gtk(self):
        response = self.session.get(self.ori_url, headers=self.headers)
        html = response.content.decode()
        token_matches = re.findall("token: '(.*?)'", html, re.S)
        for match in token_matches:
            self.token = match
        gtk_matches = re.findall("window.gtk = '(.*?)';", html, re.S)
        for match in gtk_matches:
            self.gtk = match
        # print(self.token, self.gtk)

    def get_lan_type(self):
        lan_params = {
            'query': self.content
        }
        response = self.session.post(self.detect_url, headers=self.headers, data=lan_params)
        data = json.loads(response.content.decode())
        return data['lan']

    def get_sign(self):
        js = """
            var i = null
            function a(r) {
                if (Array.isArray(r)) {
                    for (var o = 0, t = Array(r.length); o < r.length; o++)
                        t[o] = r[o];
                    return t
                }
                return Array.from(r)
            }
            function n(r, o) {
                for (var t = 0; t < o.length - 2; t += 3) {
                    var a = o.charAt(t + 2);
                    a = a >= "a" ? a.charCodeAt(0) - 87 : Number(a),
                    a = "+" === o.charAt(t + 1) ? r >>> a : r << a,
                    r = "+" === o.charAt(t) ? r + a & 4294967295 : r ^ a
                }
                return r
            }
            function e(r, gtk) {
                var t = r.length;
                t > 30 && (r = "" + r.substr(0, 10) + r.substr(Math.floor(t / 2) - 5, 10) + r.substr(-10, 10));
                var u = void 0,
                u = null !== i ? i : (i = gtk || "") || "";
                for (var d = u.split("."), m = Number(d[0]) || 0, s = Number(d[1]) || 0, S = [], c = 0, v = 0; v < r.length; v++) {
                    var A = r.charCodeAt(v);
                    128 > A ? S[c++] = A : (2048 > A ? S[c++] = A >> 6 | 192 : (55296 === (64512 & A) && v + 1 < r.length && 56320 === (64512 & r.charCodeAt(v + 1)) ? (A = 65536 + ((1023 & A) << 10) + (1023 & r.charCodeAt(++v)),
                    S[c++] = A >> 18 | 240,
                    S[c++] = A >> 12 & 63 | 128) : S[c++] = A >> 12 | 224,
                    S[c++] = A >> 6 & 63 | 128),
                    S[c++] = 63 & A | 128)
                }
                for (var p = m, F = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(97) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(54)), D = "" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(51) + ("" + String.fromCharCode(94) + String.fromCharCode(43) + String.fromCharCode(98)) + ("" + String.fromCharCode(43) + String.fromCharCode(45) + String.fromCharCode(102)), b = 0; b < S.length; b++)
                    p += S[b],
                    p = n(p, F);
                return p = n(p, D),
                p ^= s,
                0 > p && (p = (2147483647 & p) + 2147483648),
                p %= 1e6,
                p.toString() + "." + (p ^ m)
            }
        """
        sign = execjs.compile(js).call('e', self.content, self.gtk)
        return sign

    def get_trans(self):
        # 1. 获取 token 和 gtk
        self.get_token_gtk()
        # 2. 获取 sign
        sign = self.get_sign()
        # 3. 获取语言类型
        lan_type = self.get_lan_type()
        if lan_type == 'zh':
            from_lan = 'zh'
            to_lan = 'en'
        else:
            from_lan = 'en'
            to_lan = 'zh'
        # 发送翻译请求
        params = {
            'from': from_lan,
            'to': to_lan,
            'query': self.content,
            'transtype': 'realtime',
            'simple_means_flag': 3,
            'sign': sign,
            'token': self.token
        }
        response = self.session.post(self.trans_url, headers=self.headers, data=params)
        # print(response.request.headers)
        # print(response.content.decode())
        data = json.loads(response.content.decode())
        result = data['trans_result']['data'][0]['dst']
        print('翻译结果： ' + result)


if __name__ == '__main__':
    trans_str = sys.argv[1]
    trans = BaiduTranslation(trans_str)
    trans.get_trans()
