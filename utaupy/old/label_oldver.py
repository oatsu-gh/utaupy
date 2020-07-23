#!python3
# coding: utf-8
"""
歌唱データベース用のLABファイルとデータを扱うモジュールです。

当ファイルは2020年7月22日以前の仕様です。
Label オブジェクト内の音素クラスPhoneme実装前で、
Label のデータは二次元リストで扱っています。
"""


def main():
    """実行されたときの挙動"""
    print('呼び出しても使えませんが...')


def load(path, mode='r', encoding='utf-8', kiritan=False):
    """
    labファイルを読み取ってLabクラスオブジェクトにする
    時刻を整数にすることに注意
    """
    # labファイル読み取り
    with open(path, mode=mode, encoding=encoding) as f:
        lines = [s.strip().split() for s in f.readlines()]
    # 入力ファイル末尾の空白行を除去
    while lines[-1] == ['']:
        del lines[-1]

    # リストにする [[開始時刻, 終了時刻, 発音], [], ...]
    if kiritan:
        # きりたんDBのモノラベル形式の場合、時刻が 0.0000000[s] なのでfloatを経由する。
        l = [[int(10000000 * float(v[0])), int(10000000 * float(v[1])), v[2]] for v in lines]
    else:
        # Sinsyのモノラベル形式の場合、時刻が 1234567[100ns] なのでintにする。
        l = [[int(v[0]), int(v[1]), v[2]] for v in lines]
    # Labelクラスオブジェクト化
    lab = Label()
    lab.values = l
    return lab


class Label:
    """
    歌唱ラベルLABファイルを想定したクラス(2019/04/19から)
    """

    def __init__(self):
        """二次元リスト [[開始時刻, 終了時刻, 発音], [], ...]"""
        self.__phonemes = []

    @property
    def values(self):
        """propertyはgetterも兼ねるらしい"""
        return self.__phonemes

    @values.setter
    def values(self, lines):
        """値を登録"""
        if not isinstance(lines, list):
            raise TypeError('argument \'lines\' must be list instance (values.setter in utaupy.label.py)')
        self.__phonemes = lines

    def write(self, path, mode='w', encoding='utf-8', newline='\n', delimiter=' ', kiritan=False):
        """LABを保存"""
        # 出力用の文字列
        l = self.values
        if kiritan:
            lines = ['{:.7f} {:.7f} {}'.format(*v) for v in l] # 100ns -> 1s 表記変換
        else:
            lines = [f'{v[0]}{delimiter}{v[1]}{delimiter}{v[2]}' for v in l]
        # ファイル出力
        with open(path, mode=mode, encoding=encoding, newline=newline) as f:
            f.write('\n'.join(lines))
        return lines


# 
# class Phoneme:
#     """
#     ラベルの一行分の情報を持つクラス(2020/07/23から)
#     """
#     def __init__(self):
#         self.start = None
#         self.end = None
#         self.symbol = None




if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass
