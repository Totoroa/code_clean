'''
create vulnerability repository.
1. get bad functions and good functions. And split bad functions into smaller folder.
2. get bad functions' cpg, and get dependence relationship. (By Joern)
3. get slice and build vulnerability repository.
'''
import config
import os

    
def get_func_by_git():
    import vul_get_func_by_git
    vul_get_func_by_git.main()

def get_func_by_web():
    import vul_get_func_by_web
    vul_get_func_by_web.main()

if __name__ == '__main__':
    #selete how to get the vul functions.
    get_func_by_git()
    get_func_by_web()
    import split_files_to_smaller
    split_files_to_smaller.split_func_files(config.vul_badFunc_path)
    
    # use Joern generate CPG and then get dependence relationship
    
    # generate vul_repo.
    