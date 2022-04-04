import codeop
import codecs
from datetime import datetime
from flask import Flask, render_template, send_from_directory, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///main.db'
app.config['UPLOAD_FOLDER'] = 'upload'
db = SQLAlchemy(app)

class Tickets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    
    def __repr__(self):
        return '<Ticket %r>' % self.id

@app.route('/', methods=['POST', 'GET'])
def index():
    return render_template('index.html')

@app.route('/list', methods=['POST', 'GET'])
def list():
    tickets = Tickets.query.order_by(Tickets.id).all()
    return render_template('list.html', tickets=tickets)

@app.route('/add', methods=['POST', 'GET'])
def add():
    if request.method == 'POST':
        if int(request.form.get('n_of_repeats')) == 0:
            return "You need to enter a number greater than 0"
        for i in range(int(request.form.get('n_of_repeats'))):
            print('repeating 00--00', int(request.form.get('n_of_repeats')))
            import secrets
            import json
            with open('settings.json') as f:
                string = f.read()
            string = string.replace('\n', '')
            string = string.replace('   ', '')
            string = string.replace(' ', '')
            #*EXTRACTION OF JSON DATA
            Qrcode = json.loads(string)["QrCode"]

            code_insite = secrets.randbelow(Qrcode["len_max"])
            new_task = Tickets(code=code_insite)
            try:
                db.session.add(new_task)
                db.session.commit()  
            except IntegrityError as e:
                return 'Błąd podczas dodawania do bazy danych {}'.format(e) + '<br><br> Najprawdopodobniej taki kod już istnieje <br><br> <h1> <a href="/add">Spróbój Ponownie</a> </h1>'
            except Exception as e:
                return 'Błąd podczas dodawania do bazy danych {}'.format(e) + '<br><br><h1 href="/add">Spróbój Ponownie</h1>'
        return redirect('/list')
    else:
        return render_template('add.html')

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Tickets.query.get(id)
    if task_to_delete is None:
        return render_template('error-not-found.html', id=id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/list')
    except:
        return 'There was a problem deleting that ticket'

@app.route('/delete-large/<items>', methods=['GET', 'POST'])
def delete_large(items):
    items = str(items)
    items = items.split('*')
    items.pop(len(items)-1)
    if len(items) < 1:
        return 'No task Specified'
    items = [int(items[i]) for i in range(len(items))]
    for i in range(len(items)):
        task_to_delete = Tickets.query.get(items[i])
        if task_to_delete is None:
            return render_template('error-not-found.html', id=id)
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
        except:
            return 'There was a problem deleting that ticket'
    return redirect('/list')

@app.route('/delete-large/')
def delete_large_notselected():
    return 'No ticket Specified'

@app.route('/gen', methods=['POST', 'GET'])
def gen():
    if request.method == 'POST':
        print(request.form.get('generate'))
        if request.form.get('generate') == 'Generuj':
            selected_tickets = request.form.getlist('tickets_Checks')
            ticket_data = []
            for i in range(len(selected_tickets)):
                ticket_data.append(Tickets.query.get(int(selected_tickets[i])))
                ticket_data[i] = {
                    "id": ticket_data[i].id,
                    "code": ticket_data[i].code,
                    "creation_date":ticket_data[i].date_created
                    }
            print(ticket_data)
            import gen_ticket_layout
            urls = []
            for i in range(len(selected_tickets)):
                urls.append(gen_ticket_layout.generate_code(ticket_data[i]))
            print(urls)
            return render_template('gen.html', urls=urls)
        elif request.form.get('generate') == 'Usuń':
            #!TOCLEANUP - Move this part of code to delete_large
            payload = request.form.getlist('tickets_Checks')
            payload_str = ''
            for i in range(len(payload)):
                payload_str += str(payload[i]) + '*'
            return redirect('/delete-large/' + payload_str)  
        else:
            return 'Something went wrong'
    else:
        return 'Something went wrong'

@app.route('/img/<filename>')
def img(filename):
    import os
    if not os.path.isfile('upload/' + filename):
        return render_template('error-not-found.html', id=filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



if __name__ == '__main__':
    app.run(debug=True)