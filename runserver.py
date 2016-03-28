# encoding: utf-8
from flask import Flask, render_template, url_for, request, make_response, json, redirect
from sqlalchemy import create_engine, Column, desc, func
from sqlalchemy.types import String, Float, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sys

reload(sys)
sys.setdefaultencoding("utf-8")

app = Flask(__name__)

Base = declarative_base()


class Shop(Base):
    __tablename__ = 'shop'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    username = Column(String(20), unique=True)
    password = Column(String(20))

    def __init__(self, name, username, password):
        self.name = name
        self.username = username
        self.password = password

    def __repr__(self):
        return '%d' % self.id


class Member(Base):
    __tablename__ = 'member'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    phone = Column(String(20))
    credit = Column(Integer, default=0)
    balance = Column(Float)
    shop = Column(Integer)
    feature = Column(String(255), default='0')

    def __init__(self, name, phone, credit, balance, shop, feature):
        self.name = name
        self.phone = phone
        self.credit = credit
        self.balance = balance
        self.shop = shop
        self.feature = feature

    def __repr__(self):
        return "%d" % self.id


class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String(40))
    price = Column(Float)
    shop = Column(String(10))

    def __init__(self, name, price, shop):
        self.name = name
        self.price = price
        self.shop = shop

    def __repr__(self):
        return "%d" % self.id


class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    content = Column(String(255))
    member = Column(String(10))

    def __init__(self, content, member):
        self.content = content
        self.member = member

    def __repr__(self):
        return "%d" % self.id


# 初始化数据库连接:
engine = create_engine('mysql+mysqldb://root:lsq65602597@localhost:3306/crm?charset=utf8')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)


@app.route('/', methods=['GET', 'POST'])
def index():
    username = request.cookies.get('username')
    id = request.cookies.get('id')
    session = DBSession()
    currentName = session.query(Shop).filter(Shop.username == username).first().name
    members = session.query(Member).filter(Member.shop == id).all()
    session.close()
    return render_template('admin-index.html', name=currentName, members=members)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if (request.method == 'GET'):
        return render_template('admin-login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        session = DBSession()
        current = session.query(Shop).filter(Shop.username == username).first()
        session.close()
        if (current == None):
            return "0"
        elif (password != current.password):
            return "-1"
        else:
            return str(current.id)


@app.route('/add', methods=['GET', 'POST'])
def add():
    if (request.method == 'GET'):
        username = request.cookies.get('username')
        session = DBSession()
        currentName = session.query(Shop).filter(Shop.username == username).first().name
        session.close()
        return render_template('admin-add.html', name=currentName)
    else:
        username = request.cookies.get('username')
        id = request.cookies.get('id')
        name = request.form.get('name')
        phone = request.form.get('phone')
        balance = request.form.get('balance')
        session = DBSession()
        new_member = Member(name=name, phone=phone, credit=0, balance=balance, shop=id, feature='0')
        session.add(new_member)
        session.commit()
        session.close()
        return '1'


@app.route('/recharge/<id>', methods=['GET', 'POST'])
def recharge(id):
    if (request.method == 'GET'):
        username = request.cookies.get('username')
        session = DBSession()
        currentName = session.query(Shop).filter(Shop.username == username).first().name
        memberName = session.query(Member).filter(Member.id == id).first().name
        session.close()
        return render_template('admin-recharge.html', name=currentName, memberName=memberName, memberId=id)
    else:
        id = request.form.get('id')
        balance = request.form.get('balance')
        session = DBSession()
        alter_member = session.query(Member).filter(Member.id == id).first()
        alter_member.balance = float(balance) + alter_member.balance
        session.add(alter_member)
        session.commit()
        session.close()
        return '1'


@app.route('/addproject', methods=['GET', 'POST'])
def addproject():
    if (request.method == 'GET'):
        username = request.cookies.get('username')
        session = DBSession()
        currentName = session.query(Shop).filter(Shop.username == username).first().name
        session.close()
        return render_template('admin-addproject.html', name=currentName)
    else:
        username = request.cookies.get('username')
        id = request.cookies.get('id')
        name = request.form.get('name')
        price = request.form.get('price')
        session = DBSession()
        new_project = Product(name=name, price=price, shop=id)
        session.add(new_project)
        session.commit()
        session.close()
        return '1'


@app.route('/search', methods=['GET', 'POST'])
def search():
    if (request.method == 'GET'):
        username = request.cookies.get('username')
        session = DBSession()
        currentName = session.query(Shop).filter(Shop.username == username).first().name
        session.close()
        return render_template('admin-search.html')


@app.route('/consume', methods=['GET', 'POST'])
def consume():
    if (request.method == 'GET'):
        username = request.cookies.get('username')
        session = DBSession()
        currentName = session.query(Shop).filter(Shop.username == username).first().name
        session.close()
        return render_template('admin-consume.html')


@app.route('/config', methods=['GET', 'POST'])
def config():
    username = request.cookies.get('username')
    session = DBSession()
    currentName = session.query(Shop).filter(Shop.username == username).first().name
    session.close()
    return render_template('admin-config.html', name=currentName)
    # @app.route('/', methods=['GET'])
    # def index():
    #     userphone = request.cookies.get('userphone')
    #     session = DBSession()
    #     flag = 1
    #     currentname = session.query(GuestList).first().name
    #     current = session.query(GuestList).filter(GuestList.phone == userphone).first()
    #     count = session.query(GuestList).count()
    #     if userphone and current:
    #         flag = 0
    #         currentid = int(current.id)
    #         count = session.query(GuestList).filter(GuestList.id <= currentid).count()
    #         session.close()
    #     return render_template('subscribe.html', flag=flag, count=count, name=currentname)
    #
    #
    # @app.route('/subscribe', methods=['GET'])
    # def subscribe():
    #     if request.method == 'GET':
    #         session = DBSession()
    #         guests = session.query(GuestList).filter(GuestList.department == 1).all()
    #         ress = []
    #         for guest in guests:
    #             res = {
    #                 'name': guest.name,
    #                 'phone': guest.phone,
    #                 'department': str(guest.department)
    #             }
    #             ress.append(res)
    #         return json.dumps(ress)
    #
    #
    # @app.route('/information', methods=['GET', 'POST'])
    # def information():
    #     if request.method == 'GET':
    #         return render_template('information.html')
    #     else:
    #         name = request.form.get('name')
    #         phone = request.form.get('phone')
    #         session = DBSession()
    #         new_guest = GuestList(name=name, phone=phone, department='1')
    #         session.add(new_guest)
    #         session.commit()
    #         session.close()
    #         return '1'
    #
    #
    # @app.route('/admin', methods=['GET', 'POST'])
    # def admin():
    #     if request.method == "GET":
    #         session = DBSession()
    #         lists = session.query(GuestList).all()
    #         currentPerson = session.query(GuestList).first()
    #         persons = []
    #         for list in lists:
    #             person = {
    #                 'name': list.name,
    #                 'phone': list.phone,
    #             }
    #             persons.append(person)
    #         print persons
    #         return render_template('admin.html', persons=persons, currentPerson=currentPerson)
    #     else:
    #         phone = request.form.get('phone')
    #         session = DBSession()
    #         print phone
    #         query = session.query(GuestList).filter(GuestList.phone == phone).first()
    #         session.delete(query)
    #         session.commit()
    #         session.close()
    #         return '1'


if __name__ == '__main__':
    app.run(debug=True)
