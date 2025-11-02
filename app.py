from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib

app = Flask(__name__)

# Load model & encoder dengan error handling
try:
    model = joblib.load("model.pkl")
    label_encoders = joblib.load("label_encoders.pkl")
    print("✅ Model dan label encoder berhasil dimuat")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    label_encoders = None

# Halaman utama
@app.route('/')
def home():
    return render_template('index.html')

# Prediksi
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Validasi model tersedia
        if model is None or label_encoders is None:
            return jsonify({
                'success': False,
                'error': 'Model belum dimuat. Pastikan file model.pkl dan label_encoders.pkl tersedia.'
            }), 500

        # Ambil data dari form HTML
        try:
            input_data = {
                'Student_Age': int(request.form.get('Student_Age', 0)),
                'Sex': request.form.get('Sex', ''),
                'High_School_Type': request.form.get('High_School_Type', ''),
                'Scholarship': request.form.get('Scholarship', ''),
                'Additional_Work': request.form.get('Additional_Work', ''),
                'Sports_activity': request.form.get('Sports_activity', ''),
                'Transportation': request.form.get('Transportation', ''),
                'Weekly_Study_Hours': int(request.form.get('Weekly_Study_Hours', 0)),
                'Attendance': request.form.get('Attendance', ''),
                'Reading': request.form.get('Reading', ''),
                'Notes': request.form.get('Notes', ''),
                'Listening_in_Class': request.form.get('Listening_in_Class', ''),
                'Project_work': request.form.get('Project_work', '')
            }
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': f'Data tidak valid: {str(e)}'
            }), 400

        # Validasi input - periksa apakah field string kosong atau None
        # (bukan menggunakan all() karena 0 dianggap falsy)
        missing_fields = []
        for key, value in input_data.items():
            if isinstance(value, str) and value.strip() == '':
                missing_fields.append(key)
            elif value is None:
                missing_fields.append(key)
        
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Field berikut harus diisi: {", ".join(missing_fields)}'
            }), 400
        
        # Validasi range untuk numeric fields
        if input_data['Student_Age'] < 17 or input_data['Student_Age'] > 30:
            return jsonify({
                'success': False,
                'error': 'Usia mahasiswa harus antara 17-30 tahun'
            }), 400
        
        if input_data['Weekly_Study_Hours'] < 0 or input_data['Weekly_Study_Hours'] > 168:
            return jsonify({
                'success': False,
                'error': 'Jam belajar per minggu harus antara 0-168 jam'
            }), 400

        # Pastikan urutan kolom sesuai dengan model training
        # Urutan harus sama dengan saat training: Student_Age, Sex, High_School_Type, Scholarship, ...
        feature_order = [
            'Student_Age', 'Sex', 'High_School_Type', 'Scholarship', 
            'Additional_Work', 'Sports_activity', 'Transportation', 
            'Weekly_Study_Hours', 'Attendance', 'Reading', 'Notes', 
            'Listening_in_Class', 'Project_work'
        ]
        
        # Buat DataFrame dengan urutan kolom yang benar
        df = pd.DataFrame([input_data], columns=feature_order)

        # Encode kolom kategorikal
        for col, le in label_encoders.items():
            if col in df.columns and col != 'Grade':
                try:
                    df[col] = le.transform(df[col])
                except ValueError as e:
                    return jsonify({
                        'success': False,
                        'error': f'Nilai pada {col} tidak valid: {str(e)}'
                    }), 400

        # Pastikan urutan kolom sesuai dengan model sebelum prediksi
        df = df[feature_order]
        
        # Debug: cetak info DataFrame sebelum prediksi
        print(f"\n🔍 DEBUG: DataFrame sebelum prediksi:")
        print(f"   Kolom: {list(df.columns)}")
        print(f"   Data: {df.values[0]}")

        # Prediksi
        prediction_encoded = model.predict(df)[0]
        prediction_proba = model.predict_proba(df)[0]
        
        # Decode Grade kembali ke format asli
        if 'Grade' in label_encoders:
            grade_encoder = label_encoders['Grade']
            prediction_grade = grade_encoder.inverse_transform([prediction_encoded])[0]
        else:
            prediction_grade = str(prediction_encoded)

        # Hitung confidence score
        confidence = max(prediction_proba) * 100

        # Mapping grade ke deskripsi yang lebih friendly
        grade_mapping = {
            'AA': {'label': 'Sangat Baik (AA)', 'color': '#28a745', 'icon': '🌟'},
            'BA': {'label': 'Baik (BA)', 'color': '#17a2b8', 'icon': '✨'},
            'BB': {'label': 'Cukup Baik (BB)', 'color': '#ffc107', 'icon': '👍'},
            'BC': {'label': 'Cukup (BC)', 'color': '#fd7e14', 'icon': '📚'},
            'CB': {'label': 'Cukup (CB)', 'color': '#fd7e14', 'icon': '📚'},
            'CC': {'label': 'Cukup (CC)', 'color': '#dc3545', 'icon': '⚠️'},
            'CD': {'label': 'Kurang (CD)', 'color': '#e83e8c', 'icon': '📉'},
            'DC': {'label': 'Kurang (DC)', 'color': '#e83e8c', 'icon': '📉'},
            'DD': {'label': 'Kurang (DD)', 'color': '#6f42c1', 'icon': '📊'},
            'Fail': {'label': 'Gagal (Fail)', 'color': '#dc3545', 'icon': '❌'},
        }

        grade_info = grade_mapping.get(prediction_grade, {
            'label': f'Grade {prediction_grade}',
            'color': '#6c757d',
            'icon': '📝'
        })

        return jsonify({
            'success': True,
            'prediction': prediction_grade,
            'label': grade_info['label'],
            'confidence': round(confidence, 2),
            'color': grade_info['color'],
            'icon': grade_info['icon']
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Terjadi kesalahan saat melakukan prediksi: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
