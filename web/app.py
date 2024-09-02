from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = 'this+is+woncheol+secretkey'

db = pymysql.connect(host='localhost', port=3306, user='root', passwd='woncheol2ek!!', db='web', charset='utf8')
cursor = db.cursor()

@app.route('/')
def first():
    if 'id' in session:
        id = session['id']
        return render_template('goal.html', userid=id)
    return redirect(url_for('login'))

@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']
                
        cursor.execute("INSERT INTO user (id, pw) VALUES (%s, %s)", (id, pw))
        db.commit()
        
        session['id'] = id
        return redirect(url_for('first'))

    return render_template('join.html')

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

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'id' in session:
        id = session['id']
        return render_template('index.html', userid=id)
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
