#! /usr/bin/env python3
# coding: utf-8
"""
USTファイルとデータを扱うモジュールです。
"""
import re
from collections import UserDict, UserList
from copy import deepcopy


def main():
    """実行されたときの挙動"""
    print('デフォ子かわいいよデフォ子\n')

    print('ust読み取りテストをします。')
    path = input('ustのパスを入力してください。\n>>> ')
    ust = load(path)
    print()

    for note in ust.values:
        print(note)

    input('\nPress Enter to exit.')


def notenum_as_abc(notenum):
    """
    音階番号をABC表記に変更する(C1=24, C4=)
    """
    d = {'24': 'C1', '25': 'C#1', '26': 'D1', '27': 'D#1', '28': 'E1', '29': 'F1',
         '30': 'F#1', '31': 'G1', '32': 'G#1', '33': 'A1', '34': 'A#1', '35': 'B1',
         '36': 'C2', '37': 'C#2', '38': 'D2', '39': 'D#2', '40': 'E2', '41': 'F2',
         '42': 'F#2', '43': 'G2', '44': 'G#2', '45': 'A2', '46': 'A#2', '47': 'B2',
         '48': 'C3', '49': 'C#3', '50': 'D3', '51': 'D#3', '52': 'E3', '53': 'F3',
         '54': 'F#3', '55': 'G3', '56': 'G#3', '57': 'A3', '58': 'A#3', '59': 'B3',
         '60': 'C4', '61': 'C#4', '62': 'D4', '63': 'D#4', '64': 'E4', '65': 'F4',
         '66': 'F#4', '67': 'G4', '68': 'G#4', '69': 'A4', '70': 'A#4', '71': 'B4',
         '72': 'C5', '73': 'C#5', '74': 'D5', '75': 'D#5', '76': 'E5', '77': 'F5',
         '78': 'F#5', '79': 'G5', '80': 'G#5', '81': 'A5', '82': 'A#5', '83': 'B5',
         '84': 'C6', '85': 'C#6', '86': 'D6', '87': 'D#6', '88': 'E6', '89': 'F6',
         '90': 'F#6', '91': 'G6', '92': 'G#6', '93': 'A6', '94': 'A#6', '95': 'B6',
         '96': 'C7', '97': 'C#7', '98': 'D7', '99': 'D#7', '100': 'E7', '101': 'F7',
         '102': 'F#7', '103': 'G7', '104': 'G#7', '105': 'A7', '106': 'A#7', '107': 'B7',
         '108': 'C8', '109': 'C#8', '110': 'D8', '111': 'D#8', '112': 'E8', '113': 'F8',
         '114': 'F#8', '115': 'G8', '116': 'G#8', '117': 'A8', '118': 'A#8', '119': 'B8'}
    if isinstance(notenum, str):
        return d[notenum]
    if isinstance(notenum, int):
        return d[str(notenum)]
    if isinstance(notenum, (list, tuple)):
        return [d[str(v)] for v in notenum]
    raise TypeError("argument 'notenum' must be in [str, int, list, tuple]")


def load(path, mode='r', encoding='shift-jis'):
    """
    USTを読み取り
    """
    # USTを文字列として取得
    try:
        with open(path, mode=mode, encoding=encoding) as f:
            s = f.read()
    except UnicodeDecodeError:
        with open(path, mode=mode, encoding='utf-8_sig') as f:
            s = f.read()
    # USTをノート単位に分割
    l = [r'[#' + v.strip() for v in s.split(r'[#')][1:]
    # さらに行ごとに分割して二次元リストに
    l = [v.split('\n') for v in l]

    # ノートのリストを作る
    ust = Ust()
    for lines in l:
        note = Note()
        # ノートの種類
        tag = lines[0]
        note.tag = tag
        # print('Making "Note" instance from UST: {}'.format(tag))
        # タグ以外の行の処理
        if tag == '[#VERSION]':
            note['UstVersion'] = lines[1]
        elif tag == '[#TRACKEND]':
            pass
        else:
            for line in lines[1:]:
                key, value = line.split('=', 1)
                note.set_by_key(key, value)
        ust.append(note)

    # 旧形式の場合にタグの数を合わせる
    if ust[0].tag != '[#VERSION]':
        try:
            version = ust[0].get_by_key('UstVersion')
        except KeyError:
            print('WARN: USTファイルに [#VERSION] のエントリがありません。UTAU Ver 0.4.18 未満の場合はアップデートしてください。')
            version = 'older_than_1.20'
        note = Note()
        note.tag = '[#VERSION]'
        note.set_by_key('UstVersion', version)
        ust.insert(0, note)  # リスト先頭に挿入
    # UTAUプラグイン用のファイルとかで[#SETTING]がない場合にずれるのを対策
    if ust[1].tag != '[#SETTING]':
        note = Note()
        note.tag = '[#SETTING]'
        ust.insert(0, note)
    # インスタンス変数に代入
    ust.version = ust[0]
    ust.setting = ust[1]
    # 隠しパラメータ alternative_tempo を全ノートに設定
    ust.reload_tempo()
    return ust


class Ust(UserList):
    """UST"""

    def __init__(self):
        super().__init__()
        # ノート(クラスオブジェクト)からなるリスト
        self.version = None
        self.setting = None

    @property
    def values(self):
        """中身を見る"""
        return self

    @values.setter
    def values(self, l):
        """
        中身を上書きする
        テンポを正常に取得できるようにする
        """
        if not isinstance(l, list):
            raise TypeError('argument \"l\" must be list instance')
        self.data = l
        self.reload_tempo()
        return self.data

    @property
    def notes(self):
        """
        全セクションのうち、[#VERSION] と [#SETTING] [#TRACKEND] を除いたノート部分を取得
        """
        return self.data[2:-1]

    @notes.setter
    def notes(self, l):
        """
        全セクションのうち、[#VERSION] と [#SETTING] [#TRACKEND] を除いたノート部分を上書き
        """
        if not isinstance(l, list):
            raise TypeError('argument \"l\" must be list instance')
        self.data = self.data[:2] + l + self.data[-1:]
        self.reload_tempo()
        return self.data

    @property
    def tempo(self):
        """全体のBPMを見る"""
        try:
            project_tempo = self.data[1].tempo
            return project_tempo
        except KeyError:
            first_note_tempo = self.data[2].tempo
            return first_note_tempo

        print('[ERROR]--------------------------------------------------')
        print('USTのテンポが設定されていません。とりあえず120にします。')
        print('---------------------------------------------------------\n')
        return '120'

    @tempo.setter
    def tempo(self, tempo):
        """
        グローバルBPMを上書きする
        """
        self.data[1].tempo = tempo
        self.data[2].tempo = tempo
        self.reload_tempo()

    def reload_tempo(self):
        """
        各ノートでBPMが取得できるように
        独自パラメータ note.alternative_tempo を全ノートに仕込む
        """
        current_tempo = self.tempo
        for note in self.notes:
            try:
                current_tempo = note.get_by_key('Tempo')
            except KeyError:
                pass
            note.alternative_tempo = float(current_tempo)

    def reload_tag_number(self):
        """
        各ノートのノート番号を振りなおす。
        ファイル出力時に実行することを想定。
        """
        for i, note in enumerate(self.notes):
            note.tag = f'[#{str(i).zfill(4)}]'

    # ノート一括編集系関数ここから----------------------------------------------
    def replace_lyrics(self, before, after):
        """歌詞を一括置換（文字列指定・破壊的処理）"""
        for note in self.notes:
            note.lyric = note.lyric.replace(before, after)

    def translate_lyrics(self, before, after):
        """歌詞を一括置換（複数文字指定・破壊的処理）"""
        for note in self.notes:
            note.lyric = note.lyric.translate(before, after)

    def vcv2cv(self):
        """歌詞を平仮名連続音から単独音にする"""
        for note in self.notes:
            note.lyric = note.lyric.split()[-1]
    # ノート一括編集系関数ここまで----------------------------------------------

    def insert_note(self, i):
        """
        i 番目の区切りに新規ノートを挿入する。
        このときの i は音符のみのインデックス。
        編集するために、挿入したノートを返す。
        """
        note = Note()
        note.tag = '[#INSERT]'
        self.notes.insert(i, note)
        return note

    def delete_note(self, i):
        """
        i 番目のノートを [#DELETE] する。
        """
        self.notes[i].tag = '[#DELETE]'

    def make_finalnote_R(self):
        """Ustの最後のノートが必ず休符 になるようにする"""
        note = self.data[-2]
        # Ust内の最後はTRACKENDなので後ろから2番目のノートで判定
        if note.lyric not in ('pau', 'sil', 'R'):
            print('  末尾に休符を自動追加しました。')
            extra_note = deepcopy(note)
            extra_note.lyric = 'R'
            extra_note.alternative_tempo = note.tempo
            self.insert(-1, extra_note)

    def write(self, path, mode='w', encoding='shift-jis'):
        """
        USTをファイル出力
        """
        duplicated_self = deepcopy(self)
        # [#DELETE] なノートをファイル出力しないために削除
        notes = [note for note in duplicated_self.notes if note.tag != '[#DELETE]']
        duplicated_self.notes = notes
        # ノート番号を振りなおす
        duplicated_self.reload_tag_number()
        # ノートのリストを文字列のリストに変換
        lines = []
        for note in duplicated_self:
            if note.tag == '[#VERSION]':
                lines.append('[#VERSION]')
                lines.append(note['UstVersion'])
                continue
            lines.append(note.pop('Tag'))
            for k, v in note.items():
                lines.append(f'{str(k)}={str(v)}')
        # 出力用の文字列
        s = '\n'.join(lines)
        # ファイル出力
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s


class Note(UserDict):
    """UST内のノート"""

    def __init__(self, tag='[#UNDEFINED]'):
        super().__init__()
        self['Tag'] = tag
        self.alternative_tempo = 120

    def __str__(self):
        lines = [self['Tag']] + [f'{k}={v}' for (k, v) in self.items() if k != 'Tag']
        return '\n'.join(lines)

    @property
    def values(self):
        """ノートの中身を見る"""
        return self.data

    @values.setter
    def values(self, d):
        """
        ノートの中身を上書き
        """
        if not isinstance(d, dict):
            raise TypeError('argument \"d\" must be dictionary instance')
        self.data = d

    @property
    def tag(self):
        """タグを確認"""
        return self['Tag']

    @tag.setter
    def tag(self, s):
        """タグを上書き"""
        self['Tag'] = s

    @property
    def length(self):
        """ノート長を確認[Ticks]"""
        return int(self['Length'])

    @length.setter
    def length(self, x):
        """ノート長を上書き[Ticks]"""
        self['Length'] = str(x)

    @property
    def length_ms(self):
        """ノート長を確認[ms]"""
        return 125 * float(self['Length']) / self.tempo

    @length_ms.setter
    def length_ms(self, x):
        """ノート長を上書き[ms]"""
        self['Length'] = x * self.tempo // 125

    @property
    def lyric(self):
        """歌詞を確認"""
        return self['Lyric']

    @lyric.setter
    def lyric(self, x):
        """歌詞を上書き"""
        self['Lyric'] = x

    @property
    def notenum(self):
        """音階番号を確認"""
        return int(self['NoteNum'])

    @notenum.setter
    def notenum(self, x):
        """音階番号を上書き"""
        self['NoteNum'] = str(x)

    @property
    def tempo(self):
        """ローカルBPMを取得"""
        try:
            return float(self['Tempo'])
        except KeyError:
            return float(self.alternative_tempo)

    @tempo.setter
    def tempo(self, x):
        """BPMを上書き"""
        self['Tempo'] = x

    @property
    def pbs(self):
        """
        PBS (mode2ピッチ開始位置[ms]) を取得
        例) PBS=-104;20.0
        """
        # 辞書には文字列で登録してある
        str_pbs = self['PBS']
        # 浮動小数のリストに変換
        list_pbs = list(map(float, re.split('[;,]', str_pbs)))
        # PBSの値をリストで返す
        return list_pbs

    @pbs.setter
    def pbs(self, list_pbs):
        """
        PBS (mode2ピッチ開始位置[ms]) を登録
        例) PBS=-104;20.0
        """
        s1 = f'{int(list_pbs[0])};'
        s2 = ','.join(map(str, list_pbs[1:]))

        str_pbs = s1 + s2
        self['PBS'] = str_pbs

    @property
    def pbw(self):
        """
        PBW (mode2ピッチ点の間隔[ms]) を取得
        例) PBW=77,163
        """
        # 辞書には文字列で登録してある
        s_pbw = self['PBW']
        # 整数のリストに変換
        l_pbw = list(map(int, s_pbw.split(',')))
        # PBWの値をリストで返す
        return l_pbw

    @pbw.setter
    def pbw(self, list_pbw):
        """
        PBW (mode2ピッチ点の間隔[ms]) を登録
        例) PBW=77,163
        """
        # リストを整数の文字列に変換
        str_pbw = ','.join(list(map(str, map(int, list_pbw))))
        self['PBW'] = str_pbw

    @property
    def pby(self):
        """
        PBY (mode2ピッチ点の高さ) を取得
        例) PBY=-10.6,0.0
        """
        # 辞書には文字列で登録してある
        s_pby = self['PBY']
        # 整数のリストに変換
        l_pby = list(map(float, s_pby.split(',')))
        # PBYの値をリストで返す
        return l_pby

    @pby.setter
    def pby(self, list_pby):
        """
        PBY (mode2ピッチ点の高さ) を登録
        例) PBY=-10.6,0.0
        """
        # リストを小数の文字列に変換
        str_pby = ','.join(list(map(str, map(float, list_pby))))
        self['PBY'] = str_pby

    @property
    def pbm(self):
        """
        PBM (mode2ピッチ点の形状) を取得
        例) PBY=-10.6,0.0
        """
        # 辞書には文字列で登録してある
        s_pby = self['PBM']
        # 整数のリストに変換
        l_pbm = s_pby.split(',')
        # PBYの値をリストで返す
        return l_pbm

    @pbm.setter
    def pbm(self, list_pbm):
        """
        PBM (mode2ピッチ点の形状) を登録
        例) PBM=,r,j,s
        """
        # リストを文字列に変換
        str_pbm = ','.join(list_pbm)
        self['PBM'] = str_pbm

    # ここからデータ操作系-----------------------------------------------------
    def get_by_key(self, key):
        """ノートの特定の情報を上書きまたは登録"""
        return self[key]

    def set_by_key(self, key, x):
        """ノートの特定の情報を上書きまたは登録"""
        self[key] = x
    # ここまでデータ操作系-----------------------------------------------------

    # ここからノート操作系-----------------------------------------------------
    def delete(self):
        """選択ノートを削除"""
        self.tag = '[#DELETE]'
        return self

    # def insert(self):
    #     """ノートを挿入(したい)"""
    #     self.tag = '[#INSERT]'
    #     return self

    def refresh(self):
        """
        ノートの情報を引き継ぎつつ、自由にいじれるようにする
        UTAUプラグインは値の上書きはできるが削除はできない。
        一旦ノートを削除して新規ノートとして扱う必要がある。
        """
        self.tag = '[#DELETE]\n[#INSERT]'

    def suppin(self):
        """ノートの情報を最小限にする"""
        new_note = {}
        new_note['Tag'] = '[#DELETE]\n[#INSERT]'
        new_note['Lyric'] = self.lyric
        new_note['Length'] = self.length
        new_note['NoteNum'] = self.notenum
        self.data = new_note
    # ここまでノート操作系-----------------------------------------------------

    # ここからデータ出力系-----------------------------------------------------
    # Ustのほうで処理するようにしたので無効化しています。
    # -------------------------------------------------------------------------
    # def as_lines(self):
    #     """出力用のリストを返す"""
    #     d = self
    #     lines = []
    #     lines.append(d.pop('Tag'))
    #     for k, v in d.items():
    #         line = '{}={}'.format(str(k), str(v))
    #         lines.append(line)
    #     return lines
    # ここまでデータ出力系-----------------------------------------------------


if __name__ == '__main__':
    main()
