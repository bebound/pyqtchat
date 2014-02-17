# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'clientRegistrationWidget.ui'
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
        Form.setWindowModality(QtCore.Qt.ApplicationModal)
        Form.resize(228, 224)
        self.gridLayout = QtGui.QGridLayout(Form)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Form)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.userNameLineEdit = QtGui.QLineEdit(Form)
        self.userNameLineEdit.setToolTip(_fromUtf8(""))
        self.userNameLineEdit.setStatusTip(_fromUtf8(""))
        self.userNameLineEdit.setAccessibleDescription(_fromUtf8(""))
        self.userNameLineEdit.setInputMask(_fromUtf8(""))
        self.userNameLineEdit.setText(_fromUtf8(""))
        self.userNameLineEdit.setMaxLength(20)
        self.userNameLineEdit.setObjectName(_fromUtf8("userNameLineEdit"))
        self.gridLayout.addWidget(self.userNameLineEdit, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Form)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.userPWDLineEdit = QtGui.QLineEdit(Form)
        self.userPWDLineEdit.setMaxLength(20)
        self.userPWDLineEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.userPWDLineEdit.setObjectName(_fromUtf8("userPWDLineEdit"))
        self.gridLayout.addWidget(self.userPWDLineEdit, 1, 1, 1, 1)
        self.label_6 = QtGui.QLabel(Form)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)
        self.userPWDLineEdit2 = QtGui.QLineEdit(Form)
        self.userPWDLineEdit2.setMaxLength(20)
        self.userPWDLineEdit2.setEchoMode(QtGui.QLineEdit.Password)
        self.userPWDLineEdit2.setObjectName(_fromUtf8("userPWDLineEdit2"))
        self.gridLayout.addWidget(self.userPWDLineEdit2, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Form)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.userPhoneLineEdit = QtGui.QLineEdit(Form)
        self.userPhoneLineEdit.setMaxLength(11)
        self.userPhoneLineEdit.setObjectName(_fromUtf8("userPhoneLineEdit"))
        self.gridLayout.addWidget(self.userPhoneLineEdit, 3, 1, 1, 1)
        self.label_4 = QtGui.QLabel(Form)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.userIDCardLineEdit = QtGui.QLineEdit(Form)
        self.userIDCardLineEdit.setMaxLength(18)
        self.userIDCardLineEdit.setObjectName(_fromUtf8("userIDCardLineEdit"))
        self.gridLayout.addWidget(self.userIDCardLineEdit, 4, 1, 1, 1)
        self.label_5 = QtGui.QLabel(Form)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 5, 0, 1, 1)
        self.userCityLineEdit = QtGui.QLineEdit(Form)
        self.userCityLineEdit.setMaxLength(8)
        self.userCityLineEdit.setObjectName(_fromUtf8("userCityLineEdit"))
        self.gridLayout.addWidget(self.userCityLineEdit, 5, 1, 1, 1)
        self.registrationButton = QtGui.QPushButton(Form)
        self.registrationButton.setObjectName(_fromUtf8("registrationButton"))
        self.gridLayout.addWidget(self.registrationButton, 6, 0, 1, 2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "Form", None))
        self.label.setText(_translate("Form", "用户名", None))
        self.userNameLineEdit.setPlaceholderText(_translate("Form", "字母或数字(至少5位)", None))
        self.label_2.setText(_translate("Form", "密码", None))
        self.userPWDLineEdit.setPlaceholderText(_translate("Form", "字母或数字(至少6位)", None))
        self.label_6.setText(_translate("Form", "重复密码", None))
        self.userPWDLineEdit2.setPlaceholderText(_translate("Form", "字母或数字", None))
        self.label_3.setText(_translate("Form", "手机", None))
        self.label_4.setText(_translate("Form", "身份证", None))
        self.label_5.setText(_translate("Form", "城市", None))
        self.registrationButton.setText(_translate("Form", "注册", None))

