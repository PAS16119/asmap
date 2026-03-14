f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()

# Fix populateSelect calls - ensure array is passed
f=f.replace(
    'UI.populateSelect("rec-class", myClasses, "class_id", "class_name", "Choose class\u2026");',
    'UI.populateSelect("rec-class", Array.isArray(myClasses)?myClasses:(myClasses.classes||[]), "class_id", "class_name", "Choose class\u2026");'
)
f=f.replace(
    'UI.populateSelect("hist-class", myClasses, "class_id", "class_name", "All My Classes");',
    'UI.populateSelect("hist-class", Array.isArray(myClasses)?myClasses:(myClasses.classes||[]), "class_id", "class_name", "All My Classes");'
)

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','w',encoding='utf-8').write(f)
print('Done!')
