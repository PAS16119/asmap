import re
fc=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()
fs=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\supervisor.html','r',encoding='utf-8').read()

# Find makeNav usage in both
cm=re.findall(r'.{30}makeNav.{100}',fc)
sm=re.findall(r'.{30}makeNav.{100}',fs)
print('COORDINATOR makeNav:')
for m in cm: print(' ',m)
print()
print('SUPERVISOR makeNav:')
for m in sm: print(' ',m)
