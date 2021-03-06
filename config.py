import os

#common
GitBinary = r"E:\Program Files\Git\bin\git.exe"
diffBinary = r"E:\Program Files\Git\usr\bin\diff.exe"
bloomfilter_size = 4294967296 #2097152

vul_func_path = r'E:\lab\total'   #r'E:\lab\web'
vul_badFunc_path = os.path.join(vul_func_path, 'Bad')
vul_goodFunc_path = os.path.join(vul_func_path, 'Good')
vul_badFuncDpd_path = os.path.join(vul_func_path, 'BadDpd')
vul_patch_path = os.path.join(vul_func_path, 'Patch')
vul_repo_file_path = r"E:\total.json"

# VUL: get functions by git
vul_git_path = r"F:\project\git_repo\linux"  # where .git exist
keyword = "CVE-20"
RepoName = "qemu"

# VUL: get functions by web
vulrepo_src_path = r"F:\data\self_vul_repo\patches_and_files"

# SRC
src_proj_path = r"E:\lab\source-code\qemu-2.8.1"  # original project path
src_func_path = os.path.join(os.getcwd(), src_proj_path.split('\\')[-1], 'functions')  # where store the funcitons extracted from project
src_funcDpd_path = os.path.join(os.getcwd(), src_proj_path.split('\\')[-1], 'func_dpd')
result_path = os.path.join(os.getcwd(), src_proj_path.split('\\')[-1], src_proj_path.split('\\')[-1]+".html")
