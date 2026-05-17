from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search')
def search():
    query = request.args.get('query')
    
    items = [
        {"name": "Calculator", "description": "Casio FX-570", "faculty": "IT"},
        {"name": "Math Book", "description": "Algebra basics", "faculty": "Engineering"}
    ]

    return render_template('results.html', items=items)

if __name__ == "__main__":
    app.run(debug=True)