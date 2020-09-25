from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)
app.secret_key = "lokukoju"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/podaci.db'
db = SQLAlchemy(app)


class Zahtevi(db.Model):

    __tablename__ = "zahtevi"

    id = db.Column(db.Integer, primary_key=True)
    br_zahteva = db.Column(db.Integer)
    datum = db.Column(db.String(100))
    kreator = db.Column(db.String(100))
    kompanija = db.Column(db.String(100))
    ime_podnosioca = db.Column(db.String(100))
    zahtev = db.Column(db.String(200))
    napomena = db.Column(db.String(200), nullable=True)
    tip_zahteva = db.Column(db.String(200), nullable=True)
    ocekivani_datum = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(200), nullable=True)
    komentar = db.Column(db.String(200), nullable=True)
    br_sati = db.Column(db.Integer, nullable=True)
    
    def __init__(self, br_zahteva, datum, kreator, kompanija, ime_podnosioca, zahtev):

        self.br_zahteva = br_zahteva
        self.datum = datum
        self.kreator = kreator
        self.kompanija = kompanija
        self.ime_podnosioca = ime_podnosioca
        self.zahtev = zahtev
       

###############Zaposlen klienta ############################

@app.route('/zaposlen_klenta_zahtevi')
def zk_zahtev():
    zahtevi = Zahtevi.query.all()
    return render_template('zaposlenklienta/zahtevi.html', zahtevi = zahtevi)

@app.route('/zaposlen_klenta_novi_zahtevi', methods = ['GET', 'POST'])
def zk_zahtev_novi():
    if request.method == "GET":
        return render_template('zaposlenklienta/novi_zahtev.html')
    elif request.method == "POST":
        zahtev = Zahtevi(br_zahteva =request.form['br_zahteva'], kreator =request.form['kreator'], datum=request.form['datum'], kompanija=request.form['br_zahteva'], ime_podnosioca=request.form['ime_podnosioca'], zahtev=request.form['zahtev'])
        db.session.add(zahtev)
        db.session.commit()
        return redirect(url_for('zk_zahtev'))

@app.route('/zaposlen_klenta_pregled_zahteva')
def zk_zahtev_pogled():
    return render_template('zaposlenklienta/pregled_zahteva.html')

@app.route('/zaposlen_klienta_izmena')
def zk_podataka_izmena():
    return render_template('zaposlenklienta/izmena_podataka.html')

@app.route('/zaposlen_klenta_izmena_zahteva')
def zk_zahtev_izmena_zahteva():
    return render_template('zaposlenklienta/izmena_zahteva.html')

###############Administrator klienta ############################

@app.route('/administrator_klenta_zahtevi')
def ak_zahtev():
    return render_template('administratorklienta/zahtevi.html')

@app.route('/administrator_klenta_novi_zahtevi')
def ak_zahtev_novi():
    return render_template('administratorklienta/novi_zahtev.html')

@app.route('/administrator_klenta_pregled_zahteva')
def ak_zahtev_pogled():
    return render_template('administratorklienta/pregled_zahteva.html')

@app.route('/administrator_klenta_izmena_zahteva')
def ak_zahtev_izmena_zahteva():
    return render_template('administratorklienta/izmena_zahteva.html')
#####korisnik####
@app.route('/administrator_klienta_korisnici')
def ak_korisnik():
    return render_template('administratorklienta/korisnici.html')

@app.route('/administrator_klienta_novi_korisnik')
def ak_korisnik_novi():
    return render_template('administratorklienta/novi_korisnik.html')

@app.route('/administrator_klienta_izmena_korisnik')
def ak_korisnik_izmena():
    return render_template('administratorklienta/izmena_korisnika.html')

##############zaposlen kompanije ##############

@app.route('/zaposlen_kompanije_zahtevi')
def zko_zahtev():
    return render_template('zaposlenkompanije/zahtevi.html')

@app.route('/zaposlen_kompanije_novi_zahtevi')
def zko_zahtev_novi():
    return render_template('zaposlenkompanije/novi_zahtev.html')
    
@app.route('/zaposlen_kompanije_izmena')
def zko_podataka_izmena():
    return render_template('zaposlenkompanije/izmena_podataka.html')

@app.route('/zaposlen_klenta_izmena_zahteva')
def zko_zahtev_izmena_zahteva():
    return render_template('zaposlenklienta/izmena_zahteva.html')

@app.route('/zaposlen_kompanije_odgovor_zahteva')
def zko_zahtev_pogled():
    return render_template('zaposlenkompanije/odgovor_zahteva.html')

#############Administrator########################3
###zahtevi###
@app.route('/administrator_zahtevi')
def a_zahtev():
    return render_template('administrator/zahtevi.html')

@app.route('/administrator_novi_zahtevi')
def a_zahtev_novi():
    return render_template('administrator/novi_zahtev.html')

@app.route('/administrator_izmena_zahteva')
def a_zahtev_izmena_zahteva():
    return render_template('administrator/izmena_zahteva.html')

####kompanije###
@app.route('/administrator_kompanije_izmena')
def a_kompanija_izmena():
    return render_template('administrator/izmena_kompanija.html')

@app.route('/administrator_kompanije')
def a_kompanija():
    return render_template('administrator/kompanije.html')
    
@app.route('/administrator_nova_kompanija')
def a_kompanija_nova():
    return render_template('administrator/nova_kompanija.html')
####tip####
@app.route('/administrator_tip_zahteva')
def a_tip():
    return render_template('administrator/tip_zahteva.html')

@app.route('/administrator_tip_zahteva_izmena')
def a_tip_izmena():
    return render_template('administrator/izmena_tipa_zahteva.html')

@app.route('/administrator_tip_zahteva_novi')
def a_tip_novi():
    return render_template('administrator/novi_tip_zahteva.html')

#####korisnici####

@app.route('/administrator_korisnik')
def a_korisnik():
    return render_template('administrator/korisnici.html')

@app.route('/administrator_korisnik_novi')
def a_korisnik_novi():
    return render_template('administrator/novi_korisnik.html')

@app.route('/administrator_korisnik_izmena')
def a_korisnik_izmena():
    return render_template('administrator/izmena_korisnika.html')








if __name__ == '__main__':
    app.run(debug=True)
