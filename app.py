from flask import Flask, redirect, url_for, render_template, request, session
import numpy as np
import pandas as pd
import datetime as dt 


# 读取20000词汇表
df_vocab = pd.read_csv('vocab20000.csv')

# 根据当前时间的秒数设置为随机函数的种子
now = dt.datetime.now()
my_seed = now.second
np.random.seed(my_seed)



# 启动Flask Web服务
app = Flask(__name__)
app.secret_key = "secretpasswd"

@app.route("/")
@app.route("/home")
def home():
    rounds = 5    # 测试高频词的范围，每轮1000词
    num_words = 10    # 挑选测试单词的个数
    w_list = list()    # 从20000单词中随即挑选50个单词序号
    for j in range(rounds):
        for i in range(num_words):
            start = 1000 * j + 1
            end = start + 1000 
            w_list.append(np.random.randint(start, end))    # 生成一个含有十个随机数的list
    session["wlist"] = w_list
    return render_template("index.html")

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["name"]
        volume = request.form["volume"]
        session["user"] = user
        session["volume"] = int(volume)
        session["number"] = 0
        session["score"] = 0
        return redirect(url_for("test"))
    else:
        if "user" in session:
            return redirect(url_for("test"))
        return render_template("login.html")

@app.route("/test", methods=["POST", "GET"])
def test():
    student = session["user"]
    number = session["number"]    # 获取当前题号
    if request.method == "POST":
        answer = request.form["answer"]
        i = session["answer"]
        if int(answer) == i:
            session["score"] = session["score"] + 1
        score = session["score"]
        
        return render_template("result.html", number=number, answer=answer, i=i, score=score, student=student)
    else:
        word_list = session["wlist"]
        session["number"] = session["number"] + 1
        if session["number"] > 50:
            score = session["score"]
            return render_template("final.html", score=score, student=student)
        word = df_vocab.loc[word_list[number], 'Word']    # 选取测试单词

        num_choice = 6    # 每题候选项个数
        i = np.random.randint(num_choice)    # 生成一个[1,num_choice]之间的随机数
        session["answer"] = i    # 正确答案在候选项中的序号存入session
        a_list = list()    # 候选答案在20000中的序号lsit
        a = word_list[number] - i    # 候选答案的起始序号
        for m in range(num_choice):
            a_list.append(a + m)
        meaning_list = df_vocab.loc[a_list, 'Meaning']    # 从20000单词表中提取候选答案
        meaning = meaning_list.to_list()    # 从Pandas转换成Python List

        return render_template("test.html", word=word, meaning=meaning)

@app.route("/logout", methods=["POST", "GET"])
def logout():
    session.pop("user", None)
    session.pop("volume", None)
    session.pop("number", None)
    session.pop("score", None)
    session.pop("wlist", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)