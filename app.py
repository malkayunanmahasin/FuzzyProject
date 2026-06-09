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
    # 1. FUZZIFIKASI BMI (3 Parameter: Masing-masing 1 kurva berurutan)
    # =========================
    # Tidak Ideal: Kurva turun di sebelah kiri
    tidak_ideal_val = turun(bmi, 18, 22)
    
    # Ideal: Kurva segitiga di tengah (puncak di 22)
    ideal_val = segitiga(bmi, 18, 22, 26)
    
    # Sangat Ideal: Kurva naik di sebelah kanan
    sangat_ideal_val = naik(bmi, 22, 26)

    # Menentukan arah fisik untuk saran
    if bmi < 20:
        arah_fisik = "Kurus"
    elif bmi > 24:
        arah_fisik = "Gemuk"
    else:
        arah_fisik = "Proporsional"

    # =========================
    # 2. INFERENSI SUGENO ORDE-NOL (Rules)
    # =========================
    # Konstanta dasar jika aktivitas sedang/normal
    z_tidak = 30
    z_ideal = 70
    z_sangat = 100

    # Rule intervensi Aktivitas
    if aktivitas == "tinggi":
        z_tidak += 10
        z_ideal += 10
        z_sangat = 100
    elif aktivitas == "rendah":
        z_tidak -= 15
        z_ideal -= 10
        z_sangat -= 10

    # =========================
    # 3. DEFUZZIFIKASI SUGENO (Weighted Average)
    # =========================
    pembilang = (tidak_ideal_val * z_tidak) + (ideal_val * z_ideal) + (sangat_ideal_val * z_sangat)
    penyebut = tidak_ideal_val + ideal_val + sangat_ideal_val

    if penyebut > 0:
        skor_sugeno = pembilang / penyebut
    else:
        skor_sugeno = 0

    # =========================
    # 4. HASIL BERDASARKAN SKOR SUGENO (3 Kategori)
    # =========================
    if skor_sugeno >= 80:
        status = "Sangat Ideal"
        icon = "🟢"
        color_class = "green"
    elif skor_sugeno >= 50:
        status = "Ideal"
        icon = "🟡"
        color_class = "yellow"
    else:
        status = "Tidak Ideal"
        icon = "🔴"
        color_class = "red"

    pointer_map = {
        "Tidak Ideal": 15,
        "Ideal": 50,
        "Sangat Ideal": 85,
    }
    pointer = pointer_map.get(status, 50)

    # Deskripsi web
    desc = f"📊 Skor Keidealan: {round(skor_sugeno, 1)} / 100. "
    
    if arah_fisik == "Proporsional":
         desc += "Tinggi dan berat badan kamu berada dalam kondisi yang seimbang."
         advice = "Pertahankan pola makan dan olahraga rutin."
    elif arah_fisik == "Kurus":
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

    # =========================
    # GENERATE DATA GRAFIK CHART.JS
    # =========================
    bmi_labels = [x * 0.5 for x in range(20, 81)] # dari 10.0 sampai 40.0
    data_tidak = []
    data_ideal = []
    data_sangat = []
    
    for x in bmi_labels:
        data_tidak.append(round(turun(x, 18, 22), 2))
        data_ideal.append(round(segitiga(x, 18, 22, 26), 2))
        data_sangat.append(round(naik(x, 22, 26), 2))

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
        tidak_ideal=round(tidak_ideal_val, 2),
        ideal=round(ideal_val, 2),
        sangat_ideal=round(sangat_ideal_val, 2),
        bmi_labels=bmi_labels,
        data_tidak=data_tidak,
        data_ideal=data_ideal,
        data_sangat=data_sangat
    )

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=8000)