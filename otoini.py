#!/usr/bin/env python3
# coding: utf-8
"""
setParam用のINIファイルとデータを扱うモジュールです。
"""
import re

from . import table


def main():
    """実行されたときの挙動"""
    print('耳ロボPとsetParamに卍感謝卍')


def load(path, mode='r', encoding='shift-jis'):
    """otoiniを読み取ってオブジェクト生成"""
    # otoiniファイルを読み取る
    with open(path, mode=mode, encoding=encoding) as f:
        l = [re.split('[=,]', s.strip()) for s in f.readlines()]
    # 入力ファイル末尾の空白行を除去
    while l[-1] == ['']:
        del l[-1]

    # Otoクラスオブジェクトのリストを作る
    otolist = []
    for v in l:
        oto = Oto()
        oto.from_otoini(v)
        otolist.append(oto)
    # OtoIniクラスオブジェクト化
    o = OtoIni()
    o.values = otolist
    return o


class OtoIni:
    """oto.iniを想定したクラス"""

    def __init__(self):
        # 'Oto'クラスからなるリスト
        self._values = []

    @property
    def values(self):
        """中身を確認する"""
        return self._values

    @values.setter
    def values(self, list_of_oto):
        """中身を上書きする"""
        self._values = list_of_oto

    def replace_alieses(self, before, after):
        """エイリアスを置換する"""
        for oto in self._values:
            oto.alies = oto.alies.replace(before, after)
        return self

    def is_mono(self):
        """
        モノフォン形式のエイリアスになっているか判定する。
        返り値はbool。
        """
        return all(len(v.alies) == 1 for v in self.values)

    def kana2romaji(self, path_table, replace=True, dt=100):
        """
        エイリアスをローマ字にする
        かな→ローマ字 変換表のパス
        replace:
          Trueのときエイリアスをローマ字に書き換え
          Falseのときエイリアスは平仮名のまま
        """
        # ローマ字変換表読み取り
        d = table.load(path_table)
        d.update({'R': ['pau'], 'pau': ['pau'], 'sil': ['sil']})
        # 発音記号の分割数によってパラメータを調整
        for oto in self._values:
            kana = oto.alies.split()[-1]
            try:
                romaji = d[kana]
            # KeyErrorはリストにするだけで返される
            except KeyError as e:
                print('\n[KeyError in otoini.kana2romaji]---------')
                print('想定外の文字が kana として入力されました。')
                print('該当文字列(kana):', kana)
                print('エラー詳細(e)   :', e)
                print('--------------------------------------\n')
                romaji = d[kana]
            # 歌詞をローマ字化
            if replace is True:
                oto.alies = ' '.join(romaji)
            # モノフォン
            if len(romaji) == 1:
                # print('  alies: {}\t-> {}\t: オーバーラップ右シフト・先行発声右詰め'.format(alies, romaji))
                oto.overlap = 2 * dt
                oto.onset = oto.fixed
            # おもにCV形式のとき
            elif len(romaji) == 2:
                # print('  alies: {}\t-> {}\t: そのまま'.format(alies, romaji))
                pass
            # おもにCCV形式のとき
            elif len(romaji) == 3:
                # print('  alies: {}\t-> {}\t: そのままでいい？'.format(alies, romaji))
                pass
            elif len(romaji) >= 4:
                print('  [ERROR]---------')
                print('  1,2,3音素しか対応していません。')
                print('  alies: {}\t-> {}\t: そのままにします。'.format(kana, romaji))
                print('  ----------------')

    def monophonize(self):
        """音素ごとに分割"""
        # 新規OtoIniを作るために、otoを入れるリスト
        l = []
        for oto in self._values:
            alieses = oto.alies.split()
            if len(alieses) == 1:
                l.append(oto)
            elif len(alieses) in [2, 3]:
                name_wav = oto.filename
                # 1文字目(オーバーラップから先行発声まで)------------
                tmp1 = Oto()
                a = alieses[0]
                t = oto.lblank + oto.overlap  # オーバーラップの位置から
                tmp1.filename = name_wav
                tmp1.alies = a
                tmp1.lblank = t
                tmp1.overlap = 0
                l.append(tmp1)
                # 2文字目(先行発声から固定範囲まで)----------------
                tmp2 = Oto()
                a = alieses[1]
                t = oto.lblank + oto.onset  # 先行発声の位置から
                tmp2.filename = name_wav
                tmp2.alies = a
                tmp2.lblank = t
                tmp2.overlap = 0
                # tmp2.set_onset(0)
                # tmp2.set_fixed(0)
                # tmp2.set_rblank(0)
                l.append(tmp2)
                if len(alieses) == 3:
                    # 3文字目(固定範囲から右ブランクまで)----------------
                    tmp3 = Oto()
                    a = alieses[2]
                    t = oto.lblank + oto.fixed  # 固定範囲の位置から
                    tmp1.filename = name_wav
                    tmp1.alies = a
                    tmp1.lblank = t
                    tmp1.overlap = 0
                    l.append(tmp3)
            else:
                print('\n[ERROR in otoini.monophonize()]----------------')
                print('エイリアスのローマ字分割数は 1, 2, 3 以外対応していません。')
                print('alieses: {}'.format(alieses))
                print('文字を連結して処理を続行します。')
                print('-----------------------------------------------\n')
                l.append(oto)
        self.values = l

    def write(self, path, mode='w', encoding='shift-jis'):
        """OtoIniクラスオブジェクトをINIファイルに出力"""
        s = ''
        for oto in self._values:
            l = []
            l.append(oto.filename)
            l.append(oto.alies)
            l.append(oto.lblank)
            l.append(oto.fixed)
            l.append(oto.rblank)
            l.append(oto.onset)
            l.append(oto.overlap)
            # 数値部分を丸めてから文字列に変換
            l = l[:2] + [str(round(float(v), 4)) for v in l[2:]]
            s += '{}={},{},{},{},{},{}\n'.format(*l)  # 'l[0]=l[1],l[2],...'
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s


class Oto:
    """oto.ini中の1モーラ"""

    def __init__(self):
        keys = ('FileName', 'Alies', 'LBlank',
                'Fixed', 'RBlank', 'Onset', 'Overlap')
        l = [None] * 7
        self.__d = dict(zip(keys, l))

    def from_otoini(self, l):
        """1音分のリストをもらってクラスオブジェクトにする"""
        keys = ('FileName', 'Alies', 'LBlank',
                'Fixed', 'RBlank', 'Onset', 'Overlap')
        # 数値部分をfloatにする
        l = l[:2] + [float(v) for v in l[2:]]
        self.__d = dict(zip(keys, l))
        return self

    # ここからノートの全値の処理----------------------
    @property
    def values(self):
        """中身を確認する"""
        return self.__d

    @values.setter
    def values(self, d):
        """中身を上書きする"""
        self.__d = d
    # ここまでノートの全値の処理----------------------

    # ここからノートの各値の処理----------------------
    @property
    def filename(self):
        """wavファイル名を確認する"""
        return self.__d['FileName']

    @filename.setter
    def filename(self, x):
        """wavファイル名を上書きする"""
        self.__d['FileName'] = x

    @property
    def alies(self):
        """エイリアスを確認する"""
        return self.__d['Alies']

    @alies.setter
    def alies(self, x):
        """エイリアスを上書きする"""
        self.__d['Alies'] = x

    @property
    def lblank(self):
        """左ブランクを確認する"""
        return self.__d['LBlank']

    @lblank.setter
    def lblank(self, x):
        """左ブランクを上書きする"""
        self.__d['LBlank'] = x

    @property
    def fixed(self):
        """固定範囲を確認する"""
        return self.__d['Fixed']

    @fixed.setter
    def fixed(self, x):
        """固定範囲を上書きする"""
        self.__d['Fixed'] = x

    @property
    def rblank(self):
        """右ブランクを確認する"""
        return self.__d['RBlank']

    @rblank.setter
    def rblank(self, x):
        """右ブランクを上書きする"""
        self.__d['RBlank'] = x

    @property
    def rblank2(self):
        """右ブランクを絶対時刻で取得する"""
        return max(self.__d['RBlank'], self.__d['LBlank'] - self.__d['RBlank'])

    # LBlankがNullのとき処理できず、バグのもとになるので無効化
    # @rblank2.setter
    # def rblank2(self, x):
    #     """右ブランクを上書きする。負の値に強制する。"""
    #     self.__d['RBlank'] = min(x, self.__d['LBlank'] - x)

    @property
    def onset(self):
        """先行発声を確認する"""
        return self.__d['Onset']

    @onset.setter
    def onset(self, x):
        """先行発声を上書きする"""
        self.__d['Onset'] = x

    @property
    def overlap(self):
        """右ブランクを確認する"""
        return self.__d['Overlap']

    @overlap.setter
    def overlap(self, x):
        """右ブランクを上書きする"""
        self.__d['Overlap'] = x
    # ここまでノートの各値の処理----------------------


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass
