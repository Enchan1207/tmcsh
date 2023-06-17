#
# コールバック関数
#
from concurrent.futures import Future

import usb
import usbtmc


def did_send_command(command_future: Future[None]):
    """コマンド送信完了時のコールバック

    Args:
        future (Future): エグゼキュータに投げたFutureオブジェクト
    """
    try:
        _ = command_future.result()
    except (usbtmc.usbtmc.UsbtmcException, usb.core.USBError) as unexpected_error:
        print(f"Unexpected USB error occured during sending command: {unexpected_error}")


def did_receive_response(response_future: Future[bytes]):
    """受信完了時のコールバック

    Args:
        future (Future): エグゼキュータに投げたFutureオブジェクト
    """

    # とりあえず受け取る
    try:
        result = response_future.result()
    except usb.core.USBTimeoutError:
        print("Response timed out. please check command syntax or connection.")
        return
    except (usbtmc.usbtmc.UsbtmcException, usb.core.USBError) as unexpected_error:
        print(f"Unexpected USB error during waiting response: {unexpected_error}")
        return

    # 文字列への変換を試みる ダメなら16進数でダンプする
    # TODO: フォーマットを変更したり既知のコマンドについては決まった対応にしたり
    result_repr = "<< Unknown format >>"
    try:
        result_repr = result.decode()
    except UnicodeError:
        # 16byteごと分割
        separated_bytes = [result[i * 16: (i + 1) * 16] for i in range(int(len(result) / 16))]
        result_repr = "\n".join([f"{index:04X}: " + " ".join([f"{n:02X}" for n in line]) for index, line in enumerate(separated_bytes)])
    finally:
        print(result_repr, end="", flush=True)
