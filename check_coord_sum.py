fc=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\routes\coordinator.py','r',encoding='utf-8').read()
tc=fc.find('teacher-summary')
print(fc[tc:tc+1200])
