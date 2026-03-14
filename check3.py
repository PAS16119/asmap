f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\assets\api.js','r',encoding='utf-8').read()
mn=f.find('makeNav')
print('makeNav in api.js at pos:',mn)
if mn>=0:
    print(f[mn:mn+200])
