from flask import Flask, render_template, request
from datetime import datetime
import webbrowser

app = Flask("app")

pomiary = []
led = 0


@app.route("/")
def home():
    #return f"<h1>Witamy na stronie ;) {pomiary}</h1>"
    return render_template("home.html", imie="Cos", pomiary=pomiary)


@app.route("/temperatura/<pomiar>")
def temperatura(pomiar):
    print("Odczytano: ", pomiar)
    pomiary.append([pomiar + " " + str(request.remote_addr), datetime.now().strftime("%d.%m.%Y, %H:%M")])
    # zapis pomiarow do pliku
    return "OK"
    

@app.route("/led")
def dioda():
    return str(led)

@app.route("/setled")
@app.route("/setled/<int:wartosc>")
def set_led(wartosc=None):
    if wartosc is not None:
        global led
        led = wartosc
    return render_template("set-led.html", led=led)


@app.route("/browser")
def open_browser():
    webbrowser.open("https://google.com")
    return "OK"


app.run(host="0.0.0.0", port=2137, debug=True)

