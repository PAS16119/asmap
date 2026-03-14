f=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()
lines=f.split('\n')
for i in range(177,195):
    print(f'Line {i+1}: {repr(lines[i])}')
