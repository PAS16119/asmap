f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()

old = 'let myClasses = []; let activeYear = null; let selectedStudentId = null;\nconst sectionLoaded = {};'
new = 'let myClasses = []; let activeYear = null; let selectedStudentId = null;\nconst sectionLoaded = {};\nlet go;'

f=f.replace(old,new)

# Also find DOMContentLoaded and add go assignment inside it after Auth check
old2 = '  if (!Auth.requireRole("coordinator")) return;\n  UI.initHamburger(); UI.initUserDisplay(); UI.loadFullBranding();'
new2 = '  if (!Auth.requireRole("coordinator")) return;\n  go = makeNav(sectionLoaded, {\n    overview: loadOverview,\n    record:   loadRecordSection,\n    history:  loadHistorySection,\n    monitoring: initCoordMonitoring,\n    teacherSummary: loadCoordTeacherSummary,\n  });\n  UI.initHamburger(); UI.initUserDisplay(); UI.loadFullBranding();'

f=f.replace(old2,new2)

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','w',encoding='utf-8').write(f)
print('Done!')
