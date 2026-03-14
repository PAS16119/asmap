f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()
import re

# Get the inline scripts
scripts=re.findall(r'<script>(.*?)</script>',f,re.DOTALL)
print('Scripts found:',len(scripts))
print('Script 0 starts with:',scripts[0][:80])

# Find where api.js is
api_line=f[:f.find('assets/api.js')].count('\n')+1
# Find where first inline script is  
s1_line=f[:f.find('<script>')].count('\n')+1
# Find where nav divs are
nav_line=f[:f.find('onclick="go(')].count('\n')+1

print('api.js at line:',api_line)
print('First inline script at line:',s1_line)
print('First nav onclick at line:',nav_line)
