# package import
from flask import Flask, render_template, request, jsonify, redirect, url_for
import requests

# flask setting
app = Flask(__name__)

# mongodb connect
from pymongo import MongoClient
client = MongoClient('mongodb+srv://test:test@cluster0.mai7p.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta

# import certifi
# ca = certifi.where()

# 현욱님 DB
# client2 = MongoClient('mongodb+srv://test:sparta@cluster0.arjwt.mongodb.net/Cluster0?retryWrites=true&w=majority')
# db2 = client2.dbsparta

# 크롤링

import requests
from bs4 import BeautifulSoup



@app.route('/')
def main():
    # countrys = list(db.countrys.find({}, {"_id": False}).limit(10))
    countrys = list(db.countrys.find({}, {"_id": False}))
    return render_template("index.html", countrys=countrys)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/detail/<post_num>')
def detail(post_num):

    # post_num에 해당하는 국가 정보 찾음
    country = db.countrys.find_one({'post_num': int(post_num)})

    # post_num에 해당하는 comment 정보 찾음
    country_comment = list(db.comments.find({'post_num': int(post_num)}, {'_id': False}))
    print(country_comment)

    comments = list(db.comments.find({},{'_id':False}))
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

    # id_receive = request.form["id_give"]
    comment_receive = request.form["comment_give"]
    post_num_receive = request.form["post_num_give"]

    # doc = {"index": index_receive, "id":id_receive, "comment": comment_receive}
    doc = {"post_num" : int(post_num_receive) ,"comment": comment_receive}
    db.comments.insert_one(doc)
    return jsonify({'result': 'success', 'msg': '커멘트 저장'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)