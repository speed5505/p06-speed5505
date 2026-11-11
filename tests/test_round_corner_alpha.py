# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license

from thumbor.ext.filters import _round_corner

WIDTH = 100
HEIGHT = 100
RADIUS = 30
COLOR = (200, 100, 50)


def make_opaque_rgba():
    return bytes(COLOR + (255,)) * (WIDTH * HEIGHT)


def apply_transparent_round_corner():
    data = make_opaque_rgba()
    result = _round_corner.apply(
        1, "RGBA", RADIUS, RADIUS, 255, 255, 255, WIDTH, HEIGHT, data, True
    )
    return bytes(result)


def test_transparent_round_corner_keeps_edge_color():
    result = apply_transparent_round_corner()
    wrong = []
    for index in range(0, len(result), 4):
        red, green, blue, alpha = result[index : index + 4]
        if alpha == 0:
            continue
        if (red, green, blue) != COLOR:
            wrong.append((index // 4, (red, green, blue, alpha)))
    assert not wrong, f"{len(wrong)} visible pixels changed color"


def test_transparent_round_corner_smooths_through_alpha():
    result = apply_transparent_round_corner()
    alphas = {result[index] for index in range(3, len(result), 4)}
    partial = {alpha for alpha in alphas if 0 < alpha < 255}
    assert partial, "no edge pixel has partial alpha"
