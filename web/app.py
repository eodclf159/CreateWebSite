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
        return render_template('index.html', userid=id)
    return redirect(url_for('login'))

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

@app.route('/goal')
def goal():
    if 'id' in session:
        id = session['id']
        return render_template('goal.html', userid=id)
    return redirect(url_for('login'))

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
        
        cursor.execute("SELECT * FROM posting ORDER BY created_at DESC")
        posts = cursor.fetchall()
        print("데이터 베이스를 가져옵니다", len(posts))
        
        return render_template('index.html', userid=id, posts=posts)
        
    else:
        return redirect(url_for('login'))

@app.route('/write_post', methods=['GET'])
def write_post():
    if 'id' in session:
        id = session['id']
        return render_template('write_post.html', userid=id)
    return redirect(url_for('login'))

@app.route('/upload_post', methods=['POST'])
def upload_post():
    if 'id' in session:
        title = request.form['title']
        content = request.form['content']
        author = session['id']
        
        cursor.execute("INSERT INTO posting (author, title, content) VALUES (%s, %s, %s)", (author, title, content))
        db.commit()
        
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/post/<int:post_id>')
def show_post(post_id):
    if 'id' in session:
        id = session['id']
        
        cursor.execute("SELECT * FROM posting WHERE id = %s", (post_id,))
        post = cursor.fetchone()
        
        if post:
            return render_template('show_post.html', userid=id, post=post)
        else:
            return "존재하지 않는 게시물"
    else:
        return redirect(url_for('login'))

@app.route('/delete_post/<int:post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    if 'id' in session:
        cursor.execute("DELETE FROM posting WHERE id = %s", (post_id,))
        db.commit()
        print("게시글을 삭제합니다");
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/edit_post/<int:post_id>', methods=['GET'])
def edit_post(post_id):
    if 'id' in session:
        id = session['id']
        
        cursor.execute("SELECT * FROM posting WHERE id = %s", (post_id,))
        post = cursor.fetchone()
        
        if post:
            return render_template('edit_post.html', userid=id, post=post)
        else:
            return "존재하지 않는 게시물입니다."
    else:
        return redirect(url_for('login'))

@app.route('/update_post/<int:post_id>', methods=['POST'])
def update_post(post_id):
    if 'id' in session:
        id = session['id']
        title = request.form['title']
        content = request.form['content']
        
        cursor.execute("UPDATE posting SET title = %s, content = %s WHERE id = %s", (title, content, post_id))
        db.commit()
        
        return redirect(url_for('show_post', post_id=post_id))
    else:
        return redirect(url_for('login'))
        


@app.route('/search', methods=['GET'])
def search():
    search = request.args.get('search', '')
    search_option = request.args.get('search_option', 'all')

    if search_option == 'title':
        cursor.execute("SELECT * FROM posting WHERE title LIKE %s", ('%' + search + '%',))
    elif search_option == 'content':
        cursor.execute("SELECT * FROM posting WHERE content LIKE %s", ('%' + search + '%',))
    else:  
        cursor.execute("SELECT * FROM posting WHERE title LIKE %s OR content LIKE %s", ('%' + search + '%', '%' + search + '%'))

    posts = cursor.fetchall()  

    return render_template('index.html', posts=posts, search=search, search_option=search_option)
        

@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
