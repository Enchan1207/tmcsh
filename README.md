# python-usbtmcをasyncでいい感じに使う

## Overview

 - 通信中に処理がブロックされるのは厳しい
 - ついでに `^C` とか `^D` とかで中断…とまではいかなくても安全に処理したい
 - スレッドでやればいいのはそれはそうだけど、ここはasyncioを使ってみよう

## License

This repository is published under [MIT License](LICENSE).
