'''detected project.
1. get functions in project.
2. get functions' dependence relationship.(by Joern)
3. get slice in source code, and detect according to vul_repo.
'''
import os
import sys
import json
import bitarray
import time
import multiprocessing

import produce_slice
import parseutility2 as pu
import config
import detect_source_code

def get_func(source_file_path):
    file_content = []
    with open(source_file_path, 'r') as f:
        file_content = f.readlines()
    function_list = pu.parseFile_shallow(source_file_path)
    print len(function_list)
    for functions in function_list:
        func_filaName = source_file_path.split(os.path.basename(config.src_proj_path),1)[1][1:]
        func_filaName = func_filaName.replace('\\', '#~') + '$' + functions.name + '$' + str(functions.lines[0]) + '-' + str(functions.lines[1]) + '.c'
        try:
            if not os.path.exists(config.src_func_path):
                os.makedirs(config.src_func_path)
            with open(os.path.join(config.src_func_path, func_filaName), 'w') as ff:
                func_content = file_content[functions.lines[0]-1 : functions.lines[1]]
                ff.write("".join(func_content))
        except Exception,e:
            print e
            continue
    return

def get_func_in_project():
    print "[+] get and store functions."
    file_list = []
    for root, dirs, files in os.walk(config.src_proj_path):
        for f in files:
            if f.endswith('.c') or f.endswith('.cpp') or f.endswith('.cc') or f.endswith('.c++') or f.endswith('.cxx'):
                file_list.append(os.path.join(root, f))
    print len(file_list)
    
    print "[+] get file_list."
    
    time1=time.time()
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool(processes=4)
    res = pool.map(get_func, file_list)
    time2=time.time()
    
    pool.close()
    pool.join()
    print('running time: ' + str(time2 - time1) + ' s')

if __name__ == '__main__':
    # get and store functions.
    get_func_in_project()
    
    #get slice in source code and detect.
    #detect_source_code.detect_source_code()
