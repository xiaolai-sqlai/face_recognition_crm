# encoding: utf-8
from flask import Flask, render_template, url_for, request, make_response, json, redirect
from sqlalchemy import create_engine, Column, desc, func
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)

Base = declarative_base()

class Shop(Base):
    __tablename__ = 'shop'

    id = Column(String(10), primary_key=True)
    name = Column(String(40))
    username = Column(String(20))
    department = Column(Integer,default=0)

    def __init__(self,name,phone,department):
        self.name=name
        self.phone=phone
        self.department=department

    def __repr__(self):
        return '%d'%self.id


class Department(Base):
    __tablename__ = 'department'

    id = Column(Integer, primary_key=True)
    name = Column(String(40))

    def __init__(self,name):
        self.name=name

    def __repr__(self):
        return "%d"%self.id



# 初始化数据库连接:
engine = create_engine('mysql+mysqldb://root:lsq65602597@localhost:3306/subscribe?charset=utf8')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)


@app.route('/', methods=['GET'])
def index():
    userphone = request.cookies.get('userphone')
    session = DBSession()
    flag = 1
    currentname = session.query(GuestList).first().name
    current = session.query(GuestList).filter(GuestList.phone == userphone).first()
    count = session.query(GuestList).count()
    if userphone and current:
        flag = 0
        currentid = int(current.id)
        count = session.query(GuestList).filter(GuestList.id <= currentid).count()
        session.close()
    return render_template('subscribe.html', flag=flag, count=count, name=currentname)


@app.route('/subscribe',methods=['GET'])
def subscribe():
    if request.method == 'GET':
        session = DBSession()
        guests = session.query(GuestList).filter(GuestList.department==1).all()
        ress = []
        for guest in guests:
            res = {
                'name': guest.name,
                'phone': guest.phone,
                'department': str(guest.department)
            }
            ress.append(res)
        return json.dumps(ress)


@app.route('/information',methods=['GET', 'POST'])
def information():
    if request.method == 'GET':
        return render_template('information.html')
    else:
        name = request.form.get('name')
        phone = request.form.get('phone')
        session = DBSession()
        new_guest = GuestList(name=name, phone=phone, department='1')
        session.add(new_guest)
        session.commit()
        session.close()
        return '1'


@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == "GET":
        session = DBSession()
        lists = session.query(GuestList).all()
        currentPerson = session.query(GuestList).first()
        persons = []
        for list in lists:
            person = {
                'name': list.name,
                'phone': list.phone,
            }
            persons.append(person)
        print persons
        return render_template('admin.html', persons=persons, currentPerson=currentPerson)
    else:
        phone = request.form.get('phone')
        session = DBSession()
        print phone
        query= session.query(GuestList).filter(GuestList.phone == phone).first()
        session.delete(query)
        session.commit()
        session.close()
        return '1'


if __name__ == '__main__':
    app.run()
