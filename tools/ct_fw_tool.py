#!/usr/bin/env python3
from pathlib import Path
import argparse
import hashlib
import struct

NOVATION_HEADER = bytes([0xF0, 0x00, 0x20, 0x29, 0x00])
CMD_INIT   = 0x71
CMD_WRITE  = 0x72
CMD_FINISH = 0x73
CMD_HEADER = 0x7C

TARGETS = {
    0x64: "Circuit Tracks",
    0x63: "Circuit Rhythm",
}

def parse_nibbles(data: bytes) -> int:
    value = 0
    for b in data:
        if b > 0x0F:
            raise ValueError(f"Invalid nibble byte: 0x{b:02X}")
        value = (value << 4) | b
    return value

def encode_nibbles(value: int, count: int) -> bytes:
    if value < 0 or value >= (1 << (4 * count)):
        raise ValueError("Value does not fit nibble field")
    return bytes((value >> (4 * (count - 1 - i))) & 0x0F for i in range(count))

def crc32_non_reflected(data: bytes, init=0xFFFFFFFF, poly=0x04C11DB7) -> int:
    crc = init
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            if crc & 0x80000000:
                crc = ((crc << 1) ^ poly) & 0xFFFFFFFF
            else:
                crc = (crc << 1) & 0xFFFFFFFF
    return crc

def unpack_7bit(payload: bytes) -> bytes:
    # 37 MIDI-safe 7-bit bytes contain 259 useful bit positions:
    # 256 firmware bits + 3 zero padding bits.
    bits = []
    for b in payload:
        if b & 0x80:
            raise ValueError("Payload is not MIDI 7-bit clean")
        for shift in range(6, -1, -1):
            bits.append((b >> shift) & 1)
    if len(bits) < 3:
        raise ValueError("Payload too short")
    bits = bits[:-3]
    if len(bits) % 8:
        raise ValueError("Decoded bit count is not byte-aligned")
    out = bytearray()
    for i in range(0, len(bits), 8):
        v = 0
        for bit in bits[i:i+8]:
            v = (v << 1) | bit
        out.append(v)
    return bytes(out)

def pack_7bit(block: bytes) -> bytes:
    if len(block) != 32:
        raise ValueError("Firmware chunks must be exactly 32 bytes")
    bits = []
    for b in block:
        for shift in range(7, -1, -1):
            bits.append((b >> shift) & 1)
    bits += [0, 0, 0]
    out = bytearray()
    for i in range(0, len(bits), 7):
        v = 0
        for bit in bits[i:i+7]:
            v = (v << 1) | bit
        out.append(v)
    if len(out) != 37:
        raise AssertionError("Internal 7-bit packing error")
    return bytes(out)

def split_messages(data: bytes):
    msgs = []
    i = 0
    while i < len(data):
        if data[i] != 0xF0:
            raise ValueError(f"Unexpected byte 0x{data[i]:02X} at file offset 0x{i:X}")
        end = data.find(b"\xF7", i + 1)
        if end < 0:
            raise ValueError("Missing SysEx F7 terminator")
        msg = data[i:end+1]
        if msg[:5] != NOVATION_HEADER:
            raise ValueError(f"Unexpected SysEx manufacturer header at offset 0x{i:X}")
        msgs.append(msg)
        i = end + 1
    return msgs

def decode_syx(path: Path):
    raw = path.read_bytes()
    msgs = split_messages(raw)
    if len(msgs) < 3:
        raise ValueError("Too few SysEx messages")

    init = next((m for m in msgs if m[5] == CMD_INIT), None)
    header = next((m for m in msgs if m[5] == CMD_HEADER), None)
    finish = next((m for m in msgs if m[5] == CMD_FINISH), None)
    writes = [m for m in msgs if m[5] == CMD_WRITE]
    if not (init and header and finish):
        raise ValueError("Missing INIT, HEADER or FINISH message")

    init_payload = init[6:-1]
    header_payload = header[6:-1]
    if len(init_payload) < 8 or len(header_payload) < 23:
        raise ValueError("Unexpected firmware header layout")

    target_code = init_payload[1]
    init_version = parse_nibbles(init_payload[2:8])
    header_version = parse_nibbles(header_payload[1:7])
    firmware_size = parse_nibbles(header_payload[7:15])
    expected_crc = parse_nibbles(header_payload[15:23])

    # Circuit firmware deliberately sends the first 32 bytes in UPDATE_FINISH,
    # after all other 32-byte UPDATE_WRITE chunks.
    first_block = unpack_7bit(finish[6:-1])
    body = b"".join(unpack_7bit(m[6:-1]) for m in writes)
    firmware = (first_block + body)[:firmware_size]

    actual_crc = crc32_non_reflected(firmware)
    if actual_crc != expected_crc:
        raise ValueError(
            f"CRC mismatch: header=0x{expected_crc:08X}, calculated=0x{actual_crc:08X}"
        )

    return {
        "raw": raw,
        "messages": msgs,
        "init_message": init,
        "header_message": header,
        "firmware": firmware,
        "target_code": target_code,
        "target_name": TARGETS.get(target_code, f"Unknown 0x{target_code:02X}"),
        "init_version": init_version,
        "header_version": header_version,
        "firmware_size": firmware_size,
        "crc": expected_crc,
        "write_count": len(writes),
    }

def build_syx(template_path: Path, firmware: bytes) -> bytes:
    info = decode_syx(template_path)

    init = info["init_message"]
    old_header = info["header_message"]
    hp = bytearray(old_header[6:-1])

    hp[7:15] = encode_nibbles(len(firmware), 8)
    hp[15:23] = encode_nibbles(crc32_non_reflected(firmware), 8)
    header = NOVATION_HEADER + bytes([CMD_HEADER]) + bytes(hp) + b"\xF7"

    first = firmware[:32]
    if len(first) < 32:
        first += b"\xFF" * (32 - len(first))

    rest = firmware[32:]
    if len(rest) % 32:
        rest += b"\xFF" * (32 - (len(rest) % 32))

    write_msgs = []
    for i in range(0, len(rest), 32):
        payload = pack_7bit(rest[i:i+32])
        write_msgs.append(NOVATION_HEADER + bytes([CMD_WRITE]) + payload + b"\xF7")

    finish = NOVATION_HEADER + bytes([CMD_FINISH]) + pack_7bit(first) + b"\xF7"
    return init + header + b"".join(write_msgs) + finish

def print_info(path: Path, info):
    fw = info["firmware"]
    print(f"File:            {path}")
    print(f"Target:          {info['target_name']} (0x{info['target_code']:02X})")
    print(f"INIT version:    {info['init_version']}")
    print(f"HEADER version:  {info['header_version']}")
    print(f"Firmware size:   {info['firmware_size']} bytes (0x{info['firmware_size']:X})")
    print(f"UPDATE_WRITE:    {info['write_count']} chunks")
    print(f"CRC32 non-ref:   0x{info['crc']:08X}")
    print(f"Firmware SHA256: {hashlib.sha256(fw).hexdigest()}")
    if len(fw) >= 8:
        sp, reset = struct.unpack_from("<II", fw, 0)
        print(f"Vector[0] MSP:   0x{sp:08X}")
        print(f"Vector[1] Reset: 0x{reset:08X} (Thumb entry; code 0x{reset & ~1:08X})")

def cmd_unpack(args):
    src = Path(args.syx)
    info = decode_syx(src)
    out = Path(args.output) if args.output else src.with_suffix(".bin")
    out.write_bytes(info["firmware"])
    print_info(src, info)
    print(f"Wrote:           {out}")

def cmd_repack(args):
    template = Path(args.template_syx)
    bin_path = Path(args.bin)
    out = Path(args.output)
    firmware = bin_path.read_bytes()
    syx = build_syx(template, firmware)
    out.write_bytes(syx)
    print(f"Template:        {template}")
    print(f"Firmware BIN:    {bin_path}")
    print(f"Output SYX:      {out}")
    print(f"Output SHA256:   {hashlib.sha256(syx).hexdigest()}")
    # Validate what we just built
    check = decode_syx(out)
    if check["firmware"] != firmware:
        raise SystemExit("ERROR: Repacked SYX does not decode back to the input BIN")
    print("Self-check:      OK")

def cmd_roundtrip(args):
    src = Path(args.syx)
    info = decode_syx(src)
    rebuilt = build_syx(src, info["firmware"])
    same = rebuilt == info["raw"]
    print_info(src, info)
    print(f"Exact SYX match: {'YES' if same else 'NO'}")
    print(f"Original SHA256: {hashlib.sha256(info['raw']).hexdigest()}")
    print(f"Rebuilt SHA256:  {hashlib.sha256(rebuilt).hexdigest()}")
    if args.output:
        Path(args.output).write_bytes(rebuilt)
        print(f"Wrote:           {args.output}")
    if not same:
        raise SystemExit(2)

def main():
    p = argparse.ArgumentParser(description="Novation Circuit Tracks/Rhythm firmware SYX utility")
    sub = p.add_subparsers(dest="cmd", required=True)

    u = sub.add_parser("unpack", help="Extract raw firmware BIN from SYX")
    u.add_argument("syx")
    u.add_argument("-o", "--output")
    u.set_defaults(func=cmd_unpack)

    r = sub.add_parser("repack", help="Build SYX from modified BIN using an original SYX as template")
    r.add_argument("template_syx")
    r.add_argument("bin")
    r.add_argument("output")
    r.set_defaults(func=cmd_repack)

    t = sub.add_parser("roundtrip", help="Unpack then rebuild and demand a byte-identical SYX")
    t.add_argument("syx")
    t.add_argument("-o", "--output")
    t.set_defaults(func=cmd_roundtrip)

    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
