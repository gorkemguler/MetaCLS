"""Exercise the frozen CLI in isolation, including the bundled ExifTool."""
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import pikepdf
from PIL import Image

app = Path(sys.argv[1]).resolve()
exe = app / 'Contents/MacOS/MetaCLS Drop'
with tempfile.TemporaryDirectory(prefix='metacls smoke ') as directory:
    root = Path(directory)
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(('PYTHON', 'METACLS', 'VIRTUAL_ENV', 'DYLD', 'PERL'))}
    env.update(PATH='/usr/bin:/bin:/usr/sbin:/sbin', HOME=directory)

    def cli(*args):
        result = subprocess.run([str(exe), '--cli', *args], cwd=root, env=env,
                                capture_output=True, text=True, timeout=120)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
        return result.stdout

    assert 'metacls, version' in cli('--version')
    pdf_path = root / 'private document.pdf'
    pdf = pikepdf.new()
    pdf.add_blank_page()
    pdf.docinfo['/Author'] = 'Private Author'
    pdf.save(pdf_path)
    pdf.close()
    image_path = root / 'private image.jpg'
    exif = Image.Exif()
    exif[315] = 'Private Photographer'
    Image.new('RGB', (16, 16), 'green').save(image_path, exif=exif)
    office_path = root / 'private document.docx'
    with zipfile.ZipFile(office_path, 'w') as archive:
        archive.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')
        archive.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body/></w:document>')
        archive.writestr('docProps/core.xml', '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:creator>Private Author</dc:creator></cp:coreProperties>')
    for path in (pdf_path, image_path, office_path):
        cli('clean', '--in-place', '--yes', '--no-json-report', '--no-html-report', '--', str(path))
    with pikepdf.open(pdf_path) as cleaned:
        assert '/Author' not in cleaned.docinfo
    with Image.open(image_path) as cleaned:
        assert not cleaned.getexif().get(315)
    with zipfile.ZipFile(office_path) as cleaned:
        assert 'docProps/core.xml' not in cleaned.namelist() or b'Private Author' not in cleaned.read('docProps/core.xml')
    exiftool = app / 'Contents/Resources/vendor/exiftool/exiftool'
    result = subprocess.run([str(exiftool), '-ver'], cwd=root, env=env,
                            capture_output=True, text=True, check=True)
    assert result.stdout.strip() == '13.59'
    print('PASS: frozen CLI, PDF, JPEG/ExifTool and Office cleaning with system-only PATH')
