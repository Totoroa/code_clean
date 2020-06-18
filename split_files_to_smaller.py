'''
split the folders to smaller.
'''

import os
import shutil

max_size = 15000000 #B 

def get_FileSize(filePath):
    fsize = os.path.getsize(filePath)
    return fsize  #B

def get_dir_size(path):
    t = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            p = os.path.join(root, f)
            t += get_FileSize(p)
    return t

def split_func_files(func_path):
    '''split the files under func_path into folders'''
    #if get_dir_size(func_path) < max_size:
        #return
    move_path = func_path.split('\\')[-1]
    number = 0
    total_size = 0
    file_list = os.listdir(func_path)
    for f in file_list:
        file_path = os.path.join(func_path, f)
        cur_path = os.path.join(func_path, move_path+'_'+str(number))
        if not os.path.exists(cur_path):
            os.mkdir(cur_path)
        if os.path.isfile(file_path):
            if total_size < max_size:
                total_size += get_FileSize(file_path)
                shutil.move(file_path, os.path.join(cur_path, f))
                #print total_size
            else:
                print total_size
                number += 1
                cur_path = os.path.join(func_path, move_path+str(number))
                if not os.path.exists(cur_path):
                    os.mkdir(cur_path)
                total_size = get_FileSize(file_path)
                shutil.move(file_path, os.path.join(cur_path, f))        

def split_same_and_diff_func(path, flag):
    '''split files in path. under the path only have functions files, have no folders.
    first split the files that have same function name.
    then split the files that have different function name into smaller folder.
    '''
    same_name_func_path = ""
    diff_name_func_path = ""
    
    if flag != 'vul' and flag != 'src':
        print "Wrong flag !"
        return
    
    file_list = os.listdir(path)
    same_name_func_path = os.path.join(path, "same")
    diff_name_func_path = os.path.join(path, "diff")    

    if not os.path.exists(same_name_func_path):
        os.makedirs(same_name_func_path)
    if not os.path.exists(diff_name_func_path):
        os.makedirs(diff_name_func_path)
    same_list = []  #store function name
    file_list = [os.path.join(path, k) for k in file_list if k.endswith('.c')]
    for p in file_list:
        func_name = ""
        if flag == 'vul':
            func_name = os.path.basename(p).split('$')[-1][:-2]
        elif flag == 'src':
            func_name = os.path.basename(p).split('$')[-2]
        if func_name not in same_list:
            same_list.append(func_name)
            try:
                shutil.move(p, os.path.join(diff_name_func_path, os.path.basename(p)))
            except IOError:
                pass
        else:
            try:
                shutil.move(p, os.path.join(same_name_func_path, os.path.basename(p)))
            except IOError:
                pass
    #split_func_files(diff_name_func_path)