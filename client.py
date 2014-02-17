import sys
import re
import time
import threading
import requests
import localSettings
from PyQt4 import QtCore, QtGui, QtNetwork
import ui_clientMainWindow
import ui_clientLoginWidget
import ui_clientRegistrationWidget
import ui_clientAccountWidget

serverAddress = QtNetwork.QHostAddress('127.0.0.1')
serverPort = localSettings.serverPort
clientPort = localSettings.clientPort
debug = localSettings.debug
maxMessageNumber = 0
curUserName = ''
threadingList = []

#每条信息以###分割 信息内部以***分割
#clent发送信息第一段 1代表登陆 2代表注册 3代表发送信息 4断开连接 5心跳检测 6请求返回账号信息 7修改密码

#1,userName,userPWD
#2,userName,userPWD,userPhone,UserIDCard,userCity
#3,message
#4,userName
#5,userName
#6,userName
#7,userName,oldPWD,newPWD

#server发送信息第一段 1代表显示warning窗口 2代表显示information窗口 3代表对话内容 4代表登陆信息 5账号信息
#1,warning
#2,information
#3,messageNumber,time,userName,message
#4,0,失败信息 (登录失败)
#4,1 (登陆成功)
#5,validTime

class clientLoginWidget(QtGui.QWidget, ui_clientLoginWidget.Ui_Form):
    #sigClicked=QtCore.pyqtSignal(object)
    sigWarningMessage = QtCore.pyqtSignal(str)
    sigInformationMessage = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setFixedSize(300, 200)
        self.udpSocketGet = QtNetwork.QUdpSocket()
        try:
            global clientPort
            while not self.udpSocketGet.bind(QtNetwork.QHostAddress.LocalHost, clientPort,
                                             QtNetwork.QUdpSocket.DontShareAddress):
                clientPort += 1
            self.udpSocketGet.readyRead.connect(self.receive)
        except Exception as e:
            print(e)
            self.sigWarningMessage.emit('监听失败')

        self.setting = QtCore.QSettings('kk', 'ydt')
        if self.setting.value('savePwd'):
            self.savePwdCheckBox.setChecked(True)
            self.userNameLineEdit.setText(self.setting.value('user'))
            self.userPWDLineEdit.setText(self.setting.value('PWD'))

        self.userPWDLineEdit.returnPressed.connect(self.login)
        self.loginButton.clicked.connect(self.login)
        self.registrationButton.clicked.connect(self.registration)
        self.sigInformationMessage.connect(self.showInformationMessage)
        self.sigWarningMessage.connect(self.showWarningMessage)


    def login(self):
        userName = self.userNameLineEdit.text()
        userPWD = self.userPWDLineEdit.text()
        if self.savePwdCheckBox.isChecked():
            self.setting.setValue('savePwd', True)
            self.setting.setValue('user', userName)
            self.setting.setValue('PWD', userPWD)
        else:
            self.setting.setValue('savePwd', True)
            self.setting.setValue('user', '')
            self.setting.setValue('PWD', '')
        if len(userName) == 0 or len(userPWD) == 0:
            self.sigWarningMessage.emit('用户名或密码不能为空')
        else:
            if not self.sendToServer('1***' + userName + '***' + userPWD):
                self.sigWarningMessage.emit('登录失败')


    def registration(self):
        self.registrationWidget = clientRegistrationWidget()
        self.registrationWidget.show()


    def receive(self):
        while self.udpSocketGet.hasPendingDatagrams():
            size = self.udpSocketGet.pendingDatagramSize()
            if size > 0:
                data, senderAddr, senderPort = self.udpSocketGet.readDatagram(size)
                if debug:
                    print(data.decode('utf-8'), senderAddr.toString(), senderPort)
                self.parseData(data.decode('utf-8'))


    def parseData(self, data):
        dataList = data.split('###')
        for i in dataList:
            j = i.split('***')

            # 警告
            if j[0] == '1':
                self.sigWarningMessage.emit(j[1])

            # 信息
            elif j[0] == '2':
                self.sigInformationMessage.emit(j[1])

            # 登录
            elif j[0] == '4':
                if j[1] == '1':
                    self.success()
                elif j[1] == '0':
                    self.failed(j[2])

    def success(self):
        global curUserName
        curUserName = self.userNameLineEdit.text()
        self.udpSocketGet.close()
        self.close()
        self.mainWindow = clientMainWindow()
        self.mainWindow.show()

    def failed(self, info):
        self.sigWarningMessage.emit(info)

    def sendToServer(self, data):
        udpSocketSend = QtNetwork.QUdpSocket()
        udpSocketSend.bind(clientPort)
        try:
            udpSocketSend.writeDatagram(data.encode('utf-8'), serverAddress, serverPort)
            return True
        except:
            return False
        finally:
            udpSocketSend.close()

    def showWarningMessage(self, content):
        QtGui.QMessageBox.warning(self, '警告', content, buttons=QtGui.QMessageBox.Ok,
                                  defaultButton=QtGui.QMessageBox.NoButton)

    def showInformationMessage(self, content):
        QtGui.QMessageBox.information(self, '信息', content, buttons=QtGui.QMessageBox.Ok,
                                      defaultButton=QtGui.QMessageBox.NoButton)


class clientRegistrationWidget(QtGui.QWidget, ui_clientRegistrationWidget.Ui_Form):
    sigWarningMessage = QtCore.pyqtSignal(str)
    sigInformationMessage = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setFixedSize(220, 200)

        digitLetterRegex = QtCore.QRegExp(r'\w*')
        digitRegex = QtCore.QRegExp(r'\d*')
        chineseRegex = QtCore.QRegExp(r'[\u4e00-\u9fa5]*')
        self.userNameLineEdit.setValidator(QtGui.QRegExpValidator(digitLetterRegex))
        self.userPWDLineEdit.setValidator(QtGui.QRegExpValidator(digitLetterRegex))
        self.userPWDLineEdit2.setValidator(QtGui.QRegExpValidator(digitLetterRegex))
        self.userPhoneLineEdit.setValidator(QtGui.QRegExpValidator(digitRegex))
        self.userIDCardLineEdit.setValidator(QtGui.QRegExpValidator(digitLetterRegex))
        self.userCityLineEdit.setValidator(QtGui.QRegExpValidator(chineseRegex))

        self.registrationButton.clicked.connect(self.sendRegistrationData)
        self.sigInformationMessage.connect(self.showInformationMessage)
        self.sigWarningMessage.connect(self.showWarningMessage)

    def sendRegistrationData(self, a):
        userName = self.userNameLineEdit.text()
        userPWD = self.userPWDLineEdit.text()
        userPWD2 = self.userPWDLineEdit2.text()
        userPhone = self.userPhoneLineEdit.text()
        userIDCard = self.userIDCardLineEdit.text()
        userCity = self.userCityLineEdit.text()
        if len(userName) < 5:
            self.sigWarningMessage.emit('用户名至少5位')
        else:
            if userPWD != userPWD2:
                self.sigWarningMessage.emit('两次密码不相同')
            else:
                if len(userPWD) < 6:
                    self.sigWarningMessage.emit('密码长度至少为6位')
                else:
                    if len(userPhone) != 11:
                        self.sigWarningMessage.emit('手机号码错误')
                    else:
                        if len(userIDCard) != 18:
                            self.sigWarningMessage.emit('身份证号码错误')
                        else:
                            data = '2***' + userName + '***' + userPWD + '***' + userPhone + '***' + userIDCard + '***' + userCity
                            if self.sendToServer(data):
                                self.sigWarningMessage.emit('注册信息已发送')

                            else:
                                self.sigWarningMessage.emit('注册信息发送失败')

    def sendToServer(self, data):
        udpSocketSend = QtNetwork.QUdpSocket()
        udpSocketSend.bind(clientPort)
        try:
            udpSocketSend.writeDatagram(data.encode('utf-8'), serverAddress, serverPort)
            return True
        except:
            return False
        finally:
            udpSocketSend.close()


    def showWarningMessage(self, content):
        QtGui.QMessageBox.warning(self, '警告', content, buttons=QtGui.QMessageBox.Ok,
                                  defaultButton=QtGui.QMessageBox.NoButton)

    def showInformationMessage(self, content):
        QtGui.QMessageBox.information(self, '信息', content, buttons=QtGui.QMessageBox.Ok,
                                      defaultButton=QtGui.QMessageBox.NoButton)


class clientMainWindow(QtGui.QMainWindow, ui_clientMainWindow.Ui_MainWindow):
    sigWarningMessage = QtCore.pyqtSignal(str)
    sigInformationMessage = QtCore.pyqtSignal(str)
    sigAddMessage = QtCore.pyqtSignal(str, str, str, str)
    sigDisplayValidTime = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        #self.getIP()
        self.udpSocketGet = QtNetwork.QUdpSocket()
        try:
            self.udpSocketGet.bind(QtNetwork.QHostAddress.LocalHost, clientPort, QtNetwork.QUdpSocket.DontShareAddress)
            self.udpSocketGet.readyRead.connect(self.receive)
        except Exception as e:
            print(e)
            self.sigWarningMessage.emit('监听失败')
        t = threading.Thread(target=self.heartBeats)
        t.setDaemon(True)
        t.start()
        threadingList.append(t)

        self.tableWidget.setColumnCount(4)
        self.tableWidget.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.tableWidget.setHorizontalHeaderLabels(('信息编号', '时间', '用户', '信息'))
        #self.tableWidget.setColumnWidth(0,100)
        #self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        #self.tableWidget.resizeColumnsToContents()


        self.udpSocketGet.readyRead.connect(self.receive)
        self.sendButton.clicked.connect(self.sendMessage)
        self.sigInformationMessage.connect(self.showInformationMessage)
        self.sigWarningMessage.connect(self.showWarningMessage)
        self.sigAddMessage.connect(self.addMessage)
        self.accountButton.clicked.connect(self.openAccountWidget)


    def getIP(self):
        r = requests.get('http://www.whereismyip.com')
        searchIP = re.compile(r'(\d+\.\d+\.\d+\.\d+)')
        print(searchIP.search(r.text).group(1))


    def changeStatus(self, text):
        self.statusbar.showMessage(text, 2000)

    def sendMessage(self):
        text = self.textEdit.toPlainText()
        if len(text) == 0:
            self.sigWarningMessage.emit('发送信息不能为空')
        else:
            if self.sendToServer('3***' + text):
                self.sigInformationMessage.emit('已发送')
                self.textEdit.setText('')
            else:
                self.sigWarningMessage.emit('发送失败')

    def addMessage(self, messageNumber, time, userName, message):
        curRow = self.tableWidget.rowCount()
        self.tableWidget.setRowCount(curRow + 1)
        self.tableWidget.setItem(curRow, 0, QtGui.QTableWidgetItem(messageNumber))
        self.tableWidget.setItem(curRow, 1, QtGui.QTableWidgetItem(time))
        self.tableWidget.setItem(curRow, 2, QtGui.QTableWidgetItem(userName))
        self.tableWidget.setItem(curRow, 3, QtGui.QTableWidgetItem(message))
        self.tableWidget.resizeRowsToContents()

    def receive(self):
        while self.udpSocketGet.hasPendingDatagrams():
            size = self.udpSocketGet.pendingDatagramSize()
            if size > 0:
                data, senderAddr, senderPort = self.udpSocketGet.readDatagram(size)
                if debug:
                    print('receive:', data.decode('utf-8'), senderAddr.toString(), senderPort)
                self.parseData(data.decode('utf-8'))

    def changePassWord(self, userName, oldPassWord, newPassWord):
        self.sendToServer('7***' + userName + '***' + oldPassWord + '***' + newPassWord)

    def parseData(self, data):
        dataList = data.split('###')
        for i in dataList:
            j = i.split('***')
            # 警告
            if j[0] == '1':
                self.sigWarningMessage.emit(j[1])

            # 信息
            elif j[0] == '2':
                self.sigInformationMessage.emit(j[1])
            # message
            elif j[0] == '3':
                global maxMessageNumber
                if int(j[1]) > maxMessageNumber:
                    maxMessageNumber = int(j[1])
                    self.sigAddMessage.emit(j[1], j[2], j[3], j[4])
            # accountInfo
            elif j[0] == '5':
                self.sigDisplayValidTime.emit(j[1])

    def heartBeats(self):
        while True:
            self.sendToServer('5***' + curUserName)
            time.sleep(10)

    def openAccountWidget(self):
        self.accountWidget = clientAccountWidget()
        self.accountWidget.show()
        self.accountWidget.sigChangePassWord.connect(self.changePassWord)
        #self.accountWidget.sigRequestAccountInfo.connect(lambda :print('emit'))
        #self.accountWidget.sigRequestAccountInfo.connect(lambda :self.sendToServer('6***'+curUserName))
        self.sendToServer('6***' + curUserName)
        self.sigDisplayValidTime.connect(self.accountWidget.updateUI)

    def showWarningMessage(self, content):
        QtGui.QMessageBox.warning(self, '警告', content, buttons=QtGui.QMessageBox.Ok,
                                  defaultButton=QtGui.QMessageBox.NoButton)

    def showInformationMessage(self, content):
        QtGui.QMessageBox.information(self, '信息', content, buttons=QtGui.QMessageBox.Ok,
                                      defaultButton=QtGui.QMessageBox.NoButton)

    def sendToServer(self, data):
        udpSocketSend = QtNetwork.QUdpSocket()
        udpSocketSend.bind(clientPort)
        try:
            udpSocketSend.writeDatagram(data.encode('utf-8'), serverAddress, serverPort)
            if debug:
                print('sendToServer', data)
            return True
        except:
            return False
        finally:
            udpSocketSend.close()

    def closeEvent(self, event):
        self.sendToServer('4***' + curUserName)


class clientAccountWidget(QtGui.QWidget, ui_clientAccountWidget.Ui_Form):
    #sigRequestAccountInfo = QtCore.pyqtSignal()
    sigChangePassWord = QtCore.pyqtSignal(str, str, str)
    sigWarningMessage = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.setFixedSize(300, 250)

        self.changePassWordButton.clicked.connect(self.changePassWord)
        self.sigWarningMessage.connect(self.showWarningMessage)

        #self.sigRequestAccountInfo.emit()

    def changePassWord(self):
        oldPassWord = self.lineEdit.text()
        newPassWord = self.lineEdit_2.text()
        newPassWord2 = self.lineEdit_3.text()
        if len(oldPassWord) >= 6:
            if newPassWord == newPassWord2:
                if len(newPassWord) >= 6:
                    self.sigChangePassWord.emit(curUserName, oldPassWord, newPassWord)
                    self.close()
                else:
                    self.sigWarningMessage.emit('新密码小于6位')
            else:
                self.sigWarningMessage.emit('两次输入密码不一致')
        else:
            self.sigWarningMessage.emit('旧密码小于6位')

    def updateUI(self, validTime):
        self.userNameLabel.setText(curUserName)
        self.userValidLabel.setText(validTime)

    def showWarningMessage(self, content):
        QtGui.QMessageBox.warning(self, '警告', content, buttons=QtGui.QMessageBox.Ok,
                                  defaultButton=QtGui.QMessageBox.NoButton)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    loginWidget = clientLoginWidget()
    loginWidget.show()
    app.exec_()