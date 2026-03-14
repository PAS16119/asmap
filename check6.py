import re
fc=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()
fs=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\supervisor.html','r',encoding='utf-8').read()

cg=re.findall(r'.{10}go.{80}',fc[:500])
sg=re.findall(r'.{10}go.{80}',fs[:500])
print('COORDINATOR first 500 chars with go:')
for m in cg: print(' ',repr(m))
print()
print('SUPERVISOR first 500 chars with go:')
for m in sg: print(' ',repr(m))
print()
# Also check the inline script blocks
cscripts=re.findall(r'<script>(.*?)</script>',fc,re.DOTALL)
print('COORDINATOR inline scripts count:',len(cscripts))
for i,s in enumerate(cscripts):
    if 'go' in s or 'makeNav' in s or 'sectionLoaded' in s:
        print('Script',i,'(first 300):',s[:300])
