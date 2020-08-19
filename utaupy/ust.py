#!python3
# coding: utf-8
"""
USTファイルとデータを扱うモジュールです。
"""
import re
from copy import deepcopy


def main():
    """実行されたときの挙動"""
    print('デフォ子かわいいよデフォ子\n')

    print('ust読み取りテストをします。')
    path = input('ustのパスを入力してください。\n>>> ')
    ust = load(path)
    print()

    for note in ust.values:
        print(note.values)

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
    """USTを読み取り"""
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
    notes = []
    for lines in l:
        note = Note()
        # ノートの種類
        tag = lines[0]
        note.tag = tag
        # print('Making "Note" instance from UST: {}'.format(tag))
        # タグ以外の行の処理
        if tag == '[#VERSION]':
            note.set_by_key('Version', lines[1])
        elif tag == '[#TRACKEND]':
            pass
        else:
            for line in lines[1:]:
                key, value = line.split('=', 1)
                note.set_by_key(key, value)
        notes.append(note)

    # 旧形式の場合にタグの数を合わせる
    if notes[0].tag != r'[#VERSION]':
        version = notes[0].get_by_key('UstVersion')
        note = Note()
        note.tag = '[#VERSION]'
        note.set_by_key('UstVersion', version)
        notes.insert(0, note)  # リスト先頭に挿入
    # Ustクラスオブジェクト化
    u = Ust()
    u.values = notes
    u.version = notes[0]
    u.setting = notes[1]
    # 隠しパラメータ alternative_tempo を全ノートに設定
    u.reload_tempo()
    return u


class Ust:
    """UST"""

    def __init__(self):
        """インスタンス作成"""
        # ノート(クラスオブジェクト)からなるリスト
        self._notes = []
        self.version = None
        self.setting = None

    def __len__(self):
        return len(self._notes)

    @property
    def values(self):
        """中身を見る"""
        return self._notes

    @values.setter
    def values(self, l):
        """
        中身を上書きする
        テンポを正常に取得できるようにする
        """
        if not isinstance(l, list):
            raise TypeError('argument \"l\" must be list instance')
        self._notes = l
        self.reload_tempo()
        return self

    @property
    def notes(self):
        """
        全セクションのうち、VERSION と SETTING TRACKEND を除いたノート部分を取得
        """
        return self._notes[2:-1]

    @notes.setter
    def notes(self, l):
        """
        全セクションのうち、VERSION と SETTING TRACKEND を除いたノート部分を上書き
        """
        if not isinstance(l, list):
            raise TypeError('argument \"l\" must be list instance')
        self._notes = self._notes[:2] + l + self._notes[-1:]
        self.reload_tempo()
        return self

    @property
    def tempo(self):
        """全体のBPMを見る"""
        try:
            project_tempo = self._notes[1].tempo
            return project_tempo
        except KeyError:
            first_note_tempo = self._notes[2].tempo
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
        self._notes[1].tempo = tempo
        self._notes[2].tempo = tempo
        self.reload_tempo()

    def reload_tempo(self):
        """
        各ノートでBPMが取得できるように
        独自パラメータ note.alternative_tempo を全ノートに仕込む
        """
        current_tempo = self.tempo
        for note in self._notes[2:-1]:
            try:
                current_tempo = note.get_by_key('Tempo')
            except KeyError:
                pass
            note.alternative_tempo = float(current_tempo)

    # ノート一括編集系関数ここから----------------------------------------------
    def replace_lyrics(self, before, after):
        """歌詞を一括置換（文字列指定・破壊的処理）"""
        for note in self._notes[2:-1]:
            note.lyric = note.lyric.replace(before, after)

    def translate_lyrics(self, before, after):
        """歌詞を一括置換（複数文字指定・破壊的処理）"""
        for note in self._notes[2:-1]:
            note.lyric = note.lyric.translate(before, after)

    def vcv2cv(self):
        """歌詞を平仮名連続音から単独音にする"""
        for note in self._notes[2:-1]:
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
        note = self._notes[-2]
        # Ust内の最後はTRACKENDなので後ろから2番目のノートで判定
        if note.lyric not in ('pau', 'sil', 'R'):
            print('  末尾に休符を自動追加しました。')
            extra_note = deepcopy(note)
            extra_note.lyric = 'R'
            extra_note.alternative_tempo = note.tempo
            self._notes.insert(-1, extra_note)

    def write(self, path, mode='w', encoding='shift-jis'):
        """
        USTをファイル出力
        """
        lines = []
        for note in self._notes:
            # ノートを解体して行のリストにする
            d = note.values
            # DEBUG: popするせいでwriteのあとにTagを取得できなくなる
            lines.append(d.pop('Tag'))
            for k, v in d.items():
                lines.append('{}={}'.format(str(k), str(v)))
        # 出力用の文字列
        s = '\n'.join(lines)
        # ファイル出力
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s


class Note:
    """UST内のノート"""

    def __init__(self):
        self.__d = {}
        self.tag = '[#UNDEFINED]'
        self.lyric = None
        self.alternative_tempo = None

    def __str__(self):
        return f'{self.tag} {self.lyric}\t<utaupy.ust.Note object>'

    @property
    def values(self):
        """ノートの中身を見る"""
        return self.__d

    @values.setter
    def values(self, d):
        """
        ノートの中身を上書き
        """
        if not isinstance(d, dict):
            raise TypeError('argument \"d\" must be dictionary instance')
        self.__d = d

    @property
    def tag(self):
        """タグを確認"""
        return self.__d['Tag']

    @tag.setter
    def tag(self, s):
        """タグを上書き"""
        self.__d['Tag'] = s

    @property
    def length(self):
        """ノート長を確認[Ticks]"""
        return int(self.__d['Length'])

    @length.setter
    def length(self, x):
        """ノート長を上書き[Ticks]"""
        self.__d['Length'] = str(x)

    @property
    def length_ms(self):
        """ノート長を確認[ms]"""
        return 125 * float(self.__d['Length']) / self.tempo

    @length_ms.setter
    def length_ms(self, x):
        """ノート長を上書き[ms]"""
        self.__d['Length'] = x * self.tempo // 125

    @property
    def lyric(self):
        """歌詞を確認"""
        return self.__d['Lyric']

    @lyric.setter
    def lyric(self, x):
        """歌詞を上書き"""
        self.__d['Lyric'] = x

    @property
    def notenum(self):
        """音階番号を確認"""
        return int(self.__d['NoteNum'])

    @notenum.setter
    def notenum(self, x):
        """音階番号を上書き"""
        self.__d['NoteNum'] = str(x)

    @property
    def tempo(self):
        """ローカルBPMを取得"""
        try:
            return float(self.__d['Tempo'])
        except KeyError:
            return float(self.alternative_tempo)

    @tempo.setter
    def tempo(self, x):
        """BPMを上書き"""
        self.__d['Tempo'] = x

    @property
    def pbs(self):
        """
        PBS (mode2ピッチ開始位置[ms]) を取得
        例) PBS=-104;20.0
        """
        # 辞書には文字列で登録してある
        str_pbs = self.__d['PBS']
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
        self.__d['PBS'] = str_pbs

    @property
    def pbw(self):
        """
        PBW (mode2ピッチ点の間隔[ms]) を取得
        例) PBW=77,163
        """
        # 辞書には文字列で登録してある
        s_pbw = self.__d['PBW']
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
        self.__d['PBW'] = str_pbw

    @property
    def pby(self):
        """
        PBY (mode2ピッチ点の高さ) を取得
        例) PBY=-10.6,0.0
        """
        # 辞書には文字列で登録してある
        s_pby = self.__d['PBY']
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
        self.__d['PBY'] = str_pby

    @property
    def pbm(self):
        """
        PBM (mode2ピッチ点の形状) を取得
        例) PBY=-10.6,0.0
        """
        # 辞書には文字列で登録してある
        s_pby = self.__d['PBM']
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
        self.__d['PBM'] = str_pbm

    # ここからデータ操作系-----------------------------------------------------
    def get_by_key(self, key):
        """ノートの特定の情報を上書きまたは登録"""
        return self.__d[key]

    def set_by_key(self, key, x):
        """ノートの特定の情報を上書きまたは登録"""
        self.__d[key] = x
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
        self.__d = new_note
    # ここまでノート操作系-----------------------------------------------------

    # ここからデータ出力系-----------------------------------------------------
    # Ustのほうで処理するようにしたので無効化しています。
    # -------------------------------------------------------------------------
    # def as_lines(self):
    #     """出力用のリストを返す"""
    #     d = self.__d
    #     lines = []
    #     lines.append(d.pop('Tag'))
    #     for k, v in d.items():
    #         line = '{}={}'.format(str(k), str(v))
    #         lines.append(line)
    #     return lines
    # ここまでデータ出力系-----------------------------------------------------


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass
