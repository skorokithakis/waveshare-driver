#!/usr/bin/env python3
import argparse
import re
import tempfile
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


def download_image(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(response.content)
        return temp_file.name


def send(ip: str, image_file: str, fit: bool = False):
    pixel_pairs = convert_image(image_file, 640, 384, fit=fit, show=False)
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


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Send an image to a specified IP address."
    )
    parser.add_argument("ip", help="The IP address to send the image to")
    parser.add_argument("image", help="The path to the image file, or a URL")
    parser.add_argument("--fit", action="store_true", help="Fit the image to the display size")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    image = args.image
    if re.match(r"https?://", args.image):
        print(f"Downloading image from {image}")
        image = download_image(image)
        print(f"Image downloaded to {image}")

    send(args.ip, image, args.fit)
