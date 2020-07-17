#!python3
# coding: utf-8
"""
USTファイルとデータを扱うモジュールです。
"""


def main():
    """実行されたときの挙動"""
    print('デフォ子かわいいよデフォ子')


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
    elif isinstance(notenum, int):
        return d[str(notenum)]
    elif isinstance(notenum, (list, tuple)):
        return [d[str(v)] for v in notenum]
    else:
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
        note.from_ust(lines)
        notes.append(note)
    # 旧形式の場合にタグの数を合わせる
    if notes[0].section != r'[#VERSION]':
        version = notes[0].get_by_key('UstVersion')
        note = Note()
        note.section = '[#VERSION]'
        note.set_by_key('UstVersion', version)
        notes.insert(0, note)  # リスト先頭に挿入
    # Ustクラスオブジェクト化
    u = Ust()
    u.values = notes
    return u


class Ust:
    """UST"""

    def __init__(self):
        """インスタンス作成"""
        # ノート(クラスオブジェクト)からなるリスト
        self.notes = []

    @property
    def values(self):
        """中身を見る"""
        return self.notes

    @values.setter
    def values(self, l):
        """中身を上書きする"""
        self.notes = l
        return self

    @property
    def tempo(self):
        """全体のBPMを見る"""
        try:
            project_tempo = self.notes[1].tempo
            return project_tempo
        except KeyError:
            first_note_tempo = self.notes[2].tempo
            return first_note_tempo

        print('\n[ERROR]--------------------------------------------------')
        print('USTのテンポが設定されていません。とりあえず120にします。')
        print('---------------------------------------------------------\n')
        return '120'

    # NOTE: deepcopyすれば非破壊的処理にできそう。
    def replace_lyrics(self, before, after):
        """歌詞を置換（文字列指定・破壊的処理）"""
        for note in self.notes[2:-1]:
            note.lyric = note.lyric.replace(before, after)

    # NOTE: deepcopyすれば非破壊的処理にできそう。
    def translate_lyrics(self, before, after):
        """歌詞を置換（複数文字指定・破壊的処理）"""
        for note in self.notes[2:]:
            note.lyric = note.lyric.translate(before, after)

    def vcv2cv(self):
        """歌詞を平仮名連続音から単独音にする"""
        for note in self.notes[2:]:
            note.lyric = note.lyric.split()[-1]

    def write(self, path, mode='w', encoding='shift-jis'):
        """USTを保存"""
        lines = []
        for note in self.notes:
            # ノートを解体して行のリストにする
            d = note.values
            lines = []
            lines.append(d.pop('Section'))
            for k, v in d.items():
                line = '{}={}'.format(str(k), str(v))
                lines.append(line)
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
        self.section = None

    # ここからデータ入力系-----------------------------------------------------
    def from_ust(self, lines):
        """USTの一部からノートを生成"""
        # ノートの種類
        section = lines[0]
        self.section = section
        # print('Making "Note" instance from UST: {}'.format(section))
        # タグ以外の行の処理
        if section == '[#VERSION]':
            self.__d['Version'] = lines[1]
        elif section == '[#TRACKEND]':
            pass
        else:
            for v in lines[1:]:
                tmp = v.split('=', 1)
                self.__d[tmp[0]] = tmp[1]
        return self
    # ここまでデータ入力系-----------------------------------------------------

    @property
    def values(self):
        """ノートの中身を見る"""
        return self.__d

    @values.setter
    def values(self, d):
        """ノートの中身を上書き"""
        self.__d = d

    @property
    def section(self):
        """タグを確認"""
        return self.__d['Section']

    @section.setter
    def section(self, s):
        """タグを上書き"""
        self.__d['Section'] = s

    @property
    def length(self):
        """ノート長を確認[samples]"""
        return self.__d['Length']

    @length.setter
    def length(self, x):
        """ノート長を上書き[samples]"""
        self.__d['Length'] = x

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
        return self.__d['NoteNum']

    @notenum.setter
    def notenum(self, x):
        """音階番号を上書き"""
        self.__d['NoteNum'] = x

    @property
    def tempo(self):
        """BPMを確認"""
        return self.__d['Tempo']

    @tempo.setter
    def tempo(self, x):
        """BPMを上書き"""
        self.__d['Tempo'] = x

    # ここからデータ操作系-----------------------------------------------------
    # NOTE: msで長さ操作する二つ、テンポ取得を自動にしていい感じにしたい。
    def get_by_key(self, key):
        """ノートの特定の情報を上書きまたは登録"""
        try:
            return self.__d[key]
        except KeyError as e:
            print('KeyError Exception in get_by_key in ust.py : {}'.format(e))
            return None

    def set_by_key(self, key, x):
        """ノートの特定の情報を上書きまたは登録"""
        self.__d[key] = x

    def get_length_ms(self, tempo):
        """ノート長を確認[ms]"""
        return 125 * float(self.__d['Length']) / float(tempo)

    def set_length_ms(self, x, tempo):
        """ノート長を上書き[ms]"""
        self.__d['Length'] = x * tempo // 125
    # ここまでデータ操作系-----------------------------------------------------

    # ここからノート操作系-----------------------------------------------------
    def delete(self):
        """選択ノートを削除"""
        self.section = '[#DELETE]'
        return self

    def insert(self):
        """ノートを挿入(したい)"""
        self.section = '[#INSERT]'
        return self

    def refresh(self):
        """
        ノートの情報を引き継ぎつつ、自由にいじれるようにする
        UTAUプラグインは値の上書きはできるが削除はできない。
        一旦ノートを削除して新規ノートとして扱う必要がある。
        """
        self.section = '[#DELETE]\n[#INSERT]'

    def suppin(self):
        """ノートの情報を最小限にする"""
        new_note = {}
        new_note['Section'] = '[#DELETE]\n[#INSERT]'
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
    #     lines.append(d.pop('Section'))
    #     for k, v in d.items():
    #         line = '{}={}'.format(str(k), str(v))
    #         lines.append(line)
    #     return lines
    # ここまでデータ出力系-----------------------------------------------------


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass
