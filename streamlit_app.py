import streamlit as st
import numpy as np
from scipy.io import wavfile
import soundfile as sf
import matplotlib.pyplot as plt

st.title("Audio Requirements Validator")
st.write("업로드된 오디오 파일의 속성을 검증하고, 재생 및 음파를 표시하는 시스템입니다.")

# 파일 업로드 위젯
uploaded_file = st.file_uploader("오디오 파일을 업로드하세요 (WAV 형식)", type=["wav"])

if uploaded_file is not None:
    # 업로드된 파일 저장
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # 오디오 속성 분석 함수 정의
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
        if len(data.shape) > 1:  # 스테레오 파일인 경우 첫 번째 채널만 사용
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

    # 기본 속성 가져오기
    properties = get_audio_properties(file_path)
    st.subheader("파일 검증 결과")
    for key, value in properties.items():
        st.write(f"**{key}**: {value}")

    # 노이즈 플로어 계산
    noise_floor = calculate_noise_floor(file_path)
    st.write(f"**Noise Floor (dB)**: {noise_floor}")

    # 스테레오 상태 확인
    stereo_status = check_stereo_status(file_path)
    st.write(f"**Stereo Status**: {stereo_status}")

    # **오디오 재생**
    st.subheader("오디오 재생")
    st.audio(uploaded_file)

    # **음파 시각화**
    st.subheader("음파 표시")
    samplerate, data = wavfile.read(file_path)

    # 단일 채널(모노) 데이터만 사용 (스테레오의 경우 첫 번째 채널 사용)
    if len(data.shape) > 1:
        data = data[:, 0]

    # 파형 그리기
    fig, ax = plt.subplots(figsize=(10, 4))
    time_axis = np.linspace(0, len(data) / samplerate, num=len(data))
    ax.plot(time_axis, data, color='blue')
    ax.set_title("Waveform")
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Amplitude")
    st.pyplot(fig)

    # 임시 파일 삭제
    import os
    os.remove(file_path)

else:
    st.info("파일을 업로드하면 결과가 표시됩니다.")
