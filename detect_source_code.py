import sys
import os
import json
import bitarray

import produce_slice
import config
import parseutility2 as pu

def _html_escape(string):
    '''
    Escape HTML
    '''
    html_escape_dict = { '&': '&amp;', '>': '&gt;', '<': '&lt;', '"': '&quot;', '\'': '&apos;' }    
    return ''.join(html_escape_dict.get(c,c) for c in string)

def mark_content(source_ct, dpd_lines):
    """
    source_ct: List
    dpd_lines: List
    """
    if dpd_lines == 0 or dpd_lines == "":
        dpd_lines = range(1, len(dpd_lines)+1)
    dpd_lines = [i-1 for i in dpd_lines]
    for index in dpd_lines:
        temp = '<font color=\"#FFCC00\">'+source_ct[index].replace('<','&lt;').replace('>','&gt;')+'</font>'
        source_ct[index] = temp
    return source_ct
    
def mark_patch_content(patch_ct):
    """
    patch_ct: List
    """
    for index in range(len(patch_ct)):
        if patch_ct[index].startswith('-'):
            patch_ct[index] = '<font color=\"#AA0000\">'+patch_ct[index].replace('<','&lt;').replace('>','&gt;')+'</font>'
        if patch_ct[index].startswith('+'):
            patch_ct[index] = '<font color=\"#00AA00\">'+patch_ct[index].replace('<','&lt;').replace('>','&gt;')+'</font>'
    return patch_ct

def report(outfile, src_file_name, src_dpd_lines, vul_file_name, vul_dpd_lines, report_num):
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
    source_ct = mark_content(source_ct, src_dpd_lines)
    line_range = [int(num) for num in src_file_name.split("$")[2][:-2].split('-')]
        
    if len(source_ct) > show_lines_limit:
        outfile.write("""
        <div class="source">
            <div class="filepath">%s</div>""" % (os.path.basename(src_file_name)+"  # "+str(report_num)))
        outfile.write("""
            <div>
                <div class="linenumber">""")
        for i in range(line_range[0], line_range[0]+ show_lines_limit):
            outfile.write("""
                %d<br />""" % (i+1))
        outfile.write("""
                </div>
                <div class="codechunk">%s</div>
            </div>""" % _html_escape("".join(source_ct[:show_lines_limit])))
        outfile.write("""
            <a href="javascript:;" onclick="toggleNext(this);">+ show +</a><div style="display: none">
                <div class="linenumber">""")
        for i in range(line_range[0]+show_lines_limit, line_range[1]+1):
            outfile.write("""
                %d<br />""" % (i+1))
        outfile.write("""
                </div>
                <div class="codechunk">%s</div>
            </div>
        </div>""" %_html_escape("".join(source_ct[show_lines_limit:])))
    else:
        outfile.write("""
        <div class="source">
            <div class="filepath">%s</div>""" % (os.path.basename(src_file_name)+"  # "+str(report_num)))
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
        </div>""" % _html_escape("".join(source_ct)))
        
    # vul_function info
    vul_ct = []
    with open(os.path.join(config.vul_badFunc_path, vul_file_name), 'r') as f:
        vul_ct = f.readlines()
    vul_ct = mark_content(vul_ct, vul_dpd_lines)
    if len(vul_ct) > show_lines_limit:
        outfile.write("""
        #<div class="patch">
            #<div class="filepath">%s</div>""" % vul_file_name)
        outfile.write("""
            #<div>
                #<div class="codechunk">%s</div>
            #</div>"""%_html_escape("".join(vul_ct[:show_lines_limit])))
        outfile.write("""
            #<a href="javascript:;" onclick="toggleNext(this);">+ show +</a><div style="display: none">
                #<div class="codechunk">%s</div>
            #</div>
        #</div>"""%_html_escape("".join(vul_ct[show_lines_limit:])))
    else:
        outfile.write("""
        #<div class="patch">
            #<div class="filepath">%s</div>""" % vul_file_name)
        outfile.write("""
            #<div>
                #<div class="codechunk">%s</div>
            #</div>
        #</div>"""%_html_escape("".join(vul_ct)))
    
    # patch(diff) info
    patch_ct = []
    with open(os.path.join(config.vul_patch_path, vul_file_name[9:]), 'r') as f:
        patch_ct = f.readlines()
    patch_ct = mark_patch_content(patch_ct)
    if len(patch_ct) > show_lines_limit:
        outfile.write("""
        #<div class="patch">
            #<div class="filepath">%s</div>""" % vulfunc_file_name[9:])
        outfile.write("""
            #<div>
                #<div class="codechunk">%s</div>
            #</div>"""%_html_escape("".join(patch_ct[:show_lines_limit])))
        outfile.write("""
            #<a href="javascript:;" onclick="toggleNext(this);">+ show +</a><div style="display: none">
                #<div class="codechunk">%s</div>
            #</div>
        #</div>"""%_html_escape("".join(patch_ct[show_lines_limit:])))
    else:
        outfile.write("""
        #<div class="patch">
            #<div class="filepath">%s</div>""" % vulfunc_file_name[9:])
        outfile.write("""
            #<div>
                #<div class="codechunk">%s</div>
            #</div>
        #</div>"""%_html_escape("".join(patch_ct)))
    
    outfile.write("""
    </div>""")

def detect_source_code():
    bitvector_size = config.bloomfilter_size
    bitvector = bitarray.bitarray(bitvector_size)
    bitvector_dic = {}    # record the slice's hashvalue and the line numbers. eg: {1839273: [1,5,7,9,10], 34502394: [6,7,8,10,11,12]}
    
    vul_dic = {}
    with open(config.result_path, 'r') as f:
        vul_dic = json.load(f, encoding='gbk')
    print "[+]import vul completed."
    
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
    
    total = 0
    for root, dirs, files in os.walk(config.src_func_path):
        for func_file in files:
            if not func_file.endswith('.c'):
                continue
            total += 1
    
    index = 1
    report_num = 1
    for root, dirs, files in os.walk(config.src_func_path):
        for func_file in files:
            if not func_file.endswith('.c'):
                continue
            # first, get the abstracted/normalized func_Body, to detect if the hashvalue of the func_Body is vulnerability.
            print "-----------------------------------------------------------"
            print index, "/", total, os.path.join(root, func_file), "started."
            index += 1
            temp = produce_slice.produce_funcBody_hash(os.path.join(root, func_file))
            if temp == "":
                continue
            hash_value = temp[0]
            for vulfunc_file_name, record in vul_dic.items():
                if record['hashvalue'][0] == hash_value:
                    print func_file, "  Bingo(1) !", "match vul_function:", vulfunc_file_name
                    report(outfile, os.path.join(root, func_file), 0, vulfunc_file_name, "", report_num)
                    report_num += 1
                    break
            # if the func_Body is "not" vulnerablity, then produce slices for current function. 
            # Build a bitvector for current function,         
            else:  #if 'break' executed, the else will no be executed.
                slice_time1 = time.time()
                dpd_content = ""
                func_content = []
                if not os.path.exists(os.path.join(config.src_funcDpd_path, func_file)):
                    continue
                with open(os.path.join(config.src_funcDpd_path, func_file), 'r') as ff:
                    temp = ff.readlines()
                    dpd_content = "".join("".join(temp).split('\n'))
                dpd_dic = produce_slice.slice_from_project(dpd_content)
                
                with open(os.path.join(root, func_file), 'r') as ff:
                    func_content = ff.readlines()
                
                # build a bitvector according to dpd_dic
                bitvector.setall(0)
                for line_num, line_dpd in dpd_dic.items():
                    slice_content = produce_slice.get_slice_content(func_content, line_dpd)
                    temp1 = produce_slice.produce_slice_hash(os.path.join(root, func_file), slice_content)
                    slice_hash = temp1[0]
                    bitvector[slice_hash] = 1
                    bitvector_dic[slice_hash] = line_dpd
                slice_time2 = time.time()
                print "produce slices time:", str(slice_time2 - slice_time1), "s."
                
                detect_time1 = time.time()
                for vul_filename, records in vul_dic.items():
                    if bitvector[records['hashvalue'][0]] == 1:
                        print func_file, "   Bingo(3) !", vul_filename, "------------"
                        line_list = []
                        for i in matched_hash:
                            line_list.extend(bitvector_dic[i])
                        line_list = list(set(line_list))
                        line_list.sort()
                        report(outfile, os.path.join(root, func_file), line_list, vul_filename, "", report_num)
                        report_num += 1
                        break                    
                    if len(records['hashvalue']) == 1:
                        continue
                    flag = True
                    matched_hash = []
                    for n in records['hashvalue'][1:]:
                        if bitvector[n] == 1:
                            matched_hash.append(n)
                        else:
                            flag = False
                            matched_hash = []
                            break
                    if flag:
                        print func_file, "   Bingo(2) !", vul_filename, records['lineNumber'], "------------"
                        line_list = []
                        for i in matched_hash:
                            line_list.extend(bitvector_dic[i])
                        line_list = list(set(line_list))
                        line_list.sort()
                        report(outfile, os.path.join(root, func_file), line_list, vul_filename, records['lineNumber'], report_num)
                        report_num += 1
                        break
                detect_time2 = time.time()
                print "detect time: ", str(detect_time2 - detect_time1), "s."
    outfile.write("""
</div>
</body>
</html>""")
    outfile.close()