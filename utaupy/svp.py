#!python3
# coding: utf-8
"""
SynthVのS5PとSVPを扱うモジュールです。
読み取り機能のみです。
"""
import json
from collections import OrderedDict


def load(path_svp):
    """
    SVPを読み取って辞書を返す
    """
    # ファイル内容を文字列として取得
    with open(path_svp) as f:
        s = f.read()
    # 最後の改行文字とかよくわからん記号を消す
    while not s.endswith('}'):
        s = s[:-1]
    # 歌詞とプロジェクト名がバイト列なため、ひらがなにする。
    b = s.encode()
    # 辞書にする(OrderedDictのほうがいいかなあ)
    d = json.loads(b)
    d = OrderedDict(d)
    # pprint(d, width=200)
    return d
