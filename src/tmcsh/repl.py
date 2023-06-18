#
# tmc_shell REPL
#
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Optional

import usb
import usbtmc

from .device_chooser import choose_tmc_device
from .tmc_callbacks import did_receive_response, did_send_command


def repl(device: Optional[usb.core.Device], timeout: int) -> int:
    print("tmcsh REPL mode")

    # 通信対象の設定
    target_device = device if device is not None else choose_tmc_device()
    if target_device is None:
        return 1

    # 通信路の確立
    print("Establish connection...")
    instrument = usbtmc.Instrument(target_device)
    instrument.timeout = timeout
    try:
        instrument.open()
    except (usbtmc.usbtmc.UsbtmcException, usb.core.USBError) as e:
        print(f"Failed to establish connection with TMC device: {e}")
        return 1

    # TMCデバイスとの通信を担うエグゼキュータ
    tmc_command_executor = ThreadPoolExecutor()

    # コマンドのやりとり
    end_request: bool = False
    while not end_request:
        # コマンド入力 ^C, ^Dで終了
        try:
            command: str = ""
            while command == "":
                command = input(">>> ")
        except (KeyboardInterrupt, EOFError):
            print("abort")
            end_request = True
            continue

        # コマンドをエグゼキュータに投げる
        command_send_future: Future = tmc_command_executor.submit(instrument.write, command)
        command_send_future.add_done_callback(did_send_command)

        # コマンドが '?' で終わるなら、レスポンスを期待する
        is_command_require_response = command.endswith("?")
        if is_command_require_response:
            read_response_future: Future = tmc_command_executor.submit(instrument.read_raw)
            read_response_future.add_done_callback(did_receive_response)

    # 終了
    print("Closing...")
    tmc_command_executor.shutdown()
    instrument.close()
    return 0
