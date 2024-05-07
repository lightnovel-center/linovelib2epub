# pip install fontTools
from fontTools.ttLib import TTFont

read_font = TTFont('read.woff2')


def get_glyph_to_text_mapping(font_file_path):
    font = TTFont(font_file_path)
    font_map = font.getBestCmap()
    print(font_map)
    # { 59676: 'uniE91C',...}


if __name__ == '__main__':
    get_glyph_to_text_mapping('read.woff2')
