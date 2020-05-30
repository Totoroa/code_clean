'''
create vulnerability repository.
1. get bad functions and good functions. And split bad functions into smaller folder.
2. get bad functions' cpg, and get dependence relationship. (By Joern)
3. get slice and build vulnerability repository.
'''
import config
import produce_slice
import parseutility2 as pu

import os
import datetime

def generate_vul_repo():
    '''generate vul_repo according badFunc and badFuncDpd.'''
    written = {}
    
    total = 0
    for root, dirs, files in os.walk(config.vul_badFunc_path):
        for f in files:
            if f.endswith('.c'):
                total += 1
                
    start_time = datetime.datetime.now()
    idx = 1
    for root, dirs, files in os.walk(config.vul_badFunc_path):
        for f in files:
            if f.endswith('.c'):
                print f, "  start."
                badFunc_content = []   # get bad functions content.
                with open(os.path.join(root, f), 'r') as ff:
                    badFunc_content = ff.readlines()
                del_line_number = []
                for index, lines in enumerate(badFunc_content):
                    if lines.endswith('//-\n'):
                        del_line_number.append(index+1)
                if not os.path.exists(os.path.join(config.vul_badFuncDpd_path, f)):
                    idx += 1
                    continue
                
                dpd_content = ""    # get bad functions dependence content.
                with open(os.path.join(config.vul_badFuncDpd_path, f), 'r') as ff:
                    temp = ff.readlines()
                    dpd_content = "".join("".join(temp).split('\n'))
                
                #store hashvalue of function body.
                dpd_dic = produce_slice.slice_from_project(dpd_content)
                written[f] = {}
                hash_and_value = produce_slice.produce_funcBody_hash(os.path.join(root, f))                
                written[f]['hashvalue'] = []
                written[f]['hashvalue'].append(hash_and_value[0])
                written[f]['value'] = []
                written[f]['value'].append(hash_and_value[1])
                written[f]['lineNumber'] = [0]
                written[f]['lineId'] = [0]
                
                # store hashvalue of functions slices.
                for keys, values in dpd_dic.items():
                    if keys in del_line_number:
                        values.sort()
                        print "node_id:", keys
                        print "dpd_id:", values
                        slice_content = produce_slice.get_slice_content(badFunc_content, values)
                        slice_temp = produce_slice.produce_slice_hash(os.path.join(root, f), slice_content)
                        written[f]['value'].append(slice_temp[1])
                        written[f]['hashvalue'].append(slice_temp[0])
                        written[f]['lineNumber'].append('-'.join(str(nb) for nb in values))
                        written[f]['lineId'].append(keys)
                try:
                    with open(r'vulRepo_backUp.txt', 'a') as fff:
                        fff.write(f)
                        fff.write(' $$hashvalue$$ ')
                        fff.write(" ".join([str(nb) for nb in written[f]['hashvalue']]))
                        fff.write(" $$value$$ ")
                        fff.write(" ".join(written[f]['value']))
                        fff.write(" $$lineNumber$$ ")
                        fff.write(" ".join([str(nb) for nb in written[f]['lineNumber']]))
                        fff.write(" $$lineId$$ ")
                        fff.write(" ".join([str(nb) for nb in written[f]['lineId']]))
                        fff.write('\n')                        
                except UnicodeDecodeError:
                    print "write file <emm.txt> failed."
                    with open(r'emm.txt', 'a') as fff:
                        fff.write('\n')
                    written.pop(f)
                
                print "completed. ", idx, "/", total
                print "---------------------------------------------------------------------"
                idx += 1
    try:
        with open(config.vul_repo_file_path,"w") as result_f:
            json.dump(written, result_f, encoding='gbk')
            print "Okay .."
    except BaseException:
        print "write file <", result_fileName, "> failed !"
            
    end_time = datetime.datetime.now()
    print "Running time:", (end_time - start_time).seconds, "s"    

def get_func_by_git():
    import vul_get_func_by_git
    vul_get_func_by_git.main()

def get_func_by_web():
    import vul_get_func_by_web
    vul_get_func_by_web.main()

if __name__ == '__main__':
    #selete how to get the vul functions.
    #get_func_by_git()
    #get_func_by_web()
    #import split_files_to_smaller
    #split_files_to_smaller.split_func_files(config.vul_badFunc_path)
    
    # use Joern generate CPG and then get dependence relationship
    
    # generate vul_repo.
    generate_vul_repo()