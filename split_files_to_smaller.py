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
    if get_dir_size(func_path) < max_size:
        return
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
