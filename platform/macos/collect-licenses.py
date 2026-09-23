"""Include installed dependencies' license notices in the app bundle."""
from importlib.metadata import distributions

for dist in sorted(distributions(), key=lambda item: item.metadata['Name'].lower()):
    print(f"\n{'=' * 72}\n{dist.metadata['Name']} {dist.version}\n")
    print(dist.metadata.get('License-Expression') or dist.metadata.get('License') or '')
    for file in dist.files or []:
        if any(part.lower().startswith(('license', 'copying', 'notice')) for part in file.parts):
            path = dist.locate_file(file)
            if path.is_file():
                print(f'\n--- {file} ---\n{path.read_text(errors="replace")}')
