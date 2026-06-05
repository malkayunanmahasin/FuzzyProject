from flask import Flask, render_template, request

app = Flask(__name__)

# =========================
# FUNGSI MEMBERSHIP SUGENO (Fuzzifikasi)
# =========================
def turun(x, a, b):
    if x <= a:
        return 1
    elif x >= b:
        return 0
    return (b - x) / (b - a)

def naik(x, a, b):
    if x <= a:
        return 0
    elif x >= b:
        return 1
    return (x - a) / (b - a)

def segitiga(x, a, b, c):
    if x <= a or x >= c:
        return 0
    elif x == b:
        return 1
    elif x < b:
        return (x - a) / (b - a)
    return (c - x) / (c - b)

# =========================
# ROUTE HALAMAN
# =========================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/input")
def input_page():
    return render_template("input.html")

@app.route("/learn")
def learn():
    return render_template("learn.html")

@app.route("/result", methods=["POST"])
def result():
    bb = float(request.form["bb"])
    tb_cm = float(request.form["tb"])
    umur = int(request.form["umur"])
    aktivitas = request.form["aktivitas"]

    tb_m = tb_cm / 100
    bmi = bb / (tb_m * tb_m)

    # =========================
    # 1. FUZZIFIKASI BMI
    # Menghitung derajat keanggotaan (0.0 - 1.0)
    # =========================
    belum_ideal = turun(bmi, 17, 18.5)
    kurang_ideal = segitiga(bmi, 18, 20, 22)
    ideal = segitiga(bmi, 21, 23, 25)
    tidak_ideal = naik(bmi, 24.5, 30)

    # Hanya digunakan untuk mendeteksi "arah" fisik (Kurus atau Gemuk) untuk saran
    kategori_sugeno = {
        "Kurus": belum_ideal,
        "Mendekati Kurus": kurang_ideal,
        "Proporsional": ideal,
        "Gemuk": tidak_ideal
    }
    arah_fisik = max(kategori_sugeno, key=kategori_sugeno.get)

    # =========================
    # 2. INFERENSI SUGENO ORDE-NOL (Rules)
    # Menentukan nilai konstanta (Z) dari skala 0-100 untuk Skor Keidealan
    # =========================
    # Konstanta dasar jika aktivitas sedang/normal
    z_belum = 40
    z_kurang = 70
    z_ideal = 90
    z_tidak = 30

    # Rule intervensi Aktivitas terhadap nilai konstanta (Z)
    if aktivitas == "tinggi":
        z_belum += 10
        z_kurang += 10
        z_ideal = 100   # Maksimal skor 100
        z_tidak += 10
    elif aktivitas == "rendah":
        z_belum -= 10
        z_kurang -= 10
        z_ideal -= 10
        z_tidak -= 15

    # =========================
    # 3. DEFUZZIFIKASI SUGENO (Weighted Average)
    # =========================
    # Rumus: ((Derajat1 * Z1) + (Derajat2 * Z2) ... ) / (Total Derajat)
    pembilang = (belum_ideal * z_belum) + (kurang_ideal * z_kurang) + (ideal * z_ideal) + (tidak_ideal * z_tidak)
    penyebut = belum_ideal + kurang_ideal + ideal + tidak_ideal

    # Menghindari error pembagian dengan nol
    if penyebut > 0:
        skor_sugeno = pembilang / penyebut
    else:
        skor_sugeno = 0

    # =========================
    # 4. HASIL BERDASARKAN SKOR SUGENO
    # =========================
    if skor_sugeno >= 85:
        status = "Sangat Ideal"
        icon = "🟢"
        color_class = "green"
    elif skor_sugeno >= 65:
        status = "Mendekati Ideal"
        icon = "🟡"
        color_class = "yellow"
    elif skor_sugeno >= 45:
        status = "Kurang Ideal"
        icon = "🟠"
        color_class = "yellow"
    else:
        status = "Sangat Tidak Ideal"
        icon = "🔴"
        color_class = "red"

    # Peta posisi jarum agar sesuai dengan status akhir, bukan nilai skor mentah
    pointer_map = {
        "Sangat Tidak Ideal": 10,
        "Kurang Ideal": 35,
        "Mendekati Ideal": 60,
        "Sangat Ideal": 90,
    }
    pointer = pointer_map.get(status, 50)

    # Menyematkan langsung nilai Sugeno ke teks deskripsi web
    desc = f"📊 Skor Keidealan: {round(skor_sugeno, 1)} / 100. "
    
    if arah_fisik == "Proporsional":
         desc += "Tinggi dan berat badan kamu berada dalam kondisi yang seimbang."
         advice = "Pertahankan pola makan dan olahraga rutin."
    elif arah_fisik == "Kurus" or arah_fisik == "Mendekati Kurus":
         desc += "Skor ini didapat karena tubuh kamu cenderung kekurangan berat badan."
         advice = "Tingkatkan asupan nutrisi, protein, dan kalori sehat secara bertahap."
    else:
         desc += "Skor ini didapat karena berat badan kamu melebihi batas ideal."
         advice = "Kurangi makanan tinggi gula/lemak dan tingkatkan aktivitas fisik."

    # =========================
    # INTERPRETASI UMUR
    # =========================
    if umur < 18:
        desc += " Karena usia kamu masih dalam masa pertumbuhan, hasil ini sebaiknya dipahami sebagai gambaran awal."
    elif umur >= 35:
        desc += " Pada usia ini, metabolisme tubuh cenderung mulai menurun sehingga pola hidup perlu lebih dijaga."

    return render_template(
        "result.html",
        bb=bb,
        tb=tb_cm,
        umur=umur,
        aktivitas=aktivitas,
        bmi=round(bmi, 1),
        status=status,
        icon=icon,
        desc=desc,
        advice=advice,
        pointer=round(pointer, 1), 
        color_class=color_class,
        belum=round(belum_ideal, 2),
        kurang=round(kurang_ideal, 2),
        ideal=round(ideal, 2),
        tidak=round(tidak_ideal, 2)
    )

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)