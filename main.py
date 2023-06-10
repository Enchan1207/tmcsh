#
#
#
import sys
import usb
import usbtmc


def main() -> int:

    return 0


if __name__ == "__main__":
    result = 0
    try:
        result = main() or 0
    except KeyboardInterrupt:
        print("Ctrl+C")
    finally:
        sys.exit(result)
