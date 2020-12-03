#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) oatsu
"""
UTAUのプラグイン用のモジュール
基本的には utaupy.ust の Ust() とか Note() を流用する。

【注意】本スクリプトは開発初期なため仕様変更が激しいです。
"""

from copy import deepcopy
# from pprint import pprint
from sys import argv

from utaupy import ust as _ust


def run(your_function, path=None):
    """
    UTAUプラグインスクリプトファイルの入出力をする。
    path: UTAUから出力されるプラグインスクリプトのパス
    """
    if path is None:
        path = argv[1]
    # up.utauplugin.Plugin オブジェクトとしてプラグインスクリプトを読み取る
    plugin = load(path)
    # 目的のノート処理を実行
    your_function(plugin)
    # プラグインスクリプトを上書き
    plugin.write(path)


def load(path: str, encoding='shift-jis'):
    """
    UTAUプラグイン一時ファイルを読み取る
    USTのやつを一部改変
    """
    # UtauPluginオブジェクト化
    plugin = UtauPlugin()
    plugin.load(path, encoding=encoding)
    return plugin


class UtauPlugin(_ust.Ust):
    """
    UTAUプラグインの一時ファイル用のクラス
    UST用のクラスを継承
    """

    def write(self, path: str, mode: str = 'w', encoding: str = 'shift-jis') -> str:
        """
        USTをファイル出力
        """
        # 文字列にする
        s = str(deepcopy(self))
        # ファイル出力
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s
