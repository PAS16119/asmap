f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()

# Remove the second duplicate go = makeNav block (the one at line 183)
# It looks like the old one we added earlier inside DOMContentLoaded
old = '''const go = makeNav(sectionLoaded, {
  overview: loadOverview,
  record:   loadRecordSection,
  history:  loadHistorySection,
  monitoring: initCoordMonitoring,
  teacherSummary: loadCoordTeacherSummary,
});'''

# Only remove the SECOND occurrence
first=f.find(old)
second=f.find(old, first+1)
print('First at:',first,'Second at:',second)
if second>=0:
    f=f[:second]+f[second+len(old):]
    print('Removed second duplicate')
else:
    print('No second duplicate found - checking differently')

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','w',encoding='utf-8').write(f)
print('Done!')
