#! /usr/bin/env python33
# coding: utf-8
"""
歌唱データベース用のLABファイルとデータを扱うモジュールです。
"""
import logging
from collections import UserList


def main():
    """
    実行されたときの挙動
    """
    print('labファイル読み取り動作テストをします。')
    path_lab = input('path_lab: ')
    label = load(path_lab)
    print(label)


def load_as_plainlist(path, mode='r', encoding='utf-8', time_unit='100ns'):
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
    if time_unit in ('s', 'sec', 'second'):
        # きりたんDBのモノラベル形式の場合、時刻が 0.0000000[s] なのでfloatを経由する。
        l = [[int(10000000 * float(v[0])), int(10000000 * float(v[1])), v[2]] for v in lines]
    elif time_unit in ('100ns', 'subus', 'subμs'):
        # Sinsyのモノラベル形式の場合、時刻が 1234567[100ns] なのでintにする。
        l = [[int(v[0]), int(v[1]), v[2]] for v in lines]
    else:
        raise ValueError(
            'function argument "time_unit" must be in ["100ns" (recommended), "s"]')
    return l


def load(path, mode='r', encoding='utf-8', time_unit='100ns'):
    """
    labファイルを読み取って Label クラスオブジェクトにする
    時刻を整数にすることに注意
    """
    path = path.strip('"')
    # lab ファイル読み取り
    with open(path, mode=mode, encoding=encoding) as f:
        lines = [s.strip().split(maxsplit=2) for s in f.readlines()]
    # 入力ファイル末尾の空白行を除去
    while lines[-1] == ['']:
        del lines[-1]

    label = Label()
    # label.original_path = path
    # リストにする [[開始時刻, 終了時刻, 発音], [], ...]
    if time_unit in ('s', 'sec', 'second'):
        for v in lines:
            phoneme = Phoneme()
            phoneme.start = int(10000000 * float(v[0]))
            phoneme.end = int(10000000 * float(v[1]))
            phoneme.symbol = v[2]
            label.append(phoneme)

    # Sinsyのモノラベル形式の場合、時刻が 1234567[100ns] なのでintにする。
    elif time_unit in ('100ns', 'subus', 'subμs'):
        for v in lines:
            phoneme = Phoneme()
            phoneme.start = int(v[0])
            phoneme.end = int(v[1])
            phoneme.symbol = v[2]
            label.append(phoneme)
    else:
        raise ValueError(
            'function argument "time_unit" must be in ["100ns" (recommended), "s"]')
    return label


class Label(UserList):
    """
    歌唱ラベルLABファイルを想定したクラス(2019/04/19から)
    """

    # def __init__(self):
        # なんかうまく実装できない
        # ループしようとすると TypeError: __init__() takes 1 positional argument but 2 were given になる
        # super().__init__()
        # self.original_path = None

    def __str__(self):
        """
        文字列として扱うときのフォーマット
        """
        label_as_str = '\n'.join(str(phoneme) for phoneme in self)
        return label_as_str

    @property
    def offset(self) -> int:
        """
        最初の音素の発声までの時間を取得する。
        """
        return self.data[0].start

    def shift(self, time_length_100ns: int):
        """
        全体の時刻をずらす。
        """
        for phoneme in self:
            phoneme.start += time_length_100ns
            phoneme.end += time_length_100ns

    def is_valid(self, threshold: int = 0, time_unit='ms') -> bool:
        """
        発声時間が一定未満な音素ラベル行を検出
        threshold: 許容される最小の発声時間(ms)
        """
        if time_unit == 'ms':
            threshold_100ns = int(threshold * (10**4))
        elif time_unit == '100ns':
            threshold_100ns = threshold
        else:
            raise ValueError('Argument "time_unit" must be "ms" or "100ns".')
        # 既定の長さに達しない音素を検出
        invalid_phonemes = []
        for phoneme in self:
            duration = phoneme.end - phoneme.start
            if duration < threshold_100ns:
                invalid_phonemes.append(phoneme)
                logging.error('発声時間が %s%s 未満か負です : %s %s',
                              threshold, time_unit, phoneme.start, phoneme.end)

        # 前後の音素の開始・終了時刻と一致するかチェック
        for i, phoneme in enumerate(self[1:-1], 1):
            previous_phoneme = self[i - 1]
            next_phoneme = self[i + 1]
            if phoneme.start != previous_phoneme.end:
                error_message = '\n'.join([
                    '発声開始時刻が直前の発声終了時刻と一致しません',
                    f'  previous_phoneme    : {previous_phoneme.start} {previous_phoneme.end}',
                    f'  current_phoneme : {phoneme.start} {phoneme.end}'])
                logging.error(error_message)
                invalid_phonemes.append(phoneme)
            if phoneme.end != next_phoneme.start:
                error_message = '\n'.join([
                    '発声終了時刻が直後の発声終了時刻と一致しません',
                    f'  current_phoneme : {phoneme.start} {phoneme.end}',
                    f'  next_phoneme    : {next_phoneme.start} {next_phoneme.end}'])
                logging.error(error_message)
                invalid_phonemes.append(phoneme)

        return len(invalid_phonemes) == 0

    def check_invalid_time(self, threshold=0):
        """
        発声時間が一定未満な音素ラベル行を検出
        threshold: 許容される最小の発声時間(ms)
        """
        threshold_100ns = int(threshold * (10**4))
        for phoneme in self:
            duration = phoneme.end - phoneme.start
            if duration < threshold_100ns:
                error_message = f'発声時間が {threshold}ms 未満か負です'
                logging.error(error_message)
        for i, phoneme in enumerate(self[1:-1], 1):
            previous_phoneme = self[i - 1]
            next_phoneme = self[i + 1]
            if phoneme.start != previous_phoneme.end:
                error_message = '\n'.join([
                    '発声開始時刻が直前の発声終了時刻と一致しません',
                    f'  previous_phoneme: {str(previous_phoneme)}',
                    f'  current_phoneme : {str(phoneme)}'])
                logging.error(error_message)
            if phoneme.end != next_phoneme.start:
                error_message = '\n'.join([
                    '発声終了時刻が直後の発声終了時刻と一致しません',
                    f'  current_phoneme : {str(phoneme)}',
                    f'  next_phoneme    : {str(next_phoneme)}'])

    def reload(self):
        """
        発音開始時刻を参照して、発音終了時刻を自動補完する。
        ただし最終行の発音終了時刻だけは補完できないため、そのままにする。
        """
        for i, phoneme in enumerate(self[:-1]):
            phoneme.end = self[i + 1].start

    def round(self, step_size: int):
        """
        時刻を丸める。
        """
        for phoneme in self:
            phoneme.start = round(phoneme.start / step_size) * step_size
            phoneme.end = round(phoneme.end / step_size) * step_size

    def write(self, path_out, mode='w',
              encoding='utf-8', newline='\n', delimiter=' ', time_unit='100ns'):
        """
        LABファイルを書き出し
        """
        if time_unit == '100ns':
            lines = ['{0}{3}{1}{3}{2}'.format(
                ph.start, ph.end, ph.symbol, delimiter) for ph in self]
        elif time_unit in ('s', '1s', 'sec'):
            lines = ['{:.7f} {:.7f} {}'.format(
                ph.start, ph.end, ph.symbol) for ph in self]  # 100ns -> 1s 表記変換
        else:
            raise ValueError("Argument time_unit must be '100ns' or 's'.")

        # ファイル出力
        with open(path_out, mode=mode, encoding=encoding, newline=newline) as f:
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

    def __str__(self):
        return f'{self.start} {self.end} {self.symbol}'

    @property
    def duration(self) -> int:
        """
        発声時間
        """
        return self.end - self.start


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass
