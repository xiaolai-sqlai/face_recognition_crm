# encoding: utf-8
from flask import Flask, render_template, url_for, request, make_response, json, redirect
from sqlalchemy import create_engine, Column, desc, func
from sqlalchemy.types import String, Float, Integer, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sys
import datetime

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
    date = Column(Date)
    sum = Column(Float)

    def __init__(self, content, member, date, sum):
        self.content = content
        self.member = member
        self.date = date
        self.sum = sum

    def __repr__(self):
        return "%d" % self.id


# 初始化数据库连接:
engine = create_engine('mysql+mysqldb://root:lsq65602597@localhost:3306/crm?charset=utf8')
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)


@app.route('/', methods=['GET', 'POST'])
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


@app.route('/member', methods=['GET', 'POST'])
def index():
    username = request.cookies.get('username')
    id = request.cookies.get('id')
    session = DBSession()
    currentName = session.query(Shop).filter(Shop.username == username).first().name
    members = session.query(Member).filter(Member.shop == id).all()
    session.close()
    return render_template('admin-index.html', name=currentName, members=members)


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


@app.route('/recognize', methods=['GET', 'POST'])
def recognize():
    if (request.method == 'GET'):
        username = request.cookies.get('username')
        session = DBSession()
        currentName = session.query(Shop).filter(Shop.username == username).first().name
        session.close()
        return render_template('admin-recognize.html', name=currentName)


@app.route('/search', methods=['GET', 'POST'])
def search():
    username = request.cookies.get('username')
    if (request.method == 'GET'):
        session = DBSession()
        currentName = session.query(Shop).filter(Shop.username == username).first().name
        session.close()
        return render_template('admin-search.html', name=currentName)
    else:
        phone = request.form.get('phone')
        session = DBSession()
        currentName = session.query(Shop).filter(Shop.username == username).first().name
        print phone
        member = session.query(Member).filter(Member.phone == phone).one()
        session.close()
        return render_template('admin-findone.html', name=currentName, member=member)


@app.route('/consume/<id>', methods=['GET', 'POST'])
def consume(id):
    if (request.method == 'GET'):
        username = request.cookies.get('username')
        session = DBSession()
        currentName = session.query(Shop).filter(Shop.username == username).first().name
        shopId = session.query(Shop).filter(Shop.username == username).one().id
        member = session.query(Member).filter(Member.id == id).one()
        lists = session.query(Product).filter(Product.shop == shopId).all()
        session.close()
        return render_template('admin-consume.html', name=currentName, member=member, lists=lists)


@app.route('/content', methods=['GET', 'POST'])
def content():
    member = request.form.get('member')
    content = request.form.get('content')
    sum = request.form.get('sum')
    session = DBSession()
    new_history = History(content=content, member=member, date=datetime.date.today(), sum=sum)
    session.add(new_history)
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


@app.route('/history/<id>', methods=['GET'])
def history(id):
    username = request.cookies.get('username')
    session = DBSession()
    currentName = session.query(Shop).filter(Shop.username == username).first().name
    histories = session.query(History).filter(History.member == id).all()
    memberName = session.query(Member).filter(Member.id == id).first().name
    session.close()
    return render_template('admin-history.html', name=currentName, memberName=memberName, histories=histories)


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


@app.route('/list', methods=['GET', 'POST'])
def list():
    username = request.cookies.get('username')
    id = request.cookies.get('id')
    session = DBSession()
    currentName = session.query(Shop).filter(Shop.username == username).first().name
    lists = session.query(Product).filter(Product.shop == id).all()
    session.close()
    return render_template('admin-list.html', name=currentName, lists=lists)


@app.route('/alterProduct/<id>', methods=['GET', 'POST'])
def alterProduct(id):
    if(request.method == 'GET'):
        username = request.cookies.get('username')
        session = DBSession()
        currentName = session.query(Shop).filter(Shop.username == username).first().name
        productName = session.query(Product).filter(Product.id == id).first().name
        session.close()
        return render_template('admin-alterproject.html', name=currentName, productName=productName, id=id)
    else:
        price = request.form.get('price')
        session = DBSession()
        alter_product = session.query(Product).filter(Product.id == id).first()
        alter_product.price = float(price)
        session.add(alter_product)
        session.commit()
        session.close()
        return '1'


@app.route('/config', methods=['GET', 'POST'])
def config():
    username = request.cookies.get('username')
    session = DBSession()
    currentName = session.query(Shop).filter(Shop.username == username).first().name
    session.close()
    return render_template('admin-config.html', name=currentName)


if __name__ == '__main__':
    app.run(debug=True)
