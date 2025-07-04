import numpy
from PIL import Image, ImageDraw, ImageFont
import fontTools
from striprtf.striprtf import rtf_to_text
import re
class Translator:
    FONT_SIZES = {
        "Title": 24,
        "Subtitle":16,
        "Body":12,
        "Footnote":8

    }

    def __init__(self,file,text,textfile,font_path):
        self.fonts = {
            style: ImageFont.truetype(font_path, size)
            for style, size in Translator.FONT_SIZES.items()
        }
        self.textfile = textfile
        self.file = file
        self.text = text
        self.img = None
        if self.textfile is not None:
            self.auto()
        else:
            self.manual()
            
    def manual(self):
        lines = self.text.split("\n")  # assume lines contain style:text format like "Title:My Title"
        
        # Precompute total height
        total_height = 0
        line_data = []
        for line in lines:
            style, content = line.split(":", 1)
            font = self.fonts.get(style.strip(), self.fonts["Body"])  # fallback to "Body"
            width, height = font.getsize(content)
            line_data.append((style.strip(), content.strip(), width, height))
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
            draw.text((10, y), content, font=font)
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
            font = self.fonts[style]
            clean_text = rtf_to_text(content.strip())
            width, height = font.getsize(content.strip())
            parsed_lines.append((style, clean_text, width, height))

        # Calculate image size
        total_height = sum(h + 10 for _, _, _, h in parsed_lines)
        max_width = max(w for _, _, w, _ in parsed_lines)

        self.img = Image.new("RGBA", (max_width + 20, total_height + 20), (255, 255, 255, 0))
        draw = ImageDraw.Draw(self.img)

        # Render each line
        y = 10
        for style, text, width, height in parsed_lines:
            draw.text((10, y), text, font=self.fonts[style])
            y += height + 10
        self.save_image()
        
    def save_image(self):
        if self.img:
            self.img.save(self.file)
        else:
            print("Image not yet rendered. Call auto() or manual() first.")
