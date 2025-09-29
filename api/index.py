from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
import sqlite3
import subprocess
from deep_translator import GoogleTranslator

app = Flask(__name__)

DATA_FILE = 'toi_headlines_with_all_info.csv'
DB_FILE = 'feedback.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            headline TEXT,
            category TEXT,
            sentiment TEXT,
            feedback TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET'])
def index():
    language = request.args.get('language', 'en')
    df = pd.read_csv(DATA_FILE)

    translator = None
    if language != 'en':
        translator = GoogleTranslator(source='auto', target=language)

    headlines = []
    translation_cache = {}  # 🧠 cache for translations

    for _, row in df.iterrows():
        row_data = row.to_dict()
        base_text = row_data.get('Translated_Headline') or row_data['Headline']

        # 🪄 Use cache or translate once
        if translator:
            if base_text not in translation_cache:
                try:
                    translation_cache[base_text] = translator.translate(base_text)
                except Exception:
                    translation_cache[base_text] = base_text  # fallback
            display_text = translation_cache[base_text]
        else:
            display_text = base_text

        row_data['Translated_Headline'] = display_text
        headlines.append(row_data)

    return render_template('feedback.html', headlines=headlines, language=language)

@app.route('/refresh', methods=['GET'])
def refresh_news():
    subprocess.run(['python', 'full_pipeline.py'])
    return redirect(request.referrer or '/')

@app.route('/submit', methods=['POST'])
def submit_feedback():
    headline = request.form['headline']
    category = request.form['category']
    sentiment = request.form['sentiment']
    feedback = request.form['feedback']

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feedback (headline, category, sentiment, feedback)
        VALUES (?, ?, ?, ?)
    ''', (headline, category, sentiment, feedback))
    conn.commit()
    conn.close()

    return redirect(request.referrer or '/')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT headline, category, sentiment FROM feedback")
    feedback_data = cursor.fetchall()
    conn.close()

    df_fb = pd.DataFrame(feedback_data, columns=['Headline', 'Category', 'Sentiment'])
    df_fb.to_csv('grouped_data.csv', index=False)

    sentiment_counts = df_fb['Sentiment'].value_counts()
    labels = sentiment_counts.index.tolist()
    values = sentiment_counts.tolist()

    return render_template(
        'dashboard.html',
        grouped_data=df_fb.to_dict(orient='records'),
        sentiments=labels,
        counts=values
    )

@app.route('/download_csv', methods=['GET'])
def download_csv():
    return send_file('grouped_data.csv', as_attachment=True)

if __name__ == '__main__':
    #app.run(host='127.0.0.1', port=5050, debug=True)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
