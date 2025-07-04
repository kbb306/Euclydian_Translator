import re
from striprtf.striprtf import rtf_to_text
import gi
import cairo  # ← pycairo (installed via apt or pip)
import fontTools
import numpy
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
        if "\\fs" in content or "{\\rtf" in content:
            content = rtf_to_text(content)
        content = ''.join(c for c in content if c.isalpha() or c.isspace())
        content = content.replace(" ", "    ")  # Quadruple space
        return content.upper()

    def layout_lines(self, width=800, padding=10):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, 1)
        context = cairo.Context(surface)
        layout = PangoCairo.create_layout(context)

        total_height = padding
        for style, content in self.lines:
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
        for style, content in self.lines:
            font_size = self.FONT_SIZES.get(style, self.FONT_SIZES["Body"]) * Pango.SCALE
            desc = Pango.FontDescription(f"{self.font_family} {font_size // Pango.SCALE}")
            layout.set_font_description(desc)
            layout.set_text(content, -1)
            context.move_to(10, y)
            PangoCairo.update_layout(context, layout)
            PangoCairo.show_layout(context, layout)
            _, logical = layout.get_pixel_extents()
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
            raw_rtf = f.read()

        # Use striprtf to extract plain text
        plain_text = rtf_to_text(raw_rtf)

        for line in plain_text.splitlines():
            if not line.strip():
                continue
            style = "Body"  # Default for all lines unless parsing font size separately
            cleaned = self.clean_text(line.strip())
            self.lines.append((style, cleaned))

        self.draw_lines()
