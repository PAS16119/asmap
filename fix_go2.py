f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()

# Replace the broken variable declarations with correct ones including go
old = 'let myClasses = []; let activeYear = null; let selectedStudentId = null;\nconst sectionLoaded = {};\nlet go;'
new = 'let myClasses = []; let activeYear = null; let selectedStudentId = null;\nconst sectionLoaded = {};\nconst go = makeNav(sectionLoaded, {\n  overview:       loadOverview,\n  record:         loadRecordSection,\n  history:        loadHistorySection,\n  monitoring:     initCoordMonitoring,\n  teacherSummary: loadCoordTeacherSummary,\n});'

f=f.replace(old,new)

# Also remove the duplicate go = makeNav we added inside DOMContentLoaded
old2 = '  go = makeNav(sectionLoaded, {\n    overview: loadOverview,\n    record:   loadRecordSection,\n    history:  loadHistorySection,\n    monitoring: initCoordMonitoring,\n    teacherSummary: loadCoordTeacherSummary,\n  });\n  UI.initHamburger();'
new2 = '  UI.initHamburger();'

f=f.replace(old2,new2)

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','w',encoding='utf-8').write(f)
print('Done!')
