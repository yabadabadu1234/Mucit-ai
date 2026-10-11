import subprocess, sys, glob, re
for f in sorted(glob.glob('/home/user/Mucit-ai/ele224l_on_calisma/out/*.pdf')):
    t = subprocess.run(['pdftotext','-layout',f,'-'],capture_output=True,text=True).stdout
    bad = [m for m in ['%%','[[','⟦','nan','None','**','$'] if m in t]
    pages = subprocess.run(['pdfinfo',f],capture_output=True,text=True).stdout.split('Pages:')[1].split()[0]
    print(f.split('/')[-1], 'pages', pages, 'BAD:' , bad)
    for m in bad:
        for ln in t.split('\n'):
            if m in ln: print('   ', m, '->', ln.strip()[:140]); break
