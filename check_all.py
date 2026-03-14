f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()
import re
# Find ALL const/let/var go declarations
all_go=[(m.start(), f[m.start():m.start()+60]) for m in re.finditer(r'(?:const|let|var)\s+go\b',f)]
print('All go declarations:')
for pos,text in all_go:
    line=f[:pos].count('\n')+1
    print(f'  Line {line}: {repr(text)}')
print()
# Check api.js script tag position vs inline script
api_pos=f.find('assets/api.js')
script1_pos=f.find('<script>')
print('First <script> tag at line:',f[:script1_pos].count('\n')+1)
print('api.js loaded at line:',f[:api_pos].count('\n')+1)
print('api.js loads AFTER inline script:',api_pos>script1_pos)
