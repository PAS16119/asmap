f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\supervisor.html','r',encoding='utf-8').read()
import re
scripts=re.findall(r'<script>(.*?)</script>',f,re.DOTALL)
print('SUPERVISOR inline scripts count:',len(scripts))
for i,s in enumerate(scripts):
    print('--- Script',i,'(first 400 chars) ---')
    print(s[:400])
    print()
