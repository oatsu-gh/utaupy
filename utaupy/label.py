#!python3
# coding: utf-8
"""
歌唱データベース用のLABファイルとデータを扱うモジュールです。
"""


def main():
    """実行されたときの挙動"""
    print('labファイル読み取り動作テストをします。')
    path_lab = input('path_lab: ')
    label = load(path_lab)
    for phoneme in label.values:
        print(phoneme.values)


def load_as_plainlist(path, mode='r', encoding='utf-8', kiritan=False):
    """
    labファイルを ふつうの2次元リストとして読み取る。
    旧バージョンの utaupy.label.load() に近い動作をする。
    """
    # labファイルを読み取り
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
    return l


def load(path, mode='r', encoding='utf-8', kiritan=False):
    """
    labファイルを読み取って Label クラスオブジェクトにする
    時刻を整数にすることに注意
    """
    # lab ファイル読み取り
    with open(path, mode=mode, encoding=encoding) as f:
        lines = [s.strip().split() for s in f.readlines()]
    # 入力ファイル末尾の空白行を除去
    while lines[-1] == ['']:
        del lines[-1]

    # リストにする [[開始時刻, 終了時刻, 発音], [], ...]
    if kiritan:
        phonemes = []
        for v in lines:
            phoneme = Phoneme()
            phoneme.start = int(10000000 * float(v[0]))
            phoneme.end = int(10000000 * float(v[1]))
            phoneme.symbol = v[2]
            phonemes.append(phoneme)

    # Sinsyのモノラベル形式の場合、時刻が 1234567[100ns] なのでintにする。
    else:
        phonemes = []
        for v in lines:
            phoneme = Phoneme()
            phoneme.start = int(v[0])
            phoneme.end = int(v[1])
            phoneme.symbol = v[2]
            phonemes.append(phoneme)

    # Labelクラスオブジェクト化
    label = Label()
    label.values = phonemes
    return label


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
    def values(self, phonemes):
        """
        値を登録
        """
        if not isinstance(phonemes, list):
            raise TypeError('argument \'phonemes\' must be list instance (values.setter in utaupy.label.py)')
        self.__phonemes = phonemes

    def write(self, path, mode='w', encoding='utf-8', newline='\n', delimiter=' ', kiritan=False):
        """
        LABファイルを書き出し
        """
        # 出力用の文字列
        phonemes = self.values
        if kiritan:
            lines = ['{:.7f} {:.7f} {}'.format(ph.start, ph.end, ph.symbol) for ph in phonemes]  # 100ns -> 1s 表記変換
        else:
            lines = ['{0}{3}{1}{3}{2}'.format(ph.start, ph.end, ph.symbol, delimiter) for ph in phonemes]
        # ファイル出力
        with open(path, mode=mode, encoding=encoding, newline=newline) as f:
            f.write('\n'.join(lines))
        return lines


class Phoneme:
    """
    ラベルの一行分の情報を持つクラス(2020/07/23から)
    """

    def __init__(self):
        self.start = None   # 発声開始位置
        self.end = None     # 発声終了位置
        self.symbol = None  # 発音記号

    @property
    def values(self):
        """
        値を確認する用に一応実装
        setterは用意しない
        """
        d = {'self.start': self.start,
             'self.end': self.end,
             'self.symbol': self.symbol}
        return d


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass
