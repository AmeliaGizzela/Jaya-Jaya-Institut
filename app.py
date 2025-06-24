import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt

# Load model, scaler, dan nama fitur
model = joblib.load('dropout_model.pkl')
scaler = joblib.load('scaler.pkl')
feature_names = joblib.load('feature_names.pkl')
# Load dataframe original untuk mengidentifikasi kolom kategorikal dan numerik
df = pd.read_csv('students_performance/data.csv', delimiter=';')
df_prep = df.copy()

# Identifikasi kolom kategorikal dan numerik dari logika notebook
categorical_cols = [
    col for col in df_prep.drop(columns='Status').columns
    if (df_prep[col].nunique() < 20 and df_prep[col].dtype in ['int64', 'object'])
]

# Judul Aplikasi
st.title("🎓 Prediksi Dropout Mahasiswa - Jaya Jaya Institut")
st.write("Masukkan data siswa untuk memprediksi apakah ia akan Dropout, Terdaftar (Enrolled), atau Lulus (Graduate).")

# --- Input Data Mahasiswa di Halaman Utama ---
st.subheader("Input Data Mahasiswa")

# Membagi layout menjadi dua kolom
col1, col2 = st.columns(2)

with col1:
    age = st.slider('Usia saat mendaftar', 17, 70, 20)
    gender_map = {'Perempuan': 0, 'Laki-laki': 1}
    gender = st.selectbox('Jenis Kelamin', options=list(gender_map.keys()))
    admission_grade = st.slider('Nilai masuk', 95.0, 190.0, 130.0)
    displaced_map = {'Tidak': 0, 'Ya': 1}
    displaced = st.selectbox('Apakah siswa merantau?', options=list(displaced_map.keys()))
    tuition_paid_map = {'Ya': 1, 'Tidak': 0}
    tuition_paid = st.selectbox('Apakah biaya kuliah lunas?', options=list(tuition_paid_map.keys()))
    curricular_units_1st_sem_approved = st.slider('SKS Lulus Semester 1', 0, 26, 5)
    curricular_units_2nd_sem_approved = st.slider('SKS Lulus Semester 2', 0, 20, 5)

with col2:
    debtor_map = {'Tidak': 0, 'Ya': 1}
    debtor = st.selectbox('Apakah siswa punya utang?', options=list(debtor_map.keys()))
    scholarship_map = {'Tidak': 0, 'Ya': 1}
    scholarship = st.selectbox('Penerima beasiswa?', options=list(scholarship_map.keys()))
    gdp = st.slider('GDP', -4.0, 4.0, 0.0, step=0.1)
    curricular_units_1st_sem_grade = st.slider('Rata-rata Nilai Semester 1', 0.0, 20.0, 12.0)
    curricular_units_2nd_sem_grade = st.slider('Rata-rata Nilai Semester 2', 0.0, 20.0, 12.0)


# Buat dictionary dari input pengguna
input_dict = {
    'Age_at_enrollment': age,
    'Gender': gender_map[gender],
    'Admission_grade': admission_grade,
    'Displaced': displaced_map[displaced],
    'Tuition_fees_up_to_date': tuition_paid_map[tuition_paid],
    'Debtor': debtor_map[debtor],
    'Scholarship_holder': scholarship_map[scholarship],
    'Curricular_units_1st_sem_approved': curricular_units_1st_sem_approved,
    'Curricular_units_1st_sem_grade': curricular_units_1st_sem_grade,
    'Curricular_units_2nd_sem_approved': curricular_units_2nd_sem_approved,
    'Curricular_units_2nd_sem_grade': curricular_units_2nd_sem_grade,
    'GDP': gdp
}

# Buat DataFrame satu baris dari dictionary
input_df_single = pd.DataFrame([input_dict])

# Tambahkan kolom yang hilang dari dataframe asli dengan nilai default (misalnya, 0 atau modus)
# Langkah ini penting agar one-hot encoding berfungsi dengan benar
for col in df_prep.drop(columns=['Status']).columns:
    if col not in input_df_single.columns:
        # Menggunakan 0 sebagai nilai default untuk kesederhanaan
        input_df_single[col] = 0

# Lakukan one-hot encoding pada fitur kategorikal
input_encoded = pd.get_dummies(input_df_single, columns=categorical_cols, drop_first=True)

# Sejajarkan kolom dengan data training
input_aligned = input_encoded.reindex(columns=feature_names, fill_value=0)

# Identifikasi kolom numerik untuk penskalaan berdasarkan dataframe yang sudah selaras
numerical_cols_to_scale = [col for col in df.select_dtypes(include=np.number).columns if col in input_aligned.columns]

# Tombol Prediksi
if st.button('Prediksi Status Mahasiswa'):
    # Skalakan hanya fitur numerik
    input_aligned[numerical_cols_to_scale] = scaler.transform(input_aligned[numerical_cols_to_scale])

    prediction = model.predict(input_aligned)[0]
    prediction_proba = model.predict_proba(input_aligned)

    status_map = {0: 'Dropout', 1: 'Enrolled', 2: 'Graduate'}
    predicted_status = status_map[prediction]

    st.subheader(f"Hasil Prediksi: **{predicted_status}**")

    st.write("Probabilitas:")
    st.write(f"Dropout: {prediction_proba[0][0]:.2%}")
    st.write(f"Enrolled: {prediction_proba[0][1]:.2%}")
    st.write(f"Graduate: {prediction_proba[0][2]:.2%}")

    # Pie chart
    labels = ['Dropout', 'Enrolled', 'Graduate']
    sizes = prediction_proba[0]
    colors = ['#ff9999','#66b3ff','#99ff99']
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=140)
    ax.axis('equal')
    st.pyplot(fig)
