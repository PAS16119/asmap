f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()
import re
scripts=re.findall(r'<script>(.*?)</script>',f,re.DOTALL)
print('Inline scripts count:',len(scripts))
for i,s in enumerate(scripts):
    print('--- Script',i,'---')
    print(s[:600])
    print()
