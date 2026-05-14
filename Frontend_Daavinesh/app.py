from flask import Flask, render_template, request
import requests

app = Flask(__name__)
B_URL = "http://127.0.0.1:5000/api"

@app.route('/')
def home():
    try: 
        impact = requests.get(f"{B_URL}/impact").json().get('fci_community_impact', {})
    except: 
        impact = {"total_items_reused": 0, "co2_offset_kg": 0}
    return render_template('index.html', impact=impact)

@app.route('/login')
def login_page(): return render_template('login.html')

@app.route('/register')
def register_page(): return render_template('register.html')

@app.route('/verify')
def verify_page(): 
    return render_template('verify.html', email=request.args.get('email'))

@app.route('/search')
def search():
    query = request.args.get('query', '')
    try: 
        items = requests.get(f"{B_URL}/items").json()
    except: 
        items = []
    return render_template('result.html', items=items, query=query)

if __name__ == '__main__':
    app.run(port=5001, debug=True)