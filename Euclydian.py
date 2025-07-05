import re
import gi
import cairo  # ← pycairo (installed via apt or pip)
import fontTools
import numpy
from bs4 import BeautifulSoup
# Ensure the necessary GObject introspection versions are loaded
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo

class Translator:
    FONT_SIZES = {
        "Title": 24,
        "Subtitle": 16,
        "Body": 12,
        "Footnote": 8
    }

    def __init__(self, output_file, textfile, font_family):
        self.textfile = textfile
        self.output_file = output_file
        self.font_family = font_family
        self.lines = []

        if self.textfile:
            self.auto()
        else:
            self.manual()

    def clean_text(self, content):
        content = ''.join(c for c in content if c.isalpha() or c.isspace())
        content = content.replace(" ", "    ")  # Quadruple space
        return content.upper()

    def layout_lines(self, width=800, padding=10):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, 1)
        context = cairo.Context(surface)
        layout = PangoCairo.create_layout(context)

        total_height = padding
        for style, content, _ in self.lines:  # <- Note the added `_` for align
            font_size = self.FONT_SIZES.get(style, self.FONT_SIZES["Body"]) * Pango.SCALE
            desc = Pango.FontDescription(f"{self.font_family} {font_size // Pango.SCALE}")
            layout.set_font_description(desc)
            layout.set_text(content, -1)
            _, logical = layout.get_pixel_extents()
            total_height += logical.height + padding

        return width, total_height

    def draw_lines(self):
        width, height = self.layout_lines()
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
        context = cairo.Context(surface)
        layout = PangoCairo.create_layout(context)

        y = 10
        for style, content, align in self.lines:
            if align == "break":
                y += 20  # Extra vertical space for breaks
                continue

            font_size = self.FONT_SIZES.get(style, self.FONT_SIZES["Body"]) * Pango.SCALE
            desc = Pango.FontDescription(f"{self.font_family} {font_size // Pango.SCALE}")
            layout.set_font_description(desc)
            layout.set_text(content, -1)
            PangoCairo.update_layout(context, layout)

            _, logical = layout.get_pixel_extents()
            if align == "center":
                x = (width - logical.width) // 2
            elif align == "right":
                x = width - logical.width - 10
            else:
                x = 10

            context.move_to(x, y)
            PangoCairo.show_layout(context, layout)
            y += logical.height + 10

            surface.write_to_png(self.output_file)

    def manual(self):
        print("Enter your text with formatting (e.g., Title:My Title). Enter a blank line to finish.")
        while True:
            current = input()
            if not current.strip():
                break
            if ':' not in current:
                continue
            style, content = current.split(":", 1)
            cleaned = self.clean_text(content.strip())
            self.lines.append((style.strip(), cleaned))

        self.draw_lines()

    def auto(self):
        with open(self.textfile, "r", encoding="utf-8") as f:
            html = f.read()

        soup = BeautifulSoup(html, "html.parser")

        tag_style_map = {
            "h1": "Title",
            "h2": "Subtitle",
            "p": "Body",
            "small": "Footnote",
            "footer": "Footnote"
        }

        for tag in soup.body.descendants:
            if isinstance(tag, str):
                continue  # Skip NavigableString directly
            tag_name = tag.name.lower()

            # Explicit line break
            if tag_name == "br":
                self.lines.append(("Body", "", "break"))
                continue

            if tag_name not in tag_style_map:
                continue

            # Get alignment
            align = tag.get("align", "").lower()
            if not align and tag.has_attr("style"):
                match = re.search(r"text-align\s*:\s*(\w+)", tag["style"], re.IGNORECASE)
                if match:
                    align = match.group(1).lower()
            if align not in ["center", "right"]:
                align = "left"

            text = tag.get_text(strip=True)
            if not text:
                continue

            cleaned = self.clean_text(text)
            style = tag_style_map[tag_name]
            self.lines.append((style, cleaned, align))
