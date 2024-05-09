import streamlit as st
import requests
import math
from periodictable import elements

# Fungsi untuk mendapatkan deskripsi unsur dari situs web
def get_element_description(symbol):
    url = f"https://www.webelements.com/{symbol.lower()}/"
    response = requests.get(url)
    if response.status_code == 200:
        start_index = response.text.find('<div class="summary">') + len('<div class="summary">')
        end_index = response.text.find('</div>', start_index)
        description = response.text[start_index:end_index]
        return description.strip()
    else:
        return "Deskripsi tidak tersedia."

# Fungsi untuk mendapatkan kategori unsur
def get_category(element):
    if element.number <= 92:
        return 'Logam'
    else:
        return 'Non-logam'

# Fungsi untuk menghitung normalitas larutan
def hitung_normalitas(bobot_ditimbang, faktor_pengali, hasil_titrasi, BE_senyawa):
    normalitas = (bobot_ditimbang) / (faktor_pengali * hasil_titrasi * BE_senyawa)
    return normalitas

# Fungsi untuk menghitung rata-rata normalitas
def hitung_rata_rata(normalitas_list):
    if len(normalitas_list) == 0:
        return None
    else:
        rata_rata = sum(normalitas_list) / len(normalitas_list)
        return rata_rata

# Fungsi untuk menghitung persentase RSD
def hitung_persen_rsd(SD, rata_rata):
    if rata_rata == 0:
        st.error("Rata-rata konsentrasi tidak boleh nol.")
        return None
    else:
        rsd = (SD / rata_rata) * 100
        return rsd

# Fungsi untuk menampilkan halaman tentang aplikasi
def page_about():
    st.title("Tentang Aplikasi Kimia")
    st.write("""
    Aplikasi Kimia adalah aplikasi sederhana yang memungkinkan pengguna melakukan beberapa tugas kimia dasar. Aplikasi ini memungkinkan Anda:
    - Melihat informasi unsur dari tabel periodik.
    - Menghitung normalitas larutan.
    - Menghitung standar deviasi.
    - Menghitung persentase RSD.
    
    
    Aplikasi ini dibangun menggunakan Streamlit dan Python.
    """)

# Fungsi untuk menampilkan halaman kalkulator normalitas
def page_normalitas():
    st.title('Kalkulator Penghitungan Normalitas')
    st.write('Gunakan kalkulator ini untuk menghitung normalitas larutan.')

    jumlah_titrasi = st.number_input('Masukkan jumlah titrasi', min_value=1, value=1)
    normalitas_list = []
    
    for i in range(jumlah_titrasi):
        st.write(f"Titrasi ke-{i+1}")
        bobot_ditimbang = st.number_input(f'Masukkan bobot yang ditimbang untuk Titrasi ke-{i+1} (mg)', min_value=0.0, key=f"bobot_{i}")
        faktor_pengali = st.number_input(f'Masukkan faktor pengali untuk Titrasi ke-{i+1}', min_value=0.0, key=f"faktor_{i}")
        hasil_titrasi = st.number_input(f'Masukkan hasil titrasi untuk Titrasi ke-{i+1} (ml)', min_value=0.0, key=f"hasil_{i}")
        BE_senyawa = st.number_input(f'Masukkan BE senyawa untuk Titrasi ke-{i+1}', min_value=0.0, key=f"BE_{i}")

        if st.button(f'Hitung Titrasi ke-{i+1}'):
            if bobot_ditimbang == 0 or faktor_pengali == 0 or hasil_titrasi == 0 or BE_senyawa == 0:
                st.error("Input semua data.")
            else:
                normalitas = hitung_normalitas(bobot_ditimbang, faktor_pengali, hasil_titrasi, BE_senyawa)
                normalitas_list.append(normalitas)
                st.write(f'Normalitas untuk Titrasi ke-{i+1} = {normalitas:.2f} N')

    if len(normalitas_list) > 0:
        rata_rata_normalitas = hitung_rata_rata(normalitas_list)
        st.write(f'Hasil rata-rata normalitas dari semua titrasi = {rata_rata_normalitas:.2f} N')

# Fungsi untuk menampilkan halaman tabel periodik dan informasi unsur
def page_periodic_table():
    st.title("INFORMASI UNSUR")

    sorted_elements = sorted(elements, key=lambda x: x.number)

    element_choice = st.selectbox("Pilih Unsur", [element.symbol for element in sorted_elements], format_func=lambda x: x.upper())

    selected_element = elements.symbol(element_choice)

    description = get_element_description(selected_element.symbol)

    with st.container():
        st.markdown(
            f"""
            <div class="post-container">
                <div class="post-content">
                    <p style="font-size: 20px; font-weight: bold; text-align: center;">{selected_element.name} ({selected_element.symbol})</p>
                    <p><strong>Nomor Atom:</strong> {selected_element.number}</p>
                    <p><strong>Massa Atom:</strong> {selected_element.mass}</p>
                    <p><strong>Kategori:</strong> {get_category(selected_element)}</p>
                    <p><strong>Kepadatan:</strong> {selected_element.density if hasattr(selected_element, 'density') else 'Tidak Tersedia'}</p>
                    <p><strong>Jumlah Isotop:</strong> {len(selected_element.isotopes)}</p>
                    <p><strong>Deskripsi:</strong> {description}</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Fungsi untuk menampilkan halaman kalkulator persentase RSD
def page_rsd():
    st.title('Kalkulator Persentase RSD')
    SD = st.number_input('Masukkan jumlah SD', min_value=0.0)
    rata_rata = st.number_input('Masukkan rata rata konsentrasi (N)', min_value=0.1)

    if st.button('Hitung'):
        rsd = hitung_persen_rsd(SD, rata_rata)
        if rsd is not None:
            st.write(f'RSD = {rsd:.2f}%')

# Fungsi untuk menampilkan halaman kalkulator standar deviasi
def page_standar_deviasi():
    data_input = []
    num_columns = st.number_input("Jumlah Kolom Input Data", min_value=3, max_value=10, value=3)

    for i in range(num_columns):
        input_data = st.text_input(f"Masukkan data kolom {i+1}")
        if input_data:
            data_input.append([float(x.strip()) for x in input_data.split(',') if x.strip()])

    merged_data = [item for sublist in data_input for item in sublist]

    if merged_data:
        hasil_standar_deviasi = page_standar_deviasi_calc(merged_data)
        st.write("Standar Deviasi:", hasil_standar_deviasi)
    else:
        st.error("Input semua data.")

# Fungsi untuk menghitung standar deviasi
def page_standar_deviasi_calc(data):
    try:
        rata_rata = sum(data) / len(data)
        selisih_kuadrat = sum((x - rata_rata) ** 2 for x in data)
        standar_deviasi = math.sqrt(selisih_kuadrat / (len(data) - 1))
        return standar_deviasi
    except:
        return "Masukkan semua hasil konsentrasi"

# Fungsi utama
def main():
    # Menambahkan pilihan halaman ke sidebar
    page = st.sidebar.radio("Pilih Halaman", ["Tentang Aplikasi", "Informasi Unsur", "Kalkulator Normalitas", "Kalkulator Standar Deviasi", "Kalkulator Persentase RSD"])

    if page == "Tentang Aplikasi":
        page_about()
    elif page == "Informasi Unsur":
        page_periodic_table()
    elif page == "Kalkulator Normalitas":
        page_normalitas()
    elif page == "Kalkulator Standar Deviasi":
        page_standar_deviasi()
    elif page == "Kalkulator Persentase RSD":
        page_rsd()

# Memanggil fungsi utama
if __name__ == '__main__':
    main()
