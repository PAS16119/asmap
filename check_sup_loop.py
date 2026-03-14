fs=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\routes\supervisor.py','r',encoding='utf-8').read()
# Show the exact teacher loop in supervisor
ts=fs.find('for t in teac')
print(repr(fs[ts:ts+300]))
