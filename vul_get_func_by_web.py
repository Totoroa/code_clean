'''
get functions by message crawled from web.
'''

'''
build the vulnerability repository.
(*)Only C/C++ related programs are considered.

1.extract the functions corresponding to vulnerabilities, and store them in (BadFunc)files.
the vulnerability lines has been marked in (BadFunc)files.
(BadFunc)file looks like: (BadFunc)cve_id$patchfilename$funcname    eg:(BadFunc)CVE-2010-3698$net#~core#~sock.c$sock_getsockopt

2.extract the functions that have been patched, and store them in (GoodFunc)files.
the added lines has been marked in (GoodFunc)files.
(GoodFunc)file looks lik: (GoodFunc)cve_id$patchfilename$funcname   eg:(GoodFunc)CVE-2010-3698$net#~core#~sock.c$sock_getsockopt

'''

import sys
import os
import re
import shutil
import datetime
import config

import parseutility2 as pu

vulrepo_src_path = config.vulrepo_src_path
vulrepo_path = config.vul_func_path
bad_functions = config.vul_badFunc_path
good_functions = config.vul_goodFunc_path
patch_functions = config.vul_patch_path

if not os.path.exists(vulrepo_path):
    os.mkdir(vulrepo_path)
if not os.path.exists(bad_functions):
    os.mkdir(bad_functions)
if not os.path.exists(good_functions):
    os.mkdir(good_functions)

def get_patch_range_from_patch_content(patch_content):
    '''
    return: [
              [range, chunk_contentBad, chunk_contentGood], 
              [range, chunk_contentBad, chunk_contentGood], 
              ......
            ]
    '''
    pattern = re.compile(r"@@ -(\d+,\d+) \+(\d+,\d+) @@")
    flag = False
    result = []
    chunks = []
    for line in patch_content:
        if line.startswith('diff --git'):
            flag = False
            if chunks:
                result.append(chunks)
                chunks = []
        if pattern.search(line):
            flag = True
            if chunks:
                result.append(chunks)
                chunks = []
        if flag:
            chunks.append(line)
    if chunks:
        result.append(chunks)
    result = list(set(tuple(t) for t in result))
    result = [list(t) for t in result]
    r = []
    for i in result:
        temp = []
        temp.append(pattern.search(i[0]).group(1))
        chks = i[1:]
        Bad_chks = []
        Good_chks = []
        for l in chks:
            if l.startswith('-'):
                l = ' '+l[1:-1]+' //-\n'
                Bad_chks.append(l)
            elif l.startswith('+'):
                l = ' '+l[1:-1]+' //+\n'
                Good_chks.append(l)
            else:
                Bad_chks.append(l)
                Good_chks.append(l)
        temp.append(Bad_chks)
        temp.append(Good_chks)
        r.append(temp)
    r = sorted(r, key=(lambda x:int(x[0].split(',')[0])), reverse=True)
    return r

def main():
    total = 0
    for root, dirs, files in os.walk(vulrepo_src_path):
        for f in files:
            if not f.startswith('(AM)') and not f.startswith('(BM)') and not f.endswith('.txt'):
                if os.path.exists(os.path.join(root, '(BM)'+f)):
                    if f.endswith('.c') or f.endswith('.cpp') or f.endswith('.cc') or f.endswith('.c++') or f.endswith('.cxx'):
                        total += 1

    starttime = datetime.datetime.now()
    index = 0
    for root,dirs,files in os.walk(vulrepo_src_path):
        for f in files:
            if not f.startswith('(AM)') and not f.startswith('(BM)') and not f.endswith('.txt') :
            #if f == r"fs#~befs#~linuxvfs.c":
                if f.endswith('.c') or f.endswith('.cpp') or f.endswith('.cc') or f.endswith('.c++') or f.endswith('.cxx'):
                    if not os.path.exists(os.path.join(root, '(BM)'+f)):
                        continue
                    cve_id = re.search(r"CVE-\d+-\d+", root).group()
                    index += 1
                    #if index < 3272:
                        #continue
                    patch_content = ""
                    BM_content= ""
                    with open(os.path.join(root, f), 'r') as ff:
                        patch_content = ff.readlines()
                    with open(os.path.join(root, '(BM)'+f), 'r') as ff:
                        BM_content = ff.readlines()
                    change_chucks = get_patch_range_from_patch_content(patch_content)
                    for i in change_chucks:
                        start_index = int(i[0].split(',')[0])
                        ranges = int(i[0].split(',')[1])
                        BM_Bad_content = BM_content[:start_index-1]+i[1]+BM_content[start_index+ranges-1:]
                        BM_Good_content = BM_content[:start_index-1]+i[2]+BM_content[start_index+ranges-1:]
                    
                    #得到了替换后的BM_content, 解析其中的函数，把有‘+’或者‘-’的函数提取出来并进行存储。
                    with open(r'E:/BM_Bad_content.c', 'w') as ff:
                        ff.write("".join(BM_Bad_content))
                    bad_funclist = pu.parseFile_shallow(r'E:/BM_Bad_content.c')
                    with open(r"E:/BM_Good_content.c", "w") as ff:
                        ff.write("".join(BM_Good_content))
                    good_funclist = pu.parseFile_shallow(r'E:/BM_Good_content.c')                    
                    
                    for bf in bad_funclist:
                        for l in bf.funcBody:
                            if l[-4:-1] == '//-':
                                name = re.sub("/|:|\*|\?|\"|<|>|\|", "",bf.name).replace('\\',"")[:]
                                with open(os.path.join(config.vul_badFunc_path, '(BadFunc)'+cve_id+"$"+f+'$'+name+'.c'),'w') as ff:
                                    string = "".join(BM_Bad_content[bf.lines[0]-1:bf.lines[1]])
                                    ff.write(string)
                                for gf in good_funclist:
                                    if gf.name == bf.name:
                                        name = re.sub("/|:|\*|\?|\"|<|>|\|", "",gf.name).replace('\\',"")[:]
                                        with open(os.path.join(config.vul_goodFunc_path, '(GoodFunc)'+cve_id+'$'+f+'$'+name+'.c'),'w') as ff:
                                            string = "".join(BM_Good_content[gf.lines[0]-1:gf.lines[1]])
                                            ff.write(string)
                                break
                    for gf in good_funclist:
                        for l in gf.funcBody:
                            if l[-4:-1] == '//+':
                                name = re.sub("/|:|\*|\?|\"|<|>|\|", "",gf.name).replace('\\',"")[:]
                                with open(os.path.join(config.vul_goodFunc_path, '(GoodFunc)'+cve_id+"$"+f+'$'+name+'.c'),'w') as ff:
                                    string = "".join(BM_Good_content[gf.lines[0]-1:gf.lines[1]])
                                    ff.write(string)  
                                for bf in bad_funclist:
                                    if bf.name == gf.name:
                                        name = re.sub("/|:|\*|\?|\"|<|>|\|", "",bf.name).replace('\\',"")[:]
                                        with open(os.path.join(config.vul_badFunc_path, '(BadFunc)'+cve_id+'$'+f+'$'+name+'.c'),'w') as ff:
                                            string = "".join(BM_Bad_content[bf.lines[0]-1:bf.lines[1]])
                                            ff.write(string)
                                break
                    os.remove(r'E:/BM_Good_content.c')
                    os.remove(r'E:/BM_Bad_content.c')                    
                    
                    print(f, '  completed.  ', index, ' / ', total)
    endtime = datetime.datetime.now()
    print "Running time:", (endtime - starttime).seconds
