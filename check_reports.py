fa=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','r',encoding='utf-8').read()
pos=fa.find('By Class')
print(repr(fa[pos-200:pos+400]))
