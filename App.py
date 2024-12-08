import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from io import BytesIO
import base64
from pathlib import Path

# Path file (gunakan relative path)
file_path = '198_Peserta_Perhitungan_IQ.xlsx'  # Gunakan relative path
image_path = image_path = 'paper-brain-with-light-bulb.jpg'

# Load dataset
data = pd.read_excel(file_path)

# Hitung rata-rata dan standar deviasi
mean_score = data['Skor Mentah'].mean()
std_dev_score = data['Skor Mentah'].std()

def calculate_iq(raw_score, mean, std_dev):
    z_score = (raw_score - mean) / std_dev
    iq = 100 + 15 * z_score
    return iq

def categorize_iq(iq):
    if iq < 90:
        return "Di bawah rata-rata"
    elif 85 <= iq <= 110:
        return "Rata-rata"
    else:
        return "Di atas rata-rata"

# Fungsi untuk menambahkan latar belakang
def set_background(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode()
        st.markdown(f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_image});
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
            min-height: 100vh;
        }}
        </style>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error setting background: {e}")

set_background(image_path)

# Fungsi untuk membuat grafik distribusi dengan skor mentah pada sumbu X
def create_distribution_graph(mean, std_dev, raw_score):
    # Buat data skor mentah sebagai sumbu X dan IQ sebagai sumbu Y
    raw_scores = np.linspace(raw_score - 20, raw_score + 20, 100)
    iq_scores = mean + (raw_scores - raw_score) * (std_dev / 15)  # Menyesuaikan IQ berdasarkan standar deviasi

    # Buat grafik
    plt.figure(figsize=(10, 6))
    plt.plot(raw_scores, iq_scores, label="Garis Tengah Skor Mentah & Nilai IQ", color='blue')

    # Menambahkan garis untuk nilai rata-rata IQ
    plt.axhline(mean, color='red', linestyle='dashed', label=f"Mean IQ: {mean:.2f}")

    # Menambahkan garis untuk skor IQ pengguna
    user_iq = mean + (raw_score - raw_score) * (std_dev / 15)  # IQ pengguna (biasanya akan dihitung berdasarkan input)
    plt.axvline(raw_score, color='green', linestyle='dashed', label=f"Skor Mentah: {raw_score}")

    # Memberikan keterangan tambahan untuk garis
    plt.text(raw_score + 1, user_iq + 2, f"Skor Mentah: {raw_score}", color='green', fontsize=10)
    plt.text(1, mean + 2, f"Mean IQ: {mean:.2f}", color='red', fontsize=10)

    # Label dan judul
    plt.title("Grafik IQ Berdasarkan Skor Mentah")
    plt.xlabel("Skor Mentah")
    plt.ylabel("Nilai IQ")

    # Menambahkan grid dan legend
    plt.grid(True)
    plt.legend()

    # Menyimpan grafik ke dalam file sementara
    temp_file_path = "temp_graph.png"  # Simpan di lokasi saat ini
    plt.savefig(temp_file_path, bbox_inches='tight')
    plt.close()
    return temp_file_path

# Fungsi untuk membuat PDF dengan header dan footer
def generate_pdf(iq, category, raw_score, name, graph_file_path):
    pdf = FPDF()
    pdf.add_page()

    # Header dengan warna biru muda
    pdf.set_fill_color(173, 216, 230)  # Warna biru muda
    pdf.rect(0, 0, 210, 20, 'F')  # Membuat latar belakang biru muda untuk header
    pdf.set_text_color(0, 0, 0)  # Teks hitam
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, txt="Aplikasi Tes IQ", ln=True, align='C')
    pdf.set_font("Arial", style='I', size=12)

    # Informasi Nilai IQ
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)  # Teks hitam
    pdf.cell(200, 10, txt=f"Nama: {name}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Nilai IQ: {iq:.2f}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Kategori: {category}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Skor Mentah: {raw_score}", ln=True, align='L')
    pdf.ln(10)

    # Cek apakah file gambar tersedia sebelum menambahkannya ke PDF
    try:
        if os.path.exists(graph_file_path):
            pdf.image(graph_file_path, x=10, y=None, w=190)
        else:
            st.error(f"File gambar tidak ditemukan di path {graph_file_path}")
            return None
    except Exception as e:
        st.error(f"Error menambahkan gambar ke PDF: {e}")
        return None

    # Keterangan grafik
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 10, txt=f"""
    1. Grafik di atas menunjukkan hubungan antara skor mentah dan nilai IQ.
    2. Garis putus-putus merah menggambarkan nilai rata-rata IQ (Mean: {mean_score:.2f}).
    3. Garis putus-putus hijau menunjukkan posisi skor mentah pengguna (Skor Mentah: {raw_score}).
    """)

    # Menambahkan kalimat inspiratif di tengah dengan format cetak miring dan kotak biru muda
    pdf.set_fill_color(173, 216, 230)  # Warna biru muda (RGB: 173, 216, 230)
    pdf.set_font("Arial", style='I', size=10)
    pdf.cell(0, 10, txt=" ~ Bukan tentang seberapa pintar Kamu, melainkan seberapa baik Kamu mengenali potensi diri sendiri ~", 
             align='C', ln=True, fill=True)  # fill=True untuk memberi warna latar belakang

    # Simpan PDF ke buffer
    buffer = BytesIO()
    buffer.write(pdf.output(dest='S').encode('latin1'))
    buffer.seek(0)

    # Hapus file grafik sementara setelah selesai
    if os.path.exists(graph_file_path):
        os.remove(graph_file_path)

    return buffer

# Streamlit UI
st.title("Aplikasi Tes IQ")
st.markdown("Masukkan nama dan skor mentah untuk menghitung IQ Anda!")

# Input Nama
name = st.text_input("Masukkan Nama Anda:")

# Input skor mentah
raw_score = st.number_input("Masukkan Skor Mentah:", min_value=0, max_value=200)

if st.button("Hitung IQ"):
    # Perhitungan IQ
    iq = calculate_iq(raw_score, mean_score, std_dev_score)
    category = categorize_iq(iq)
    st.success(f"Nilai IQ Anda: {iq:.2f}")
    st.info(f"Kategori: {category}")
    st.write(f"Skor Mentah Anda: {raw_score}")

    # Buat grafik distribusi dengan garis skor mentah
    graph_file_path = create_distribution_graph(mean_score, std_dev_score, raw_score)

    # Tampilkan grafik di Streamlit
    st.image(graph_file_path, caption="Distribusi Skor IQ", use_container_width=True)

    # Buat PDF
    pdf_buffer = generate_pdf(iq, category, raw_score, name, graph_file_path)

    # Download PDF
    if pdf_buffer:
        st.download_button(
            label="📥 Download Hasil PDF",
            data=pdf_buffer,
            file_name="Hasil_Test_IQ.pdf",
            mime="application/pdf"
        )
