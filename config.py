import os

#common
GitBinary = r"E:\Program Files\Git\bin\git.exe"
diffBinary = r"E:\Program Files\Git\usr\bin\diff.exe"
bloomfilter_size = 2097152

vul_func_path = r'E:\lab\openssl\functions'
vul_badFunc_path = os.path.join(vul_func_path, 'Bad')
vul_goodFunc_path = os.path.join(vul_func_path, 'Good')
vul_badFuncDpd_path = os.path.join(vul_func_path, 'BadDpd')
vul_patch_path = os.path.join(vul_func_path, 'Patch')
vul_repo_file_path = r"E:\new-emm.json"

# VUL: get functions by git
vul_git_path = r"F:\project\git_repo\openssl"  # where .git exist
keyword = "CVE-20"
RepoName = "openssl"

# VUL: get functions by web
vulrepo_src_path = r"F:\data\self_vul_repo\patches_and_files"

# SRC
src_proj_path = r"F:\project\project_source\openssl-1.0.0a"
src_func_path = os.path.join(os.getcwd(), src_proj_path.split('\\')[-1], 'functions')
src_funcDpd_path = os.path.join(os.getcwd(), src_proj_path.split('\\')[-1], 'dpd')
result_path = os.path.join(os.getcwd(), src_proj_path.split('\\')[-1], src_proj_path.split('\\')[-1]+".html")
