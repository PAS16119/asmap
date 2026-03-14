fa=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\admin.html','r',encoding='utf-8').read()

# Find the setup section to add periods management
setup_pos=fa.find('id="section-setup"')
print('Setup section found:',setup_pos>=0)
# Find loadSetup function
ls_pos=fa.find('async function loadSetup')
print('loadSetup at:',ls_pos)
print(fa[ls_pos:ls_pos+200])
