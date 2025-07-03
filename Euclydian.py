import numpy
from PIL import Image, ImageDraw, ImageFont
import fontTools

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
        if self.textfile:
            self.multiline()
        else:
            self.oneline()
    def oneline(self):
        pass
    
    def multiline(self):
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
