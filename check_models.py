import os
# Check what tables/models exist
f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\backend\models.py','r',encoding='utf-8').read()
# Find monitoring record model
mr=f.find('class MonitoringRecord')
print('MonitoringRecord model:')
print(f[mr:mr+400])
print()
# Find Period if exists
p=f.find('class Period')
print('Period model exists:',p>=0)
if p>=0:
    print(f[p:p+200])
