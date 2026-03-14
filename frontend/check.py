f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()
import re
ids=[m.group(1) for m in re.finditer(r'id="(section-[^"]+)"',f)]
print('Section IDs:',ids)
apijs=f.find('api.js')
pc=f.find('page-content')
for i in ids:
    pos=f.find('id="'+i+'"')
    print(i,'pos:',pos,'inside page-content:',pc<pos<apijs)
