#!python3
# coding: utf-8
"""
UTAUの録音リストを扱うモジュール
録音リストは休憩する部分で空白行を入れてね
"""


def main():
    """直接実行されたときの動作"""
    print('録音リストを扱うためのモジュールです。importして使ってね。')


def load(path, mode='r', encoding='shift-jis'):
    """録音リストを読み取ってオブジェクト生成"""
    # 録音リストを読み取る
    with open(path, mode=mode, encoding=encoding) as f:
        l = [re.split('[=,]', s.strip()) for s in f.readlines()]
    # # 空白の行を削除
    # l = [v for v in l if v != '']
    r = RecList()
    r.values = l
    return r


class RecList:
    """録音リスト"""

    def __init__(self):
        self.__values = []

    @property
    def values(self):
        """中身を取得"""
        return self.__values

    @values.setter
    def values(self, l):
        self.__values = l

    def save_as_reaper_region_csv(self, path_csvfile, offset_beats=4):
        """
        path_csvfile: 出力パス
        録音リストからReaperのリージョンCSVをつくる。
        これを使うと原音の分割が楽にできる。
        """
        l = self.values()
        head = '#,Name,Start,End,Length'
        for i, v in enumerate():
            if v != '':
                name = v
                start = '{}.1.00'
                end = '{}.1.00'
                length = '{}.0.00'
                line = 'R{},{},'










if __name__ == '__main__':
    main()
