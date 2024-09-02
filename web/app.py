#Flask 구동에 필요한 모듈들을 불러옵니다
from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

#세션을 사용할 때 필요한 비밀키를 임의의 값으로 설정합니다. 보안상 취약하지만 일단 개발단계라서 할 수 있는 방법을 조금 더 공부가 필요합니다.
app = Flask(__name__)
app.secret_key = 'this+is+woncheol+secretkey'

#로컬에 구동되고 있는 MySQL DB에 연결합니다. SQL 쿼리 사용을 위해 cursor라는 객체를 생성합니다.
db = pymysql.connect(host='localhost', port=3306, user='root', passwd='woncheol2ek!!', db='web', charset='utf8')
cursor = db.cursor()

#127.0.0.1:5000/ 페이지 이미 세션이 생성되어 있다면 index페이지를 반환하고 아닐경우 login페이지로 리다이렉션 합니다.
@app.route('/')
def first():
    if 'id' in session:
        id = session['id']
        return render_template('index.html', userid=id)
    return redirect(url_for('login'))

#join 호출 시 id와 pw를 form에서 submit 된 값을 변수에 넣고 미리 연결된 DB에 INSERT 구문을 활용하여 데이터를 생성합니다. 세션이 성공하면 id값을 goal에 전달합니다
@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']
                
        cursor.execute("INSERT INTO user (id, pw) VALUES (%s, %s)", (id, pw))
        db.commit()
        
        session['id'] = id
        return redirect(url_for('goal'))
    return render_template('join.html')

#회원가입이 완료되고 goal 호출 시 goal.html으로 세션을 통해 id를 전달합니다. 없을 경우 다시 login 페이지로 리다이렉션합니다.
@app.route('/goal')
def goal():
    if 'id' in session:
        id = session['id']
        return render_template('goal.html', userid=id)
    return redirect(url_for('login'))

#login 호출 시 login.htmldml form에서 submit 된 값을 변수에 넣고 SELECT 구문을 통해 사용자를 조회합니다. 사용자가 존재하면 로그인 성공을 서버 콘솔에 출력하고 index페이지에 id값을 전달하며 이외에는 서버 콘솔에 로그인 실패를 출력하고 다시 login 페이지로 리다이렉션 합니다.
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']

        
        cursor.execute("SELECT * FROM user WHERE id=%s AND pw=%s", (id, pw))
        user = cursor.fetchone()
        
        
        if user:
            print('로그인 성공');
            session['id'] = id
            return redirect(url_for('index'))
        
        else:
            print('로그인 실패');
            return redirect(url_for('login'))
        
    return render_template('login.html')

#index 페이지 호출 시 세션에서 id값을 받아와서 페이지에 출력해줍니다.
@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'id' in session:
        id = session['id']
        return render_template('index.html', userid=id)
    else:
        return redirect(url_for('login'))

#logout 시 세션의 id값을 빼주고 다시 login 페이지로 리다이렉션합니다.
@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
