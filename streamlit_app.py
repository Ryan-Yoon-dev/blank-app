import streamlit as st
import numpy as np
from scipy.io import wavfile
import soundfile as sf
import matplotlib.pyplot as plt
import pandas as pd

st.title("Audio Requirements Validator")
st.write("업로드된 오디오 파일의 속성을 검증하고, 요구사항과 비교하여 결과를 제공합니다.")

# **파일 요구사항 선택**
st.sidebar.header("파일 요구사항 설정")
required_format = st.sidebar.selectbox("Format", ["WAV", "MP3", "AAC"])
required_channels = st.sidebar.selectbox("Channels", [1, 2])
required_sample_rate = st.sidebar.selectbox("Sample Rate (kHz)", [44.1, 48, 96, 192]) * 1000
required_bit_depth = st.sidebar.selectbox("Bit Depth", [16, 24, 32])
required_noise_floor = st.sidebar.slider("Noise Floor (dB)", min_value=-100, max_value=0, value=-60)
required_stereo_status = st.sidebar.selectbox(
    "Stereo Status", ["Dual Mono", "Mono", "True Stereo", "Joint Stereo"]
)

# 여러 파일 업로드 위젯
uploaded_files = st.file_uploader(
    "오디오 파일을 업로드하세요 (WAV 형식 등 여러 개 가능)", type=["wav", "mp3", "aac"], accept_multiple_files=True
)

if uploaded_files:
    results = []  # 결과 데이터를 저장할 리스트

    for idx, uploaded_file in enumerate(uploaded_files):
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
        noise_floor = calculate_noise_floor(file_path)
        stereo_status = check_stereo_status(file_path)

        # 요구사항과 비교
        matches_format = uploaded_file.name.lower().endswith(required_format.lower())
        matches_channels = properties["Channels"] == required_channels
        matches_sample_rate = properties["Sample Rate"] == required_sample_rate
        matches_bit_depth = properties["Bit Depth"] == required_bit_depth
        matches_noise_floor = noise_floor >= required_noise_floor
        matches_stereo_status = stereo_status == required_stereo_status

        matches_all = all(
            [
                matches_format,
                matches_channels,
                matches_sample_rate,
                matches_bit_depth,
                matches_noise_floor,
                matches_stereo_status,
            ]
        )

        # 결과 저장
        results.append({
            "No.": idx + 1,
            "Filename": uploaded_file.name,
            "Format": required_format if matches_format else f"Mismatch ({uploaded_file.name.split('.')[-1].upper()})",
            "Sample Rate": f"{properties['Sample Rate']} Hz",
            "Bit Depth": properties["Bit Depth"],
            "Channels": properties["Channels"],
            "Stereo Status": stereo_status,
            "Noise Floor (dB)": noise_floor,
            "Duration (seconds)": properties["Duration (seconds)"],
            "Matches Requirements": "O" if matches_all else "X",
        })

        # **미리 듣기**
        st.subheader(f"미리 듣기: {uploaded_file.name}")
        st.audio(uploaded_file)

        # **노이즈 음파 시각화**
        st.subheader(f"음파 및 노이즈 시각화: {uploaded_file.name}")
        samplerate, data = wavfile.read(file_path)

        # 단일 채널(모노) 데이터만 사용 (스테레오의 경우 첫 번째 채널 사용)
        if len(data.shape) > 1:
            data = data[:, 0]

        # 파형 그리기 - 노이즈가 심한 구간을 확인하기 위한 스타일
        fig, ax = plt.subplots(figsize=(10, 4))
        time_axis = np.linspace(0, len(data) / samplerate, num=len(data))
        ax.plot(time_axis, data, color='royalblue', linewidth=0.7)
        ax.axhline(y=required_noise_floor, color='red', linestyle='--', label="Required Noise Floor")
        
        # 시간축을 5초 단위로 설정
        ax.set_xticks(np.arange(0, max(time_axis), step=5))

        ax.set_title("Waveform with Noise Floor")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Amplitude")
        ax.legend()
        st.pyplot(fig)

        # 임시 파일 삭제
        import os
        os.remove(file_path)

    # **결과를 표 형태로 출력**
    st.subheader("파일 검증 결과")
    df_results = pd.DataFrame(results)  # 결과를 DataFrame으로 변환

    # 표 스타일링: 일치 여부에 따라 행 색상 변경
    def highlight_rows(row):
        color = 'background-color: lightgreen;' if row["Matches Requirements"] == "O" else 'background-color: lightcoral;'
        return [color] * len(row)

    styled_df_results = df_results.style.apply(highlight_rows, axis=1).format(precision=2)
    st.table(styled_df_results)

else:
    st.info("파일을 업로드하면 결과가 표시됩니다.")
