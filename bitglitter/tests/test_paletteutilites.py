import pytest


from bitglitter.palettes.paletteutilities import color_distance


def test_color_distance_with_default_1bit_palette():
    t_palette = ((0,0,0), (255,255,255))
    t_expect = 441.67
    t_result = color_distance(t_palette)
    assert len(t_palette) == 2 # number of colors
    assert t_expect == t_result

def test_color_distance_with_alternate_1bit_palette():
    t_palette = ((255, 0, 255), (0, 255, 255))
    t_expect = 360.62
    t_result = color_distance(t_palette)
    assert len(t_palette) == 2 # number of colors
    assert t_expect == t_result

def test_color_distance_with_default_2bit_palette():
    t_palette = ((0,0,0), (255,0,0), (0,255,0), (0,0,255))
    t_expect = 255
    t_result = color_distance(t_palette)
    assert len(t_palette) == 4 # number of colors
    assert t_expect == t_result

def test_color_distance_with_alternate_2bit_palette():
    t_palette = ((0, 0, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255))
    t_expect = 360.62
    t_result = color_distance(t_palette)
    assert len(t_palette) == 4 # number of colors
    assert t_expect == t_result


def test_color_distance_with_default_3bit_palette():
    t_palette = ((0,0,0), (255,0,0), (0,255,0), (0,0,255), (255,255,0), (0,255,255),
                (255,0,255), (255,255,255))
    t_expect = 255
    t_result = color_distance(t_palette)
    assert len(t_palette) == 8 # number of colors
    assert t_expect == t_result

def test_color_distance_with_default_4bit_palette():
    t_palette = ((0,0,0), (128,128,128), (192,192,192), (128,0,0), (255,0,0), (128,128,0), 
                (255,255,0), (0,255,0), (0,128,128), (0,128,0), (0,0,128), (0,0,255), 
                (0,255,255), (128,0,128), (255,0,255), (255,255,255))
    t_expect = 109.12
    t_result = color_distance(t_palette)
    assert len(t_palette) == 16 # number of colors
    assert t_expect == t_result

def test_color_distance_with_default_6bit_palette():
    t_palette = ((0,0,0), (0,0,85), (0,0,170), (0,0,255), (0,85,0), (0,85,85), 
                (0,85,170), (0,85,255), (0,170,0), (0,170,85),(0,170,170), 
                (0,170,255), (0,255,0), (0,255,85), (0,255,170), (0,255,255), 
                (85,0,0),(85,0,85), (85,0,170), (85,0,255), (85,85,0), (85,85,85), 
                (85,85,170), (85,85,255),(85,170,0), (85,170,85), (85,170,170), 
                (85,170,255), (85,255,0), (85,255,85), (85,255,170), (85,255,255), 
                (170,0,0), (170,0,85), (170,0,170), (170,0,255), (170,85,0), 
                (170,85,85),(170,85,170), (170,85,255), (170,170,0), (170,170,85), 
                (170,170,170), (170,170,255),(170,255,0), (170,255,85), (170,255,170), 
                (170,255,255), (255,0,0), (255,0,85), (255,0,170), (255,0,255), 
                (255,85,0), (255,85,85), (255,85,170), (255,85,255), (255,170,0), 
                (255,170,85), (255,170,170), (255,170,255), (255,255,0), (255,255,85), 
                (255,255,170), (255,255,255))
    t_expect = 85
    t_result = color_distance(t_palette)
    assert len(t_palette) == 64 # number of colors
    assert t_expect == t_result


def test_color_distance_with_duplicate_values():
    t_palette = ((0,0,0), (255,0,0), (0,255,0), (0,0,0))
    t_expect = 0
    t_result = color_distance(t_palette)
    assert len(t_palette) == 4 # number of colors
    assert t_expect == t_result


