f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\models.py','r',encoding='utf-8').read()
mr=f.find('class MonitoringRecord')
print(f[mr:mr+800])
