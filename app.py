from pymongo import MongoClient
import jwt
import certifi
import datetime
import requests
from bs4 import BeautifulSoup
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


# flask setting
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

# mongodb connect

ca = certifi.where()

client = MongoClient('mongodb+srv://test:test@cluster0.mai7p.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

# 현욱님 DB
# client2 = MongoClient('mongodb+srv://test:sparta@cluster0.arjwt.mongodb.net/Cluster0?retryWrites=true&w=majority')
# db2 = client2.dbsparta

# 크롤링

SECRET_KEY = 'SPARTA'

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login3.html', msg=msg)


@app.route('/user/<username>')
def user(username):
    # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.users.find_one({"username": username}, {"_id": False})
        return render_template('user.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,  # 아이디
        "password": password_hash,  # 비밀번호
        "profile_name": username_receive,  # 프로필 이름 기본값은 아이디
        "profile_pic": "",  # 프로필 사진 파일 이름
        "profile_pic_real": "profile_pics/profile_placeholder.png",  # 프로필 사진 기본 이미지
        "profile_info": ""  # 프로필 한 마디
    }
    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.users.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/')
def main():
    # countrys = list(db.countrys.find({}, {"_id": False}).limit(10))
    countrys = list(db.countrys.find({}, {"_id": False}))
    return render_template("index.html", countrys=countrys)


@app.route('/detail/<post_num>')
def detail(post_num):

    # post_num에 해당하는 국가 정보 찾음
    country = db.countrys.find_one({'post_num': int(post_num)})

    # post_num에 해당하는 comment 정보 찾음
    country_comment = list(db.comments.find({'post_num': int(post_num)}, {'_id': False}))
    # print(country_comment)
    comments = list(db.comments.find({},{'_id':False}))

    try:
        token_receive = request.cookies.get('mytoken')
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]},{'_id':False})
        return render_template("detail.html", country_comment=country_comment, country=country, user_info=user_info)

    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return render_template("detail.html", country_comment=country_comment, country=country)



# 메인화면에서 나라, 이미지, desc 등 정보 크롤링, 저장
@app.route("/info", methods=["POST"])
def main_info():
    url = 'https://www.skyscanner.co.kr/news/inspiration/top10-europe-destinations-where-koreans-love-to-go'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    card_image = soup.select('#post-321 > div > div > div.entry-content > figure')
    card_title = soup.select('#post-321 > div > div > div.entry-content > h2')

    n = 0
    desc_list = []
    short_desc_list = []
    for desc in soup.select("p", class_="entry-content"):
        n = n + 1
        if (n > 2):
            desc_list.append(desc.text)
            short_desc_list.append((desc.text).split('.')[0])

    # print(desc_list)
    print(short_desc_list)

    check = list(db.countrys.find({}, {'_id': False}))
    # print(check)
    count = 0

    if len(check) == 0:
        for image, title in zip(card_image, card_title):
            count = count + 1
            image = image.select_one('img')['src']
            title = title.select_one('a').text
            # print(image, title)
            doc = {
                'post_num': count,
                'title': title,
                'image_link': image,
                'desc': desc_list[count - 1],
                'short_desc': short_desc_list[count - 1]
            }
            print(doc)

            db.countrys.insert_one(doc)

    return jsonify({'msg': 'main화면정보 저장완료'})



@app.route('/detail/save_comment', methods=['POST'])
def save_comment():
    # (to-do) id 변수로 가져오고 db에 넣어야함

    token_receive = request.cookies.get('mytoken')
    print("토큰정보")
    print(token_receive)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        comment_receive = request.form["comment_give"]
        post_num_receive = request.form["post_num_give"]

        doc = {
            "post_num": int(post_num_receive),
            "comment": comment_receive,
            "username": user_info["username"]
        }
        db.comments.insert_one(doc)
        return jsonify({'result': 'success', 'msg': '커멘트 저장'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/')
def log_out():
    token_receive = request.cookies.get('mytoken')
    if token_receive is not None:
        login_status = 1
        return render_template('index.html', login=login_status)
    else:
        login_status = 0
        return render_template('index.html', login=login_status)

if __name__ == '__main__':
    app.run('0.0.0.0', port=5500, debug=True)
