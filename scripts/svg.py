from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

BLOCK_WIDTH = 300
BLOCK_HEIGHT = 400
BASELINE_Y = 200
VERTICAL_OFFSET = 25 
DIACRITIC_LENGTH = 50
MIDDLE_LINE_X = BLOCK_WIDTH // 2
DOT_RADIUS = 10

# vowels
vowel_props = {
    "e": {"type": "light", "height": "high"},
    "a": {"type": "light", "height": "mid"},
    "oh": {"type": "light", "height": "low"},
    "uh": {"type": "neut", "height": None},
    "i": {"type": "dark", "height": "high"},
    "o": {"type": "dark", "height": "mid"},
    "u": {"type": "dark", "height": "low"}
}

VOWELS = set(vowel_props.keys())
GLIDES = {"w", "y"}

# consonants
CONSONANT_SHAPES = {
    "m": "square", "p": "square", "b": "square", "f": "square",
    "n": "triangle", "t": "triangle", "d": "triangle", "s": "triangle", "l": "triangle",
    "ng": "circle", "k": "circle", "g": "circle", "h": "circle"
}

CONSONANT_DIACRITICS = {
    "p": "left",
    "b": "right",
    "f": "down",
    "t": "left",
    "d": "right",
    "s": "down",
    "l": "dot",
    "m": None,
    "n": None,
    "ng": None,
    "k": "left",
    "g": "right",
    "h": "down",
    "w": None,
    "y": None
}

def parse_syllable(syllable):
    initial = None
    glide = None
    vowel = None
    final = None

    for v in sorted(VOWELS, key=len, reverse=True):
        if v in syllable:
            vowel = v
            break
    if not vowel:
        raise ValueError(f"No vowel in {syllable}")

    idx = syllable.find(vowel)
    before = syllable[:idx]
    after = syllable[idx + len(vowel):]

    # glide detection
    if before[-1] in GLIDES:
        glide = before[-1]
        initial = before[:-1] if len(before) > 1 else None
    else:
        initial = before if before else None

    final = after if after else None
    return initial, glide, vowel, final

def draw_consonant(svg, x_offset, consonant, final=False, row_offset=0):
    shape = CONSONANT_SHAPES.get(consonant)
    cx = x_offset + 150
    cy = 100 + (final * 200) + row_offset

    if shape == "square":
        SubElement(svg, "rect", {
            "x": str(cx - 50), "y": str(cy - 50),
            "width": "100", "height": "100",
            "style": "fill:#000;stroke-width:5;stroke:white"
        })
    elif shape == "triangle":
        SubElement(svg, "polygon", {
            "points": f"{cx},{cy-50} {cx-57.74},{cy+50} {cx+57.74},{cy+50}",
            "style": "fill:#000;stroke-width:5;stroke:white"
        })
    elif shape == "circle":
        SubElement(svg, "circle", {
            "cx": str(cx), "cy": str(cy),
            "r": "50",
            "style": "fill:#000;stroke-width:5;stroke:white"
        })

    # draw diacritic if any
    typ = CONSONANT_DIACRITICS.get(consonant)
    
    if not typ:
        return

    if final and typ in {"left", "right"}:
        typ = "up"

    if shape == "triangle":
        h = w = 100
        tri_top = (cx, cy - h/2)
        tri_left = (cx - w/2, cy + h/2)
        tri_right = (cx + w/2, cy + h/2)

        # centroid
        centroid = ((tri_top[0] + tri_left[0] + tri_right[0]) / 3,
                    (tri_top[1] + tri_left[1] + tri_right[1]) / 3)

        if typ == "left":
            x2, y2 = ((tri_top[0] + tri_left[0]) / 2, (tri_top[1] + tri_left[1]) / 2)
        elif typ == "right":
            x2, y2 = ((tri_top[0] + tri_right[0]) / 2, (tri_top[1] + tri_right[1]) / 2)
        elif typ == "down":
            x2, y2 = ((tri_left[0] + tri_right[0]) / 2, (tri_left[1] + tri_right[1]) / 2)
        elif typ == "up":
            x2, y2 = tri_top
        elif typ == "dot":
            SubElement(svg, "circle", {
                "cx": str(centroid[0]), "cy": str(centroid[1]),
                "r": str(DOT_RADIUS),
                "style": "fill:white;stroke-width:0"
            })
            return

        SubElement(svg, "line", {
            "x1": str(centroid[0]), "y1": str(centroid[1]),
            "x2": str(x2), "y2": str(y2),
            "style": "stroke:white;stroke-width:5"
        })

    elif shape in {"square", "circle"}:
        if typ == "left":
            x2, y2 = cx - DIACRITIC_LENGTH, cy
        elif typ == "right":
            x2, y2 = cx + DIACRITIC_LENGTH, cy
        elif typ == "down":
            x2, y2 = cx, cy + DIACRITIC_LENGTH
        elif typ == "up":
            x2, y2 = cx, cy - DIACRITIC_LENGTH

        SubElement(svg, "line", {
            "x1": str(cx), "y1": str(cy),
            "x2": str(x2), "y2": str(y2),
            "style": "stroke:white;stroke-width:5"
        })

def word_to_svg_points(word, x_offset, row_offset=0):
    initial, glide, vowel, final = parse_syllable(word)
    start_x = x_offset + 50
    end_x = x_offset + 250
    start_y = BASELINE_Y + row_offset
    end_y = BASELINE_Y + row_offset
    points = []

    # glide vertical
    if glide == "w":
        points.append(f"{start_x},{start_y - VERTICAL_OFFSET}")
    elif glide == "y":
        points.append(f"{start_x},{start_y + VERTICAL_OFFSET}")

    # baseline
    points.append(f"{start_x},{start_y}")
    points.append(f"{end_x},{end_y}")

    # right bend for vowel
    vp = vowel_props.get(vowel)
    if vp and vowel != "uh":
        bend_y = end_y - VERTICAL_OFFSET if vp["type"] == "light" else end_y + VERTICAL_OFFSET
        points.append(f"{end_x},{bend_y}")

    # middle line
    middle_line = None
    if vp:
        x_mid = x_offset + MIDDLE_LINE_X
        if vp["height"] == "high":
            middle_line = (x_mid, BASELINE_Y, x_mid, BASELINE_Y - VERTICAL_OFFSET)
        elif vp["height"] == "mid":
            middle_line = (x_mid, BASELINE_Y, x_mid, BASELINE_Y)
        elif vp["height"] == "low":
            middle_line = (x_mid, BASELINE_Y, x_mid, BASELINE_Y + VERTICAL_OFFSET)

    return points, middle_line, initial, final

def text_to_svg(text):
    lines = text.split("\n")
    max_words_in_line = max(len(line.split()) for line in lines)
    svg_width = max_words_in_line * BLOCK_WIDTH
    svg_height = len(lines) * BLOCK_HEIGHT

    svg = Element("svg", {
        "xmlns": "http://www.w3.org/2000/svg",
        "width": str(svg_width),
        "height": str(svg_height),
        "style": "background-color:#000"
    })
    SubElement(svg, "rect", {"width": "100%", "height": "100%", "fill": "#000"})

    for row_index, line in enumerate(lines):
        words = line.split(" ")
        row_offset = row_index * BLOCK_HEIGHT  # vertical offset for this row

        for i, word in enumerate(words):
            x_offset = i * BLOCK_WIDTH
            try:
                points, middle_line, initial, final = word_to_svg_points(word, x_offset)
            except:
                pass
            else:
                # adjust all y-coordinates in points for row offset
                points = [f"{x},{float(y)+row_offset}" for x, y in (pt.split(",") for pt in points)]

                # draw initial consonant if present
                if initial:
                    draw_consonant(svg, x_offset, initial, final=False, row_offset=row_offset)

                # polyline for vowel/glide
                SubElement(svg, "polyline", {
                    "points": " ".join(points),
                    "style": "fill:#000;stroke-width:5;stroke:white"
                })

                # middle line
                if middle_line:
                    x1, y1, x2, y2 = middle_line
                    SubElement(svg, "line", {
                        "x1": str(x1), "y1": str(y1 + row_offset),
                        "x2": str(x2), "y2": str(y2 + row_offset),
                        "style": "fill:#000;stroke-width:5;stroke:white"
                    })

                # draw final consonant if present
                if final:
                    draw_consonant(svg, x_offset, final, final=True, row_offset=row_offset)

    rough_string = tostring(svg, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

# example usage
text = "puh tuh kuh\nbuh duh guh\nmuh nuh nguh \nfuh suh huh\n luh"
svg_code = text_to_svg(text)
with open("test.svg", "w") as f:
    f.write(svg_code)
