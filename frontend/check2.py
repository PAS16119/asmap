f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()
# Find the makeNav call and go function definition
import re
# Find makeNav
mn=f.find('makeNav')
print('makeNav call:')
print(f[mn:mn+300])
print()
# Find the nav items onclick
navs=re.findall(r'onclick="go\([^"]+\)"',f)
print('Nav onclick handlers:')
for n in navs:
    print(' ',n)
