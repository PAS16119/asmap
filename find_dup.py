f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()
import re
# Find ALL occurrences of go = makeNav or const go
matches=[(m.start(),f[m.start():m.start()+100]) for m in re.finditer(r'(const|let|var)?\s*go\s*=\s*makeNav',f)]
print('All go=makeNav declarations:')
for pos,text in matches:
    lines=f[:pos].count('\n')+1
    print(f'  Line {lines}, pos {pos}:',repr(text[:80]))
