f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()

# Remove api.js script tag from body
f=f.replace('<script src="assets/api.js"></script>\n','')
f=f.replace('<script src="assets/api.js"></script>','')

# Add it in head before </head>
f=f.replace('</head>','<script src="assets/api.js"></script>\n</head>')

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','w',encoding='utf-8').write(f)
print('Done!')
