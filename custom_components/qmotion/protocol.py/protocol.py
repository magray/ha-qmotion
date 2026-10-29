"""Async TCP client for the QMotion QSync protocol.

The command and record layout follows the publicly documented observations in
https://github.com/devbobo/qmotion (MIT). The hub's protocol does not expose
actual blind position; positions in Home Assistant are therefore estimated.
"""

import asyncio
import logging
from dataclasses import dataclass

from .const import POSITION_CODES, SUPPORTED_POSITIONS

_LOGGER = logging.getLogger(__name__)
TCP_TIMEOUT = 8


@dataclass(frozen=True)
class Blind:
    """A blind reported by a QSync hub."""
    address: str
    name: str


class QMotionClient:
    """Communicate with one QSync hub over TCP."""

    def __init__(self, host: str, port: int = 9760) -> None:
        self.host = host
        self.port = port

    async def _exchange(self, command: bytes, *, quiet: float = 0.3) -> bytes:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), TCP_TIMEOUT)
        try:
            writer.write(command)
            await writer.drain()
            chunks = []
            deadline = asyncio.get_running_loop().time() + TCP_TIMEOUT
            while True:
                remaining = deadline - asyncio.get_running_loop().time()
                if remaining <= 0:
                    break
                try:
                    chunk = await asyncio.wait_for(reader.read(4096), min(remaining, quiet))
                except TimeoutError:
                    break
                if not chunk:
                    break
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass

    async def async_get_blinds(self) -> list[Blind]:
        """Read the hub inventory using command 16020000."""
        response = await self._exchange(bytes.fromhex("16020000"), quiet=0.6)
        data = response.hex()
        if data.startswith("1604") and len(data) > 12:
            data = data[12:]
        blinds = []
        offset = 0
        while offset + 12 <= len(data):
            if data.startswith("163b", offset):
                length = 122
            elif data.startswith("162c", offset):
                length = 92
            else:
                found = [i for i in (data.find("162c", offset + 2), data.find("163b", offset + 2)) if i >= 0]
                if not found:
                    break
                offset = min(found)
                continue
            record = data[offset:offset + length]
            offset += length
            if len(record) < 56 or not record.startswith("162c"):
                continue
            address = record[10:12] + record[8:10] + record[6:8]
            try:
                name = bytes.fromhex(record[52:]).decode("utf-8", errors="replace").split("\x00", 1)[0].strip()
            except ValueError:
                continue
            blinds.append(Blind(address, name or f"QMotion Blind {address.upper()}"))
        return blinds

    async def async_move(self, address: str, position: float) -> None:
        """Move a blind to its nearest supported preset."""
        preset = min(SUPPORTED_POSITIONS, key=lambda value: abs(value - position))
        commands = (bytes.fromhex("1b00"), bytes.fromhex("1b0100"), bytes.fromhex(f"1b0500{address}{POSITION_CODES[preset]}"))
        reader, writer = await asyncio.wait_for(asyncio.open_connection(self.host, self.port), TCP_TIMEOUT)
        try:
            for command in commands:
                writer.write(command)
                await writer.drain()
                try:
                    await asyncio.wait_for(reader.read(4096), TCP_TIMEOUT)
                except TimeoutError:
                    _LOGGER.debug("No acknowledgement received for QMotion command")
        finally:
            writer.close()
            try:
                await writer.wait_closed()
            except OSError:
                pass
