from flask import Flask, render_template, request,redirect,url_for,make_response,session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
# import pdfkit

app = Flask(__name__)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='masuk'
app.config['MYSQL_DB']='rebecca_kasir'
app.secret_key = 'masuk'
mysql = MySQL(app)

# @app.route('/export')
# def export():
#     config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    
#     name = 'Laporan Penjualan'
#     html = render_template(
#         "index.html",
#         name=name,configuration=config)
#     pdf = pdfkit.from_string(html, False)
#     response = make_response(pdf)
#     response.headers["Content-Type"] = "application/pdf"
#     response.headers["Content-Disposition"] = "inline; filename=output.pdf"
#     return response
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            # session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            return main()
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
#    session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

                # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users VALUES ( %s, %s, %s)', (username, password, email))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)

def cari(menu):
    text = "SELECT * from menu where menu=%s"
    cur = mysql.connection.cursor()
    cur.execute(text,(menu))
    res = cur.fetchall()
    cur.close()
    return res
@app.route("/")
def main():
    if 'loggedin' in session:
        cur =  mysql.connection.cursor()
        cur.execute("SELECT sum(laba_bersih) FROM transaksi")
        value = cur.fetchall()
        
        cur.execute("SELECT count(menu) FROM menu")
        value2= cur.fetchall()
        cur.close()
        return render_template('index.html',value=value,value2=value2,username=session['username'])
        # User is loggedin show them the home page
        # return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return render_template('login.html')

    
#?=============================================================BARANG================================================================
@app.route("/masterbarang")
def masterbarang():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM menu")
    menu = cur.fetchall()
    cur.close()
    return render_template('masterbarang.html',menu='master',submenu='barang',data=menu)

@app.route("/formmasterbarang")
def formmasterbarang():
    return render_template('formmasterbarang.html',menu='master',submenu='barang')

#!untuk menyimpan hasil form ke DB
@app.route("/simpanformmasterbarang",methods=['POST'])
def simpanformmasterbarang():
    id_menu = request.form['id_menu']
    menu = request.form['menu']
    harga = request.form['harga']
    hpp = request.form['hpp']
    laba = request.form['laba']
    
    #!insert ke databasenya 
    #!cur.execute("INSERT INTO menu(nama_atribut_berdasarkan_database) VALUES(%s,%s,%s,%s,%s)",(variable_yang_digunakan_pada_fungsi_ini))
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO menu(id_menu,menu,harga,hpp,laba_bersih) VALUES(%s,%s,%s,%s,%s)",(id_menu,menu,harga,hpp,laba))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('masterbarang'))
#?==============================================================SUPPLIER=======================================================
@app.route("/mastersupplier")
def mastersupplier():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM supplier")
    supplier = cur.fetchall()
    cur.close()
    return render_template('mastersupplier.html',menu='master',submenu='supplier',data=supplier)

@app.route("/formmastersupplier")
def formmastersupplier():
    return render_template('formmastersupplier.html',menu='master',submenu='supplier')

#!untuk menyimpan hasil form ke DB
@app.route("/simpanformmastersupplier",methods=['POST'])
def simpanformmastersupplier():
    barang = request.form['barang']
    satuan = request.form['satuan']
    qty = request.form['qty']
    total = request.form['total']
    
    #!insert ke databasenya 
    #!cur.execute("INSERT INTO menu(nama_atribut_berdasarkan_database) VALUES(%s,%s,%s,%s,%s)",(variable_yang_digunakan_pada_fungsi_ini))
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO supplier(barang,harga_satuan,qty,total) VALUES(%s,%s,%s,%s)",(barang,satuan,qty,total))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('mastersupplier'))
#?===========================================================PELANGGAN===============================================================
@app.route("/masterpelanggan")
def masterpelanggan():
    return render_template('masterpelanggan.html',menu='master',submenu='pelanggan')

@app.route("/formpembelian")
def formpembelian():
    return render_template('formpembelian.html',menu='pembelian',submenu='formpembelian')
@app.route("/datapembelian")
def datapembelian():
    return render_template('datapembelian.html',menu='pembelian',submenu='datapembelian')

@app.route("/formpenjualan")
def formpenjualan():
    cur =  mysql.connection.cursor()
    cur.execute('SELECT * FROM menu')
    list_menu = cur.fetchall()
    cur.close()
    return render_template('formpenjualan.html',menu='penjualan',submenu='formpenjualan',list_menu=list_menu)
@app.route("/datapenjualan")
def datapenjualan():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM transaksi")
    transaction = cur.fetchall()
    cur.close()
    return render_template('datapenjualan.html',menu='penjualan',submenu='datapenjualan',data = transaction)

#!hapus row in database
@app.route('/hapussupplier/<string:ids>',methods=["GET"])
def hapussupplier(ids):
    cur =  mysql.connection.cursor()
    cur.execute("DELETE FROM supplier where barang=%s" ,(ids,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('mastersupplier'))

@app.route('/hapusbarang/<string:ids>',methods=["GET"])
def hapusbarang(ids):
    cur =  mysql.connection.cursor()
    cur.execute("DELETE FROM menu where id_menu=%s" ,(ids,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('masterbarang'))

@app.route('/hapustransaksi/<string:ids>',methods=["GET"])
def hapustransaksi(ids):
    cur =  mysql.connection.cursor()
    cur.execute("DELETE FROM transaksi where no = (%s)" ,(ids,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('datapenjualan'))
#! menambahkan transaksi
@app.route('/add',methods=['POST'])
def add():
    menu = request.form.get('menu')
    qty = request.form['num']
    print(menu)
    # hasil = cari(menu)
    cur =  mysql.connection.cursor()
    cur.execute("SELECT * FROM menu where menu=%s", (menu,))
    hasil = cur.fetchall()
    
    cur.close()
    print(hasil)
    untung = int(hasil[0][4])
    jumlah = int(qty)   
    laba = untung*jumlah
    
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO transaksi(id_menu,menu,qty,harga,hpp,laba_bersih) VALUES(%s,%s,%s,%s,%s,%s)",(hasil[0][0],hasil[0][1],qty,hasil[0][3],hasil[0][4],laba))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('datapenjualan'))

#! dashboard
    
if __name__ == "__main__":
    app.run(debug=True)