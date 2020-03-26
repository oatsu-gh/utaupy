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
    # Tableクラス化
    table = Table()
    table.set_values(d)
    return table

def kana2roma(table, kana):
    """平仮名をローマ字に変換してリストで返す"""
    if isinstance(table, dict):
        d = table
    else:
        d = table.get_values()
    try:
        return d[kana]
    # 辞書になかったらそのまま返す
    except KeyError as e:
        print('\n[KeyError in table.kana2roma]---------')
        print('想定外の文字が kana として入力されました。')
        print('該当文字列(kana):', kana)
        print('エラー詳細(e)   :', e)
        print('--------------------------------------\n')
        return [kana]

# NOTE: 未実装
def roma2kana(table, roma):
    """ローマ字を平仮名に変換して文字列で返す"""
    print('\n[WARN in table.kana2roma]-------------')
    print('未実装です。')
    print('table:', table)
    print('roma :', roma)
    print('--------------------------------------\n')
    return ''.join(roma)

class Table:
    """japanese.tableを想定したクラス"""

    def __init__(self):
        self.d = {}

    def get_values(self):
        """値を確認"""
        return self.d

    def set_values(self, d):
        """値を上書き"""
        self.d = d
        return self

    def update(self, d):
        """辞書に要素を追加、重複項目は上書き"""
        self.d.update(d)
        return self


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    print('utaupy.table imported')
