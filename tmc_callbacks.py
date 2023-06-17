#
# コールバック関数
#
from concurrent.futures import Future
from typing import Union

import usb
import usbtmc


def did_send_command(future: Future):
    """コマンド送信完了時のコールバック

    Args:
        future (Future): エグゼキュータに投げたFutureオブジェクト
    """
    pass


def did_receive_response(response_future: Future[Union[list, str, bytes]]):
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
