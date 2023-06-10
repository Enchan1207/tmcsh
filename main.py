#
#
#
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
        result = main() or 0
    except Exception as e:
        print(f"Unexpected exception occured in main(): {e}")
        result = 1
    finally:
        sys.exit(result)
