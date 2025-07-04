import numpy
from PIL import Image, ImageDraw, ImageFont
import fontTools
from fontTools.ttLib import TTFont
from striprtf.striprtf import rtf_to_text
import re
class Translator:
    FONT_SIZES = {
        "Title": 24,
        "Subtitle":16,
        "Body":12,
        "Footnote":8

    }

    def __init__(self,file,textfile,font_path):
        self.fonts = {
            style: ImageFont.truetype(font_path, size)
            for style, size in Translator.FONT_SIZES.items()
        }
        self.textfile = textfile
        self.file = file
        self.font_path = font_path
        self.fillcolor = self.extract_colr_cpal_colors(self.font_path)

        self.img = None
        if self.textfile is not None:
            self.auto()
        else:
            self.manual()
            
    def manual(self):
        lines = []
        print("Enter your text with formatting data (size:text). Press enter on a blank line when done.")
        while True:
            current = input()
            if not current:
                break
            lines.append(current)
                
        # Precompute total height
        total_height = 0
        line_data = []
        for line in lines:
            style, content = line.split(":", 1)
            content = self.cleanText(content)
            font = self.fonts.get(style.strip(), self.fonts["Body"])  # fallback to "Body"
            width, height = (font.getbbox(content)[2]- font.getbbox(content)[0],font.getbbox(content)[3]-font.getbbox(content)[1]) #Use bbox to get width and height.
            line_data.append((style.strip(), content, width, height))
            total_height += height + 10  # 10 px spacing

        # Determine image width (e.g. max line width)
        max_width = max(width for _, _, width, _ in line_data)

        # Create the image
        self.img = Image.new("RGBA", (max_width + 20, total_height + 20), (255, 255, 255, 0))
        draw = ImageDraw.Draw(self.img)

        # Draw each line
        y = 10
        for style, content, width, height in line_data:
            font = self.fonts[style]
            x = 10
        for c in content:
            if c == " ":
                x += font.getbbox(" ")[2] - font.getbbox(" ")[0]  # space width
                continue
            color = self.fillcolor.get(c.upper(), (0, 0, 0, 255))
            draw.text((x, y), c, font=font, fill=color)
            bbox = font.getbbox(c)
            x += bbox[2] - bbox[0]  # advance for next character
            
        y += height + 10
        self.save_image()



    def auto(self):
        # Load raw RTF content
        with open(self.textfile, "r", encoding="utf-8") as f:
            raw_rtf = f.read()

        # Extract lines with font sizes
        line_entries = re.findall(r"(\\fs\d+)?([^\\]+)", raw_rtf)
        parsed_lines = []

        for fs_tag, content in line_entries:
            if not content.strip():
                continue

            size_pt = 12  # default
            if fs_tag:
                size_halfpt = int(re.search(r"\d+", fs_tag).group())
                size_pt = size_halfpt // 2

            # Map to nearest style
            style = min(
                self.FONT_SIZES,
                key=lambda k: abs(self.FONT_SIZES[k] - size_pt)
            )
            content = self.cleanText(content)
            font = self.fonts[style]
            width, height = font.getsize(content.strip())
            parsed_lines.append((style, content, width, height))

        # Calculate image size
        total_height = sum(h + 10 for _, _, _, h in parsed_lines)
        max_width = max(w for _, _, w, _ in parsed_lines)

        self.img = Image.new("RGBA", (max_width + 20, total_height + 20), (255, 255, 255, 0))
        draw = ImageDraw.Draw(self.img)

        # Render each line
        y = 10
        for style, text, width, height in parsed_lines:
            for c in content:
                if c == " ":
                    x += font.getbbox(" ")[2] - font.getbbox(" ")[0]  # space width
                    continue
                color = self.fillcolor.get(c.upper(), (0, 0, 0, 255))
                draw.text((x, y), c, font=font, fill=color)
                bbox = font.getbbox(c)
                x += bbox[2] - bbox[0]  # advance for next character
            y += height + 10
        self.save_image()
        
    def save_image(self):
        if self.img:
            self.img.save(self.file)
        else:
            print("Image not yet rendered. Call auto() or manual() first.")

    def cleanText(self, content):
        # Detect and clean RTF if needed
        if "\\fs" in content or "{\\rtf" in content:
            content = rtf_to_text(content)

        # Keep only alphabet and space characters
        content = ''.join(c for c in content if c.isalpha() or c.isspace())

        # Expand each space to four spaces
        content = content.replace(" ", "    ")

        return content.upper()


    def extract_colr_cpal_colors(self,font_path):
        ttf = TTFont(font_path)
        
        if "COLR" not in ttf or "CPAL" not in ttf:
            print("Font does not contain COLR/CPAL tables.")
            return {}

        colr_table = ttf["COLR"]
        cpal_table = ttf["CPAL"]
        
        # Get the first palette (default)
        palettes = cpal_table.palettes
        default_palette = palettes[cpal_table.paletteTypes[0]] if cpal_table.paletteTypes else palettes[0]

        glyph_color_map = {}

        # COLR v0 format: look for ColorLayers
        if hasattr(colr_table, "ColorLayers"):
            for glyph_name in colr_table.ColorLayers:
                layers = colr_table.ColorLayers[glyph_name]
                if layers:
                    first_layer = layers[0]
                    color_index = first_layer.colorID
                    if 0 <= color_index < len(default_palette):
                        rgba = default_palette[color_index]
                        glyph_color_map[glyph_name] = rgba

        # Filter to A–Z only
        return {
            glyph: rgba for glyph, rgba in glyph_color_map.items()
            if glyph in [chr(c) for c in range(ord('A'), ord('Z') + 1)]
        }
