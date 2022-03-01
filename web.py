from flask import Flask, render_template, request,redirect,url_for,make_response
from flask_mysqldb import MySQL
import pdfkit

app = Flask(__name__)
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']='masuk'
app.config['MYSQL_DB']='rebecca_kasir'
mysql = MySQL(app)

@app.route('/export')
def export():
    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    
    name = 'Laporan Penjualan'
    html = render_template(
        "index.html",
        name=name,configuration=config)
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = "inline; filename=output.pdf"
    return response

def cari(menu):
    text = "SELECT * from menu where menu=%s"
    cur = mysql.connection.cursor()
    cur.execute(text,(menu))
    res = cur.fetchall()
    cur.close()
    return res
@app.route("/")
def main():
    cur =  mysql.connection.cursor()
    cur.execute("SELECT sum(laba_bersih) FROM transaksi")
    value = cur.fetchall()
    
    cur.execute("SELECT count(menu) FROM menu")
    value2= cur.fetchall()
    cur.close()
    return render_template('index.html',value=value,value2=value2)
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
    cur.execute('SELECT * FROM menu order by no')
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
    cur.execute("DELETE FROM supplier where no=%s" ,(ids))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('mastersupplier'))

@app.route('/hapusbarang/<string:ids>',methods=["GET"])
def hapusbarang(ids):
    cur =  mysql.connection.cursor()
    cur.execute("DELETE FROM menu where no=%s" ,(ids))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('masterbarang'))

@app.route('/hapustransaksi/<string:ids>',methods=["GET"])
def hapustransaksi(ids):
    cur =  mysql.connection.cursor()
    cur.execute("DELETE FROM transaksi where no=%s" ,(ids))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('datapenjualan'))
#! menambahkan transaksi
@app.route('/add',methods=['POST'])
def add():
    menu = request.form.get('menu')
    qty = request.form['num']
    # hasil = cari(menu)
    cur =  mysql.connection.cursor()
    cur.execute("SELECT * FROM menu where id_menu='%s'" %menu)
    hasil = cur.fetchall()
    cur.close()

    untung = int(hasil[0][5])
    jumlah = int(qty)   
    laba = untung*jumlah

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO transaksi(id_menu,menu,qty,harga,hpp,laba_bersih) VALUES(%s,%s,%s,%s,%s,%s)",(hasil[0][1],hasil[0][2],qty,hasil[0][3],hasil[0][4],laba))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('formpenjualan'))

#! dashboard
    
if __name__ == "__main__":
    app.run(debug=True)