from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import psycopg2
import localSettings

Base = declarative_base()


class User(Base):
    __tablename__ = 'user2'

    userID = Column(Integer, primary_key=True)
    userName = Column(String)
    hashedPassWord=Column(String)
    salt=Column(String)
    phone=Column(String)
    IDCard=Column(String)
    city=Column(String)
    activated=Column(Boolean)
    validTime=Column(Date)
    note=Column(String)
    userType=Column(Integer)
    regIP=Column(String)
    lastLoginIP=Column(String)
    lastLoginTime=Column(DateTime)
    messageNumber=Column(Integer)
    regDate=Column(DateTime)



    def __repr__(self):
        return "<User(id={0},userName={1})>".format(self.id, self.userName)

database='postgresql+psycopg2://'+localSettings.postgreUser+':'+localSettings.postgrePWD+'@localhost/'+localSettings.postgreDatabase
db = create_engine(database)

# 创建数据库
Base.metadata.create_all(db)

Session = sessionmaker()
Session.configure(bind=db)
session = Session()
# 插入
# tempUser=User(userName='kk2')
# session.add(tempUser)
# session.commit()

# for user in session.query(User).filter_by(userName='kk'):
#     print(user)

# 删除
# temp=session.query(User).filter_by(userName='kk')
# session.delete(temp)



