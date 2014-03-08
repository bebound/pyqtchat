import sys
import hashlib
import threading
import queue
import time
import datetime
import uuid
import localSettings
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg2
from PyQt4 import QtCore, QtGui, QtNetwork
import ui_serverMainWindow

Base = declarative_base()
serverPort = localSettings.serverPort
debug = localSettings.debug

#IP,port,username,心跳计时
clientList = []
#messageNumber,time,username,message
tempMessageList = []
messageNumber = 1
messageNumberLock = threading.Lock()
threadingList = []
stopThread = 0

#每条信息以###分割 信息内部以***分割
#clent发送信息第一段 1代表登陆 2代表注册 3代表发送信息 4断开连接 5心跳检测

#1,userName,userPWD
#2,userName,userPWD,userPhone,UserIDCard,userCity
#3,message
#4,断开连接
#5,心跳

#server发送信息第一段 1代表显示warning窗口 2代表显示information窗口 3代表对话内容 4代表登陆信息
#1,warning
#2,information
#3,messageNumber,time,userName,message
#4,0,失败信息 登录失败
#4,1 登陆成功

class User(Base):
    __tablename__ = 'user2'

    userID = Column(Integer, primary_key=True)
    userName = Column(String)
    hashedPassWord = Column(String)
    salt = Column(String)
    phone = Column(String)
    IDCard = Column(String)
    city = Column(String)
    activated = Column(Boolean)
    validTime = Column(Date)
    note = Column(String)
    userType = Column(Integer)
    regIP = Column(String)
    lastLoginIP = Column(String)
    messageNumber = Column(Integer)
    regDate = Column(DateTime)
    lastLoginTime = Column(DateTime)


    def __repr__(self):
        return "<User(id={0},userName={1})>".format(self.id, self.userName)


class serverMainWindow(QtGui.QMainWindow, ui_serverMainWindow.Ui_MainWindow):
    db = create_engine(localSettings.database)
    Session = sessionmaker()
    Session.configure(bind=db)
    session = Session()
    sigWarningMessage = QtCore.pyqtSignal(str)
    sigInformationMessage = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.setFixedSize(300, 200)
        self.stopButton.setEnabled(False)
        self.start()

        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.sigInformationMessage.connect(self.showInformationMessage)
        self.sigWarningMessage.connect(self.showWarningMessage)

    def changeStatus(self, text):
        self.statusbar.showMessage(text, 2000)

    def start(self):
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.changeStatus('开始运行')
        self.udpSocketGet = QtNetwork.QUdpSocket()
        try:
            self.udpSocketGet.bind(QtNetwork.QHostAddress.LocalHost, serverPort, QtNetwork.QUdpSocket.DontShareAddress)
            self.udpSocketGet.readyRead.connect(self.receive)
        except Exception as e:
            print(e)
            self.sigWarningMessage.emit('监听失败')
        t = threading.Thread(target=self.sendMessage)
        t.start()
        threadingList.append(t)
        t = threading.Thread(target=self.heartBeats)
        t.setDaemon(True)
        t.start()
        threadingList.append(t)
        t = threading.Thread(target=self.updateUI)
        t.setDaemon(True)
        t.start()
        threadingList.append(t)


    def stop(self):
        self.udpSocketGet.close()
        global stopThread
        stopThread = 1
        self.sendToEveryClient('2***服务器已停止，请稍后重新登录')
        self.stopButton.setEnabled(False)
        self.startButton.setEnabled(True)
        self.changeStatus('已停止')

    def receive(self):
        while self.udpSocketGet.hasPendingDatagrams():
            size = self.udpSocketGet.pendingDatagramSize()
            if size > 0:
                data, senderAddr, senderPort = self.udpSocketGet.readDatagram(size)
                if debug:
                    print('receive:', data.decode('utf-8'), senderAddr.toString(), senderPort)
                self.parseData(data.decode('utf-8'), senderAddr.toString(), senderPort)


    def sendToClient(self, data, clientAddress, clientPort):
        if debug:
            print('sendToClient:', clientAddress, clientPort, data)
        udpSocketSend = QtNetwork.QUdpSocket()
        try:
            udpSocketSend.writeDatagram(data.encode('utf-8'), QtNetwork.QHostAddress(clientAddress), clientPort)
            return True
        except:
            return False
        finally:
            udpSocketSend.close()


    def parseData(self, data, senderIP, senderPort):
        dataList = data.split('###')
        for i in dataList:
            j = i.split('***')

            # 登陆
            if j[0] == '1':
                if self.validatePassword(j[1], j[2]):
                    kk = self.session.query(User).filter_by(userName=j[1]).one()
                    if kk.activated:
                        if kk.validTime >= datetime.date.today():
                            self.sendToClient('4***1', senderIP, senderPort)
                            clientList.append([senderIP, senderPort, j[1], 0])
                            if debug:
                                print('登陆user:', j[1])
                            self.session.delete(kk)
                            kk.lastLoginIP = senderIP
                            kk.lastLoginTime = datetime.datetime.now()
                            self.session.add(kk)
                            self.session.commit()
                        else:
                            self.sendToClient('4***0***账号已过期', senderIP, senderPort)
                    else:
                        self.sendToClient('4***0***账号未激活', senderIP, senderPort)
                else:
                    self.sendToClient('4***0***用户名或密码错误', senderIP, senderPort)

            # 注册
            elif j[0] == '2':
                if (len(j[1]) >= 5 and len(j[2]) >= 6 and len(j[3]) == 11 and len(j[4]) == 18 and len(j[5]) > 0):
                    kk = 0
                    try:
                        kk = self.session.query(User).filter_by(userName=j[1]).one()
                    except Exception as e:
                        print(e)
                    if not kk:
                        tempHashedPassWord, tempSalt = self.createPassWord(j[2])
                        # regDate=time.strftime('%F %H:%M:%S'
                        tempUser = User(userName=j[1], hashedPassWord=tempHashedPassWord, salt=tempSalt, phone=j[3],
                                        IDCard=j[4], city=j[5], regIP=senderIP, regDate=datetime.datetime.now(),
                                        activated=False)
                        self.session.add(tempUser)
                        self.session.commit()
                        if debug:
                            print('添加新user:' + tempUser.userName)
                        self.sendToClient('1***注册成功', senderIP, senderPort)
                    else:
                        self.sendToClient('1***用户名已存在', senderIP, senderPort)
                else:
                    self.sendToClient('1***注册失败', senderIP, senderPort)

            # 接受信息
            elif j[0] == '3':
                username = ''
                for i in clientList:
                    if senderIP == i[0]:
                        username = i[2]
                        break
                if username:
                    global messageNumber
                    with messageNumberLock:
                        tempMessageList.append((messageNumber, time.strftime('%H:%M:%S'), username, j[1]))
                        messageNumber += 1

            # 断开连接
            elif j[0] == '4':
                for i in clientList:
                    if (i[0], i[2]) == (senderIP, j[1]):
                        clientList.remove(i)
                        break

            # 心跳
            elif j[0] == '5':
                for i in clientList:
                    if (i[0], i[2]) == (senderIP, j[1]):
                        i[3] = 0
                        break

            # 账号信息
            elif j[0] == '6':
                for i in clientList:
                    if (i[0], i[2]) == (senderIP, j[1]):
                        kk = self.session.query(User).filter_by(userName=j[1]).one()
                        validTime = kk.validTime
                        print(type(validTime), str(validTime))
                        self.sendToClient('5***' + str(validTime), senderIP, senderPort)

            # 改密码
            elif j[0] == '7':
                for i in clientList:
                    if (i[0], i[2]) == (senderIP, j[1]):
                        if self.validatePassword(j[1], j[2]):
                            kk = self.session.query(User).filter_by(userName=j[1]).one()
                            self.session.delete(kk)
                            tempHashedPassWord, tempSalt = self.createPassWord(j[3])
                            kk.salt = tempSalt
                            kk.hashedPassWord = tempHashedPassWord
                            self.session.add(kk)
                            self.session.commit()
                            self.sendToClient('1***密码修改成功', senderIP, senderPort)
                        else:
                            self.sendToClient('2***旧密码错误', senderIP, senderPort)
                        break


    def heartBeats(self):
        while not stopThread:
            for i in clientList:
                i[3] += 1
            for i in clientList:
                if i[3] >= 3:
                    clientList.remove(i)
            time.sleep(10)

    def updateUI(self):
        while not stopThread:
            self.lcdNumber.display(len(clientList))
            self.lcdNumber_2.display(messageNumber - 1)
            time.sleep(1)


    def sendMessage(self):
        while not stopThread:
            global tempMessageList
            if tempMessageList:
                sendData = ''
                for i in tempMessageList:
                    sendData = sendData + '3***' + str(i[0]) + '***' + str(i[1]) + '***' + str(i[2]) + '***' + str(
                        i[3]) + '###'
                if debug:
                    print('sendMeessage:', sendData)

                t = threading.Thread(target=self.sendToEveryClient, args=(sendData,))
                t.start()
                t.join()
                tempMessageList = []
            time.sleep(1)

    def sendToEveryClient(self, data):
        sendQueue = queue.Queue()
        for i in clientList:
            sendQueue.put((i[0], i[1]))
        th = []
        for i in range(100):
            t = threading.Thread(target=self.sendMessageToClient, args=(data, sendQueue))
            t.start()
            th.append(t)
        for i in th:
            i.join()

    def sendMessageToClient(self, data, sendQueue):
        while not sendQueue.empty():
            clientAddress, clientPort = sendQueue.get()
            if debug:
                print('sendMessageToClient:', clientAddress, clientPort, data)
            udpSocketSend = QtNetwork.QUdpSocket()
            try:
                udpSocketSend.writeDatagram(data.encode('utf-8'), QtNetwork.QHostAddress(clientAddress), clientPort)
            except:
                sendQueue.put(clientAddress)
            finally:
                sendQueue.task_done()


    def closeEvent(self, event):
        self.sendToEveryClient('2***服务器已停止，请稍后重新登录')
        global stopThread
        stopThread = 1
        self.udpSocketGet.close()

    def showWarningMessage(self, content):
        QtGui.QMessageBox.warning(self, '警告', content, buttons=QtGui.QMessageBox.Ok,
                                  defaultButton=QtGui.QMessageBox.NoButton)

    def showInformationMessage(self, content):
        QtGui.QMessageBox.information(self, '信息', content, buttons=QtGui.QMessageBox.Ok,
                                      defaultButton=QtGui.QMessageBox.NoButton)


    def createPassWord(self, password):
        salt = str(uuid.uuid4().hex)
        hashedPassword = hashlib.sha512(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()
        if debug:
            print('createPassWord:', password, salt, hashedPassword)
        return hashedPassword, salt


    def validatePassword(self, userName, password):
        kk = 0
        try:
            kk = self.session.query(User).filter_by(userName=userName).one()
        except Exception as e:
            if debug:
                print(e)
        if kk:
            tempHashedPassWord = kk.hashedPassWord
            tempSalt = kk.salt
            return tempHashedPassWord == hashlib.sha512(password.encode('utf-8') + tempSalt.encode('utf-8')).hexdigest()
        else:
            return False


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    myWindow = serverMainWindow()
    myWindow.show()
    app.exec_()