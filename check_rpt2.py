fa=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','r',encoding='utf-8').read()
pos=fa.find('async function loadReports')
print(fa[pos:pos+1000])
