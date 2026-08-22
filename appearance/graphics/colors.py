import colorsys

from color import Color

WHITE = Color(255, 255, 255)
BLACK = Color(0, 0, 0)

BACKGROUND = Color(111, 139, 158)

SHORE = Color.from_hex_string("#5ACCCE").lerp(WHITE, .07)
WATER = Color.from_hex_string("#4c7d9e").lerp(WHITE, .07)
HIGHLIGHTED_WATER = WATER.lerp(SHORE.lerp(WHITE, .1), .5)

MOUNTAIN = Color(173, 173, 173)
FOREST = Color(59, 134, 93).lerp(BLACK, .1)
SWAMP = Color(59, 134, 93).lerp(Color(64, 106, 173), .3)
DESERT = Color(215, 201, 60)

PAUSE_MENU_BACKGROUND = Color(0, 0, 0, 150)

DEFAULT_BUTTON = Color.from_hex_string("#8B6244")
ACTIVE_BUTTON = Color(134, 177, 18)

PLAYERS = [
    Color(173, 82, 64),
    Color(64, 106, 173),
    Color(59, 134, 93),
    Color(215, 151, 60),
    Color.from_hex_string("#61937D"),
    Color.from_hex_string("#41634D"),
    Color.from_hex_string("#AAC25A"),
    Color.from_hex_string("#CDBD50"),
    Color.from_hex_string("#DC7438"),
    Color.from_hex_string("#932E2E"),
    Color.from_hex_string("#BC6D76"),
    Color.from_hex_string("#8F5CBC"),
    Color.from_hex_string("#824570"),
    Color.from_hex_string("#AE63A7"),
]


def get_colors(colors_count: int, deepness: float = 0.7, lightness: float = 1.0) -> list[Color]:
    colors = list[Color]()
    for color in range(colors_count):
        hue = color / colors_count

        r, g, b = colorsys.hsv_to_rgb(hue, deepness, lightness)
        r_255 = int(r * 255)
        g_255 = int(g * 255)
        b_255 = int(b * 255)
        hex_color = f"#{r_255:02x}{g_255:02x}{b_255:02x}"
        colors.append(Color.from_hex_string(hex_color))
    return colors
