from flask import Flask, render_template, url_for, request, redirect, make_response, json
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from sqlalchemy import update
from sqlalchemy.orm import backref
from sqlalchemy import and_, or_
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
app = Flask(__name__)

app.secret_key = "lokukoju"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/podaci.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class Zahtevi(db.Model):

    __tablename__ = "zahtevi"

    id = db.Column(db.Integer, primary_key=True)
    br_zahteva = db.Column(db.String(100))
    datum = db.Column(db.String(100))
    kompanija = db.Column(db.String(100))
    ime_podnosioca = db.Column(db.String(100))
    zahtev = db.Column(db.String(200))
    napomena = db.Column(db.String(200), nullable=True)
    tip_zahteva = db.Column(db.String(200), nullable=True)
    ocekivani_datum = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(200), nullable=True)
    komentar = db.Column(db.String(200), nullable=True)
    br_sati = db.Column(db.Integer, nullable=True)
    
    def __init__(self, br_zahteva, datum, kompanija, ime_podnosioca, zahtev):

        self.br_zahteva = br_zahteva
        self.datum = datum
        self.kompanija = kompanija
        self.ime_podnosioca = ime_podnosioca
        self.zahtev = zahtev
       
class Tip_zahteva(db.Model):
    
    __tablename__ = "tip_zahteva"

    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(100))
    oznaka = db.Column(db.String(100))

class Status(db.Model):
    
    __tablename__ = "status"

    id = db.Column(db.Integer, primary_key=True)
    naziv_statusa = db.Column(db.String(100))


 
class Korisnici(UserMixin, db.Model):
    __tablename__ = "korisnici"
   
    id = db.Column(db.Integer, primary_key=True)
    ime = db.Column(db.String(100))
    prezime = db.Column(db.String(100))
    kompanija_naziv = db.Column(db.String(100),  nullable=True)
    rola = db.Column(db.String(100))
    email = db.Column(db.String(100))
    username = db.Column(db.String(100))
    password = db.Column(db.String(100))
    kompanija = db.relationship('Kompanije', backref=backref("korisnici", cascade="all,delete"), lazy=True, cascade='all, delete-orphan', passive_deletes=True)

    @login_manager.user_loader
    def logovanje(id):
        return Korisnici.query.get(int(id))

class Kompanije(db.Model):
    __tablename__= 'kompanije'
   
    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(100))
    adresa = db.Column(db.String(100))
    telefon = db.Column(db.Integer)
    korisnici_id = db.Column(db.Integer, db.ForeignKey('korisnici.id'), nullable=False)

def covek(captcha_response):
    payload = {'response': captcha_response, 'secret':'6LfZndcZAAAAAKej2C1cmKWiTuOiaY_2lIAwh6vd'}
    response = requests.post('https://www.google.com/recaptcha/api/siteverify', data = payload)
    response_text = json.loads(response.text)
    return response_text['success']


@app.route('/')     
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template('login.html', pub_key='6LfZndcZAAAAAB7Mm7B0e9wqWa95YNpE-8tPs__s')
    elif request.method == "POST":
        username = request.form['username']
        password = request.form['password'] 
        captcha_response = request.form['g-recaptcha-response']
        korisnik = Korisnici.query.filter(Korisnici.username.contains(username)).first()
        if korisnik and covek(captcha_response):    
            if check_password_hash(korisnik.password, password):
                login_user(korisnik)
                return redirect(url_for('a_zahtev'))
            else:
                return redirect(url_for('login'))
        else:
                return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))




#############################################################################################zahtevi###
@app.route('/zahtevi')
@login_required
def a_zahtev():
    statusi = Status.query.all()
    tipovi_zahteva = Tip_zahteva.query.all()
    
    podnosilac = request.args.get('podnosilac')
    datum = request.args.get('datum')
    status = request.args.get('status')
    tip = request.args.get('tip')

    if  podnosilac or datum or status or tip:
        podnosilac = "%{}%".format(podnosilac)
        datum = "%{}%".format(datum)
        status = "%{}%".format(status)
        tip = "%{}%".format(tip)
        zahtevi = Zahtevi.query.filter(and_(Zahtevi.ime_podnosioca.like(podnosilac), Zahtevi.datum.like(datum), Zahtevi.status.like(status), Zahtevi.tip_zahteva.like(tip)))
   
    else:    
        zahtevi = Zahtevi.query.all()

    return render_template('administrator/zahtevi.html', zahtevi = zahtevi, tipovi_zahteva = tipovi_zahteva, statusi = statusi, )
   

@app.route('/novi_zahtevi', methods=['GET', 'POST'])
@login_required
def a_zahtev_novi():
    if request.method == "GET":
        datum = date.today()
        tipovi = Tip_zahteva.query.all()
        statusi = Status.query.all()
        korisnici = Korisnici.query.all()
        kompanije = Kompanije.query.all()
        return render_template('administrator/novi_zahtev.html', tipovi = tipovi, statusi = statusi, korisnici = korisnici, kompanije = kompanije, datum = datum)
    elif request.method == "POST":
        zahtev = Zahtevi(br_zahteva =request.form['br_zahteva'], datum=request.form['datum'], kompanija=request.form['kompanija'], ime_podnosioca=request.form['ime_podnosioca'], zahtev=request.form['zahtev'])
        db.session.add(zahtev)
        db.session.commit()
        return redirect(url_for('a_zahtev'))
   
    

@app.route('/izmena_zahteva/<int:id>', methods=['GET', 'POST'])
@login_required
def a_zahtev_izmena_zahteva(id):
    if request.method == "GET":
        zahtev = Zahtevi.query.get(id)   
        korisnici = Korisnici.query.all()
        kompanije = Kompanije.query.all()
        return render_template('administrator/izmena_zahteva.html',zahtev = zahtev, korisnici = korisnici, kompanije = kompanije)
    elif request.method == "POST":
        zahtev = Zahtevi.query.filter(Zahtevi.id == id)
        zahtev.update({'br_zahteva' : request.form['br_zahteva'], 'datum': request.form['datum'], 'kompanija': request.form['kompanija'], 'ime_podnosioca': request.form['ime_podnosioca'], 'zahtev': request.form['zahtev']})     
        db.session.commit()
        return redirect(url_for('a_zahtev'))
    
@app.route('/prikaz_zahteva/<int:id>', methods = ['GET', 'POST'])
@login_required
def a_zahtev_prikaz(id):
    if request.method == "GET":
        zahtev = Zahtevi.query.get(id)  
        tipovi = Tip_zahteva.query.all()
        statusi = Status.query.all()
        return render_template('administrator/prikaz_zahteva.html', zahtev = zahtev,tipovi = tipovi, statusi = statusi)
    elif request.method == "POST":
        zahtev = Zahtevi.query.filter(Zahtevi.id == id)
        zahtev.update({'napomena' : request.form['napomena'], 'tip_zahteva' : request.form['tip_zahteva'], 
            'ocekivani_datum': request.form['ocekivani_datum'], 'status': request.form['status'], 'komentar': request.form['komentar'], 
            'br_sati': request.form['br_sati']})     
        db.session.commit()
        return redirect(url_for('a_zahtev'))
        

@app.route('/brisanje_zahteva/<int:id>')
@login_required
def a_zahtev_brisanje(id):
        zahtev = Zahtevi.query.get(id)
        db.session.delete(zahtev)
        db.session.commit()
        return redirect(url_for('a_zahtev'))
#############################################################################################kompanije###

@app.route('/kompanije_izmena/<int:id>/<int:korisnik>', methods=['GET', 'POST'])
@login_required
def a_kompanija_izmena(id,korisnik):
    if request.method == "GET":
        kompanija = Kompanije.query.get(id)
      
        return render_template('administrator/izmena_kompanija.html', kompanija = kompanija)
    elif request.method == "POST":
        kompanija = Kompanije.query.filter(Kompanije.id == id)
        kompanija.update({'naziv' :request.form['naziv'], 'adresa' :request.form['adresa'], 'telefon' :request.form['telefon']})
        korisnik = Korisnici.query.filter(Korisnici.id == korisnik)
        korisnik.update({'ime':request.form['ime'], 'prezime':request.form['prezime'],'email' :request.form['email'], 'username' :request.form['username'], 'password' :request.form['password']})    
        db.session.commit()
        return redirect(url_for('a_kompanija'))
@app.route('/kompanije')
@login_required
def a_kompanija():
    kompanije = Kompanije.query.join(Korisnici).all()
    admin = request.args.get('admin')
    naziv = request.args.get('kompanija')
    if admin or naziv:
        kompanija = "%{}%".format(naziv)
        korisnik = "%{}%".format(admin)
        kompanije = Kompanije.query.join(Korisnici).filter(or_(Kompanije.korisnici_id == Korisnici.ime.like(korisnik), Kompanije.naziv.like(kompanija)))
   
    else:
        kompanije = Kompanije.query.join(Korisnici).all()

    return render_template('administrator/kompanije.html', kompanije = kompanije)
    
@app.route('/nova_kompanija', methods =['GET', 'POST'])

def a_kompanija_nova():
    if request.method == "GET":
        return render_template('administrator/nova_kompanija.html')
    elif request.method == "POST":
        password = generate_password_hash(request.form['password'], method='sha256')
        korisnik = Korisnici(ime =request.form['ime'], prezime =request.form['prezime'], kompanija_naziv = "-Admin", rola  = "admin", email =request.form['email'], username =request.form['username'], password = password)
        kompanija = Kompanije(naziv =request.form['naziv'], adresa =request.form['adresa'], telefon =request.form['telefon'], korisnici = korisnik)
        db.session.add(korisnik)
        db.session.add(kompanija)
        db.session.commit()
        return redirect(url_for('a_kompanija'))

@app.route('/brisanje_kompanije/<int:id>/<naziv>')
@login_required
def a_kompanija_brisanje(id,naziv):
        kompanija = Kompanije.query.get(id)
        korisnici = Korisnici.query.filter(Korisnici.kompanija_naziv == naziv).all()
        db.session.delete(kompanija)
        for korisnik in korisnici:
            db.session.delete(korisnik)  
        zahtevi = Zahtevi.query.filter(Zahtevi.kompanija == naziv).all()
        for zahtev in zahtevi:
            db.session.delete(zahtev) 
        db.session.commit()
        return redirect(url_for('a_kompanija')) 

##############################################################################################tip####
@app.route('/tip_zahteva')
@login_required
def a_tip():
    tipovi_zahteva = Tip_zahteva.query.all()
    return render_template('administrator/tip_zahteva.html',tipovi_zahteva = tipovi_zahteva)

@app.route('/tip_zahteva_izmena/<int:id>', methods=['GET', 'POST'])
@login_required
def a_tip_izmena(id):
    if request.method == "GET":
        tip_zahteva = Tip_zahteva.query.get(id)   
        return render_template('administrator/izmena_tipa_zahteva.html',tip_zahteva = tip_zahteva)
    elif request.method == "POST":
        tip_zahteva = Tip_zahteva.query.filter(Tip_zahteva.id == id)
        tip_zahteva.update({'naziv' : request.form['naziv'], 'oznaka' : request.form['oznaka']})     
        db.session.commit()
        return redirect(url_for('a_tip'))
    

@app.route('/tip_zahteva_novi', methods = ['GET', 'POST'])
@login_required
def a_tip_novi():
    if request.method == "GET":
       return render_template('administrator/novi_tip_zahteva.html')
    elif request.method == "POST":
        zahtev = Tip_zahteva(naziv =request.form['naziv'], oznaka =request.form['oznaka'])
        db.session.add(zahtev)
        db.session.commit()
        return redirect(url_for('a_tip'))

@app.route('/brisanje_tipa_zahteva/<int:id>')
@login_required
def a_tip_brisanje(id):
        tip_zahteva = Tip_zahteva.query.get(id)
        db.session.delete(tip_zahteva)
        db.session.commit()
        return redirect(url_for('a_tip')) 
   
   ##############################################################################################korisnici####

@app.route('/korisnici')
@login_required
def a_korisnik():
    kompanije = Kompanije.query.all()
    kompanija = request.args.get('kompanija')
    ime = request.args.get('ime')
    if kompanija or ime:
        kompanija = "%{}%".format(kompanija)
        korisnik = "%{}%".format(ime)
        korisnici = Korisnici.query.filter(and_(Korisnici.ime.like(korisnik), Korisnici.kompanija_naziv.like(kompanija)))
    else:    
        korisnici = Korisnici.query.all()    
    return render_template('administrator/korisnici.html', korisnici = korisnici, kompanije = kompanije)

@app.route('/korisnik_novi', methods = ['GET', 'POST'])
@login_required
def a_korisnik_novi():
    if request.method == "GET":
        kompanije = Kompanije.query.all()
        return render_template('administrator/novi_korisnik.html', kompanije = kompanije)
    elif request.method == "POST":
        password = generate_password_hash(request.form['password'], method='sha256')
        
        korisnik = Korisnici(ime =request.form['ime'], prezime =request.form['prezime'], kompanija_naziv=request.form['kompanija'],  email =request.form['email'], username =request.form['username'], password = password)
      
        db.session.add(korisnik)
       
        db.session.commit()
        return redirect(url_for('a_korisnik'))

@app.route('/korisnik_izmena/<int:id>', methods = ['GET', 'POST'])
@login_required
def a_korisnik_izmena(id):
    if request.method == "GET":
        korisnik = Korisnici.query.get(id)
        return render_template('administrator/izmena_korisnika.html', korisnik = korisnik)
    elif request.method == "POST":
        korisnik = Korisnici.query.filter(Korisnici.id == id)
        korisnik.update({'ime':request.form['ime'], 'prezime':request.form['prezime'],  
        'email' :request.form['email'], 'username' :request.form['username'], 'password' :request.form['password']})
        db.session.commit()
        return redirect(url_for('a_korisnik'))

@app.route('/korisnik_brisanje/<int:id>')
@login_required
def a_korisnik_brisanje(id):
        korisnik = Korisnici.query.get(id)
        db.session.delete(korisnik)
        db.session.commit()
        return redirect(url_for('a_korisnik')) 


if __name__ == '__main__':
    app.run(debug=True)
