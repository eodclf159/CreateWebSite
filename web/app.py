# Flask 웹 프레임 워크를 통한 웹 서버 생성 및 Pymysql을 통한 Database 연결
import os
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import pymysql
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'this+is+woncheol+secretkey' # 세션 암호화를 통한 비밀키

db = pymysql.connect(host='localhost', port=3306, user='root', passwd='woncheol2ek!!', db='web', charset='utf8') # 로컬 구성 DB 연결
cursor = db.cursor() # 데이터베이크 쿼리 실행 준비

#파일 업로드 구조 드가자
UPLOAD_FOLDER = 'files' # 파일 첨부 시 저장할 디렉터리 설정
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#확장자 검증 보안에 중요함 이건 뽀너스 ㅋㅋ
ALLOWED_EXTENSIONS = {'txt', 'png', 'jpg', 'jpeg'}

@app.route('/files/<filename>') # 파일 다운로드 경로 접근 시
def download_file(filename):
    print(filename.split('\\')[-1]) # 디버깅 코드로 파일을 제대로 불러오는지 확인
    real_filename = filename.split('\\')[-1] # 파일 경로에서 폴더를 제외하고 파일이 저장된 이름과 확장자만 가져옴
    
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], real_filename) #os.path.join을 통해 업로드 된 폴더의 경로와 파일 이름을 더해 최종으로 파일 경로를 생성
    if os.path.isfile(file_path):
        print(f"다운중 {real_filename}")
        return send_from_directory(app.config['UPLOAD_FOLDER'], real_filename, as_attachment=True) #파일이 존재하면 send_from_directory를 통해 파일 다운로드 실행, as_attachment=True는 파일을 브라우저에서 안열고 바로 다운로드 하도록 한다.
    else:
        print(f"파일이 존재하지 않음: {file_path}")
        return "파일을 찾을 수 없습니다.", 404

    return send_from_directory('files', filename)


#확장자 검증 보안에 중요함 이건 뽀너스 ㅋㅋ
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/view_profile/<username>')
def view_profile(username):
    cursor.execute("SELECT id, name, school, gender, profile_img_path FROM user WHERE id = %s", (username,))
    user_info = cursor.fetchone()
    if user_info:
        id, name, school, gender, profile_img_path = user_info
        if not profile_img_path:  # 프로필 이미지 없으면 기본 이미지 경로 설정
                profile_img_path = 'defaultprofile.png'
        return render_template('view_profile.html', userid=id, name=name, school=school, gender=gender, profile_img_path=profile_img_path)
    else:
        return "사용자 계정을 찾을 수 없습니다.", 404

@app.route('/profile')
def profile():
    if 'id' in session:
        id = session['id']
        
        cursor.execute("SELECT name, school, gender, profile_img_path FROM user WHERE id = %s", (id,))
        user_info = cursor.fetchone()
        print(user_info)
        if user_info:
            name, school, gender, profile_img_path = user_info
            if not profile_img_path:  # 프로필 이미지 없으면 기본 이미지 경로 설정
                profile_img_path = 'defaultprofile.png'
            return render_template('show_profile.html', userid=id, name=name, school=school, gender=gender, profile_img_path=profile_img_path)
        else:
            return "사용자 정보를 찾을 수 없습니다.", 404
    return redirect(url_for('login'))

@app.route('/edit_profile', methods=['GET', 'POST']) # edit_profile에 접근 시
def edit_profile():
    if 'id' in session:
        id = session['id']
        
        if request.method == 'POST': #POST 요청을 받으면 form 태그에서 받은 값을 각각 변수에 저장
            name = request.form['name']
            school = request.form['school']
            gender = request.form['gender']
            
            file = request.files.get('profile_img') #사용자가 파일을 업로드 한것도 변수에 저장
            if file and allowed_file(file.filename): #확장자가 허용된 파일 형식이면
                filename = secure_filename(file.filename) #파일의 이름을 안전하게 처리하고
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) # 파일 업로드 폴더에 저장함
                file.save(file_path)
            else:
                filename = None

            cursor.execute("UPDATE user SET name = %s, school = %s, gender = %s, profile_img_path = %s WHERE id = %s", (name, school, gender, filename, id)) # 사용자가 수정한 정보를 데이터 베이스에 업데이트함.
            db.commit()

            return redirect(url_for('profile')) # 수정 완료 후 다시 profile 페이지로 리다이렉트 함
        
        cursor.execute("SELECT name, school, gender, profile_img_path FROM user WHERE id = %s", (id,))
        user_info = cursor.fetchone()
        
        if user_info:
            name, school, gender, profile_img_path = user_info
            if not profile_img_path:  # 프로필 이미지 없으면 기본 이미지 경로 설정
                profile_img_path = 'defaultprofile.png'
            return render_template('edit_profile.html', userid=id, name=name, school=school, gender=gender, profile_img_path=profile_img_path)
        else:
            return "사용자 정보를 찾을 수 없습니다.", 404
    
    return redirect(url_for('login'))


@app.route('/')
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
        name = request.form['name']
        school = request.form['school']
        gender = request.form['gender']
        
        profile_img = request.files.get('profile_img')
        
        if profile_img and allowed_file(profile_img.filename):
            filename = secure_filename(profile_img.filename)
            profile_img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            profile_img.save(profile_img_path)
        else:
            profile_img_path = None
            
                
        cursor.execute("INSERT INTO user (id, pw, name, school, gender, profile_img_path) VALUES (%s, %s, %s, %s, %s, %s)", (id, pw, name, school, gender, profile_img_path)) # user 테이블에 각각 업데이트
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

@app.route('/write_post', methods=['GET']) # 게시글 작성 접근 시
def write_post():
    if 'id' in session: # 로그인 한 사람이라면
        id = session['id']
        return render_template('write_post.html', userid=id) # write_post.html 반환 및 userid에 id 전달
    return redirect(url_for('login')) # 로그인 안하면 로그인 페이지 리다이렉트

@app.route('/upload_post', methods=['POST']) # 게시글 업로드 시 (write_post.html에서 호출)
def upload_post():
    if 'id' in session:
        title = request.form['title'] # form 에서 전달 받은 값을 각각 변수에 저장
        content = request.form['content'] # form 에서 전달 받은 값을 각각 변수에 저장 
        post_password = request.form['post_password'] # form 에서 전달 받은 값을 각각 변수에 저장
        is_secret = 1 if 'is_secret' in request.form else 0 # form 에서 전달 받은 값을 각각 변수에 저장
        author = session['id']
        
        file = request.files['file']
        
        
        if file and allowed_file(file.filename): # 파일 형식 체크
            filename = secure_filename(file.filename) # 파일 이름 처리
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) # 파일 경로 생성
            file.save(file_path) # 파일 저장
            print(file_path)
        else:
            file_path = None

        cursor.execute("INSERT INTO posting (author, title, content, post_password, file_path, is_secret) VALUES (%s, %s, %s, %s, %s, %s)", 
                       (author, title, content, post_password, file_path, is_secret)) # DB에 저장
        db.commit()
        
        return redirect(url_for('index'))
    else:
        return redirect(url_for('login'))

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    if 'id' in session:
        id = session['id']
        
        cursor.execute("SELECT * FROM posting WHERE id = %s", (post_id,)) # posting 테이블에 id 값이 변수로 불러온 post_id 인 값을 조회
        post = cursor.fetchone() # 행 1개만 post 변수에 저장
        
        if post: # post에 데이터 저장 시
            if post[6]:  #비밀번호 설정 시 
                if request.method == 'POST':
                    entered_password = request.form['post_password'] # 입력받은 비밀번호 변수에 저장
                    if entered_password == post[3]:  #비밀번호 일치여부 확인
                        return render_template('show_post.html', userid=id, post=post) # 비밀번호 일치 시 게시글 내용 보여줌
                    else:
                        return "비밀번호가 틀렸습니다.", 403

                return render_template('enter_password.html', userid=id, post_id=post_id)
            else:
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
        title = request.form['title'] # form에서 받은 데이터를 각각 변수에 저장
        content = request.form['content']
        post_password = request.form['post_password']
        is_secret = 1 if 'is_secret' in request.form else 0
        
        file = request.files['file']
        
        
        if file and allowed_file(file.filename): # 파일 확장자 체크
            filename = secure_filename(file.filename) # 파일 이름 저장
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename) # 파일 경로 저장
            file.save(file_path) # 파일 저장 
            cursor.execute("UPDATE posting SET title = %s, content = %s, post_password = %s, file_path = %s, is_secret = %s WHERE id = %s", 
                           (title, content, post_password, file_path, is_secret, post_id))#DB에 변경사항 저장(파일 있을 경우)
        else:
            cursor.execute("UPDATE posting SET title = %s, content = %s, post_password = %s, is_secret = %s WHERE id = %s", #DB에 변경사항 저장( 파일 없을 경우)
                           (title, content, post_password, is_secret, post_id))
        
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

    return render_template('index.html', userid=id, posts=posts, search=search, search_option=search_option)
        

@app.route('/logout')
def logout():
    session.pop('id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True) # 디버그 모드 활성화 개발 용이성
