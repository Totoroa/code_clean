# 9000个文件一个文件夹。要把名字相同的文件放入不同文件夹.
import shutil
import os
import random


def get_diff(filelist, threshold, flag):
    '''return two list, one is diff list contains filename less than threshold, the other is a list contains remains filename.'''
    if flag != 'vul' and flag != 'src':
        print "Wrong flag !"
    name = []
    cur_diff = []
    cur_same = []
    for i in range(len(filelist)):
        func_name = ""
        if flag == 'vul':
            func_name = filelist[i].split('$')[-1][:-2]
        elif flag == 'src':
            func_name = filelist[i].split('$')[-2]
        if func_name in name:
            cur_same.append(filelist[i])
        else:
            name.append(func_name)
            cur_diff.append(filelist[i])
        if len(cur_diff) > threshold:
            cur_same.extend(filelist[i+1:])
            return (cur_diff, cur_same)
    return (cur_diff, cur_same)

def split_same_and_diff_func(path, flag):
    threshold = 9000
    
    file_list = os.listdir(path)
    #random.shuffle(file_list)
    same_name_func_path = os.path.join(path, "same")
    diff_name_func_path = os.path.join(path, "diff")    
    
    result = []
    while(True):
        diff, same = get_diff(file_list, threshold, flag)
        if len(diff) < 20:
            result.append(diff)
            file_list = same
            break
        result.append(diff)
        file_list = same
    
    del_elem = []
    for j in range(len(file_list)):
        for i in range(len(result)):
            i_name = []
            j_name = ""
            if flag == 'vul':
                i_name = [ii.split('$')[-1][:-2] for ii in result[i]]
                j_name = file_list[j].split('$')[-1][:-2]
            elif flag == 'src':
                i_name = [ii.split('$')[-2] for ii in result[i]]
                j_name = file_list[j].split('$')[-2]
            if j_name not in i_name:
                result[i].append(file_list[j])
                del_elem.append(file_list[j])
                break
    for k in del_elem:
        file_list.remove(k)
    
    for i in range(len(result)):
        diff_dirname = os.path.join(diff_name_func_path, "diff_"+str(i))
        if not os.path.exists(diff_dirname):
            os.makedirs(diff_dirname)
        for files in result[i]:
            src_path = os.path.join(path, files)
            dst_path = os.path.join(diff_dirname, files)
            shutil.move(src_path, dst_path)
    for i in file_list:
        src_path = os.path.join(path, i)
        dst_path = os.path.join(same_name_func_path, i)
        if not os.path.exists(same_name_func_path):
            os.makedirs(same_name_func_path)
        shutil.move(src_path, dst_path)

if __name__ == "__main__":
    split_same_and_diff_func(r"C:\Users\admin\Desktop\workspace-python\cleancode\qemu-2.8.1\functions", 'src')
    print "split OK.."