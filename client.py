#!/usr/bin/env python3
import sys
from typing import Literal

import requests
from PIL import Image
from PIL import ImageOps

BLACK = (0, 0, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

type Color = tuple[Literal[255], Literal[255], Literal[255]]


def resize_image(image, width, height, fit=False):
    im = image.copy()
    if fit:
        im = ImageOps.pad(im, (width, height), color=(255, 255, 255))
    else:
        im = ImageOps.fit(im, (width, height))
    return im


def convert_image(
    infile: str,
    max_width: int,
    max_height: int,
    fit: bool = False,
    dither: bool = False,
    show: bool = False,
) -> list[tuple[Color, Color]]:
    im = Image.open(infile).convert("RGB")

    im = resize_image(im, max_width, max_height, fit)

    palette = [0, 0, 0, 255, 255, 255, 255, 0, 0]
    palimg = Image.new("P", (16, 16))
    palimg.putpalette(palette)

    im_dithered = im.quantize(
        colors=3, method=2, palette=palimg, dither=Image.FLOYDSTEINBERG
    )

    im = im_dithered.convert("RGB")

    if show:
        im.show()

    contents = []

    for y in range(0, im.size[1]):
        for x in range(0, im.size[0]):
            pixel = im.getpixel((x, y))
            contents.append(pixel)

    pixel_pairs = []
    for pixel_counter in range(0, len(contents), 2):
        pixel_pairs.append((contents[pixel_counter], contents[pixel_counter + 1]))
    return pixel_pairs


def send(ip: str, image_file: str):
    pixel_pairs = convert_image(image_file, 640, 384, dither=True, show=False)
    chunks = []
    chunk = []
    encodict = {
        (WHITE, WHITE): "f",
        (WHITE, RED): "n",
        (WHITE, BLACK): "b",
        (RED, WHITE): "h",
        (RED, RED): "p",
        (RED, BLACK): "d",
        (BLACK, WHITE): "e",
        (BLACK, RED): "m",
        (BLACK, BLACK): "a",
    }
    for pair in pixel_pairs:
        chunk.append(encodict[pair])
        if len(chunk) == 1000:
            chunks.append("".join(chunk))
            chunk = []
    else:
        if chunk:
            chunks.append("".join(chunk))

    print("Sending...")
    requests.post(f"http://{ip}/EPDu_")
    for counter, chunk in enumerate(chunks):
        print(f"Sending chunk {counter}...")
        requests.post(f"http://{ip}/{chunk}iodaLOAD_")
    requests.post(f"http://{ip}/SHOW_")
    print("Done.")


send(sys.argv[1], sys.argv[2])
