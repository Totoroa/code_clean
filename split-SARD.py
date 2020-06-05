#coding = utf-8
'''get train cases and test cases from SARD'''
import os
import shutil
import parseutility2 as pu
import random

sard_path = r"F:\project\C\testcases"
train_store_path = r"E:\lab\SARD\SARD"  # 80%
test_store_path = r"E:\lab\source-code\SARD"  #20%

train_func_path = r"E:\lab\SARD\functions\Bad"

def extract_train_func():
    idx = 1
    for root, dirs, files in os.walk(train_store_path):
        for f in files:
            func_list = pu.parseFile_shallow(os.path.join(root, f))
            for fc in func_list:
                if 'bad' in fc.name.lower() and 'good' not in fc.name.lower():
                    print idx, "th"
                    idx += 1
                    name = '(BadFunc)' + f + "$" + fc.name + '.c'
                    file_content = []
                    with open(os.path.join(root, f)) as fp:
                        file_content = fp.readlines()
                    with open(os.path.join(train_func_path, name), 'w') as fp:
                        fp.write("".join(file_content[fc.lines[0]-1 : fc.lines[1]]))

if __name__ == '__main__':
    extract_train_func()

#total_path = []
#for root, dirs, files in os.walk(sard_path):
    #for d in dirs:
        #cur_path = os.path.join(root, d)
        #file_list = os.listdir(cur_path)
        #flag = True
        #for f in file_list:
            #if not os.path.isfile(os.path.join(cur_path, f)):
                #flag = False
                #break
        #if flag:
            #total_path.append(os.path.join(root, d))
            
## 将total_path中的文件按照80%，20%随机分开。
#total_path = [k for k in total_path if 's06' in k]
#total = len(total_path)
#train_set = []  # 80%
#test_set = []  # 20% 
#for index, path in enumerate(total_path):
    #f_list = os.listdir(path)
    #f_num = len(f_list)
    #split_num = int(f_num * 0.8)
    #print index+1, '/', total, path
    
    #for i in range(split_num):
        #a = random.choice(f_list)
        #f_list.remove(a)
        #a = os.path.join(path, a)        
        #train_set.append(a)
    #b = [os.path.join(path, t) for t in f_list]
    #test_set.extend(b)

#for p in train_set:
    #if not p.endswith('.c'):
        #continue
    #shutil.copyfile(p, os.path.join(train_store_path, os.path.basename(p)))
#for p in test_set:
    #if not p.endswith('.c'):
        #continue
    #shutil.copyfile(p, os.path.join(test_store_path, os.path.basename(p)))

#print "OK.."