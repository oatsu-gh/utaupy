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
    o.set_values(otolist)
    return o


class OtoIni:
    """oto.iniを想定したクラス"""

    def __init__(self):
        # 'Oto'クラスからなるリスト
        self.otolist = []

    def get_values(self):
        """中身を確認する"""
        return self.otolist

    def set_values(self, l):
        """中身を上書きする"""
        self.otolist = l

    def replace_alieses(self, before, after):
        """エイリアスを置換する"""
        for oto in self.otolist:
            oto.set_alies(oto.get_alies().replace(before, after))
        return self

    def kana2roma(self, path_table, replace=True, dt=100):
        """
        エイリアスをローマ字にする
        かな→ローマ字 変換表のパス
        replace:
          Trueのときエイリアスをローマ字に書き換え
          Falseのときエイリアスは平仮名のまま
        """
        # ローマ字変換表読み取り
        d = table.load(path_table)
        d.update({'R': ['pau'], 'pau': ['pau'], 'br': ['br']})
        # 発音記号の分割数によってパラメータを調整
        for oto in self.otolist:
            kana = oto.get_alies().split()[-1]
            try:
                roma = d[kana]
            # KeyErrorはリストにするだけで返される
            except KeyError as e:
                print('\n[KeyError in otoini.kana2roma]---------')
                print('想定外の文字が kana として入力されました。')
                print('該当文字列(kana):', kana)
                print('エラー詳細(e)   :', e)
                print('--------------------------------------\n')
                roma = d[kana]
            # 歌詞をローマ字化
            if replace is True:
                oto.set_alies(' '.join(roma))
            # モノフォン
            if len(roma) == 1:
                # print('  alies: {}\t-> {}\t: オーバーラップ右シフト・先行発声右詰め'.format(alies, roma))
                oto.set_overlap(2 * dt)
                oto.set_onset(oto.get_fixed())
            # おもにCV形式のとき
            elif len(roma) == 2:
                # print('  alies: {}\t-> {}\t: そのまま'.format(alies, roma))
                pass
            # おもにCCV形式のとき
            elif len(roma) == 3:
                # print('  alies: {}\t-> {}\t: そのままでいい？'.format(alies, roma))
                pass
            elif len(roma) >= 4:
                print('  [ERROR]---------')
                print('  1,2,3音素しか対応していません。')
                print('  alies: {}\t-> {}\t: そのままにします。'.format(kana, roma))
                print('  ----------------')

    def monophonize(self):
        """音素ごとに分割"""
        # 新規OtoIniを作るために、otoを入れるリスト
        l = []
        for oto in self.otolist:
            alieses = oto.get_alies().split()
            if len(alieses) == 1:
                l.append(oto)
            elif len(alieses) in [2, 3]:
                name_wav = oto.get_filename()
                # 1文字目(オーバーラップから先行発声まで)------------
                tmp1 = Oto()
                a = alieses[0]
                t = oto.get_lblank() + oto.get_overlap()  # オーバーラップの位置から
                tmp1.set_filename(name_wav)
                tmp1.set_alies(a)
                tmp1.set_lblank(t)
                tmp1.set_overlap(0)
                l.append(tmp1)
                # 2文字目(先行発声から固定範囲まで)----------------
                tmp2 = Oto()
                a = alieses[1]
                t = oto.get_lblank() + oto.get_onset()  # 先行発声の位置から
                tmp2.set_filename(name_wav)
                tmp2.set_alies(a)
                tmp2.set_lblank(t)
                tmp2.set_overlap(0)
                # tmp2.set_onset(0)
                # tmp2.set_fixed(0)
                # tmp2.set_rblank(0)
                l.append(tmp2)
                if len(alieses) == 3:
                    # 3文字目(固定範囲から右ブランクまで)----------------
                    tmp3 = Oto()
                    a = alieses[2]
                    t = oto.get_lblank() + oto.get_fixed()  # 固定範囲の位置から
                    tmp1.set_filename(name_wav)
                    tmp1.set_alies(a)
                    tmp1.set_lblank(t)
                    tmp1.set_overlap(0)
                    l.append(tmp3)
            else:
                print('\n[ERROR in otoini.monophonize()]----------------')
                print('エイリアスのローマ字分割数は 1, 2, 3 以外対応していません。')
                print('alieses: {}'.format(alieses))
                print('文字を連結して処理を続行します。')
                print('-----------------------------------------------\n')
                l.append(oto)
        self.set_values(l)

    def write(self, path, mode='w', encoding='shift-jis'):
        """OtoIniクラスオブジェクトをINIファイルに出力"""
        s = ''
        for oto in self.otolist:
            l = []
            l.append(oto.get_filename())
            l.append(oto.get_alies())
            l.append(oto.get_lblank())
            l.append(oto.get_fixed())
            l.append(oto.get_rblank())
            l.append(oto.get_onset())
            l.append(oto.get_overlap())
            # 数値部分を丸めてから文字列に変換
            l = l[:2] + [str(round(float(v), 3)) for v in l[2:]]
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
        self.d = dict(zip(keys, l))

    def from_otoini(self, l):
        """リストをもらってクラスオブジェクトにする"""
        keys = ('FileName', 'Alies', 'LBlank',
                'Fixed', 'RBlank', 'Onset', 'Overlap')
        # 数値部分をfloatにする
        l = l[:2] + [float(v) for v in l[2:]]
        self.d = dict(zip(keys, l))
        return self

    # ここからノートの全値の処理----------------------
    def get_values(self):
        """中身を確認する"""
        return self.d

    def set_values(self, d):
        """中身を上書きする"""
        self.d = d
    # ここまでノートの全値の処理----------------------

    # ここからノートの各値の参照----------------------
    def get_filename(self):
        """wavファイル名を確認する"""
        return self.d['FileName']

    def get_alies(self):
        """エイリアスを確認する"""
        return self.d['Alies']

    def get_lblank(self):
        """左ブランクを確認する"""
        return self.d['LBlank']

    def get_fixed(self):
        """固定範囲を確認する"""
        return self.d['Fixed']

    def get_rblank(self):
        """右ブランクを確認する"""
        return self.d['RBlank']

    def get_onset(self):
        """先行発声を確認する"""
        return self.d['Onset']

    def get_overlap(self):
        """右ブランクを確認する"""
        return self.d['Overlap']
    # ここまでノートの各値の参照----------------------

    # ここからの各値の上書き----------------------
    def set_filename(self, x):
        """wavファイル名を上書きする"""
        self.d['FileName'] = x

    def set_alies(self, x):
        """エイリアスを上書きする"""
        self.d['Alies'] = x

    def set_lblank(self, x):
        """左ブランクを上書きする"""
        self.d['LBlank'] = x

    def set_fixed(self, x):
        """固定範囲を上書きする"""
        self.d['Fixed'] = x

    def set_rblank(self, x):
        """右ブランクを上書きする"""
        self.d['RBlank'] = x

    def set_onset(self, x):
        """先行発声を上書きする"""
        self.d['Onset'] = x

    def set_overlap(self, x):
        """右ブランクを上書きする"""
        self.d['Overlap'] = x
    # ここまでノートの各値の上書き----------------------


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    print('utaupy.otoini imported')
