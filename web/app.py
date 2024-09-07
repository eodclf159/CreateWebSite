# Flask 웹 프레임 워크를 통한 웹 서버 생성 및 Pymysql을 통한 Database 연결
from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = 'this+is+woncheol+secretkey' # 세션 암호화를 통한 비밀키

db = pymysql.connect(host='localhost', port=3306, user='root', passwd='woncheol2ek!!', db='web', charset='utf8')  # 로컬 구성 DB 연결
cursor = db.cursor() # 데이터베이크 쿼리 실행 준비

@app.route('/') # 루트 디렉토리 접근 시
def first():
    if 'id' in session: # 로그인 상태라면
        id = session['id']
        return render_template('index.html', userid=id) # index.html 반환
    return redirect(url_for('login')) # 로그인 아니라면 로그인 페이지 반환

@app.route('/join', methods=['GET', 'POST']) # 회원가입 접근 시
def join():
    if request.method == 'POST': # 포스트 방식으로 받은 데이터를 각각 저장해서
        id = request.form['id']
        pw = request.form['pw']
                
        cursor.execute("INSERT INTO user (id, pw) VALUES (%s, %s)", (id, pw)) # user 테이블에 id, pw 값 추가
        db.commit() #데이터 베이스 저장
        
        session['id'] = id # 세션 발행
        return redirect(url_for('goal')) # 회원가입 성공으로 리다이렉트
    return render_template('join.html') 

@app.route('/goal') # 회원가입 성공 접근 시
def goal():
    if 'id' in session: # 세션이 있다면
        id = session['id'] 
        return render_template('goal.html', userid=id) # 회원가입 성공 페이지 반환 및 userid에 id 값 전달
    return redirect(url_for('login')) # 아니면 로그인 페이지 리다이렉트

@app.route('/login', methods=['GET', 'POST']) # 로그인 페이지 접근 시
def login():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']
        
        cursor.execute("SELECT * FROM user WHERE id=%s AND pw=%s", (id, pw)) # user 테이블에 입력받은 id, pw와 일치하는 값 검색
        user = cursor.fetchone() # 행 1개 가지고 와서 user에 저장
        
        
        if user: # 행 1개가 저장됐다면
            print('로그인 성공'); # 로그인 성공 로깅
            session['id'] = id # 세션 발행
            return redirect(url_for('index')) # index 리다이렉트
        
        else: # 행에 저장되지 않았다면
            print('로그인 실패'); # 로그인 실패 로깅
            return redirect(url_for('login')) # login 리다이렉트
        
    return render_template('login.html') 

@app.route('/index', methods=['GET', 'POST']) # 인덱스 페이지 접근 시
def index():
    if 'id' in session: # 로그인 한 계정이라면
        id = session['id'] 
        
        cursor.execute("SELECT * FROM posting ORDER BY created_at DESC") # posting 테이블에서 생성날짜를 기준으로 내림차순 정렬하여 게시글 목록 가져오기
        posts = cursor.fetchall() # 전체 데이터를 가지고 옴
        print("데이터 베이스를 가져옵니다", len(posts)) # 웹 서버에 로깅
        
        return render_template('index.html', userid=id, posts=posts)
        
    else: # 로그인 한 사람이 아니라면
        return redirect(url_for('login')) # login 리다이렉트

@app.route('/write_post', methods=['GET']) # 게시글 작성 접근 시
def write_post():
    if 'id' in session: # 로그인 한 사람이라면
        id = session['id'] 
        return render_template('write_post.html', userid=id) # write_post.html 반환 및 userid에 id 전달
    return redirect(url_for('login')) # 로그인 안하면 로그인 페이지 리다이렉트

@app.route('/upload_post', methods=['POST']) # 게시글 업로드 시 (write_post.html에서 호출)
def upload_post():
    if 'id' in session:
        title = request.form['title'] # form 에서 전달 받은 title값을 title 변수에 저장 
        content = request.form['content'] # form 에서 전달 받은 content값을 content 변수에 저장
        author = session['id']
        
        cursor.execute("INSERT INTO posting (author, title, content) VALUES (%s, %s, %s)", (author, title, content)) # posting 테이블 변수 author, title, content 필드에 변수 author, title, content 값을 저장
        db.commit() # 데이터 베이스 저장
        
        return redirect(url_for('index')) # index 리다이렉트
    else:
        return redirect(url_for('login')) # 로그인 안했으면 로그인 페이지 리다이렉트

@app.route('/post/<int:post_id>') #/post에 게시글 번호 접근 시
def show_post(post_id): #정수 형태의 post_id 를 변수로 불러옴
    if 'id' in session:
        id = session['id']
        
        cursor.execute("SELECT * FROM posting WHERE id = %s", (post_id,)) # posting 테이블에 id 값이 변수로 불러온 post_id 인 값을 조회
        post = cursor.fetchone() # 행 1개만 post 변수에 저장
        
        if post: # post에 데이터가 저장되어 있으면
            return render_template('show_post.html', userid=id, post=post) # show_post.html(상세 게시글 페이지) 반환 userid에 세션 속 id값, post에 조회된 post 값 포함하여 리다이렉트
        else:
            return "존재하지 않는 게시물" # post에 데이터가 저장되어 있지 않으면 빈페이지에 "존재하지 않는 게시물" 반환
    else:
        return redirect(url_for('login')) # 로그인 안했으면 login 페이지 리다이렉트

@app.route('/delete_post/<int:post_id>', methods=['GET', 'POST']) # /delete_post에 게시글 번호 접근 시
def delete_post(post_id): # 정수 형태의 post_id를 변수로 불러옴
    if 'id' in session:
        cursor.execute("DELETE FROM posting WHERE id = %s", (post_id,)) # posting 테이블에 id 값이 변수로 불러온 post_id 인 값을 삭제
        db.commit() # DB 저장
        print("게시글을 삭제합니다"); # 웹 서버에 게시글 삭제 로깅
        return redirect(url_for('index')) # index 리다이렉트
    else:
        return redirect(url_for('login')) # 로그인 안했으면 로그인 페이지 리다이렉트

@app.route('/edit_post/<int:post_id>', methods=['GET']) # /edit_post에 게시글 번호 접근 시
def edit_post(post_id): # 정수 형태의 post_id를 변수로 불러옴
    if 'id' in session:
        id = session['id']
        
        cursor.execute("SELECT * FROM posting WHERE id = %s", (post_id,)) # posting 테이블에 id 값이 변수로 불러온 post_id 인 값을 조회
        post = cursor.fetchone() # 행 1개만 post 변수에 저장
        
        if post: # post에 데이터가 저장되어 있으면 
            return render_template('edit_post.html', userid=id, post=post) #edit_post.html 리다이렉트 userid에는 세션 속 id 값, post에는 쿼리를 통해 반환된 post값을 포함하여 리다이렉트
        else:
            return "존재하지 않는 게시물입니다."
    else:
        return redirect(url_for('login'))

@app.route('/update_post/<int:post_id>', methods=['POST']) #update_post에 게시글 번호 접근 시
def update_post(post_id): # 정수 형태의 post_id를 변수로 불러옴
    if 'id' in session:
        id = session['id']
        title = request.form['title'] # form에서 title로 전달된 값을 title 변수에 저장
        content = request.form['content'] # form에서 content로 전달된 값을 content 변수에 저장
        
        cursor.execute("UPDATE posting SET title = %s, content = %s WHERE id = %s", (title, content, post_id)) # posting 테이블에 title, content값을 각각 입력받은 데이터대로 변경하는데 입력받은 post_id의 값이 일치하는 데이터에 대해서 수행한다.
        db.commit()
        
        return redirect(url_for('show_post', post_id=post_id))
    else:
        return redirect(url_for('login'))
        


@app.route('/search', methods=['GET']) /search에 접근 시 
def search():
    search = request.args.get('search', '') # URL의 search 파라미터를 통해 전달된 payload를 search에 저장
    search_option = request.args.get('search_option', 'all') # URL의 search_option 파라미터를 통해 전달된 payload를 search_option에 저장

    if search_option == 'title': # search_option이 title이면 (제목 기준 검색)
        cursor.execute("SELECT * FROM posting WHERE title LIKE %s", ('%' + search + '%',)) # posting 테이블의 title에 search 값을 검색
    elif search_option == 'content':
        cursor.execute("SELECT * FROM posting WHERE content LIKE %s", ('%' + search + '%',)) # posting 테이블의 content에 search 값을 검색
    else:  
        cursor.execute("SELECT * FROM posting WHERE title LIKE %s OR content LIKE %s", ('%' + search + '%', '%' + search + '%')) # posting 테이블의 title에 search 값이나 content에 search값이 있는 데이터를 검색

    posts = cursor.fetchall()  # DB 쿼리 결과 모두를 posts에 저장

    return render_template('index.html', posts=posts, search=search, search_option=search_option) # index.html에 posts, search, search_option 변수화 함께 리다이렉트
        

@app.route('/logout') #logout에 접근 시
def logout():
    session.pop('id', None) #flask 세션에서 id라는 키를 삭제
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True) # 디버그 모드를 활성화 (데이터 변경 시 즉시 변경사항 적용)
