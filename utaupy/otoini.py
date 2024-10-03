#! /usr/bin/env python3
# coding: utf-8
"""
setParam用のINIファイルとデータを扱うモジュールです。
"""
import re
import os
import sys
import csv
from collections import UserList
from utils._trie import Trie

# TODO: setParam用のコメントファイルを扱えるようにする。


def main():
    """
    直接実行されたときの挙動
    """
    print('耳ロボPとsetParamに卍感謝卍')


def load(path, mode='r', encoding='cp932'):
    """
    otoiniを読み取ってオブジェクト生成
    """
    # otoiniファイルを読み取る
    path = path.strip('"')
    with open(path, mode=mode, encoding=encoding) as f:
        lines = [line.strip() for line in f.readlines()]

    # Otoクラスオブジェクトのリストを作る
    otoini = OtoIni()
    for line in lines:
        params = re.split('[=,]', line.strip())
        params = params[:2] + [float(v) for v in params[2:]]
        oto = Oto()
        (oto.filename, oto.alias, oto.offset, oto.consonant,
         oto.cutoff, oto.preutterance, oto.overlap) = params
        otoini.append(oto)
    return otoini


def read_in_param(key=None):
    """
    inParam.txtを読み込む。

    Reference:
        setParam.exeのあるフォルダ > plugins > README.txt

    Example of Use:
        from utaupy.otoini import load, read_in_param, OtoIni # インポート
        path = read_in_param("oto_sp_path") # パス取得
        otoini = load(path) # 原音設定を読み込む
        otoing = OtoIni(otoini) # インスタンス化
        otoing.round_param(1) # 原音設定を編集(例: 小数点以下1桁で四捨五入)
        otoing.write(path) # 原音設定を保存
    """
    # inParam.txtを探す
    cur_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    par_dir = os.path.dirname(cur_dir)
    in_param_path = os.path.join(par_dir, 'inParam.txt')

    # inParam.txtを読み込む
    with open(in_param_path, 'r', encoding='cp932') as f:
        lines = [line.strip() for line in f.readlines()]
    vb_dir = lines[0]
    oto_sp_path = lines[1]
    f0_interval = float(lines[2])
    power_interval = float(lines[3])
    view_rows = int(lines[4])
    select_rows_str = lines[5]
    select_rows = (
        list(map(int, select_rows_str.split(',')))
        if ',' in select_rows_str
        else int(select_rows_str))

    # inParam.txtのパスを元に、残りのパスを取得
    oto_ini_path = os.path.join(vb_dir, 'oto.ini')
    comment_txt_path = os.path.join(vb_dir, 'oto-comment.txt')
    comment_sp_path = os.path.join(vb_dir, 'oto-autoEstimation-comment.txt')

    settings = {}
    settings = {
        'cur_dir': cur_dir,  # プラグイン本体の保存フォルダのパス
        'vb_dir': vb_dir,  # 処理対象の音源フォルダの絶対パス
        'oto_sp_path': oto_sp_path,  # 更新用の原音設定の絶対パス(ここから読み、ここに保存すること)
        'oto_ini_path': oto_ini_path,  # 原音設定の絶対パス
        'f0_interval': f0_interval,  # F0の抽出間隔(単位=秒)
        'power_interval': power_interval,  # パワーの抽出間隔(単位=秒)
        'view_rows': view_rows,  # setParamの波形窓で現在表示しているデータの行番号
        'select_rows': select_rows,  # setParamのパラメータ一覧表で現在選択しているセルの行番号
        'comment_sp_path': comment_sp_path,  # 更新用のsetParam用コメントテキストのパス
        'comment_txt_path': comment_txt_path,  # setParam用コメントテキストのパス
    }
    if key:
        return settings.get(key, None)
    return settings


def load_sp():
    """
    setParamプラグインの汎用的な初期設定を行う。

    Example of Use:
        from utaupy.otoini import load_sp  # インポート
        path, otoing = load_sp()  # 原音設定を読み込む、OtoIniのインスタンス化
        otoing.round_param(1):  # 原音設定を編集(例: 小数点以下1桁で四捨五入)
        otoing.write(path)  # 原音設定を保存
    """
    path = read_in_param("oto_sp_path")
    otoini = load(path)
    otoing = OtoIni(otoini)
    return path, otoing


class OtoIni(UserList):
    """
    oto.iniを想定したクラス
    """

    def replace_aliases(self, before, after):
        """
        エイリアスを置換する
        """
        for oto in self:
            oto.alias = oto.alias.replace(before, after)
        return self

    def _apply_regex(self, func, *args, pattern=None):
        """
        エイリアスが正規表現に完全一致したら、その行で関数を実行する。

        Parameters:
            func(function): 対象行に実行する関数名。
            *args(Tuple): funcの引数。複数可能。
            pattern(str): 対象行の正規表現のパターン。完全一致。省略時は全行に実行。
        """
        # 正規表現がNone以外なら、エイリアスが完全一致した行で実行
        if pattern is not None:
            regex = re.compile(rf"{pattern}")
            for oto in self:
                if regex.fullmatch(oto.alias):
                    func(oto, *args)

        # 正規表現がNoneなら、全行で実行
        else:
            for oto in self:
                func(oto, *args)
        return self

    def replace_regexp_alias(self, before, after=None, pattern=None):
        """
        エイリアスを置換する。(正規表現対応)

        Parameters:
            before(str): 置換する文字列。
            after(str): 置換後の文字列。省略時は空文字。
            pattern(str): 対象行の正規表現のパターン。完全一致。省略時は全行に実行。
        """
        # 入力を取得 or デフォルト値を設定
        before = str(before or "")
        after = str(after or "")

        # 一致した行 or 全行で置換
        def replace_func(oto, before, after):
            oto.alias = oto.alias.replace(before, after)
        return self._apply_regex(replace_func, before, after, pattern=pattern)

    def add_alias(self, prefix=None, suffix=None, pattern=None):
        """
        エイリアスに接頭辞と接尾辞を追加する。

        Parameters:
            prefix(str): 追加する接頭辞。省略時は追加しない。
            suffix(str): 追加する接尾辞。省略時は追加しない。
            pattern(str): 対象行の正規表現のパターン。完全一致。省略時は全行に実行。
        """
        # 入力を取得 or デフォルト値を設定
        prefix = str(prefix or "")
        suffix = str(suffix or "")

        # 一致した行 or 全行に追加
        def add_alias_func(oto):
            oto.alias = (prefix or "") + oto.alias + (suffix or "")
        return self._apply_regex(add_alias_func, pattern=pattern)

    def trim_alias(self, prefix_len=None, suffix_len=None, pattern=None):
        """
        エイリアスの前後から指定した文字数を削除する。

        Parameters:
            prefix(int): 語頭から削除する桁数。省略時は削除しない。
            suffix(int): 語尾から削除する桁数。省略時は削除しない。
            pattern(str): 対象行の正規表現のパターン。完全一致。省略時は全行に実行。
        """
        # 入力を整数として取得 or デフォルト値を設定
        prefix_len = int(prefix_len or 0)
        suffix_len = int(suffix_len or 0)

        # 一致した行 or 全行から削除
        def trim_func(oto):
            oto.alias = oto.alias[prefix_len:len(oto.alias)-suffix_len]
        return self._apply_regex(trim_func, pattern=pattern)

    def remove_duplicate(self):
        """
        エイリアスが重複している行を削除する。対象は全行。
        """
        seen_aliases = set()
        unique_otoini = []
        for oto in self:
            if oto.alias not in seen_aliases:
                unique_otoini.append(oto)
                seen_aliases.add(oto.alias)
        self.data = unique_otoini

    def copy_rename(self, before, after):
        """
        エイリアスを複製 & リネームする。
        エイリアスにbeforeがあり、afterがない場合、
        beforeの行を複製して、afterにリネームする。
        正規表現「[^ぁ-んァ-ヶ]*$」は接尾辞を想定。

        Parameters:
            prefix(str): 複製前のエイリアス。
            suffix(str): 複製後のエイリアス。
        """
        # 入力を取得してコンパイル
        before_regex = re.compile(rf"^{str(before)}[^ぁ-んァ-ヶ]*$")
        after_regex = re.compile(rf"^{str(after)}[^ぁ-んァ-ヶ]*$")

        # 条件に一致した行を複製 & リネーム
        for oto in self:
            if before_regex.fullmatch(oto.alias) and not any(
                after_regex.fullmatch(oto_after.alias) for oto_after in self
            ):
                new_oto = Oto()
                new_oto.filename = oto.filename
                new_oto.alias = after
                new_oto.offset = oto.offset
                new_oto.consonant = oto.consonant
                new_oto.cutoff = oto.cutoff
                new_oto.preutterance = oto.preutterance
                new_oto.overlap = oto.overlap
                self.append(new_oto)
                break
        return self

    def copy_rename_csv(self, csv_path):
        """
        エイリアス複製さん向けの複製規則.iniを読み込み、
        各行の「before,after」を元にcopy_renameを実行する。

        Parameters:
            csv_path(str): 複製規則.iniのパス。csv形式。
        """
        with open(csv_path, newline='', encoding='cp932') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if len(row) == 2:
                    before, after = row
                    self.copy_rename(before, after)
                else:
                    continue
        return self

    def round_param(self, digits=None, pattern=None):
        """
        小数点以下の桁数を指定して四捨五入する。

        Parameters:
            digits(int): 小数点以下の桁数。省略時は3桁。
            pattern(str): 対象行の正規表現のパターン。完全一致。省略時は全行に実行。
        """
        # 入力を整数として取得 or デフォルト値を設定
        digits = int(digits or 3)

        # 一致した行 or 全行で四捨五入
        def round_param_func(oto):
            oto.offset = round(oto.offset, digits)
            oto.consonant = round(oto.consonant, digits)
            oto.cutoff = round(oto.cutoff, digits)
            oto.preutterance = round(oto.preutterance, digits)
            oto.overlap = round(oto.overlap, digits)
        return self._apply_regex(round_param_func, pattern=pattern)

    def overlap_1_3(self, value=None, fixed=None, pattern=None):
        """
        オーバーラップを先行発声の1/3にする。

        Parameters:
            value(float): 先行発声。または収録BPM。
            fixed(bool): Trueではvalue=先行発声、それ以外ではvalue=収録BPMとして受け取る。
            pattern(str): 対象行の正規表現のパターン。完全一致。省略時は全行に実行。
        """
        if fixed is True:
            # 先行発声を入力したとき
            new_preutterance = float(value or 250)
            new_overlap = new_preutterance / 3
        else:
            # 収録BPMを入力したとき
            bpm = float(value or 120)
            new_preutterance = (60000 / bpm) / 2
            new_overlap = new_preutterance / 3

        # 一致した行 or 全行で計算
        def overlap_1_3_func(oto):
            moving_value = oto.preutterance - new_preutterance
            oto.offset = oto.offset + moving_value
            oto.preutterance = new_preutterance
            oto.overlap = new_overlap
            oto.consonant -= moving_value
            if oto.cutoff < 0:
                oto.cutoff += moving_value
            else:
                oto.cutoff = oto.cutoff

        return self._apply_regex(overlap_1_3_func, pattern=pattern)

    def convert_vcv(self, bpm=None, pattern=None):
        """
        収録BPMから連続音パラメータを求めて適用する。

        Parameters:
            bpm(float): 収録BPM。省略時は120。
            pattern(str): 対象行の正規表現のパターン。完全一致。省略時は全行に実行。

        Example of Pattern:
            ローマ字: "^[aiueon] ([aiueoN]{1}|[a-z]{1,2}[aiueo]).*$"
            ひらがなカタカナ: "^[aiueon] [ぁ-んァ-ヶ]+[ぁ-んァ-ヶ]*$"
            ALL:
            "^[aiueon] ([ぁ-んァ-ヶ]+|[aiueoN]{1}|[a-z]{1,2}[aiueo])[^ぁ-んァ-ヶ]*$"
        """
        # 入力を浮動小数点数として取得 or デフォルト値を設定
        bpm = float(bpm or 120)

        # 収録BPMから計算
        note_4th = 60000 / bpm
        new_preutterance = note_4th / 2
        new_overlap = new_preutterance / 3
        new_consonant = new_preutterance * 1.5
        new_cutoff = (note_4th + new_overlap) * -1

        # 一致した行 or 全行で計算
        def convert_vcv_func(oto):
            oto.offset = oto.offset + oto.preutterance - new_preutterance
            oto.consonant = new_consonant
            oto.cutoff = new_cutoff
            oto.preutterance = new_preutterance
            oto.overlap = new_overlap
        return self._apply_regex(convert_vcv_func, pattern=pattern)

    def convert_cv(self, bpm=None, pattern=None):
        """
        収録BPMから単独音パラメータを求めて適用する。

        Parameters:
            bpm(float): 収録BPM。省略時は120。
            pattern(str): 対象行の正規表現のパターン。完全一致。
            省略時は、ひらがなと一部のカタカナの単独音が対象。
            単独音にあたる部分が1回目の()になっていれば、他の正規表現でも可能。

        Example of Pattern:
            ローマ字: "^[- ]*([aiueoN]{1}|[a-z]{1,2}[aiueo]).*$"
            ひらがなカタカナ: "^[- ]*([ぁ-んァ-ヶ]+)[ぁ-んァ-ヶ]*$"
            ALL: "^[- ]*([ぁ-んァ-ヶ]+|[aiueoN]{1}|[a-z]{1,2}[aiueo])[^ぁ-んァ-ヶ]*$"
        """
        # 入力を取得 or デフォルト値を設定
        bpm = float(bpm or 120)
        new_consonant = (60000 / bpm) * 0.75
        regex = re.compile(rf"{pattern}" or (r"^[- ]*([ぁ-んァ-ヶ]+)[ぁ-んァ-ヶ]*$"))

        # 単独音の辞書を作成
        cv_dict = create_cv_dict()

        # 1行ずつ適用
        for oto in self.data:
            # 原音設定が正規表現に一致しなければ次の行へ
            match = regex.match(oto.alias)
            if not match:
                continue

            # 辞書に正規表現の()が一致しなければ次の行へ
            cv_key = match.group(1)
            params = cv_dict.search(cv_key)
            if not params:
                continue

            # 一致した行でパラメータを計算
            new_preutterance = params.get('cv_pre')
            moving_value = oto.preutterance - new_preutterance
            oto.offset += moving_value
            oto.preutterance = new_preutterance
            oto.overlap = params.get('cv_ovl')
            oto.consonant = new_consonant - moving_value
            if oto.cutoff < 0:
                oto.cutoff += moving_value  # マイナス値のcutoffは、offsetと連動して動く
            else:
                oto.cutoff = oto.cutoff  # プラス値のcutoffは、offsetが動いても変わらない
        return self

    def set_cv_vcv(self, bpm=None, cv_pattern=None, vcv_pattern=None):
        """
        単独音パラメータと連続音パラメータを適用する。

        Parameters:
            bpm(float): 収録BPM。省略時は120。
            cv_pattern(str): 単独音パラメータ対象行の正規表現のパターン。完全一致。
            vcv_pattern(str): 連続音パラメータ対象行の正規表現のパターン。完全一致。
            pattern省略時は、「- あ」を単独音、「a あ」を連続音とする。
        """
        # 連続音 (連続音パラメータ) , 単独音のcutoffもマイナスで統一
        vcv_pattern = vcv_pattern or ("^[-aiueon] [ぁ-んァ-ヶ]+[ぁ-んァ-ヶ]*$")
        self.convert_vcv(bpm=bpm, pattern=vcv_pattern)
        # 連続音歌いだし (単独音パラメータ)
        cv_pattern = cv_pattern or ("^- *([ぁ-んァ-ヶ]+)[^ぁ-んァ-ヶ]*$")
        self.convert_cv(bpm=bpm, pattern=cv_pattern)
        return self

    def is_mono(self):
        """
        モノフォン形式のエイリアスになっているか判定する。
        すべてのエイリアスに空白がなければモノフォンと判断する。
        返り値はbool。
        """
        return all((' ' not in oto.alias) for oto in self)

    def monophonize(self):
        """
        音素ごとに分割する。
        otoini→label 変換の用途を想定
        音素の発声開始位置: 左ブランク=先行発声
        """
        # 新規OtoIniを作るために、otoを入れるリスト
        mono_otoini = OtoIni()
        for oto in self:
            phonemes = oto.alias.split()
            if len(phonemes) == 1:
                mono_otoini.append(oto)
            elif len(phonemes) in [2, 3]:
                name_wav = oto.filename
                # 1文字目(オーバーラップから先行発声まで)------------
                mono_oto = Oto()
                mono_oto.filename = name_wav
                mono_oto.alias = phonemes[0]
                mono_oto.offset = oto.offset + oto.overlap  # オーバーラップの位置に左ブランクを移動
                mono_oto.preutterance = 0
                mono_otoini.append(mono_oto)
                # 2文字目(先行発声から固定範囲まで)----------------
                mono_oto = Oto()
                mono_oto.filename = name_wav
                mono_oto.alias = phonemes[1]
                mono_oto.offset = oto.offset + oto.preutterance  # 先行発声の位置に左ブランクを移動
                mono_oto.preutterance = 0
                mono_otoini.append(mono_oto)
                if len(phonemes) == 3:
                    # 3文字目(固定範囲から右ブランクまで)----------------
                    mono_oto = Oto()
                    mono_oto.filename = name_wav
                    mono_oto.alias = phonemes[2]
                    mono_oto.offset = oto.offset + oto.consonant  # 固定範囲の位置に左ブランクを移動
                    mono_oto.preutterance = 0
                    mono_otoini.append(mono_oto)
            else:
                print('\n[ERROR in otoini.monophonize()]----------------')
                print('  1エイリアスの音素数は 1, 2, 3 以外対応していません。')
                print('  phonemes: {}'.format(phonemes))
                print('  文字を連結して処理を続行します。')
                print('-----------------------------------------------\n')
                mono_otoini.append(oto)
        return mono_otoini

    def write(self, path, mode='w', encoding='cp932'):
        """
        ファイル出力
        """
        s = '\n'.join([str(oto) for oto in self]) + '\n'
        with open(path, mode=mode, encoding=encoding) as f:
            f.write(s)
        return s


class Oto:
    """
    oto.ini中の1モーラ
    """

    def __init__(self):
        self.filename: str = ''
        self.alias: str = ''
        self.offset = 0
        self.consonant = 0
        self.cutoff = 0
        self.preutterance = 0
        self.overlap = 0
        self.comment = None

    def __str__(self):
        s = '{}={},{},{},{},{},{}'.format(
            self.filename,
            self.alias,
            round(float(self.offset), 4),
            round(float(self.consonant), 4),
            round(float(self.cutoff), 4),
            round(float(self.preutterance), 4),
            round(float(self.overlap), 4)
        )
        return s

    @property
    def cutoff2(self):
        """
        右ブランクを絶対時刻で取得する
        """
        cutoff = self.cutoff
        if cutoff > 0:
            raise ValueError(f'Cutoff(右ブランク) must be negative : {str(self)}')
        return self.offset - cutoff

    @cutoff2.setter
    def cutoff2(self, absolute_cutoff_time):
        """
        右ブランクを絶対時刻で受け取り、負の値で上書きする
        """
        if absolute_cutoff_time < 0:
            raise ValueError(
                f'Argument "absolute_cutoff_time" must be positive : {absolute_cutoff_time}')
        self.cutoff = self.offset - absolute_cutoff_time


def create_cv_dict():
    """
    トライ木を作成し、単独音の辞書データを解析して挿入する。
    パラメータは、れんたんさんのtable.csvを参考にしつつ、対象エイリアスを追加した。

    Dict Parameters:
        cv_pre(int): 単独音の先行発声。
        cv_ovl(int): 単独音のオーバラップ。
    """
    cv_dict = Trie()
    cv_dict_data = """
    cv_pre=20,cv_ovl=10,あ,い,う,え,お,ん,を,ン,a,i,u,e,o,N
    cv_pre=55,cv_ovl=15,が,ぎ,ぐ,げ,ご,だ,で,ど,ga,gi,gu,ge,go,da,de,do
    cv_pre=55,cv_ovl=15,ぴゃ,ぴゅ,ぴぇ,ぴょ,pya,pyu,pye,pyo
    cv_pre=60,cv_ovl=40,ヴぁ,va
    cv_pre=70,cv_ovl=0,た,て,と,ぱ,ぴ,ぷ,ぺ,ぽ,ta,te,to,pa,pi,pu,pe,po
    cv_pre=70,cv_ovl=25,は,ふ,へ,ほ,ば,び,ぶ,べ,ぼ,ha,hu,fu,he,ho,ba,bi,bu,be,bo
    cv_pre=80,cv_ovl=0,きゃ,きゅ,きぇ,きょ,てぃ,とぅ,kya,kyu,kye,kyo,ti,tu
    cv_pre=80,cv_ovl=20,ぎゃ,ぎゅ,ぎぇ,ぎょ,gya,gyu,gye,gyo
    cv_pre=80,cv_ovl=30,ら,り,る,れ,ろ,わ,ra,ri,ru,re,ro,wa
    cv_pre=80,cv_ovl=40,ま,み,む,め,も,ma,mi,mu,me,mo
    cv_pre=85,cv_ovl=30,ざ,じ,ず,ぜ,ぞ,ぢ,づ,な,に,ぬ,ね,の,za,ji,zu,ze,zo,di,du,na,ni,nu,ne,no
    cv_pre=90,cv_ovl=30,や,いぃ,ゆ,いぇ,よ,うぁ,うぃ,うぅ,うぇ,うぉ,ya,yi,yu,ye,yo,wi,we,wo
    cv_pre=100,cv_ovl=0,か,き,く,け,こ,くぁ,くぃ,くぇ,くぉ,ちゃ,ちゅ,ちぇ,ちょ,\
        つぁ,つぃ,つぇ,つぉ,てゅ,ぷぁ,ぷぃ,ぷぇ,ぷぉ,\
        ka,ki,ku,ke,ko,kwa,kwi,kwe,kwo,cha,chu,che,cho,tsa,tsi,tse,tso,pwa,pwi,pwe,pwo
    cv_pre=100,cv_ovl=30,ぐぁ,ぐぃ,ぐぇ,ぐぉ,じゃ,じゅ,じぇ,じょ,ぢゃ,ぢゅ,ぢぇ,ぢょ,\
        gwa,gwi,gwe,gwo,ja,ju,je,jo,dya,dyu,dye,dyo
    cv_pre=100,cv_ovl=40,でぃ,でゅ,どぅ,dhi,dhu,dwu
    cv_pre=120,cv_ovl=0,ち,つ,chi,tsu
    cv_pre=120,cv_ovl=40,ヴぃ,ヴ,ヴぇ,ヴぉ,ヴゃ,ヴゅ,ヴぇ,ヴょ,ガ,ギ,グ,ゲ,ゴ,ギャ,ギュ,ギェ,ギョ,\
        にゃ,にゅ,にぇ,にょ,ひゃ,ひ,ひゅ,ひぇ,ひょ,びゃ,びゅ,びぇ,びょ,ふぁ,ふぃ,ふぇ,ふぉ,みゃ,みゅ,みぇ,みょ,\
        りゃ,りゅ,りぇ,りょ,ぬぁ,ぬぃ,ぬぇ,ぬぉ,むぁ,むぃ,むぇ,むぉ,\
        るぁ,るぃ,るぇ,るぉ,ずぁ,ずぃ,ずぇ,ずぉ,ぶぁ,ぶぃ,ぶぇ,ぶぉ,\
    vi,vu,ve,vo,vya,vyu,vye,vyo,nga,ngi,ngu,nge,ngo,hya,hi,hyu,hye,hyo,bya,byu,bye,byo,fa,fi,fe,fo,\
    mya,myu,mye,myo,rya,ryu,rye,ryo,nwa,nwi,nwe,nwo,\
    mwa,mwi,mwe,mwo,rwa,rwi,rwe,rwo,zwa,zwi,zwe,zwo,bwa,bwi,bwe,bwo
    cv_pre=120,cv_ovl=50,さ,すぃ,す,せ,そ,しゃ,し,しゅ,しぇ,しょ,すぁ,すぇ,すぉ,\
        sa,si,su,se,so,sha,shi,shu,she,she,sho,swa,swi,swe,swo
    """
    cv_dict.parse_and_insert(cv_dict_data)
    return cv_dict


if __name__ == '__main__':
    main()

if __name__ == '__init__':
    pass
