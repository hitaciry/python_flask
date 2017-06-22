import datetime

from flask import Flask, send_from_directory, jsonify, request
import mysql.connector
import collections
import glob

cnx = mysql.connector.connect(user='root', password='root',
                              host='127.0.0.1',
                              database='aliona_db')

curs = cnx.cursor()
addUserQuery = ("INSERT INTO users "
                "(login, password) "
                "VALUES (%s, %s)")
addGoodQuery = ("INSERT INTO goods"
                "(name,description,photo,count,price)"
                "VALUES ($s,$s,$s,$s, $s)")

addHistoryQuery = "INSERT INTO history ( user_id,good_id,time) VALUES($s,$s,$s) "
updateUserQuery = ("update users "
                   "SET login = %s, password = %s) "
                   "where id=%s")
updateGoodQuery = ("update goods"
                   "set name=%s,description=%s,photo=%s,count=%s,price=%s)"
                   "where id=%s")
incrimentGoodQuery = ("update goods"
                      "set count=count-1"
                      "where id=%s")
updateHistoryQuery = ()
deleteUserQuery = ("DELETE  users"
                   "WHERE id=%s ")
deleteGoodQuery = ("DELETE  users"
                   "WHERE id=%s ")
deleteHistoryQuery = ("DELETE  users"
                      "WHERE id=%s ")
UsersQuery = "Select * from users"
GoodsQuery = "Select * from goods"
HistorysQuery = "Select * from history_view"
HistorysForUserQuery = "Select * from history_view where  user_id=%s"
GetUserByLogin = "Select * from users where login=%s and password=%s"
app = Flask(__name__)


@app.route('/')
def index():
    return send_from_directory('site', "index.html")


@app.route('/bootstrap.css')
def bs():
    return send_from_directory('site', "bootstrap.css")


@app.route('/bootstrap-theme.css')
def bst():
    return send_from_directory('site', "bootstrap-theme.css")


@app.route('/jquery-3.2.1.min.js')
def jq():
    return send_from_directory('site', "jquery-3.2.1.min.js")


@app.route('/img/<string:name>')
def get_img(name):
    return send_from_directory('site/img', name)


@app.route('/goods')
def goods():
    goods_dict = []
    for row in curs.execute(GoodsQuery):
        d = collections.OrderedDict()
        d['id'] = row.id
        d['name'] = row.name
        d['description'] = row.description
        d['photo'] = row.photo
        d['count'] = row.count
        d['price'] = row.price
        goods_dict.append(d)
    return jsonify(goods_dict)


@app.route('/goods/edit')
def editGoods():
    d = request.get_json()
    curs.execute(updateGoodQuery, (d['name'], d['description'], d['photo'], d['count'], d['price'], d['id']))
    return {'success': 'done'}


@app.route('/goods/add')
def addGoods():
    d = request.get_json()
    curs.execute(addGoodQuery, (d['name'], d['description'], d['photo'], d['count'], d['price']))
    return {'success': 'done'}


@app.route('/goods/delete/<id>')
def deleteGoods(id):
    curs.execute(deleteGoods, id)
    return {'success': 'done'}


@app.route('/history/add?user_id=<user_id>&good_id=<good_id>')
def addHistory(user_id, good_id):
    curs.execute(addHistoryQuery, (user_id, good_id, datetime.now()))
    curs.execute(incrimentGoodQuery, good_id)
    return {'success': 'good added'}


@app.route('/history/<id>')
def historys(id=None):
    if id is None:
        row_history = curs.execute(HistorysQuery)
    else:
        row_history = curs.execute(HistorysQuery, id)
    users_dict = []
    for row in row_history:
        d = collections.OrderedDict()
        d['id'] = row.id
        d['login'] = row.login
        d['name'] = row.name
        d['price'] = row.price
        d['time'] = row.time
        d['user_id'] = row.user_id
        users_dict.append(d)
    return jsonify(users_dict)


@app.route('/history/delete/<id>')
def deleteHistory(id):
    curs.execute(deleteHistory, id)
    return {'success': 'done'}


@app.route('/login')
def loginf(login=None, password=None):
    if login is None:
        login = request.args.get('login')
    if password is None:
        password = request.args.get('password')
    try:
        usr = curs.execute(GetUserByLogin, (login, password))[0]
    except mysql.connector.errors:
        return {"error": "user with this parameters not exist"}
    return {"id": usr.id, "login": usr.login, 'isAdmin': usr.isAdmin}


@app.route('/reg')
def reg():
    login = request.args.get('login')
    password = request.args.get('password')
    try:
        usr = curs.execute(GetUserByLogin, (login, password))[0]
    except mysql.connector.errors.InternalError:
        curs.execute(addUserQuery, (login, password))
        return loginf(login, password)
    return {"error": "user with this parameters already exist"}


@app.route('/users')
def users():
    users_dict = []
    for row in curs.execute(UsersQuery):
        d = collections.OrderedDict()
        d['id'] = row.id
        d['login'] = row.login
        d['password'] = row.password
        d['isAdmin'] = row.isAdmin
        users_dict.append(d)
    return jsonify(users_dict)


@app.route('/user/edit')
def editUser():
    d = request.get_json()
    curs.execute(updateUserQuery, (d['login'], d['password'], d['isAdmin'], d['id']))
    return {'success': 'done'}


@app.route('/user/delete/<id>')
def deleteUser(id):
    curs.execute(deleteUser, id)
    return {'success': 'done'}


@app.route('/imgs')
def getImg():
    return jsonify(glob.glob("/img/*"))


if __name__ == '__main__':
    app.run(debug=True)
