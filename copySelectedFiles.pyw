from PyQt4 import QtCore, QtGui
import os
import os.path
import shutil

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding =QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
        def _translate(context, text, disambig):
            return QtGui.QApplication.translate(context, text, disambig)

def _getFiles(path):
    for root, dirs, files in os.walk(path):
        for name in files:
            yield os.path.realpath(os.path.join(root, name), path)

def _getFilesList(path):
    file_list = list()
    for root, dirs, files in os.walk(path):
        for name in files:
            file_list.append(os.path.relpath(os.path.join(root, name), path))
    return file_list

def _compareAndExclude(file_list1, file_list2, folder1, folder2, str_rex='-isf-parser-apex'):
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

def _copyFiles(files, str_srcFolder, str_dstFolder, process_bar, copy_button):
    copy_button.setDisabled(True)
    process_bar.setMaximum(len(files))
    for name in files:
        dst_dir = os.path.dirname(os.path.join(str_dstFolder, name))
        if not os.path.isdir(dst_dir):
            os.makedirs(dst_dir)
        print('Copy file %s' %name)
        shutil.copy2(os.path.join(str_srcFolder, name), dst_dir)
        value = process_bar.value()+1
        process_bar.setValue(value)
        QtGui.qApp.processEvents()
    copy_button.setEnabled(True)

def copySelectedFiles(str_srcFolder, str_dstFolder, str_rex, process_bar, copy_button):
    file_list1 = _getFilesList(str_srcFolder)
    file_list2 = _getFilesList(str_dstFolder)
    file2Copy = _compareAndExclude(file_list1, file_list2, str_srcFolder, str_dstFolder)
    _copyFiles(file2Copy, str_srcFolder, str_dstFolder, process_bar, copy_button)


class ui_CopySelectedFiles(QtGui.QDialog):
    def __init__(self):
        super(ui_CopySelectedFiles, self).__init__()
        self.createGridGroupBox()

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.gridGroupBox)
        self.setLayout(mainLayout)

        self.setWindowTitle('copySelectedFiles')
        self.str_srcFolder = str()
        self.str_dstFolder = str()
        self.str_rex = str()

        self._copy = False

    def createGridGroupBox(self):
        self.gridGroupBox = QtGui.QGroupBox('Grid layout')
        layout = QtGui.QGridLayout()

        src_lineEdit = QtGui.QLineEdit()
        src_lineEdit.setReadOnly(True)
        layout.addWidget(src_lineEdit, 0,0,1,4)

        src_browse = QtGui.QPushButton()
        src_browse.setText('Source')
        src_browse.clicked.connect(lambda: self.__folderBorwse(src_lineEdit))
        layout.addWidget(src_browse, 0,4,1,1)

        dst_lineEdit = QtGui.QLineEdit()
        dst_lineEdit.setReadOnly(True)
        layout.addWidget(dst_lineEdit, 1,0,1,4)

        dst_browse = QtGui.QPushButton()
        dst_browse.setText('Destination')
        dst_browse.clicked.connect(lambda: self.__folderBorwse(dst_lineEdit))
        layout.addWidget(dst_browse, 1,4,1,1)

        '''tableWidget = QtGui.QTableWidget()
        tableWidget.setColumnCount(2)
        tableWidget.setRowCount(5)
        for i, header in enumerate(['Copy from', 'Copy to']):
            item = QtGui.QTableWidgetItem(header)
            tableWidget.setHorizontalHeaderItem(i, item)
            item.setTextAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
            font = QtGui.QFont()
            font.setBold(True)
            font.setWeight(75)
            item.setFont(font)
        tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        tableWidget.verticalHeader().setVisible(False)
        layout.addWidget(tableWidget, 2,0,5,1)'''

        src_label = QtGui.QLabel('From')
        dst_label = QtGui.QLabel('To')
        to_label = QtGui.QLabel('-'*10)

        layout.addWidget(src_label, 2,0,1,1)
        layout.addWidget(dst_label, 2,3,1,1)

        self.src_model = QtGui.QFileSystemModel()
        self.src_model.setRootPath(QtCore.QDir.currentPath())
        self.treeView1 = QtGui.QTreeView()
        self.treeView1.setModel(self.src_model)
        layout.addWidget(self.treeView1, 3,0,5,1)

        self.dst_model = QtGui.QFileSystemModel()
        self.dst_model.setRootPath(QtCore.QDir.currentPath())
        self.treeView2 = QtGui.QTreeView()
        self.treeView2.setModel(self.dst_model)
        layout.addWidget(self.treeView2, 3,3,5,1)


        flt_list = ['Exclude *.isf','Exclude apex','Exclude parser']
        for i, radio in enumerate(flt_list):
            flt_radio = QtGui.QCheckBox(radio)
            layout.addWidget(flt_radio, 3+i,4,1,1)
            flt_radio.stateChanged.connect(self.__fltCheckBox)

        process_bar = QtGui.QProgressBar()
        process_bar.setMinimum(1)
        layout.addWidget(process_bar, 8,0,1,6)
        self.gridGroupBox.setLayout(layout)

        copy_button = QtGui.QPushButton('Copy')
        layout.addWidget(copy_button, 6,4,1,1)
        copy_button.clicked.connect(lambda: self.__copyFiles(copy_button, process_bar))

    def __copyFiles(self, copy_button, process_bar):
        if not self._copy:
            #self._copy = True
            copy_button.setDisabled(True)
            if process_bar.value() == process_bar.maximum():
                process_bar.reset()
                copy_button.setEnabled(True)
            QtCore.QTimer.singleShot(0, lambda: copySelectedFiles(self.str_srcFolder, self.str_dstFolder, self.str_rex, process_bar, copy_button))

    def __fltCheckBox(self):
        flt_radio= self.sender()
        checkname = flt_radio.text().replace('.', ' ').split(' ')[-1]
        if flt_radio.isChecked():
            self.str_rex += '-%s'%checkname
            print('%s checked.' %checkname)
        else:
            self.str_rex = self.str_rex.replace('-%s'%checkname,'')
            print('%s unchecked.' %checkname)
        print(self.str_rex)

    def __folderBorwse(self, lineEdit):
        pushButton = self.sender()
        fname = QtGui.QFileDialog.getExistingDirectory(caption = 'Locate %s folder'%(pushButton.text()))
        if len(fname)>1:
            if pushButton.text() == 'Source':
                self.str_srcFolder = fname
                lineEdit.setText(self.str_srcFolder)
                self.treeView1.setRootIndex(self.src_model.index(fname))
            elif pushButton.text() == 'Destination':
                self.str_dstFolder = fname
                lineEdit.setText(self.str_dstFolder)
                self.treeView2.setRootIndex(self.dst_model.index(fname))


if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    dialog = ui_CopySelectedFiles()
    sys.exit(dialog.exec_())
