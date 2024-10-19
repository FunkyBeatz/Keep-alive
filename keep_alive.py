# Flask setup to keep the bot alive
from flask import Flask
from threading import Thread

app = Flask('__name__')

@app.route('/')
def home():
    return "I'm alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Using this 2nd folder only to make it work in Vercel
