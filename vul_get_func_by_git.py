'''
get (BM)files and patch files by git.
'''
import subprocess
import os
import re
import parseutility2 as pu
import config

gitDir = config.vul_git_path  # where .git exist
functions_stored_path = config.vul_func_path  #store BadFunc/BadDpd/GoodFunc/Patch files.

GitBinary = config.GitBinary
diffBinary = config.diffBinary
keyword = config.keyword
RepoName = config.RepoName

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

def callGitLog(gitDir):
    """
    Collect CVE commit log from repository
    :param gitDir: repository path
    :return:
    """
    # print "Calling git log...",
    commitsList = []
    gitLogOutput = ""
    command_log = "\"{0}\" --no-pager log --all --pretty=fuller --grep=\"{1}\"".format(GitBinary, keyword)
    print gitDir
    os.chdir(gitDir)
    try:
        try:
            gitLogOutput = subprocess.check_output(command_log, shell=True)
            commitsList = re.split('[\n](?=commit\s\w{40}\nAuthor:\s)|[\n](?=commit\s\w{40}\nMerge:\s)', gitLogOutput)
        except subprocess.CalledProcessError as e:
            print "[-] Git log error:", e
    except UnicodeDecodeError as err:
        print "[-] Unicode error:", err

    # print "Done."
    return commitsList

def callGitShow(gitBinary, commitHashValue):
    """
    Grep data of git show.
    :param commitHashValue: 
    :return: 
    """
    # print "Calling git show...",
    command_show = "\"{0}\" show --pretty=fuller {1}".format(gitBinary, commitHashValue)

    gitShowOutput = ''
    try:
        gitShowOutput = subprocess.check_output(command_show, shell=True)
    except subprocess.CalledProcessError as e:
        print "error:", e

    # print "Done."
    return gitShowOutput

def filterCommitMessage(commitMessage):
    """
    Filter false positive commits 
    Will remove 'Merge', 'Revert', 'Upgrade' commit log
    :param commitMessage: commit message
    :return: 
    """
    filterKeywordList = ["merge", "revert", "upgrade"]
    matchCnt = 0
    for kwd in filterKeywordList:
        keywordPattern = r"\W" + kwd + r"\W|\W" + kwd + r"s\W"
        compiledKeyworddPattern = re.compile(keywordPattern)
        match = compiledKeyworddPattern.search(commitMessage.lower())

        # bug fixed.. now revert and upgrade commits will be filtered out.
        if match:
            matchCnt += 1

    if matchCnt > 0:
        return 1
    else:
        return 0 

def parallel_process(subRepoName, commitMessage):
    '''
    process each commit.
    get bad functions and good functions.
    '''
    if filterCommitMessage(commitMessage):
        return
    else:
        commitHashValue = commitMessage[7:47]

        cvePattern = re.compile('CVE-20\d{2}-\d{4,7}')  # note: CVE id can now be 7 digit numbers
        cveIdList = list(set(cvePattern.findall(commitMessage)))

        if len(cveIdList) == 0:
            if info.cveID is None:
                return
            else:
                minCve = info.cveID  # when CVE ID is given manually through command line argument
        else:
            minCve = cveIdList[0]

        gitShowOutput = callGitShow(GitBinary, commitHashValue)
        
        print len(gitShowOutput.split("diff --git ")[1:])
        for diffs in gitShowOutput.split("diff --git ")[1:]:
            patch_content = "diff --git " + diffs
            patch_content = patch_content.split('\n')
            patch_content = [k+'\n' for k in patch_content]
            diff_filename = patch_content[2][6:-1]
            diff_filename = diff_filename.replace('/', '#~')
            
            if diff_filename.endswith('.c') or diff_filename.endswith('.cpp') or diff_filename.endswith('.cc') or \
               diff_filename.endswith('.c++') or diff_filename.endswith('.cxx'):
                print "diff_filename: ", diff_filename            
                if diff_filename == "CHANGES":
                    continue
                filehash = patch_content[1].split(' ')[1].split('..')[0]
                print "filehash:", filehash
                javaCommand = "\"{0}\" show {1}".format(GitBinary, filehash)
                BM_content = subprocess.check_output(javaCommand, shell=True)
                BM_content = BM_content.split('\n')
                BM_content = [k+'\n' for k in BM_content]
                change_chucks = get_patch_range_from_patch_content(patch_content)
                BM_Bad_content = ""
                for i in change_chucks:
                    start_index = int(i[0].split(',')[0])
                    ranges = int(i[0].split(',')[1])
                    BM_Bad_content = BM_content[:start_index-1]+i[1]+BM_content[start_index+ranges-1:]
                    BM_Good_content = BM_content[:start_index-1]+i[2]+BM_content[start_index+ranges-1:]
                    #print "\n------------BM_Bad_content-------------\n",BM_Bad_content
                    
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
                            with open(os.path.join(config.vul_badFunc_path, '(BadFunc)'+minCve+"$"+diff_filename+'$'+name+'.c'),'w') as ff:
                                string = "".join(BM_Bad_content[bf.lines[0]-1:bf.lines[1]])
                                ff.write(string)
                            for gf in good_funclist:
                                if gf.name == bf.name:
                                    name = re.sub("/|:|\*|\?|\"|<|>|\|", "",gf.name).replace('\\',"")[:]
                                    with open(os.path.join(config.vul_goodFunc_path, '(GoodFunc)'+minCve+'$'+diff_filename+'$'+name+'.c'),'w') as ff:
                                        string = "".join(BM_Good_content[gf.lines[0]-1:gf.lines[1]])
                                        ff.write(string)
                            break
                for gf in good_funclist:
                    for l in gf.funcBody:
                        if l[-4:-1] == '//+':
                            name = re.sub("/|:|\*|\?|\"|<|>|\|", "",gf.name).replace('\\',"")[:]
                            with open(os.path.join(config.vul_goodFunc_path, '(GoodFunc)'+minCve+"$"+diff_filename+'$'+name+'.c'),'w') as ff:
                                string = "".join(BM_Good_content[gf.lines[0]-1:gf.lines[1]])
                                ff.write(string)  
                            for bf in bad_funclist:
                                if bf.name == gf.name:
                                    name = re.sub("/|:|\*|\?|\"|<|>|\|", "",bf.name).replace('\\',"")[:]
                                    with open(os.path.join(config.vul_badFunc_path, '(BadFunc)'+minCve+'$'+diff_filename+'$'+name+'.c'),'w') as ff:
                                        string = "".join(BM_Bad_content[bf.lines[0]-1:bf.lines[1]])
                                        ff.write(string)
                            break
                os.remove(r'E:/BM_Good_content.c')
                os.remove(r'E:/BM_Bad_content.c')

def process(commitsList, subRepoName):
    flag = 0
    if len(commitsList) > 0 and commitsList[0] == '':
        flag = 1
        print "No commit in", RepoName,
    else:
        print len(commitsList), "commits in", RepoName,
    if subRepoName is None:
        print "\n"
    else:
        print subRepoName
        os.chdir(os.path.join(GitStoragePath, RepoName, subRepoName))

    if flag:
        return
    
    total = len(commitsList)
    idx = 1
    for commitMessage in commitsList:
        parallel_process(subRepoName, commitMessage)    # process each commit in commitsList
        print idx, '/', total
        idx += 1
    
def get_diff_files():
    bad = config.vul_badFunc_path
    good = config.vul_goodFunc_path
    patch = config.vul_patch_path
    
    bfiles = os.listdir(bad)
    gfiles = os.listdir(good)
    
    idx = 0
    for f in bfiles:
        if '(GoodFunc)'+f[9:] in gfiles:
            patch_fname = f[9:]
            diffCommand = "\"{0}\" -u {1} {2} > {3}".format(diffBinary,os.path.join(bad, f),os.path.join(good, '(GoodFunc)'+f[9:]),os.path.join(patch, patch_fname))
            os.system(diffCommand)
            print f, "completed"
            idx += 1
    print "total files: ", idx
    
    
if __name__ == "__main__":
    commitsList = callGitLog(gitDir)
    process(commitsList, None)
    get_diff_files()