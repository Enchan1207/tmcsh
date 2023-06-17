# USB-TMC Shell

## Overview

Interactive command shell for USB Test and Measurement device Class (TMC) device.

## Installation

It can be installed from GitHub using pip:

```
pip install git+https://github.com/Enchan1207/tmcsh
```

After installation, command `tmcsh` will be available.

## Usage

### 1. Choosing a communication device

When you start `tmcsh`, you will be prompted to select a device.

```
$ tmcsh
USB-TMC shell v0.1.0
Connected USB-TMC devices:
  [0] Tektronix TDS2012B (0699:0367)
Enter the index of the device you want to communicate with.
Type 'r' to reload, ^C or ^D to abort.
>
```

Type index for communicate with:

```
0
```

After it, shell tries to establish connection.

```
Establish connection...
```

If that succeeds, you'll see a REPL-like prompt.

```
>>> 
```

### 2. Query the device

You can send IEEE 488 common commands...

```
>>> *IDN?
TEKTRONIX,TDS 2012B,C062851,CF:91.1CT FV:v22.01
```

```
>>> *ESR?
128
```

model-specific commands...

```
>>> DATA?
RPBINARY;REFA;CH2;1;2500;1
```

or commands that return binary.

```
>>> DATA:SOURCE?
CH2
>>> DATA:SOURCE CH1
>>> CURVE?
0000: 23 34 32 35 30 30 81 81 80 80 80 80 80 81 80 81
0001: 81 81 80 80 80 80 80 81 80 80 80 81 80 81 80 81
0002: 80 80 80 80 81 80 81 80 80 80 80 81 81 80 80 80
0003: 80 81 80 80 80 81 80 80 80 80 81 80 80 81 81 80
0004: 80 81 80 81 81 81 81 80 80 81 80 80 81 80 80 80
0005: 80 80 81 80 80 80 81 80 80 80 80 81 81 80 80 80
0006: 80 80 80 81 80 80 80 81 80 81 80 80 80 80 80 80
0007: 81 81 80 81 80 81 80 80 80 80 80 81 80 81 80 81
0008: 80 81 80 80 80 80 81 80 80 80 80 80 81 80 80 80
0009: 81 80 80 81 80 80 81 81 81 81 81 80 80 81 81 80
...
```

## License

This repository is published under [MIT License](LICENSE).
