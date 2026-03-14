fc=open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','r',encoding='utf-8').read()

# Replace hardcoded period select with dynamic loading
old_period='''      <div><label class="form-label">Period</label>
        <select id="monPeriod" class="form-input">
          <option value="">Select Period</option>
          <option value="Period 1 (07:00-08:50)">Period 1 (07:00 - 08:50)</option>
          <option value="Period 2 (09:00-09:50)">Period 2 (09:00 - 09:50)</option>
          <option value="Period 3 (09:50-10:40)">Period 3 (09:50 - 10:40)</option>
          <option value="Period 4 (10:40-11:30)">Period 4 (10:40 - 11:30)</option>
          <option value="Period 5 (11:30-12:20)">Period 5 (11:30 - 12:20)</option>
          <option value="Period 6 (12:20-13:10)">Period 6 (12:20 - 13:10)</option>
          <option value="Period 7 (13:10-14:00)">Period 7 (13:10 - 14:00)</option>
          <option value="Extended Teaching">Extended Teaching</option>
        </select>
      </div>'''

new_period='''      <div><label class="form-label">Period</label>
        <select id="monPeriod" class="form-input">
          <option value="">Select Period</option>
        </select>
      </div>'''

if old_period in fc:
    fc=fc.replace(old_period,new_period)
    print('Period dropdown replaced in coordinator')
else:
    print('Pattern not found in coordinator - trying partial match')
    # Find any select with id monPeriod
    import re
    m=re.search(r'<select id="monPeriod".*?</select>',fc,re.DOTALL)
    if m:
        print('Found at:',m.start(),'-',m.end())
        print(repr(m.group()[:200]))

open(r'D:\ADOMBRA PROJECTS\ASMAP\ASMAP V1\ASMaP_v1.0_complete\asmap\frontend\coordinator.html','w',encoding='utf-8').write(fc)
