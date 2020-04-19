#!/usr/bin/env python3
# coding: utf-8
"""
日本語とアルファベットの対応表を扱うモジュールです。
"""


def main():
    """呼び出されても特に何もしない"""
    print('平仮名とアルファベットの対応表を扱うモジュールです。')
    print('平仮名やUSTの歌詞判定の機能もあります。（まだない）')


def load(path):
    """テーブルを読み取ってインスタンス生成"""
    d = {}
    # ファイル読み取り
    with open(path) as f:
        with open(path, 'r') as f:
            l = [v.split() for v in f.readlines()]
    # 辞書にする
    for v in l:
        d[v[0]] = v[1:]
    return d


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    print('utaupy.table imported')
