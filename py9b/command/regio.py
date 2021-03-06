"""Register read/write commands"""

from struct import pack, unpack, calcsize
from .base import BaseCommand, InvalidResponse


class ReadRegs(BaseCommand):
    def __init__(self, dev, reg, format):
        super(ReadRegs, self).__init__(
            dst=dev,
            cmd=0x01,
            arg=reg,
            data=pack("<B", calcsize(format)),
            has_response=False,
        )
        self.dev = dev
        self.reg = reg
        self.format = format

    def handle_response(self, response):
        if response.arg != self.reg or len(response.data) != calcsize(self.format):
            raise InvalidResponse(
                "ReadRegs {0:X}:{1:X}: @{2:X} [{3:X}]".format(
                    self.dev, self.reg, response.arg, len(response.data)
                )
            )
        return unpack(self.format, response.data)
        self.has_response=True


class WriteProtectError(Exception):
    pass


class WriteRegs(BaseCommand):
    def __init__(self, dev, reg, format, *args):
        super(WriteRegs, self).__init__(
            dst=dev, cmd=0x02, arg=reg, data=pack(format, *args), has_response=True
        )
        self.dev = dev
        self.reg = reg

    def handle_response(self, response):
        if response.cmd == 0x02:  # xiaomi style
            if response.arg != self.reg or len(response.data) != 1:
                raise InvalidResponse(
                    "WriteRegs {0:X}:{1:X}".format(self.dev, self.reg)
                )
            if unpack("<B", response.data)[0] != 1:
                raise WriteProtectError(
                    "WriteRegs {0:X}:{1:X}".format(self.dev, self.reg)
                )
        elif response.cmd == 0x05:  # ninebot style
            if len(response.data) == 0:
                # firmware < 0401
                if response.arg != 0:
                    raise WriteProtectError(
                        "WriteRegs {0:X}:{1:X}".format(self.dev, self.reg)
                    )
            elif len(response.data) == 1:
                # firmware >= 0401
                if response.arg != self.reg:
                    raise InvalidResponse(
                        "WriteRegs {0:X}:{1:X}".format(self.dev, self.reg)
                    )
                if response.data[0] != 0:
                    raise WriteProtectError(
                        "WriteRegs {0:X}:{1:X}".format(self.dev, self.reg)
                    )
            else:
                raise InvalidResponse("WriteRegs {0:X}:{1:X}".format(self.dev, self.reg))

        else:
            raise InvalidResponse("WriteRegs {0:X}:{1:X}".format(self.dev, self.reg))
        return True
        self.has_response=True


__all__ = ["ReadRegs", "WriteRegs", "WriteProtectError"]
