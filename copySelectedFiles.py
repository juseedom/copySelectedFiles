import os
import os.path
import shutil

def _getFiles(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            yield os.path.realpath(os.path.join(root, name), path)

def _getFIlesList(path):
    file_list = list()
    for root, dirs, files in os.walk(path):
        for name in files:
            file_list.append(os.path.relpath(os.path.join(root, name), path))
    return file_list

def _compareAndExclude(file_list, file_list2, folder1, folder2, str_rex='-isf-parser-apex'):
    commfile = list(set(file_list1)&set(file_list2))
    for name in commfile:
        file1 = os.stat(os.path.join(folder1, name))
        file2 = os.stat(os.path.join(folder2, name))
        if file1.st_size==file2.st_size and file1.st_mtime==file2.st_mtime:
            print('File %s already existed.' %name)
            file_list1.remove(name)
        else:
            print('File %s already existed but different version.' %name)
    if len(str_rex) != 0:
        ext = str_rex.split('-')[1:]
        print(file_list1)
        if 'isf' in ext:
            file_list1 = [a for a in file_list1 if a.split('.')[-1]!='isf']
        if 'parser' in ext:
            file_list1 = [a for a in file_list1 if a.count('\\')<1 or a.split('\\')[-2]!='parser_output']
        if 'apex' in ext:
            file_list1 = [a for a in file_list1 if a.count('\\')<2 or a.split('\\')[-3]!='apex_output']
    return file_list1

def _copyFiles(files, str_srcFolder, str_dstFolder):
    for name in files:
        dst_dir = os.path.dirname(os.path.join(str_dstFolder, name))
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        print('Copy file %s' %name)
        shutil.copy2(os.path.join(str_srcFolder, name), dst_dir)

def copySelectedFiles(str_srcFolder, str_dstFolder, str_rex, process_bar):
    file_list1 = _getFIlesList(str_srcFolder)
    file_list2 = _getFIlesList(str_dstFolder)
    file2Copy = _compareAndExclude(file_list1, file_list2, str_srcFolder, str_dstFolder)
    # process_bar.setMaximum(len(file2Copy))
    _copyFiles(file2Copy, str_srcFolder, str_dstFolder)

if __name__ == '__main__':
    str_srcFolder = ''
    str_dstFolder = ''
    str_rex = ''
    copySelectedFiles(str_srcFolder, str_dstFolder, str_rex)
