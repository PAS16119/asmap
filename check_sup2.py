import re
fs=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\supervisor.html','r',encoding='utf-8').read()

# Show the full rec-period select and initRecordForm
m=re.search(r'id="rec-period"',fs)
print('rec-period select:')
print(repr(fs[m.start()-200:m.start()+400]))
print()
# Show initRecordForm
pos=fs.find('initRecordForm')
print('initRecordForm:')
print(fs[pos:pos+600])
