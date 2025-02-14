import streamlit as st
import numpy as np
from scipy.io import wavfile
import soundfile as sf

st.title("Audio File Validator")
st.write("업로드된 오디오 파일의 속성을 검증하는 시스템입니다.")

uploaded_file = st.file_uploader("오디오 파일을 업로드하세요 (WAV 형식)", type=["wav"])

if uploaded_file is not None:
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    def get_audio_properties(file_path):
        data, samplerate = sf.read(file_path)
        bit_depth = 'Unknown'
        if data.dtype == 'int16':
            bit_depth = 16
        elif data.dtype == 'int32':
            bit_depth = 32
        elif data.dtype == 'float32':
            bit_depth = '32 (float)'
        
        channels = data.shape[1] if len(data.shape) > 1 else 1
        duration = len(data) / samplerate

        return {
            "Sample Rate": samplerate,
            "Channels": channels,
            "Bit Depth": bit_depth,
            "Duration (seconds)": round(duration, 2)
        }

    def calculate_noise_floor(file_path):
        samplerate, data = wavfile.read(file_path)
        if len(data.shape) > 1:
            data = data[:, 0]
        noise_floor = 20 * np.log10(np.mean(np.abs(data)))
        return round(noise_floor, 2)

    def check_stereo_status(file_path):
        data, _ = sf.read(file_path)
        if len(data.shape) == 1:
            return "Mono"
        elif np.array_equal(data[:, 0], data[:, 1]):
            return "Dual Mono"
        else:
            return "True Stereo"

    properties = get_audio_properties(file_path)
    st.subheader("파일 검증 결과")
    for key, value in properties.items():
        st.write(f"**{key}**: {value}")
    
    noise_floor = calculate_noise_floor(file_path)
    st.write(f"**Noise Floor (dB)**: {noise_floor}")
    
    stereo_status = check_stereo_status(file_path)
    st.write(f"**Stereo Status**: {stereo_status}")
    
    import os
    os.remove(file_path)
else:
    st.info("파일을 업로드하면 결과가 표시됩니다.")
