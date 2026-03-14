import re
f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()

# Extract all inline scripts
inline_scripts=re.findall(r'<script>(.*?)</script>',f,re.DOTALL)

# Remove all inline scripts from body
f=re.sub(r'<script>.*?</script>','' ,f,flags=re.DOTALL)

# Rebuild them all as one block and inject into head after api.js
combined='<script>\n'+''.join(inline_scripts)+'\n</script>'
f=f.replace('</head>', combined+'\n</head>')

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','w',encoding='utf-8').write(f)
print('Done!')
