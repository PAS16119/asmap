fs=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\supervisor.html','r',encoding='utf-8').read()
import re
# Find subject loading in supervisor
pos=fs.find('subjects')
print('subjects found at:',pos)
print(repr(fs[pos-50:pos+200]))
print()
# Also find period select
m=re.search(r'id="period"',fs)
if m:
    print('period select at:',m.start())
    print(repr(fs[m.start()-100:m.start()+200]))
else:
    print('No id=period found')
    # Check what period field looks like
    p=fs.find('period')
    print('period word at:',p)
    print(repr(fs[p-50:p+150]))
