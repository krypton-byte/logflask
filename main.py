#!/usr/bin/python
import os,sqlite3,secrets
from flask import *
MyApp = Flask(__name__)
MyApp.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
@MyApp.route('/set')
def set():
	return render_template('set.html')
@MyApp.route('/bot')
def bot():
    return render_template('bot.html')

@MyApp.route('/profile')
def profile():
    return render_template('profile.html')

@MyApp.route('/script')
def script():
    return render_template('script.html')

@MyApp.route('/')
def red():
	return redirect(url_for('index'))

@MyApp.route('/delete')
def delete():
	if 'email' in session and 'password' in session:
		c  = sqlite3.connect('users.db')
		db = c.cursor()
		email    = session['email']
		password = session['password']
		if db.execute(f"SELECT * FROM USERS WHERE EMAIL='{email}' AND PASSWORD='{password}'").fetchmany():
			token = db.execute(f"SELECT * FROM USERS WHERE EMAIL='{email}' AND PASSWORD='{password}' ").fetchall()[0][3]
			os.remove(f'{token}.db')
			db.execute(f"DELETE FROM USERS WHERE EMAIL='{email}' AND PASSWORD='{password}' ")
			session.pop('email',None)
			session.pop('password',None)
			c.commit()
			c.close()
			print('akun terhapus')
			return redirect(url_for('index'))
		else:
			print('password di dalam sesi tidak sesuai')
			return redirect(url_for('index'))
	else:
		print('sesi tidak ada')
		return redirect(url_for('index'))
@MyApp.route('/logout')
def logout():
	session.pop('email',None)
	session.pop('password',None)
	return redirect(url_for('index'))
@MyApp.route('/daftar',methods=['POST','GET'])
def daftar():
	if request.method == 'POST':
		token = secrets.token_urlsafe(32)
		nama    = request.form.get('nama')
		profesi = request.form.get('profesi')
		bio     = request.form.get('bio')
		email   = request.form.get('email')
		hape    = request.form.get('hape')
		password= request.form.get('password')
		gender  = request.form.get('gender')
		c  = sqlite3.connect('users.db')
		db = c.cursor()
		db.execute(f"INSERT INTO USERS VALUES ('{nama}','{email}','{password}','{token}')")
		c.commit()
		c.close()
		c  = sqlite3.connect(f'{token}.db')
		db = c.execute("CREATE TABLE PROFILE ('nama','email','password','profesi','bio','hape','gender')")
		db = c.execute(f"INSERT INTO PROFILE VALUES ('{nama}','{email}','{password}','{profesi}','{bio}','{hape}','{gender}')")
		db.execute(f"CREATE TABLE SCRIPTS ('id','token','script')")
		c.commit()
		c.close()
		session['email'] = email
		session['password'] = password
		return redirect(url_for('index'))
	else:
		return render_template('daftar.html')


@MyApp.route('/dashboard')
def das():
	if 'email' in session and 'password' in session:
		email = session['email']
		password = session['password']
		c  = sqlite3.connect('users.db')
		db = c.cursor()
		if db.execute(f"SELECT * FROM USERS WHERE EMAIL='{email}' AND PASSWORD='{password}'").fetchmany():
			data = db.execute(f"SELECT * FROM USERS WHERE EMAIL='{email}' AND PASSWORD='{password}'").fetchmany()[0]
			token = data[3]
			c.commit()
			c.close()
			c = sqlite3.connect(f'{token}.db')
			del db
			db = c.cursor()
			print(token)
			dat = db.execute(f"SELECT * FROM PROFILE").fetchmany()[0]
			c.commit()
			c.close()
			nama = dat[0]
			email = dat[1]
			password = dat[2]
			profesi = dat[3]
			bio = dat[4]
			hape = dat[5]
			gender = dat[6]
			return render_template('dashboard.html',nama=nama,email=email,hape=hape,profesi=profesi,bio=bio,gender=gender)
		else:
			session.pop('email',None)
			session.pop('password',None)
			return redirect(url_for('index'))
	else:
		return redirect(url_for('index'))


@MyApp.route('/login',methods=['GET','POST'])
def index():
	if 'email' in session and 'password' in session:
		return redirect(url_for('das'))
	elif request.method == 'POST':
		email = request.form.get('email')
		password = request.form.get('password')
		if (True in [(i in ['=','\'','"','`'])for i in list(email)]) or (True in [(i in ['=','\'','"','`'])for i in list(password)]):
			return render_template('index.html')
		else:
			c  = sqlite3.connect('users.db')
			db = c.cursor()
			print('login\nemail : %s password : %s'%(email,password))
			if db.execute(f"SELECT * FROM USERS WHERE EMAIL='{email}' AND PASSWORD='{password}'").fetchmany():
				data=db.execute(f"SELECT * FROM USERS WHERE EMAIL='{email}' AND PASSWORD='{password}'").fetchmany()[0]
				session['email'] = data[1]
				session['password'] = data[2]
				print('nama : %s\npass : %s'%(data[1],data[2]))
				return redirect(url_for('das'))
			else:
				print('gagal')
				return render_template('index.html')
	else:
		return render_template('index.html')


@MyApp.errorhandler(404)
def error(e):
	return render_template('error.html'),404
if __name__ == '__main__':
	MyApp.run(host='0.0.0.0',port=int(os.environ.get('PORT','5000')),debug=True)
