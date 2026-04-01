import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DB_NAME = "efkar.db"


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mood TEXT NOT NULL,
            content TEXT NOT NULL,
            reply TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def generate_reply(content, mood):
    """
    İlk sürüm için sahte-AI / kural tabanlı cevap sistemi.
    Sonradan gerçek API ile değiştirilebilir.
    """
    text = content.lower()

    # Anahtar kelime bazlı basit cevaplar
    if "yalnız" in text or "yalniz" in text:
        return "Yalnız hissetmen, gerçekten yalnız olduğun anlamına gelmez. Bazen insanın içi kalabalığın ortasında bile sessizleşir."
    if "sınav" in text or "sinav" in text or "ders" in text:
        return "Şu an baskı büyük gibi geliyor olabilir ama her yük parça parça taşınır. Bugün sadece bir küçük adım atman bile değerlidir."
    if "aşk" in text or "seviyorum" in text or "hoşlanıyorum" in text:
        return "Kalp bazen mantıktan hızlı gider. Kendini kaybetmeden hislerini anlamaya çalışman en sağlam yoldur."
    if "aile" in text or "annem" in text or "babam" in text:
        return "Aile meseleleri insanın içine en çok oturan şeylerdendir. Ama her düğüm bir anda çözülmez; önce neyin seni kırdığını netleştirmek gerekir."
    if "arkadaş" in text or "kanka" in text:
        return "Dostlukta en ağır gelen şey anlaşılmamaktır. Belki önce kırıldığın noktayı kendi içinde netleştirmen iyi gelir."

    # Ruh haline göre genel cevap
    mood_replies = {
        "üzgün": "Üzgün hissetmen zayıflık değil. İnsan bazen taşıdığı yükü ancak durunca fark eder.",
        "öfkeli": "Öfke çoğu zaman görünen yüzdür; altında kırgınlık ya da hayal kırıklığı yatar. Önce sebebi ayıklamak gerekir.",
        "karışık": "Kafanın karışık olması kötü değil. Bazen doğru cevap, hemen karar vermemekte saklıdır.",
        "mutlu": "İyi hissettiğin anları küçümseme. İnsan bazen ayakta kalmayı böyle küçük iyi anlarla öğrenir.",
        "boşlukta": "Boşluk hissi sessizdir ama ağırdır. Yine de insanı toparlayan şey çoğu zaman küçük düzenler ve küçük hedeflerdir."
    }

    return mood_replies.get(
        mood,
        "İçinden geçenleri yazman bile iyi bir başlangıç. İnsan bazen önce dökerek toparlanır."
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        mood = request.form.get("mood", "").strip()
        content = request.form.get("content", "").strip()

        if not mood or not content:
            return render_template(
                "index.html",
                error="Ruh hali ve metin alanı boş bırakılamaz.",
                posts=get_posts()
            )

        reply = generate_reply(content, mood)
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO posts (mood, content, reply, created_at) VALUES (?, ?, ?, ?)",
            (mood, content, reply, created_at)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    return render_template("index.html", posts=get_posts(), error=None)


def get_posts():
    conn = get_db_connection()
    posts = conn.execute(
        "SELECT * FROM posts ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return posts


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
