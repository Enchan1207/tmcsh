# python-usbtmcをasyncでいい感じに使う

## Overview

 - 通信中に処理がブロックされるのは厳しい
 - ついでに `^C` とか `^D` とかで中断…とまではいかなくても安全に処理したい
 - スレッドでやればいいのはそれはそうだけど、ここはasyncioを使ってみよう

## Discussion

### 基本的なやりとり

`python-usbtmc` を用いてTMCデバイスと通信する場合、基本的にはこのようなコードになります。

```python
import sys
from typing import Optional
import usb
import usbtmc

def main() -> int:
    # 通信対象の選択
    device: Optional[usb.core.Device] = choose_tmc_device()
    if device is None:
        return 1

    # 通信路の確立
    print("Establish connection...")
    instrument = usbtmc.Instrument(device)
    instrument.timeout = 2
    instrument.open()

    # コマンドのやりとり
    end_request: bool = False
    while not end_request:
        try:
            command = input(">>> ")
            print(instrument.ask(command))
        except (KeyboardInterrupt, EOFError):
            end_request = True

    # 終了
    print("Closing...")
    instrument.close()
    return 0
```

結果:

```
% python main.py
Connected USB-TMC devices:
  [0] Tektronix TDS2012B (0699:0367)
Enter the index of the device you want to communicate with.
Type 'r' to reload, ^C or ^D to abort.
> 0
Establish connection...
>>> *IDN?
TEKTRONIX,TDS 2012B,C062851,CF:91.1CT FV:v22.01
>>> *ESR?
164
>>> LANG?
JAPANESE
>>> Closing...
```

対話シェルっぽくやり取りできています。

### タイムアウトとスレッドブロック

しかし、*測定器を現在の状態に設定するのに必要な、すべてのコマンドのASCII文字列を返* すコマンド、`*LRN` などは処理に時間がかかることがあります。現状のコードでこのコマンドを実行すると、環境によってはタイムアウトで落ちてしまいます。

```
Establish connection...
>>> *LRN?
Unexpected exception occured in main(): [Errno 60] Operation timed out
```

タイムアウト時間を伸ばせば想定通りの応答が得られますが…

```
>>> *LRN?
POSITION2 -6.4E0;:MEASUREMENT:MEAS1:TYPE PWIDTH;SOURCE CH1;:MEASUREMENT:MEAS2…(省略)
```

それでも、応答が得られるまで (正確には、`usbtmc.ask()`が返るまで) はメインスレッドがブロックされてしまいます。`KeyboardInterrupt` もいい感じに補足しづらいため、シェルとしても操作感がよくありません。

そこで…

### asyncioによる非同期処理

TMCデバイスとの通信処理を非同期に持っていき、メインスレッドがブロックされないようにすることでこれを解決していきます。

`usbtmc.Instrument` で定義されている関数 `read` や `write`、`ask` 等の関数は `async def` な関数ではないので、ただ `await instrument.ask()` とするだけでは結局スレッドがブロックされてしまいます(1敗)。
そこで、`asyncio` の関数 `run_in_executor` によりこれら関数を非同期コンテキストで呼び出すように変更していきます。

```python
ask_task = event_loop.run_in_executor(None, instrument.ask, command)
```

このように記述することで、TMCデバイスのI/Oでメインスレッドがブロックされるのを防ぐことができます。
また `ask_task` は `asyncio.Future` ですので、 `.done()` を見ることで通信が完了したかどうかを取得できます。

このような関数を作り…

```python
async def console_wait_anim(task: asyncio.Future):
    """引数に与えられたFutureが完了するまでコンソールでアニメーションする

    Args:
        task (asyncio.Future): 待機対象のFuture
    """
    keyframe_max = 4
    keyframe_index = 0

    while not task.done():
        keyframe_index = (keyframe_index + 1) % keyframe_max
        indicator = "." * keyframe_index + " " * (keyframe_max - 1 - keyframe_index)
        print(f"{indicator}\r", end="")
        await asyncio.sleep(0.1)

    print(f"{' ' * keyframe_max}\r", end="")
```

引数に先程の `ask_task` を渡して `await` すれば、通信中にちょっとしたインジケータを表示することも可能です。

※イメージ

コマンド送信直後

```
>>> *LRN?
...
```

↓ 完了

```
>>> *LRN?
:HEADER 0;:VERBOSE 1;:DATA …(省略)
```


## License

This repository is published under [MIT License](LICENSE).
