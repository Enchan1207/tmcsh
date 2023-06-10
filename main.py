#
#
#
import asyncio
import sys
from typing import Optional

import usb
import usbtmc


async def main() -> int:
    # 通信対象の選択
    device: Optional[usb.core.Device] = choose_tmc_device()
    if device is None:
        return 1

    # 通信路の確立
    print("Establish connection...")
    instrument = usbtmc.Instrument(device)
    instrument.timeout = 5
    instrument.open()

    # コマンドのやりとり
    event_loop = asyncio.get_event_loop()
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

        # 通信メソッドは非同期コンテキストで呼び出し、完了するまでコンソールで遊ぶ
        try:
            ask_task = event_loop.run_in_executor(None, instrument.ask, command)
            await console_wait_anim(ask_task)
            print(ask_task.result())
        except usb.core.USBTimeoutError:
            print("Response timed out. please check command syntax or connection.")
            continue
        except usb.core.USBError as usberror:
            print(f"Unexpected USB error: {usberror.strerror}")
            end_request = True
            continue

    # 終了
    print("Closing...")
    instrument.close()
    return 0


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


def choose_tmc_device() -> Optional[usb.core.Device]:
    """通信対象のTMCデバイスをユーザに選択させる

    Returns:
        Optional[usb.core.Device]: 選択されたデバイス

    Note:
        有効なデバイスが選択されるか、SIGINT(^C), EOF(^D) が入力されるまでループします。
        デバイスが選択されないままループを抜けた場合はNoneが返ります。
    """

    selected_device: Optional[usb.core.Device] = None
    end_request: bool = False
    while not end_request:
        # 一覧表示
        print("Connected USB-TMC devices:")
        connected_tmc_devices = usbtmc.list_devices()
        for index, tmc_device in enumerate(connected_tmc_devices):
            device_identifiers_str = f"{tmc_device.idVendor:04X}:{tmc_device.idProduct:04X}"
            product_info_str = usb.util.get_string(tmc_device, tmc_device.iProduct)
            print(f"  [{index}] {product_info_str} ({device_identifiers_str})")

        # 選択させる
        print("Enter the index of the device you want to communicate with.")
        print("Type 'r' to reload, ^C or ^D to abort.")
        try:
            command = ""
            while command == "":
                command = input("> ")
        except (KeyboardInterrupt, EOFError):
            print("Abort")
            end_request = True
            continue

        if command == "r":
            print("Reloading..")
            continue

        try:
            target_device_index = int(command)
            if target_device_index < 0 or target_device_index >= len(connected_tmc_devices):
                print("Invalid index")
                continue

            selected_device = connected_tmc_devices[target_device_index]
            end_request = True
        except ValueError:
            pass

    return selected_device


if __name__ == "__main__":
    result = 0
    try:
        event_loop = asyncio.get_event_loop()
        result = event_loop.run_until_complete(main())
    except Exception as e:
        print(f"Unexpected exception occured in main(): {e}")
        sys.exit(result)
