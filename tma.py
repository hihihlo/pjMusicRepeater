##
import wx, re
import sys
import requests

# headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
#
# def downYoudao(word):
#     data = {"audio": word, "lang": "zh", "type": 2}  # 向有道批次發請求，得到單詞、短語的發音
#     resp = requests.post("https://dict.youdao.com/dictvoice", data=data, headers=headers)  # 發起資料請求
#     with open(f'test_ref/word/youd-{word}.mp3', "wb") as f:  # 獲取請求結果並寫入本地
#         f.write(resp.content)
#
# downYoudao('book')
# downYoudao('computer')
# downYoudao('syntax')

raw_text = """
  1. ### Dr.eye 譯典通
### bear
    * KK[bɛr]
    * DJ[bɛə]
美式
    * vt.
支持，承受；承擔；運送；攜帶；帶走[O]
    * vi.
承受重量（或壓力）；用力推（或擠，壓）
    * #### 動詞變化： **bore** / **borne** / **born** / **bearing**
  2.      * 釋義
     * 同反義
     * 相關詞
"""

rm = re.search(r'\n\s*### bear(\n\s*\*.*){3}', raw_text)
rm.group(1)