# utaupy
[![PyPI](https://img.shields.io/pypi/v/utaupy.svg)](https://pypi.python.org/pypi/utaupy)

UTAU周辺のデータ処理を行うPythonのパッケージです。READMEは書いてる途中です。  
PythonでUTAUプラグインを作りたい場合は、C# 用の **[utauPlugin](https://github.com/delta-kimigatame/utauPlugin)** をPythonに移植した **[pyUtau](https://github.com/UtaUtaUtau/pyUtau)** のほうがいいかもしれません。ビブラートやピッチの扱いが便利そうです。

## 利用規約

LICENSE ファイルをご覧ください。

## 処理できるファイル

- .ust (UTAU)
- .txt (UTAU Plugin Script)
- .txt (録音リスト)
- .ini (setParam および UTAU音源原音設定)
- .lab (歌唱データベース用音素ラベル)
- .table (ローマ字かな対応表)
- .svp (Synthesizer V R2)
- .csv (REAPER リージョン・マーカー用)



## 機能概要

- INI, UST, LAB ファイルのデータをクラスオブジェクトとして扱います。
- INI, UST, LAB ファイルを変換できます。ただし不可逆の処理が多いです。



# Methods

---

## utaupy.ust

### load(path)

USTファイルを読み取り、Ust オブジェクトにする。

```Python
ust = load(ust)  # type(ust): <utaupy.ust.Ust class object>
```

### _notenum_as_abc_
音階番号を C4 とかの音階表記に変換する。国際表記に準拠。

```Python
notenum = 61
s = notenum_as_abc(notenum)
print(s)  # C4
```

---

### Ust(collections.UserList)

UST ファイルを取り扱うための class

#### _\_\_init\_\__

パラメータを格納する _list_ self.\_notes を作成する。

```Python
def __init__(self):
"""インスタンス作成"""
# ノート(クラスオブジェクト)からなるリスト
self._notes = []
```

#### _\_\_len\_\__

len(self) したときに Version, Setting, PREV, NEXT, TRACKEND を含む、UST内の全エントリ数を返す。

```Python
n = len(ust)  # type(n): int
```

#### _write_

Ust オブジェクトをファイル出力にする。出力した文字列を返す

```Python
ust.write(path)  # type(path): str
# return strings written in ustfile
```

#### property: _notes_

音符と休符の情報をリストで取得または登録する。

```Python
# Getter
l = ust.notes  # l: [Note, Note, Note, ..., Note] <list of utaupy.ust.Note objects>
# Setter
ust.notes = l  # l: [Note, Note, Note, ..., Note] <list of utaupy.ust.Note objects>
```

#### property: _tempo_

トラックのグローバルテンポを取得する。

```Python
# Getter
x = ust.tempo  # x: float
# Setter
ust.tempo = x  # x: float
```

#### _reload_tempo_

self._notes 内の全 Note にローカルテンポ取得用のパラメータ \_alternative_tempo を設定する。

self.values や self.values の setter を使うと自動的にで実行される。

```Python
ust.reload_tempo()
# no return
```

#### *reload_tag_number*

全ノートのエントリ番号（タグ）を振りなおす。ファイル出力時に実行することを想定。
```Python
ust.reload_tag_number()
# no return
```


#### property: _replace_lyrics(str old_lyric, str new_lyric)_

全ノートの歌詞を置換する。
```Python
ust.replace_lyrics('か', 'か強')
# no return
```

#### _vcv2cv_

全ノートの連続音エイリアスを単独音にする。（空白で区切った後半をエイリアスにする）

#### _make_finalnote_R_

最後のノートが休符になるようにする。
```Python
ust.make_finalenote_R()
# no return
```

---

### Note(collections.UserDict)

#### _\_\_init\_\__

パラメータを格納する _dict_ self.\_\_d 、エントリを識別するタグ self.tag 、歌詞を管理する self.lyricを作成する。

```Python
def __init__(self):
    self.__d = {}
    self.tag = '[#UNDEFINED]'
    self.lyric = None
    self._alternative_tempo = None
```

#### _\_\_str\_\__

文字列出力するフォーマット

```Python
def __str__(self):
    return f'{self.tag} {self.lyric}\t<utaupy.ust.Note object>'
    # '[#0000] か    <utaupy.ust.Note object>'
```

#### ~~property: _values_~~

~~ノートの各種パラメータを辞書で取得または上書きする。~~

```Python
# Getter
d = note.values  # type(d): dict
# Setter
note.values = d  # type(d): dict
```

#### property: _tag_

ノートのエントリを識別するタグを取得または上書きする。'[#SETTING]' とか '[#0000]' とか。

```Python
# Getter
s = note.tag  # type(s): str
# Setter
note.tag = s  # type(s): str

print(note.tag)  # '[#0000]' (for example)
```

#### property: _length_
```Python
# Getter
s = note.tag  # type(s): str
# Setter
note.tag = s  # type(s): str

print(note.tag)  # '[#0000]' (for example)
```

#### property: _length\_ms_
```Python
# Getter
s = note.tag  # type(s): str
# Setter
note.tag = s  # type(s): str

print(note.tag)  # '[#0000]' (for example)
```

#### property: _lyric_
```Python
# Getter
s = note.tag  # type(s): str
# Setter
note.tag = s  # type(s): str

print(note.tag)  # '[#0000]' (for example)
```

#### property: _notenum_
```Python
# Getter
s = note.tag  # type(s): str
# Setter
note.tag = s  # type(s): str

print(note.tag)  # '[#0000]' (for example)
```
#### property: _tempo_

ノートのある位置でのテンポを取得または上書きする。
Setterとして使用した場合、直後に上位Ustオブジェクトの Ust.reload_tempo() の実行を推奨。

```Python
# Getter
n = note.tempo  # type(n): float
print(n)        # float 100.0 (for example)

# Setter
note.tempo = 120
print(note.tempo) # float 120.0
# After setting tempo, please do 'reload_tempo()' of Ust object which contains the Note object.
ust.reload_tempo()

```

#### _get\_by\_key_

任意のパラメータを取得する。存在しない場合 KeyError になる。

Get the parameter of note, by key you like. This may raise KeyError.

```Python
get_by_key('Modulation')  # '0'
get_by_key('Lyric')  # 'a か'
get_by_key('Tag')  # '[#0000]'
```

#### *set\_by\_key*

任意のパラメータを新規登録または上書きする。

```Python
print(get_by_key('Modulation'))  # KeyError
note.set_by_key('Modulation', 0)
print(get_by_key('Modulation'))  # '0'
```


#### _delete_

```Python
print(note.tag)  # '[#0000]'
note.refresh()
print(note.tag)  # '[#DELETE]'
```

#### _insert_

Not reccomended to use

```Python
print(note.tag)  # '[#0000]'
note.refresh()
print(note.tag)  # '[#INSERT]'
```

#### _refresh_


```Python
print(note.tag)  # '[#0000]'
note.refresh()
print(note.tag)  # '[#DELETE]\n[#INSERT]'
```

#### *suppin*

ノートの情報を最小限にする

```Python
note.suppin()
```

---

## utaupy.otoini

UTAUの原音設定ファイルを扱うモジュール。setParamでの利用を想定。

---

### OtoIni(collections.UserList)

oto.ini ファイルを扱うためのクラス。list を継承。

---

### Oto(collections.UserDict)

oto.ini に含まれる各原音のパラメータを扱うクラス。

---

## utaupy.table

かなローマ字変換表などを扱うモジュール。

## utaupy.convert

Ust オブジェクト、OtoIni オブジェクト、Label オブジェクトなどを変換するモジュール。

## utaupy.reaper

REAPER (DAW) のリージョン・マーカー用CSVファイルを扱うモジュール。

## utaupy.utau

UTAUエディタで行う操作の代替と、UTAU音源の原音値取得などをするモジュール。「パラメータ自動調整」などができる。

## utaupy.utauplugin

UTAUプラグインをつくるためのモジュール。utaupy.utauplugin.UtauPlugin クラスは utaupy.ust.Ust を継承し、プラグイン用に最適化した子クラス。

使用例として半音上げプラグインを貼っておきます。

```Python
import utaupy

def notenum_plus1(utauplugin):
    """
    utauplugin: utaupy.utauplugin.UtauPlugin class object
    全てのノートを半音上げる
    """
    # UtauPluginオブジェクトのうちノート部分を取得
    notes = utauplugin.notes
    # 半音上げ
    for note in notes:
        note.notenum += 1

if __name__ == '__main__':
    # automatically 
        # read the utau plugin script
        # load as utaupy.utauplugin.UtauPlugin class object
        # overwrite the utau plugin script
    utaupy.utauplugin.run(notenum_plus1)
```





## 連絡先

- Twitter: @oatsu_c

- GitHub: oatsu-gh
