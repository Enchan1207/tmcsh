#
#
#
import sys
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Optional, Union

import usb
import usbtmc

from device_chooser import choose_tmc_device


def main() -> int:
    # 通信対象の選択
    device: Optional[usb.core.Device] = choose_tmc_device()
    if device is None:
        return 1

    # 通信路の確立
    print("Establish connection...")
    instrument = usbtmc.Instrument(device)
    instrument.timeout = 5
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
        response_future: Future = tmc_command_executor.submit(instrument.ask, command)
        response_future.add_done_callback(on_receive_response)

    # 終了
    print("Closing...")
    tmc_command_executor.shutdown()
    instrument.close()
    return 0


def on_receive_response(response_future: Future[Union[list, str, bytes]]):
    """受信完了時のコールバック

    Args:
        future (Future): エグゼキュータに投げたFutureオブジェクト
    """
    try:
        result = response_future.result()
        print(result)
    except usb.core.USBTimeoutError:
        print("Response timed out. please check command syntax or connection.")
    except (usbtmc.usbtmc.UsbtmcException, usb.core.USBError) as unexpected_error:
        print(f"Unexpected USB error: {unexpected_error}")


if __name__ == "__main__":
    result: int = main() or 0
    sys.exit(result)
