document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('predictionForm');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    const resultContainer = document.getElementById('resultContainer');
    const errorContainer = document.getElementById('errorContainer');
    const resetBtn = document.getElementById('resetBtn');

    // Validasi form sebelum submit
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Validasi semua field
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.style.borderColor = '#dc3545';
                field.addEventListener('input', function() {
                    this.style.borderColor = '#e9ecef';
                }, { once: true });
            }
        });

        if (!isValid) {
            showError('Mohon lengkapi semua field yang wajib diisi');
            return;
        }

        // Sembunyikan hasil sebelumnya
        resultContainer.style.display = 'none';
        errorContainer.style.display = 'none';

        // Tampilkan loading state
        submitBtn.disabled = true;
        btnText.style.display = 'none';
        btnLoading.style.display = 'flex';
        form.classList.add('loading');

        // Ambil form data
        const formData = new FormData(form);

        try {
            const response = await fetch('/predict', {
                method: 'POST',
                body: formData
            });

            // Cek jika response OK
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Parse JSON response
            let data;
            try {
                data = await response.json();
            } catch (jsonError) {
                throw new Error('Respon dari server tidak valid (bukan JSON)');
            }

            if (data.success) {
                showResult(data);
            } else {
                showError(data.error || 'Terjadi kesalahan saat melakukan prediksi');
            }
        } catch (error) {
            showError('Terjadi kesalahan: ' + error.message);
        } finally {
            // Reset loading state
            submitBtn.disabled = false;
            btnText.style.display = 'flex';
            btnLoading.style.display = 'none';
            form.classList.remove('loading');
            
            // Ensure button displays correctly
            submitBtn.style.display = 'flex';
        }
    });

    // Fungsi untuk menampilkan hasil
    function showResult(data) {
        const resultIcon = document.getElementById('resultIcon');
        const resultTitle = document.getElementById('resultTitle');
        const resultGrade = document.getElementById('resultGrade');
        const confidenceFill = document.getElementById('confidenceFill');
        const confidenceValue = document.getElementById('confidenceValue');

        // Set icon dan warna
        resultIcon.textContent = data.icon;
        resultIcon.style.color = data.color;
        
        // Set title
        resultTitle.textContent = data.label;
        resultTitle.style.color = data.color;

        // Set grade
        resultGrade.textContent = data.prediction;
        resultGrade.style.color = data.color;

        // Set confidence
        confidenceFill.style.width = '0%';
        setTimeout(() => {
            confidenceFill.style.width = data.confidence + '%';
        }, 100);
        
        confidenceValue.textContent = data.confidence + '%';

        // Tampilkan container
        resultContainer.style.display = 'block';

        // Scroll ke hasil
        resultContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    // Fungsi untuk menampilkan error
    function showError(message) {
        const errorMessage = document.getElementById('errorMessage');
        errorMessage.textContent = message;
        errorContainer.style.display = 'block';
        
        // Scroll ke error
        errorContainer.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        // Auto hide setelah 5 detik
        setTimeout(() => {
            errorContainer.style.display = 'none';
        }, 5000);
    }

    // Reset button
    resetBtn.addEventListener('click', function() {
        resultContainer.style.display = 'none';
        errorContainer.style.display = 'none';
        
        // Reset border colors
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            input.style.borderColor = '';
        });
    });

    // Animasi saat input focus
    const inputs = form.querySelectorAll('input, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });

        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });

    // Validasi real-time untuk number inputs
    const numberInputs = form.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function() {
            const min = parseInt(this.getAttribute('min'));
            const max = parseInt(this.getAttribute('max'));
            const valueStr = this.value.trim();
            
            // Jika input kosong, reset validasi
            if (!valueStr) {
                this.style.borderColor = '';
                this.setCustomValidity('');
                return;
            }
            
            const value = parseInt(valueStr);
            
            // Validasi jika nilai bukan NaN dan di luar range
            if (!isNaN(value) && (value < min || value > max)) {
                this.style.borderColor = '#dc3545';
                this.setCustomValidity(`Nilai harus antara ${min} dan ${max}`);
            } else {
                this.style.borderColor = '';
                this.setCustomValidity('');
            }
        });
    });
});

