#!/usr/bin/env python3
# coding: utf-8
"""
USTファイルとデータを扱うモジュールです。
"""


def main():
    """実行されたときの挙動"""
    print('デフォ子かわいいよデフォ子')


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
    # さらに行ごとに分割
    l = [v.split('\n') for v in l]

    # ノートのリストを作る
    notes = []
    for lines in l:
        note = Note()
        note.from_ust(lines)
        notes.append(note)
    # 旧形式の場合にタグの数を合わせる
    if notes[0].tag != r'[#VERSION]':
        ust_version = notes[0].by_key('UstVersion')
        note = Note()
        note.tag = r'[#VERSION]'
        note.set_by_key('UstVersion', ust_version)
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
            lines.append(d.pop('Tag'))
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
        self.d = {'Tag': None}

    # ここからデータ入力系-----------------------------------------------------
    def from_ust(self, lines):
        """USTの一部からノートを生成"""
        # ノートの種類
        tag = lines[0]
        self.d['Tag'] = tag
        # print('Making "Note" instance from UST: {}'.format(tag))
        # タグ以外の行の処理
        if tag == '[#VERSION]':
            self.d['UstVersion'] = lines[1]
        elif tag == '[#TRACKEND]':
            pass
        else:
            for v in lines[1:]:
                tmp = v.split('=', 1)
                self.d[tmp[0]] = tmp[1]
        return self
    # ここまでデータ入力系-----------------------------------------------------

    # ここからデータ参照系-----------------------------------------------------
    @property
    def values(self):
        """ノートの中身を見る"""
        return self.d

    @property
    def tag(self):
        """タグを確認"""
        return self.d['Tag']

    @property
    def length(self):
        """ノート長を確認[samples]"""
        return self.d['Length']

    @property
    def lyric(self):
        """歌詞を確認"""
        return self.d['Lyric']

    @property
    def notenum(self):
        """音階番号を確認"""
        return self.d['NoteNum']

    @property
    def tempo(self):
        """BPMを確認"""
        return self.d['Tempo']
    # ここまでgetter-----------------------------------------------------

    # ここからsetter-----------------------------------------------------
    @values.setter
    def values(self, d):
        """ノートの中身を上書き"""
        self.d = d

    @tag.setter
    def tag(self, s):
        """タグを上書き"""
        self.d['Tag'] = s

    @length.setter
    def length(self, x):
        """ノート長を上書き[samples]"""
        self.d['Length'] = x

    @lyric.setter
    def lyric(self, x):
        """歌詞を上書き"""
        self.d['Lyric'] = x

    @notenum.setter
    def notenum(self, x):
        """音階番号を上書き"""
        self.d['NoteNum'] = x

    @tempo.setter
    def tempo(self, x):
        """BPMを上書き"""
        self.d['Tempo'] = x
    # ここまでデータ上書き系-----------------------------------------------------

    # ここからデータ操作系-----------------------------------------------------
    # NOTE: msで長さ操作する二つ、テンポ取得を自動にしていい感じにしたい。

    def set_by_key(self, key, x):
        """ノートの特定の情報を上書きまたは登録"""
        self.d[key] = x

    def get_length_ms(self, tempo):
        """ノート長を確認[ms]"""
        return 125 * float(self.d['Length']) / float(tempo)

    def set_length_ms(self, x, tempo):
        """ノート長を上書き[ms]"""
        self.d['Length'] = x * tempo // 125
    # ここまでデータ操作系-----------------------------------------------------

    # ここからノート操作系-----------------------------------------------------
    def delete(self):
        """選択ノートを削除"""
        self.d['Tag'] = '[#DELETE]'
        return self

    def insert(self):
        """ノートを挿入(したい)"""
        self.d['Tag'] = '[#INSERT]'
        return self
    # ここまでノート操作系-----------------------------------------------------

    # ここからデータ出力系-----------------------------------------------------
    # Ustのほうで処理するようにしたので無効化しています。
    # -------------------------------------------------------------------------
    # def as_lines(self):
    #     """出力用のリストを返す"""
    #     d = self.d
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
