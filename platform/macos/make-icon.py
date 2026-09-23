"""Draw the existing dark/green document-and-wipe motif as a macOS icon."""
from pathlib import Path

from PIL import Image, ImageDraw

im = Image.new('RGBA', (1024, 1024))
draw = ImageDraw.Draw(im)
draw.rounded_rectangle((32, 32, 992, 992), radius=210, fill='#0c1110')
draw.rounded_rectangle((560, 245, 815, 775), radius=36, fill='#13201c', outline='#34d399', width=18)
draw.polygon([(720, 245), (815, 340), (720, 340)], fill='#34d399')
for y, width, color in [(380, 270, '#34d399'), (492, 210, '#279c7c'), (604, 145, '#1e6654')]:
    draw.rounded_rectangle((170, y, 170 + width, y + 42), radius=21, fill=color)
im.save(Path('build/macos/MetaCLS.icns'))
