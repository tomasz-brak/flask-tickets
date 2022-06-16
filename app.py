# Check if important directories exist and create them if they don't
import os
if os.path.exists("upload") != True:
    os.mkdir("upload")
if os.path.exists("temp") != True:
    os.mkdir("temp")
if os.path.exists("temp/pdfs") != True:
    os.mkdir("temp/pdfs")

import codeop
import codecs
from datetime import datetime
from flask import (
    Flask,
    render_template,
    send_file,
    send_from_directory,
    url_for,
    request,
    redirect,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///main.db"
app.config["UPLOAD_FOLDER"] = "upload"
db = SQLAlchemy(app)


class Tickets(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Integer, unique=True)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return "<Ticket %r>" % self.id


@app.route("/", methods=["POST", "GET"])
def index():
    return render_template("index.html")


@app.route("/search")
def search():
    return render_template("search.html")

@app.route("/search/query", methods=["GET"])
def search_query():
    query = request.args.get("query")
    if query:
        #check if code exists in database
        ticket = Tickets.query.filter_by(code=query).first()
        if ticket:
            return render_template("search_result.html", code=query, found="Znaleziono Bilet ✅")
        return render_template("search_result.html", code=query, found="NIE Znaleziono Bilet ❌")
    else:
        return "Nie znaleziono"

@app.route("/list", methods=["POST", "GET"])
def list():
    tickets = Tickets.query.order_by(Tickets.id).all()
    return render_template("list.html", tickets=tickets)


@app.route("/add", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        if int(request.form.get("n_of_repeats")) == 0:
            return "You need to enter a number greater than 0"
        for i in range(int(request.form.get("n_of_repeats"))):
            print("repeating 00--00", int(request.form.get("n_of_repeats")))
            import secrets
            import json

            with open("settings.json") as f:
                string = f.read()
            string = string.replace("\n", "")
            string = string.replace("   ", "")
            string = string.replace(" ", "")
            # *EXTRACTION OF JSON DATA
            Qrcode = json.loads(string)["QrCode"]

            code_insite = secrets.randbelow(Qrcode["len_max"])
            new_task = Tickets(code=code_insite)
            try:
                db.session.add(new_task)
                db.session.commit()
            except IntegrityError as e:
                return (
                    "Błąd podczas dodawania do bazy danych {}".format(e)
                    + '<br><br> Najprawdopodobniej taki kod już istnieje <br><br> <h1> <a href="/add">Spróbój Ponownie</a> </h1>'
                )
            except Exception as e:
                return (
                    "Błąd podczas dodawania do bazy danych {}".format(e)
                    + '<br><br><h1 href="/add">Spróbój Ponownie</h1>'
                )
        return redirect("/list")
    else:
        return render_template("add.html")


@app.route("/delete/<int:id>")
def delete(id):
    task_to_delete = Tickets.query.get(id)
    if task_to_delete is None:
        return render_template("error-not-found.html", id=id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect("/list")
    except:
        return "There was a problem deleting that ticket"


@app.route("/delete-large/<items>", methods=["GET", "POST"])
def delete_large(items):
    items = str(items)
    items = items.split("*")
    items.pop(len(items) - 1)
    if len(items) < 1:
        return "No task Specified"
    items = [int(items[i]) for i in range(len(items))]
    for i in range(len(items)):
        task_to_delete = Tickets.query.get(items[i])
        if task_to_delete is None:
            return render_template("error-not-found.html", id=id)
        try:
            db.session.delete(task_to_delete)
            db.session.commit()
        except:
            return "There was a problem deleting that ticket"
    return redirect("/list")


@app.route("/gen", methods=["POST", "GET"])
def gen():
    if request.method == "POST":
        import shutil

        try:
            shutil.rmtree("upload")
            print("deleted $upload$ folder")
        except FileNotFoundError:
            print("$upload$ folder not found")
        print(request.form.get("generate"))
        if request.form.get("generate") == "Generuj":
            selected_tickets = request.form.getlist("tickets_Checks")
            ticket_data = []
            for i in range(len(selected_tickets)):
                ticket_data.append(Tickets.query.get(int(selected_tickets[i])))
                ticket_data[i] = {
                    "id": ticket_data[i].id,
                    "code": ticket_data[i].code,
                    "creation_date": ticket_data[i].date_created,
                }
            print(ticket_data)
            import gen_ticket_layout

            urls = []
            for i in range(len(selected_tickets)):
                urls.append(gen_ticket_layout.generate_code(ticket_data[i]))
            print(urls)
            return render_template("gen.html", urls=urls)
        elif request.form.get("generate") == "Usuń":
            #!TOCLEANUP - Move this part of code to delete_large
            payload = request.form.getlist("tickets_Checks")
            payload_str = ""
            for i in range(len(payload)):
                payload_str += str(payload[i]) + "*"
            return redirect("/delete-large/" + payload_str)
        else:
            return "Something went wrong"
    else:
        return "Something went wrong"


@app.route("/download")
def download():
    from PIL import Image
    import math

    # get size of template.png
    img = Image.open("template.png")
    width, height = img.size
    img.close()
    print(width, height)
    # open a new image size of a4 paper
    a4_width = 2480
    a4_height = 3508
    # open all images from /upload folder
    images = [img for img in os.listdir("upload")]
    if images == []:
        return "No images selected"
    print(images)
    #get pixel size of template.png
    img = Image.open("template.png")
    width, height = img.size
    img.close()
    # get number of pages
    if width > a4_width:
        return "Template is too wide"
    if height > a4_height:
        return "Template is too tall"
    #check how may will fill vertically
    vertical_img_per_page = math.floor(a4_height / height)
    horizontal_img_per_page = math.floor(a4_width / width)

    # images per page
    images_per_page = vertical_img_per_page * horizontal_img_per_page
    additonal_page_images = len(images) % images_per_page
    normal_pages = math.floor(len(images) / images_per_page)

    page = Image.new("RGB", (a4_width, a4_height), color="white")   
    counter = 0
    # add images to page
    for i in range(normal_pages):
        for j in range(horizontal_img_per_page):
            for k in range(vertical_img_per_page):
                img = Image.open("upload/" + images[counter])
                counter += 1
                page.paste(img, (j * width, k * height))
        page.save("temp/pdfs/" + str(i) + ".pdf")
        page = Image.new("RGB", (a4_width, a4_height), color="white")

    # add additonal images to page
    if additonal_page_images > 0:
        for i in range(horizontal_img_per_page):
            for j in range(vertical_img_per_page):
                if counter < len(images):
                    img = Image.open("upload/" + images[counter])
                    counter += 1
                    page.paste(img, (i * width, j * height))
        page.save("temp/pdfs/last.pdf")

    # merge all pdfs
    from PyPDF2 import PdfFileMerger
    pdfs = [pdf for pdf in os.listdir("temp/pdfs")]
    merger = PdfFileMerger()
    for pdf in pdfs:
        merger.append("temp/pdfs/" + pdf)
    merger.write("temp/result.pdf")
    return send_file("temp/result.pdf", as_attachment=True)


@app.route("/img/<filename>")
def img(filename):
    import os

    if not os.path.isfile("upload/" + filename):
        return render_template("error-not-found.html", id=filename)
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
