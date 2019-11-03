import pytest


from bitglitter.palettes.paletteutilities import color_distance


def test_default_1bit_palette():
    t_palette = ((0,0,0), (255,255,255))
    t_expect = 441.67
    t_result = color_distance(t_palette)
    assert t_expect == t_result



