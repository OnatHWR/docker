import time
import redis
from flask import Flask, render_template
import os
from dotenv import load_dotenv
import pandas as pd
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()

# Configure Redis
cache = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379, password=os.getenv('REDIS_PASSWORD'))

app = Flask(__name__)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)

@app.route('/')
def hello():
    count = get_hit_count()
    return render_template('hello.html', name="BIPM", count=count)

@app.route('/titanic')
def titanic():
    # Load the Titanic dataset
    df = pd.read_csv('titanic.csv')
    
    # Generate a bar chart for survival by gender
    survival_by_gender = df.groupby(['Sex', 'Survived']).size().unstack()
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    survival_by_gender.plot(kind='bar')
    plt.title('Survival by Gender')
    plt.xlabel('Gender')
    plt.ylabel('Count')
    plt.xticks(rotation=0)
    plt.legend(['Did not survive', 'Survived'])
    
    # Ensure static directory exists
    os.makedirs('static', exist_ok=True)
    
    # Save the plot
    plt.savefig('static/survival_chart.png')
    
    # Generate HTML table with first 5 rows
    table = df.head(5).to_html(classes='table table-striped')
    
    return render_template('titanic.html', table=table)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)