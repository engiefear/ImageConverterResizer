from pathlib import Path
import re

ROOT = Path('GameHelper2/Plugins/StashUtility')

# Give the customized plugin a distinct CLR namespace/type identity so it can
# live next to the original StashUtility without GameHelper de-duplicating it.
for path in ROOT.rglob('*.cs'):
    text = path.read_text(encoding='utf-8')
    text = re.sub(r'\bStashUtility\b', 'StashUtility_Advanced', text)
    text = text.replace('StashUtilityCore', 'StashUtility_AdvancedCore')
    path.write_text(text, encoding='utf-8')

# Distinct assembly/file name. Keep the project filename/path untouched because
# GameHelper2's build layout expects Plugins/StashUtility/StashUtility.csproj.
csproj = ROOT / 'StashUtility.csproj'
text = csproj.read_text(encoding='utf-8')
anchor = '    <TargetFramework>net10.0-windows</TargetFramework>\n'
insert = '    <AssemblyName>StashUtility_Advanced</AssemblyName>\n    <RootNamespace>StashUtility_Advanced</RootNamespace>\n'
if '<AssemblyName>StashUtility_Advanced</AssemblyName>' not in text:
    if anchor not in text:
        raise RuntimeError('Could not find TargetFramework anchor in StashUtility.csproj')
    text = text.replace(anchor, anchor + insert, 1)
csproj.write_text(text, encoding='utf-8')

# Sanity checks: the original exact namespace and original core type must be gone.
combined = '\n'.join(p.read_text(encoding='utf-8') for p in ROOT.rglob('*.cs'))
if re.search(r'namespace\s+StashUtility(?:\.|\s*\{)', combined):
    raise RuntimeError('Original StashUtility namespace still present after rename')
if 'class StashUtilityCore' in combined:
    raise RuntimeError('Original StashUtilityCore type still present after rename')

print('Advanced identity applied: StashUtility_Advanced / StashUtility_AdvancedCore')
