#
# USBデバイス選択
#


from typing import Optional

import usb
import usbtmc


def choose_tmc_device() -> Optional[usb.core.Device]:
    """通信対象のTMCデバイスをユーザに選択させる

    Returns:
        Optional[usb.core.Device]: 選択されたデバイス

    Note:
        メインスレッドでの実行を想定しています。
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
            # デバイスの基本的な情報を表示
            device_info_str = create_device_info_string(tmc_device)
            print(f"  [{index}] {device_info_str}")

        # 選択させる
        print("Enter the index of the device you want to communicate with.")
        print("Type 'r' to reload, ^C or ^D to abort.")
        try:
            command = ""
            while command == "":
                command = input("> ")
        except (KeyboardInterrupt, EOFError):
            print("abort")
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


def create_device_info_string(device: usb.core.Device) -> str:
    """USBデバイスの基本的な情報を取得し、文字列形式で返す

    Args:
        device (usb.Device): 対象のデバイス

    Returns:
        str: デバイス情報を表す文字列

    Note:
        idVendor, idProductを調べ、16進数で表現します。
        またiProductからディスクリプタを取得し、製品情報の取得を試みます。
    """
    # デバイスの基本的な情報を取得
    device_idvendor: int = device.idVendor      # type:ignore
    device_idproduct: int = device.idProduct    # type:ignore
    device_iproduct: int = device.iProduct      # type:ignore
    try:
        product_info_str = usb.util.get_string(device, device_iproduct) or "<< No device info >>"
    except usb.USBError:
        product_info_str = "<< Failed to fetch device info >>"

    # 表示
    return f"{product_info_str} ({device_idvendor:04X}:{device_idproduct:04X})"
