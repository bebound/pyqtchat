# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'serverAccount.ui'
#
# Created: Fri Feb 14 14:20:48 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(614, 380)
        self.tableView = QtGui.QTableView(Form)
        self.tableView.setGeometry(QtCore.QRect(10, 10, 311, 331))
        self.tableView.setObjectName(_fromUtf8("tableView"))
        self.verticalLayoutWidget = QtGui.QWidget(Form)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(370, 30, 191, 291))
        self.verticalLayoutWidget.setObjectName(_fromUtf8("verticalLayoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.activeButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.activeButton.setObjectName(_fromUtf8("activeButton"))
        self.verticalLayout.addWidget(self.activeButton)
        self.pushButton = QtGui.QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.activeButton.setText(_translate("Form", "激活账号", None))
        self.pushButton.setText(_translate("Form", "PushButton", None))

