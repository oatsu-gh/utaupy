#! /usr/bin/env python3
# coding: utf-8
# Copyright (c) oatsu
"""
UTAUのプラグイン用のモジュール
utaupy.ust.Ust をもとに、ファイル入出力機能を変更したもの。
"""

from copy import deepcopy
from sys import argv
from typing import Callable
from os.path import splitext

from utaupy import ust as _ust


def run(your_function: Callable, option=None, path=None):
    """
    UTAUプラグインスクリプトファイルの入出力をする。
    your_function: 実行したい関数
    arguments: 実行オプションとか
    path: UTAUから出力されるプラグインスクリプトのパス
    """
    if path is None:
        path = argv[1]
    # up.utauplugin.Plugin オブジェクトとしてプラグインスクリプトを読み取る
    plugin = load(path)
    # 目的のノート処理を実行
    if option is None:
        your_function(plugin)
    else:
        your_function(plugin, option)

    # 拡張子がustの時は、プラグインとしてではなくUSTとして上書き保存する。
    if splitext(path)[1] in ['.ust', '.UST']:
        plugin.as_ust().write(path)
    # プラグインスクリプトを上書き
    else:
        plugin.write(path)


def load(path: str, encoding='cp932'):
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

    def __init__(self):
        super().__init__()
        # プラグインのときは[#TRACKEND]が不要
        self.trackend = None

    def write(self, path: str, mode: str = 'w', encoding: str = 'cp932') -> str:
        """
        USTをファイル出力
        """
        # 文字列にする
        s = str(deepcopy(self)) + '\n'
        # ファイル出力
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s

    def as_ust(self) -> _ust.Ust:
        """
        utaupy.ust.Ustオブジェクトに変換する。
        USTファイルとして保存するときに使う。
        """
        plugin = deepcopy(self)
        # Ustオブジェクトを生成
        ust = _ust.Ust()
        # [#SETTING] の情報をコピー
        ust.version = plugin.version   # [#VERSION]
        ust.setting = plugin.setting  # [#SETTING]
        ust.notes = plugin.notes  # [#1234], [#INSERT], [#DELETE]
        return ust
