fa=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','r',encoding='utf-8').read()
pos=fa.find('report-by-class')
# Find the JS that populates these
rpos=fa.find('loadReports')
print('loadReports function:')
print(fa[rpos:rpos+800])
