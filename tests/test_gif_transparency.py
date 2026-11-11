# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license

from io import BytesIO
from os.path import abspath, dirname, join

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine

IMAGES_PATH = abspath(join(dirname(__file__), "../course/images"))
SIZE = (240, 160)


def load_source():
    with open(join(IMAGES_PATH, "sticker.gif"), "rb") as image_file:
        return image_file.read()


def resize_to_gif():
    config = Config(
        ENGINE="thumbor.engines.pil",
        ALLOW_ANIMATED_GIFS=False,
        PILLOW_PRESERVE_INDEXED_MODE=True,
    )
    engine = Engine(Context(config=config))
    engine.load(load_source(), ".gif")
    assert engine.original_mode == "P"
    engine.resize(*SIZE)
    return Image.open(BytesIO(engine.read(".gif")))


def alpha_of(image):
    return image.convert("RGBA").getchannel("A")


def count_transparent(alpha):
    return sum(1 for value in alpha.getdata() if value == 0)


def test_source_has_transparency():
    source = Image.open(BytesIO(load_source()))
    assert "transparency" in source.info
    assert count_transparent(alpha_of(source)) > 0


def test_resized_gif_carries_a_transparency_index():
    result = resize_to_gif()
    assert result.format == "GIF"
    assert result.size == SIZE
    assert "transparency" in result.info


def test_resized_gif_keeps_transparent_pixels_transparent():
    source = Image.open(BytesIO(load_source()))
    expected = alpha_of(source).resize(SIZE, Image.Resampling.NEAREST)
    result = alpha_of(resize_to_gif())

    expected_count = count_transparent(expected)
    assert expected_count > 0
    assert count_transparent(result) >= expected_count * 0.9
    assert result.getpixel((0, 0)) == expected.getpixel((0, 0)) == 0
    assert result.getpixel((SIZE[0] // 2, SIZE[1] // 2)) == 255
