import sys
import os
import json
import bitarray
import time

import produce_slice
import config
import parseutility2 as pu
from multiprocessing import Pool, Lock
from multiprocessing import Process
import multiprocessing
import threading

def _html_escape(oneList):
    '''
    Escape HTML
    oneList: List
    
    return: List
    '''
    html_escape_dict = { '&': '&amp;', '>': '&gt;', '<': '&lt;', '"': '&quot;', '\'': '&apos;' }
    tp = []
    for line in oneList:
        tp.append("".join(html_escape_dict.get(c,c) for c in line))
    return tp

def mark_content(source_ct, dpd_lines):
    """
    source_ct: List
    dpd_lines: List
    
    return: List
    """
    if dpd_lines == 0 or dpd_lines == "":
        dpd_lines = range(1, len(source_ct)+1)
    if dpd_lines[0] == 0:
        tp = '-'.join(dpd_lines[1:]).split('-')
        dpd_lines = list(set([int(k) for k in tp]))
    dpd_lines = [i-1 for i in dpd_lines]
    for index in dpd_lines:
        temp = '<font color=\"#DAA520\">'+source_ct[index]+'</font>'
        source_ct[index] = temp
    return source_ct
    
def mark_patch_content(patch_ct):
    """
    patch_ct: List
    """
    for index in range(len(patch_ct)):
        if patch_ct[index].startswith('-'):
            patch_ct[index] = '<font color=\"#AA0000\">'+patch_ct[index]+'</font>'
        if patch_ct[index].startswith('+'):
            patch_ct[index] = '<font color=\"#00AA00\">'+patch_ct[index]+'</font>'
    return patch_ct

def report(src_file_name, src_dpd_lines, vul_file_name, vul_dpd_lines, tag):
    outfile = open(config.result_path, 'a')
    show_lines_limit = 20
    
    with open("simple_record.txt", 'a') as ff:
        ff.write(src_file_name+" $ "+str(src_dpd_lines)+" $ "+vul_file_name+" $ "+str(vul_dpd_lines)+"\n")
    outfile.write("""
    <div class="container">
        <br />""")
    
    #source info
    source_ct = []
    with open(src_file_name, 'r') as f:
        source_ct = f.readlines()
    #source_ct = mark_content(source_ct, src_dpd_lines)
    #line_range = [int(num) for num in src_file_name.split("$")[2][:-2].split('-')]         # change it latter.  !!!!!!
    line_range = [i + 1 for i in range(len(source_ct))]
    temp_src_ct = mark_content(_html_escape(source_ct), src_dpd_lines)
        
    if len(source_ct) > show_lines_limit:
        outfile.write("""
        <div class="source">
            <div class="filepath">%s</div>""" % (os.path.basename(src_file_name)+"  # "+"  "+tag))
        outfile.write("""
            <div>
                <div class="linenumber">""")
        for i in range(line_range[0], line_range[0]+ show_lines_limit):
            outfile.write("""
                %d<br />""" % i)
        outfile.write("""
                </div>
                <div class="codechunk">%s</div>
            </div>""" % "".join(temp_src_ct[:show_lines_limit]))
       
        outfile.write("""
            <a href="javascript:;" onclick="toggleNext(this);">+ show +</a><div style="display: none">
                <div class="linenumber">""")
        for i in range(line_range[0]+show_lines_limit, line_range[1]):
            outfile.write("""
                %d<br />""" % (i+1))
        outfile.write("""
                </div>
                <div class="codechunk">%s</div>
            </div>
        </div>""" % "".join(temp_src_ct[show_lines_limit:]))
    else:
        outfile.write("""
        <div class="source">
            <div class="filepath">%s</div>""" % (os.path.basename(src_file_name)+"  # "+"  "+tag))
        outfile.write("""
            <div>
                <div class="linenumber">""")
        for i in range(line_range[0], line_range[1]+1):
            outfile.write("""
                %d<br />""" % (i+1))
        outfile.write("""
                </div>
                <div class="codechunk">%s</div>
            </div>
        </div>""" % "".join(temp_src_ct))
        
    # vul_function info
    vul_ct = []
    with open(os.path.join(config.vul_badFunc_path, vul_file_name), 'r') as f:
        vul_ct = f.readlines()
    #vul_ct = mark_content(vul_ct, vul_dpd_lines)
    temp_vul_ct = mark_content(_html_escape(vul_ct), vul_dpd_lines)
    if len(vul_ct) > show_lines_limit:
        outfile.write("""
        <div class="patch">
            <div class="filepath">%s</div>""" % vul_file_name)
        outfile.write("""
            <div>
                <div class="codechunk">%s</div>
            </div>"""% "".join(temp_vul_ct[:show_lines_limit]))
        outfile.write("""
            <a href="javascript:;" onclick="toggleNext(this);">+ show +</a><div style="display: none">
                #<div class="codechunk">%s</div>
            </div>
        </div>"""% "".join(temp_vul_ct[show_lines_limit:]))
    else:
        outfile.write("""
        <div class="patch">
            <div class="filepath">%s</div>""" % vul_file_name)
        outfile.write("""
            <div>
                <div class="codechunk">%s</div>
            </div>
        </div>"""% "".join(temp_vul_ct))
    
    # patch(diff) info
    patch_ct = []
    try:
        with open(os.path.join(config.vul_patch_path, vul_file_name[9:]), 'r') as f:
            patch_ct = f.readlines()
    except:
        patch_ct = ["no patch now. "]
    #patch_ct = mark_patch_content(patch_ct)
    
    if len(patch_ct) > show_lines_limit:
        outfile.write("""
        <div class="patch">
            <div class="filepath">%s</div>""" % vul_file_name[9:])
        outfile.write("""
            <div>
                <div class="codechunk">%s</div>
            </div>""" % "".join(mark_patch_content(_html_escape(patch_ct[:show_lines_limit]))))
        outfile.write("""
            <a href="javascript:;" onclick="toggleNext(this);">+ show +</a><div style="display: none">
                <div class="codechunk">%s</div>
            </div>
        </div>""" % "".join(mark_patch_content(_html_escape(patch_ct[show_lines_limit:]))))
    else:
        outfile.write("""
        <div class="patch">
            <div class="filepath">%s</div>""" % vul_file_name[9:])
        outfile.write("""
            <div>
                <div class="codechunk">%s</div>
            </div>
        </div>""" % "".join(mark_patch_content(_html_escape(patch_ct))))
    
    outfile.write("""
    </div>""")
    outfile.close()

def process_func_files(file_path):
    print file_path, "   started.."
    bitvector_size = config.bloomfilter_size
    bitvector = bitarray.bitarray(bitvector_size)
    bitvector_dic = {}    # record the slice's hashvalue and the line numbers. eg: {1839273: [1,5,7,9,10], 34502394: [6,7,8,10,11,12]}
    
    vul_dic = {}
    with open(config.vul_repo_file_path, 'r') as f:
        vul_dic = json.load(f, encoding='gbk')
    #print "[+]import vul completed."
    
    #index = 1
    #report_num = 1
    if not file_path.endswith(".c"):
        return
    
    # get variable list
    function = pu.parseFile_deep(file_path)
    
    if len(function) == 0:
        print "The file <", file_path, "> has ", len(function), "functions."
        return
    if len(function) != 1:
        print "The file <", file_path, "> has ", len(function), "functions."
            
    # a threshold for function
    if len(pu.normalize(function[0].funcBody)) < 50:
        return
    variable_list = function[0].variableList
        
    temp = produce_slice.produce_funcBody_hash(function[0])
    if temp == "":
        return
    hash_value = temp[0]
    for vulfunc_file_name, record in vul_dic.items():
        if record['hashvalue'][0] == hash_value:
            lock.acquire()
            report(file_path, 0, vulfunc_file_name, "", "Bingo(1)")
            lock.release()
            return
        
    dpd_content = ""
    func_content = []
    
    if not os.path.exists(os.path.join(config.src_funcDpd_path, os.path.basename(file_path))):
        return
    with open(os.path.join(config.src_funcDpd_path, os.path.basename(file_path)), "r") as ff:
        temp = ff.readlines()
        dpd_content = "".join("".join(temp).split("\n"))
    dpd_dic = produce_slice.slice_from_project(dpd_content)
    with open(file_path, "r") as ff:
        func_content = ff.readlines()
        
    # build a bitvector according to dpd_dic
    bitvector.setall(0)
    for line_num, line_dpd in dpd_dic.items():
        slice_content = produce_slice.get_slice_content(func_content, line_dpd)
        if slice_content == []:
            continue
        if slice_content == "":
            print "[Error]The dpd-files wrong."
            return
        
        temp1 = produce_slice.produce_slice_hash(variable_list, slice_content)
        slice_hash = temp1[0]
        bitvector[slice_hash] = 1
        bitvector_dic[slice_hash] = line_dpd
        
        for vul_filename, record in vul_dic.items():
            if bitvector[record['hashvalue'][0]] == 1:
                line_list = bitvector_dic[record['hashvalue'][0]]
                line_list = list(set(line_list))
                line_list.sort()
                lock.acquire()
                report(file_path, line_list, vul_filename, "", "Bingo(3)")
                lock.release()
                return
            if len(record['hashvalue']) == 1:
                continue
            flag = True
            matched_hash = []
            for n in record['hashvalue'][1:]:
                if bitvector[n] == 1:
                    matched_hash.append(n)
                else:
                    flag = False
                    matched_hash = []
                    break
            if flag:
                line_list = []
                for i in matched_hash:
                    line_list.extend(bitvector_dic[i])
                line_list = list(set(line_list))
                line_list.sort()
                lock.acquire()
                report(file_path, line_list, vul_filename, record['lineNumber'], "Bingo(2)")
                lock.release()
                return
    return

def init(l):
    global lock
    lock = l

def detect_source_code():
    if os.path.exists(config.result_path):
        os.remove(config.result_path)
    outfile = open(config.result_path, 'a')
    outfile.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Result - Report</title>
    <style type="text/css">
    .container { padding: 3px 3px 3px 3px; font-size: 14px; }
    .patch { background-color: #CCCCCC; border: 2px solid #555555; margin: 0px 0px 5px 0px }
    .source { background-color: #DDDDDD; padding: 3px 3px 3px 3px; margin: 0px 0px 5px 0px }
    .filepath { font-size: small; font-weight: bold; color: #0000AA; padding: 5px 5px 5px 5px; }
    .codechunk { font-family: monospace; font-size: small; white-space: pre-wrap; padding: 0px 0px 0px 50px; }
    .linenumber { font-family: monospace; font-size: small; float: left; color: #777777; }
    </style>
    <script language="javascript">
        function togglePrev(node) {
            var targetDiv = node.previousSibling;
            targetDiv.style.display = (targetDiv.style.display=='none')?'block':'none';
            node.innerHTML = (node.innerHTML=='+ show +')?'- hide -':'+ show +';
        }
        function toggleNext(node) {
            var targetDiv = node.nextSibling;
            targetDiv.style.display = (targetDiv.style.display=='none')?'block':'none';
            node.innerHTML = (node.innerHTML=='+ show +')?'- hide -':'+ show +';
        }
    </script>
</head>
<body>
<div style="width: 100%; margin: 0px auto">""")
    outfile.close()
    
    file_to_be_processed = []
    for root, dirs, files in os.walk(config.src_func_path):
        for func_file in files:
            if not func_file.endswith('.c'):
                continue
            file_to_be_processed.append(os.path.join(root, func_file))
    
    print "total:", len(file_to_be_processed)
    # multiprocess.
    #for i in file_to_be_processed:
        #process_func_files(i)
    mutex = Lock()
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool(processes=3, initializer=init, initargs=(mutex,))
    #pool = Pool(3)
    for arg in file_to_be_processed:
        pool.apply_async(process_func_files, args=(arg,))
    
    #pool.map_async(process_func_files, file_to_be_processed)
    pool.close()
    pool.join()
    
    outfile = open(config.result_path, 'a')
    outfile.write("""
</div>
</body>
</html>""")
    outfile.close()