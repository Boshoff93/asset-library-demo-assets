"""Generates every asset in this repo, so all of it is original and free to reuse (CC0).

Run from the repo root: python3 tools/generate_assets.py
"""

import json
import math
import random
import struct
import wave
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


# Images


def write_png(path: Path, width: int, height: int, pixel) -> None:
    rows = bytearray()
    for y in range(height):
        rows.append(0)
        for x in range(width):
            rows.extend(pixel(x, y))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))

    header = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(bytes(rows), 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def mix(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def checker(x, y):
    return (235, 235, 235) if (x // 64 + y // 64) % 2 == 0 else (90, 96, 110)


def sunset(x, y):
    t = y / 511
    sky = mix((255, 170, 90), (70, 40, 120), t)
    sun = math.hypot(x - 256, y - 330)
    return mix((255, 236, 170), sky, min(1, max(0, (sun - 70) / 30)))


def bricks(x, y):
    row = y // 32
    offset = 32 if row % 2 else 0
    in_mortar = y % 32 < 4 or (x + offset) % 64 < 4
    if in_mortar:
        return (200, 195, 185)
    shade = ((x + offset) // 64 * 37 + row * 53) % 30
    return (150 + shade, 62 + shade // 2, 48)


def hazard(x, y):
    return (250, 200, 30) if ((x + y) // 48) % 2 == 0 else (30, 30, 30)


# Models


def write_glb(path: Path, name: str, positions, normals, indices, color) -> None:
    pos_bytes = b"".join(struct.pack("<3f", *p) for p in positions)
    nrm_bytes = b"".join(struct.pack("<3f", *n) for n in normals)
    idx_bytes = b"".join(struct.pack("<H", i) for i in indices)
    idx_bytes += b"\x00" * (-len(idx_bytes) % 4)
    binary = pos_bytes + nrm_bytes + idx_bytes
    gltf = {
        "asset": {"version": "2.0", "generator": "asset-library-demo-assets"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": name}],
        "materials": [
            {
                "name": f"{name}Material",
                "pbrMetallicRoughness": {
                    "baseColorFactor": [*color, 1.0],
                    "metallicFactor": 0.0,
                    "roughnessFactor": 0.8,
                },
            }
        ],
        "meshes": [
            {
                "name": name,
                "primitives": [
                    {"attributes": {"POSITION": 0, "NORMAL": 1}, "indices": 2, "material": 0}
                ],
            }
        ],
        "buffers": [{"byteLength": len(binary)}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(pos_bytes), "target": 34962},
            {
                "buffer": 0,
                "byteOffset": len(pos_bytes),
                "byteLength": len(nrm_bytes),
                "target": 34962,
            },
            {
                "buffer": 0,
                "byteOffset": len(pos_bytes) + len(nrm_bytes),
                "byteLength": len(indices) * 2,
                "target": 34963,
            },
        ],
        "accessors": [
            {
                "bufferView": 0,
                "componentType": 5126,
                "count": len(positions),
                "type": "VEC3",
                "min": [min(p[i] for p in positions) for i in range(3)],
                "max": [max(p[i] for p in positions) for i in range(3)],
            },
            {"bufferView": 1, "componentType": 5126, "count": len(normals), "type": "VEC3"},
            {"bufferView": 2, "componentType": 5123, "count": len(indices), "type": "SCALAR"},
        ],
    }
    json_bytes = json.dumps(gltf, separators=(",", ":")).encode()
    json_bytes += b" " * (-len(json_bytes) % 4)
    body = (
        struct.pack("<I4s", len(json_bytes), b"JSON")
        + json_bytes
        + struct.pack("<I4s", len(binary), b"BIN\x00")
        + binary
    )
    path.write_bytes(struct.pack("<4sII", b"glTF", 2, 12 + len(body)) + body)


def add_face(positions, normals, indices, corners):
    """Adds a flat face from counter-clockwise corners, as triangles fanned from the first."""
    a, b, c = corners[0], corners[1], corners[2]
    u = [b[i] - a[i] for i in range(3)]
    v = [c[i] - a[i] for i in range(3)]
    n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
    length = math.sqrt(sum(value * value for value in n))
    n = [value / length for value in n]
    start = len(positions)
    positions.extend(corners)
    normals.extend([n] * len(corners))
    for i in range(1, len(corners) - 1):
        indices.extend([start, start + i, start + i + 1])


def crate():
    positions, normals, indices = [], [], []
    s = 1.0
    faces = [
        [(-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s)],
        [(s, -s, -s), (-s, -s, -s), (-s, s, -s), (s, s, -s)],
        [(-s, s, s), (s, s, s), (s, s, -s), (-s, s, -s)],
        [(-s, -s, -s), (s, -s, -s), (s, -s, s), (-s, -s, s)],
        [(s, -s, s), (s, -s, -s), (s, s, -s), (s, s, s)],
        [(-s, -s, -s), (-s, -s, s), (-s, s, s), (-s, s, -s)],
    ]
    for face in faces:
        add_face(positions, normals, indices, face)
    return positions, normals, indices


def pyramid():
    positions, normals, indices = [], [], []
    apex = (0.0, 1.5, 0.0)
    base = [(-1.0, 0.0, 1.0), (1.0, 0.0, 1.0), (1.0, 0.0, -1.0), (-1.0, 0.0, -1.0)]
    for i in range(4):
        add_face(positions, normals, indices, [base[i], base[(i + 1) % 4], apex])
    add_face(positions, normals, indices, list(reversed(base)))
    return positions, normals, indices


def gem(sides=8):
    positions, normals, indices = [], [], []
    top, bottom = (0.0, 0.6, 0.0), (0.0, -1.0, 0.0)
    ring = [
        (math.cos(2 * math.pi * i / sides), 0.0, -math.sin(2 * math.pi * i / sides))
        for i in range(sides)
    ]
    for i in range(sides):
        a, b = ring[i], ring[(i + 1) % sides]
        add_face(positions, normals, indices, [a, b, top])
        add_face(positions, normals, indices, [b, a, bottom])
    return positions, normals, indices


# Audio

RATE = 44100


def write_wav(path: Path, samples) -> None:
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(RATE)
        out.writeframes(
            b"".join(struct.pack("<h", round(max(-1, min(1, s)) * 30000)) for s in samples)
        )


def coin():
    samples = []
    for freq, length in ((988, 0.08), (1319, 0.35)):
        n = int(RATE * length)
        samples += [
            0.6 * math.sin(2 * math.pi * freq * i / RATE) * math.exp(-6 * i / n) for i in range(n)
        ]
    return samples


def click():
    rng = random.Random(7)
    n = int(RATE * 0.04)
    return [rng.uniform(-1, 1) * 0.7 * math.exp(-60 * i / n) for i in range(n)]


def hum():
    n = int(RATE * 4)
    out = []
    for i in range(n):
        t = i / RATE
        chord = sum(math.sin(2 * math.pi * f * t) for f in (110, 165, 220)) / 3
        swell = 0.5 + 0.5 * math.sin(2 * math.pi * 0.25 * t - math.pi / 2)
        fade = min(1, t / 0.3, (4 - t) / 0.3)
        out.append(0.5 * chord * (0.4 + 0.6 * swell) * fade)
    return out


def main() -> None:
    for folder in ("decals", "models", "audio"):
        (ROOT / folder).mkdir(exist_ok=True)

    write_png(ROOT / "decals" / "checker_tiles.png", 512, 512, checker)
    write_png(ROOT / "decals" / "sunset_gradient.png", 512, 512, sunset)
    write_png(ROOT / "decals" / "brick_wall.png", 512, 512, bricks)
    write_png(ROOT / "decals" / "hazard_stripes.png", 512, 512, hazard)

    write_glb(ROOT / "models" / "crate.glb", "Crate", *crate(), (0.55, 0.36, 0.2))
    write_glb(ROOT / "models" / "pyramid.glb", "Pyramid", *pyramid(), (0.9, 0.75, 0.3))
    write_glb(ROOT / "models" / "gem.glb", "Gem", *gem(), (0.2, 0.7, 0.9))

    write_wav(ROOT / "audio" / "coin_pickup.wav", coin())
    write_wav(ROOT / "audio" / "button_click.wav", click())
    write_wav(ROOT / "audio" / "ambient_hum.wav", hum())


if __name__ == "__main__":
    main()
