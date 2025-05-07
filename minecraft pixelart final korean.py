from PIL import Image, ImageTk  # 이미지 처리 및 Tkinter에서 이미지 표시용 라이브러리 임포트
import tkinter as tk  # GUI 생성용 Tkinter 임포트
from tkinter import filedialog, messagebox, colorchooser  # 파일 선택 대화상자, 메시지 박스, 색상 선택기 임포트
import os  # 운영체제 관련 기능 임포트(경로 처리 등)
import numpy as np  # 배열 및 수치 계산용 넘파이 임포트
from scipy.spatial import KDTree  # 색상 근접 탐색을 위한 KD트리 자료구조 임포트
import mcschematic  # 마인크래프트 스케마틱 파일 생성용 라이브러리 임포트
try:
    import picamera  # Raspberry Pi 카메라 제어용 라이브러리
except ImportError:
    class MockPiCamera:
        def __init__(self):
            pass
        def start_preview(self):
            pass
        def stop_preview(self):
            pass
        def capture(self, output):
            with open(output, 'wb') as f:
                f.write(b"Mock image data")
        def close(self):
            pass
    picamera = MockPiCamera
import time  # 시간 지연용
import tempfile  # 임시 파일 생성용

# 마인크래프트 기본 색상 팔레트 (RGB 튜플 리스트)
base_colors = [
    (9999, 9999, 9999), (127, 178, 56), (247, 233, 163), (199, 199, 199), (255, 0, 0),
    (160, 160, 255), (167, 167, 167), (0, 124, 0), (255, 255, 255), (164, 168, 184),
    (151, 109, 77), (112, 112, 112), (64, 64, 255), (143, 119, 72), (255, 252, 245),
    (216, 127, 51), (178, 76, 216), (102, 153, 216), (229, 229, 51), (127, 204, 25),
    (242, 127, 165), (76, 76, 76), (153, 153, 153), (76, 127, 153), (127, 63, 178),
    (51, 76, 178), (102, 76, 51), (102, 127, 51), (153, 51, 51), (25, 25, 25),
    (250, 238, 77), (92, 219, 213), (74, 128, 255), (0, 217, 58), (129, 86, 49),
    (112, 2, 0), (209, 177, 161), (159, 82, 36), (149, 87, 108), (112, 108, 138),
    (186, 133, 36), (103, 117, 53), (160, 77, 78), (57, 41, 35), (135, 107, 98),
    (87, 92, 92), (122, 73, 88), (76, 62, 92), (76, 50, 35), (76, 82, 42),
    (142, 60, 46), (37, 22, 16), (189, 48, 49), (148, 63, 97), (92, 25, 29),
    (22, 126, 134), (58, 142, 140), (86, 44, 62), (20, 180, 133), (100, 100, 100),
    (216, 175, 147), (127, 167, 150),
    # 새로 추가한 라이트 핑크 색상들
    (255, 182, 193),  # 라이트 핑크
    (255, 192, 203),  # 핑크
    (255, 209, 220),  # 베이비 핑크
    (255, 223, 229)   # 페일 핑크
]

# 확장된 색상 팔레트 (음영 포함 등 더 많은 색상 포함)
extended_colors = [(9999, 9999, 9999)]*4 + [
    (89, 125, 39), (109, 153, 48), (127, 178, 56), (67, 94, 29), (174, 164, 115),
    (213, 201, 140), (247, 233, 163), (130, 123, 86), (140, 140, 140), (171, 171, 171),
    (199, 199, 199), (105, 105, 105), (180, 0, 0), (220, 0, 0), (255, 0, 0), (135, 0, 0),
    (112, 112, 180), (138, 138, 220), (160, 160, 255), (84, 84, 135), (117, 117, 117),
    (144, 144, 144), (167, 167, 167), (88, 88, 88), (0, 87, 0), (0, 106, 0), (0, 124, 0),
    (0, 65, 0), (180, 180, 180), (220, 220, 220), (255, 255, 255), (135, 135, 135),
    (115, 118, 129), (141, 144, 158), (164, 168, 184), (86, 88, 97), (106, 76, 54),
    (130, 94, 66), (151, 109, 77), (79, 57, 40), (79, 79, 79), (96, 96, 96), (112, 112, 112),
    (59, 59, 59), (45, 45, 180), (55, 55, 220), (64, 64, 255), (33, 33, 135), (100, 84, 50),
    (123, 102, 62), (143, 119, 72), (75, 63, 38), (180, 177, 172), (220, 217, 211),
    (255, 252, 245), (135, 133, 129), (152, 89, 36), (186, 109, 44), (216, 127, 51),
    (114, 67, 27), (125, 53, 152), (153, 65, 186), (178, 76, 216), (94, 40, 114),
    (72, 108, 152), (88, 132, 186), (102, 153, 216), (54, 81, 114), (161, 161, 36),
    (197, 197, 44), (229, 229, 51), (121, 121, 27), (89, 144, 17), (109, 176, 21),
    (127, 204, 25), (67, 108, 13), (170, 89, 116), (208, 109, 142), (242, 127, 165),
    (128, 67, 87), (53, 53, 53), (65, 65, 65), (76, 76, 76), (40, 40, 40), (108, 108, 108),
    (132, 132, 132), (153, 153, 153), (81, 81, 81), (53, 89, 108), (65, 109, 132),
    (76, 127, 153), (40, 67, 81), (89, 44, 125), (109, 54, 153), (127, 63, 178), (67, 33, 94),
    (36, 53, 125), (44, 65, 153), (51, 76, 178), (27, 40, 94), (72, 53, 36), (88, 65, 44),
    (102, 76, 51), (54, 40, 27), (72, 89, 36), (88, 109, 44), (102, 127, 51), (54, 67, 27),
    (108, 36, 36), (132, 44, 44), (153, 51, 51), (81, 27, 27), (17, 17, 17), (21, 21, 21),
    (25, 25, 25), (13, 13, 13), (176, 168, 54), (215, 205, 66), (250, 238, 77), (132, 126, 40),
    (64, 154, 150), (79, 188, 183), (92, 219, 213), (48, 115, 112), (52, 90, 180),
    (63, 110, 220), (74, 128, 255), (39, 67, 135), (0, 153, 40), (0, 187, 50), (0, 217, 58),
    (0, 114, 30), (91, 60, 34), (111, 74, 42), (129, 86, 49), (68, 45, 25), (79, 1, 0),
    (96, 1, 0), (112, 2, 0), (59, 1, 0), (147, 124, 113), (180, 152, 138), (209, 177, 161),
    (110, 93, 85), (112, 57, 25), (137, 70, 31), (159, 82, 36), (84, 43, 19), (105, 61, 76),
    (128, 75, 93), (149, 87, 108), (78, 46, 57), (79, 76, 97), (96, 93, 119), (112, 108, 138),
    (59, 57, 73), (131, 93, 25), (160, 114, 31), (186, 133, 36), (98, 70, 19), (72, 82, 37),
    (88, 100, 45), (103, 117, 53), (54, 61, 28), (112, 54, 55), (138, 66, 67), (160, 77, 78),
    (84, 40, 41), (40, 28, 24), (49, 35, 30), (57, 41, 35), (30, 21, 18), (95, 75, 69),
    (116, 92, 84), (135, 107, 98), (71, 56, 51), (61, 64, 64), (75, 79, 79), (87, 92, 92),
    (46, 48, 48), (86, 51, 62), (105, 62, 75), (122, 73, 88), (64, 38, 46), (53, 43, 64),
    (65, 53, 79), (76, 62, 92), (40, 32, 48), (53, 35, 24), (65, 43, 30), (76, 50, 35),
    (40, 26, 18), (53, 57, 29), (65, 70, 36), (76, 82, 42), (40, 43, 22), (100, 42, 32),
    (122, 51, 39), (142, 60, 46), (75, 31, 24), (26, 15, 11), (31, 18, 13), (37, 22, 16),
    (19, 11, 8), (133, 33, 34), (163, 41, 42), (189, 48, 49), (100, 25, 25), (104, 44, 68),
    (127, 54, 83), (148, 63, 97), (78, 33, 51), (64, 17, 20), (79, 21, 25), (92, 25, 29),
    (48, 13, 15), (15, 88, 94), (18, 108, 115), (22, 126, 134), (11, 66, 70), (40, 100, 98),
    (50, 122, 120), (58, 142, 140), (30, 75, 74), (60, 31, 43), (74, 37, 53), (86, 44, 62),
    (45, 23, 32), (14, 127, 93), (17, 155, 114), (20, 180, 133), (10, 95, 70), (70, 70, 70),
    (86, 86, 86), (100, 100, 100), (52, 52, 52), (152, 123, 103), (186, 150, 126),
    (216, 175, 147), (114, 92, 77), (89, 117, 105), (109, 144, 129), (127, 167, 150),
    (67, 88, 79),
    # 새로 추가한 라이트 핑크 색상들
    (255, 182, 193),  # 라이트 핑크
    (255, 192, 203),  # 핑크
    (255, 209, 220),  # 베이비 핑크
    (255, 223, 229)   # 페일 핑크
]

# 블록 인덱스와 마인크래프트 블록 ID 문자열 매핑 함수
def get_block_mapping():
    return {
        0: "minecraft:air",  # 공기 블록
        1: "minecraft:grass_block",  # 잔디 블록
        2: "minecraft:sand",  # 모래 블록
        3: "minecraft:white_wool",  # 흰색 양털
        4: "minecraft:tnt",  # TNT 블록
        5: "minecraft:ice",  # 얼음 블록
        6: "minecraft:iron_block",  # 철 블록
        7: "minecraft:oak_leaves",  # 참나무 잎
        8: "minecraft:snow_block",  # 눈 블록
        9: "minecraft:clay",  # 점토 블록
        10: "minecraft:dirt",  # 흙 블록
        11: "minecraft:stone",  # 돌 블록
        12: "minecraft:water",  # 물 블록
        13: "minecraft:oak_planks",  # 참나무 판자
        14: "minecraft:quartz_block",  # 석영 블록
        15: "minecraft:orange_terracotta",  # 주황색 테라코타
        16: "minecraft:magenta_wool",  # 마젠타 양털
        17: "minecraft:light_blue_wool",  # 연한 파랑 양털
        18: "minecraft:yellow_wool",  # 노랑 양털
        19: "minecraft:lime_wool",  # 라임 양털
        20: "minecraft:pink_wool",  # 분홍 양털
        21: "minecraft:gray_wool",  # 회색 양털
        22: "minecraft:light_gray_wool",  # 연한 회색 양털
        23: "minecraft:cyan_wool",  # 청록 양털
        24: "minecraft:purple_wool",  # 보라 양털
        25: "minecraft:blue_wool",  # 파랑 양털
        26: "minecraft:brown_wool",  # 갈색 양털
        27: "minecraft:green_wool",  # 초록 양털
        28: "minecraft:red_wool",  # 빨강 양털
        29: "minecraft:black_wool",  # 검정 양털
        30: "minecraft:gold_block",  # 금 블록
        31: "minecraft:diamond_block",  # 다이아몬드 블록
        32: "minecraft:lapis_block",  # 청금석 블록
        33: "minecraft:emerald_block",  # 에메랄드 블록
        34: "minecraft:podzol",  # 포졸 블록
        35: "minecraft:netherrack",  # 네더락
        36: "minecraft:white_terracotta",  # 흰색 테라코타
        37: "minecraft:orange_terracotta",  # 주황 테라코타
        38: "minecraft:magenta_terracotta",  # 마젠타 테라코타
        39: "minecraft:light_blue_terracotta",  # 연한 파랑 테라코타
        40: "minecraft:yellow_terracotta",  # 노랑 테라코타
        41: "minecraft:lime_terracotta",  # 라임 테라코타
        42: "minecraft:pink_terracotta",  # 분홍 테라코타
        43: "minecraft:gray_terracotta",  # 회색 테라코타
        44: "minecraft:light_gray_terracotta",  # 연한 회색 테라코타
        45: "minecraft:cyan_terracotta",  # 청록 테라코타
        46: "minecraft:purple_terracotta",  # 보라 테라코타
        47: "minecraft:blue_terracotta",  # 파랑 테라코타
        48: "minecraft:brown_terracotta",  # 갈색 테라코타
        49: "minecraft:green_terracotta",  # 초록 테라코타
        50: "minecraft:red_terracotta",  # 빨강 테라코타
        51: "minecraft:black_terracotta",  # 검정 테라코타
        52: "minecraft:crimson_nylium",  # 크림슨 나일리움
        53: "minecraft:crimson_stem",  # 크림슨 줄기
        54: "minecraft:crimson_hyphae",  # 크림슨 히파이
        55: "minecraft:warped_nylium",  # 왜곡된 나일리움
        56: "minecraft:warped_stem",  # 왜곡된 줄기
        57: "minecraft:warped_hyphae",  # 왜곡된 히파이
        58: "minecraft:warped_wart_block",  # 왜곡된 워트 블록
        59: "minecraft:deepslate",  # 딥슬레이트
        60: "minecraft:raw_iron_block",  # 원석 철 블록
        61: "minecraft:glow_lichen",  # 빛나는 이끼
        # 새로 추가한 라이트 핑크 색상에 대한 블록 매핑
        62: "minecraft:pink_concrete",  # 라이트 핑크 - 핑크 콘크리트
        63: "minecraft:pink_concrete",  # 핑크 - 핑크 콘크리트
        64: "minecraft:pink_concrete",  # 베이비 핑크 - 핑크 콘크리트
        65: "minecraft:pink_concrete",  # 페일 핑크 - 핑크 콘크리트
    }

# 색상 인덱스 행렬을 받아 마인크래프트 스케마틱 파일(.litematic) 생성 함수
def create_schematic_from_idx_matrix(idx_matrix, output_path, schem_name):
    height = len(idx_matrix)  # 행렬 세로 크기(이미지 높이)
    width = len(idx_matrix[0]) if height > 0 else 0  # 행렬 가로 크기(이미지 너비)

    schem = mcschematic.MCSchematic()  # 새 스케마틱 객체 생성
    block_mapping = get_block_mapping()  # 블록 인덱스-아이디 매핑 딕셔너리 호출

    for y in range(height):  # 세로 방향 순회
        for x in range(width):  # 가로 방향 순회
            idx = idx_matrix[y][x]  # 현재 위치 색상 인덱스
            if idx in block_mapping:  # 매핑된 블록이 있으면
                block_id = block_mapping[idx]  # 블록 아이디 얻기
                schem.setBlock((x, 0, y), block_id)  # 스케마틱에 블록 배치 (y축은 0층)

    output_dir = os.path.dirname(output_path)  # 출력 경로 폴더
    schem.save(  # 스케마틱 파일 저장
        output_dir,
        schem_name,
        mcschematic.Version.JE_1_12_1  # 마인크래프트 1.12.1 버전 포맷 지정
    )
    return os.path.join(output_dir, f"{schem_name}.litematic")  # 저장된 파일 경로 반환

# GUI 애플리케이션 클래스 정의
class App:
    def __init__(self, root):
        self.root = root  # 루트 윈도우 저장
        self.file_path = ''  # 선택된 이미지 파일 경로 초기화

        # 파일 업로드 영역 프레임 생성 및 배치
        self.frame = tk.LabelFrame(self.root, padx=10, pady=10)
        self.frame.pack(padx=10, pady=10, fill="x")

        # 파일 선택 버튼 생성 및 클릭 시 upload_file 함수 호출
        self.file_btn = tk.Button(self.frame, text="파일 탐색...", command=self.upload_file)
        self.file_btn.pack(side="left")

        # 카메라 촬영 버튼 생성 및 클릭 시 capture_from_camera 함수 호출
        self.capture_btn = tk.Button(self.frame, text="카메라 촬영", command=self.capture_from_camera)
        self.capture_btn.pack(side="left", padx=10)

        # 선택된 파일 이름 표시 라벨 생성 및 배치
        self.file_label = tk.Label(self.frame, text="")
        self.file_label.pack(side="left", padx=10)

        # 이미지 미리보기 라벨 (초기 상태는 '선택된 이미지 없음')
        self.preview_image_label = tk.Label(self.frame, text="선택된 이미지 없음")
        self.preview_image_label.pack(side="left", padx=10)

        # 원본 이미지 크기 저장용 변수 초기화
        self.width = 0
        self.height = 1

        # 해상도 입력값을 저장할 StringVar 변수 생성
        self.var_res_width = tk.StringVar()
        self.var_res_height = tk.StringVar()

        # 해상도 입력창 프레임 생성
        self.resolution_frame = tk.Frame(root)

        # 해상도 레이블 생성 및 배치
        self.resolution_label = tk.Label(self.resolution_frame, text="해상도", font=("Arial", 13))
        self.resolution_label.pack(fill='both')

        # 너비 입력창 생성 및 배치
        self.resolution_w_entry = tk.Entry(self.resolution_frame, textvariable=self.var_res_width,
                                           width=6, font=("Arial", 13), justify='right')
        self.resolution_w_entry.pack(side='left')

        # 곱셈 기호 레이블 생성 및 배치
        self.resolution_x = tk.Label(self.resolution_frame, text="×", font=("Arial", 13))
        self.resolution_x.pack(side='left')

        # 높이 입력창 생성 및 배치
        self.resolution_h_entry = tk.Entry(self.resolution_frame, textvariable=self.var_res_height,
                                           width=6, font=("Arial", 13), justify='right')
        self.resolution_h_entry.pack(side='left')

        # 너비 입력창 포커스 아웃 시 높이 자동 계산 함수 연결
        self.resolution_w_entry.bind("<FocusOut>", self.update_height)
        # 엔터 입력 시 포커스 해제 함수 연결
        self.resolution_w_entry.bind("<Return>", self.unfocus)
        self.resolution_h_entry.bind("<FocusOut>", self.update_width)
        self.resolution_h_entry.bind("<Return>", self.unfocus)

        # 해상도 프레임 배치
        self.resolution_frame.pack(pady=10)

        # 옵션 프레임 생성 및 배치
        option_frame = tk.Frame(root)
        option_frame.pack(pady=10, anchor="w", padx=20)

        # 옵션 제목 라벨 생성
        tk.Label(option_frame, text="옵션").pack(anchor='w')

        # 옵션 변수 생성 및 초기값 설정
        self.var_maintain_aspect_ratio = tk.BooleanVar(value=True)  # 비율 유지 여부
        self.var_crop = tk.BooleanVar()  # 자르기 옵션 여부
        self.var_transparent_fill = tk.BooleanVar()  # 투명 픽셀 색상 채우기 여부
        self.selected_color = "#ffffff"  # 투명 픽셀 채우기 기본 색상(흰색)
        self.var_shade = tk.BooleanVar()  # 음영 포함 여부

        # 비율 유지 체크박스 생성 및 상태 변경 함수 연결
        self.cb0 = tk.Checkbutton(option_frame, text="비율 유지",
                                  variable=self.var_maintain_aspect_ratio,
                                  command=self.cb0_update_state)
        self.cb0.pack(anchor='w')

        # 비율 다를 경우 자르기 체크박스 생성, 초기 비활성화
        self.cb1 = tk.Checkbutton(option_frame, state='disabled',
                                  text="비율이 다를 경우 잘라내기",
                                  variable=self.var_crop)
        self.cb1.pack(anchor='w')

        # 투명 픽셀 색상 채우기 체크박스 및 색상 선택 버튼 프레임 생성
        self.cb2_frame = tk.Frame(option_frame)

        # 투명 픽셀 색상 채우기 체크박스 생성 및 상태 변경 함수 연결
        self.cb2 = tk.Checkbutton(self.cb2_frame, text="투명 픽셀을 다음 색상으로 채움",
                                  variable=self.var_transparent_fill,
                                  command=self.cb2_update_state)
        self.cb2.pack(anchor='w', side='left')

        # 색상 선택 버튼 생성, 초기 비활성화, 클릭 시 색상 선택 함수 호출
        self.color_picker = tk.Button(self.cb2_frame, state='disabled',
                                      text="색 선택...", bg=self.selected_color,
                                      command=self.choose_color)
        self.color_picker.pack(anchor='w', side='left')
        self.cb2_frame.pack()

        # 음영 포함 체크박스 생성
        self.cb3 = tk.Checkbutton(option_frame, text="음영 포함",
                                  variable=self.var_shade)
        self.cb3.pack(anchor='w')

        # 실행 버튼 생성 및 클릭 시 go_action 함수 호출
        go_btn = tk.Button(root, text="GO", font=("Arial", 16, "bold"),
                           command=self.go_action)
        go_btn.pack(pady=10)

    # 엔터 입력 시 포커스 해제 함수
    def unfocus(self, event):
        event.widget.master.focus_set()

    # 너비 입력 변경 시 높이 자동 계산 (비율 유지 시)
    def update_height(self, *args):
        if self.var_maintain_aspect_ratio.get():
            aspect_ratio = self.width / self.height  # 원본 이미지 비율
            try:
                width = float(self.var_res_width.get())  # 입력된 너비 값
                height = int(round(width / aspect_ratio, 0))  # 비율에 맞게 높이 계산
                self.var_res_height.set(f"{height}")  # 높이 입력창에 자동 설정
            except ValueError:
                pass  # 숫자 변환 실패 시 무시

    # 높이 입력 변경 시 너비 자동 계산 (비율 유지 시)
    def update_width(self, *args):
        if self.var_maintain_aspect_ratio.get():
            aspect_ratio = self.width / self.height
            try:
                height = float(self.var_res_height.get())
                width = int(round(height * aspect_ratio, 0))
                self.var_res_width.set(f"{width}")
            except ValueError:
                pass

    # 비율 유지 체크박스 상태 변경 시 자르기 옵션 활성화/비활성화 조절
    def cb0_update_state(self):
        if self.var_maintain_aspect_ratio.get():
            self.var_crop.set(False)  # 비율 유지 시 자르기 옵션 해제
            self.cb1.config(state='disabled')  # 자르기 체크박스 비활성화
            self.update_height()  # 높이 자동 업데이트
        else:
            self.cb1.config(state='normal')  # 비율 유지 해제 시 자르기 활성화

    # 투명 픽셀 채우기 체크박스 상태 변경 시 색상 선택 버튼 활성화/비활성화 조절
    def cb2_update_state(self):
        if self.var_transparent_fill.get():
            self.color_picker.config(state='normal')  # 체크 시 색상 선택 버튼 활성화
        else:
            self.color_picker.config(state='disabled')  # 체크 해제 시 비활성화

    # 색상 선택기 실행 및 선택된 색상 저장, 버튼 배경색과 글자색 변경
    def choose_color(self):
        color_code = colorchooser.askcolor(title="색상 선택")
        if color_code[1]:
            self.selected_color = color_code[1]  # 선택된 색상(16진수)
            hex_color = self.selected_color.lstrip('#')
            r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]  # RGB 값 추출
            brightness = (r*299 + g*587 + b*114) / 1000  # 밝기 계산(가중 평균)
            # 밝기에 따라 글자색 흰색 또는 검정색으로 설정
            self.color_picker.config(fg='white' if brightness < 128 else 'black',
                                    bg=self.selected_color)

    # 파일 탐색기 열어 이미지 파일 선택, 선택 시 정보 표시 및 미리보기 생성
    def upload_file(self):
        self.file_path = filedialog.askopenfilename(
            title="이미지 파일 선택",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All Files", "*.*")]
        )
        if self.file_path:
            self.file_label.config(text=os.path.basename(self.file_path))  # 파일명 표시
            img = Image.open(self.file_path)  # 이미지 열기
            self.width, self.height = img.size  # 원본 이미지 크기 저장
            # 미리보기용 이미지 크기 조절 (최대 50픽셀 크기 유지)
            preview_size = (
                int(self.width / max(self.width, self.height) * 50),
                int(self.height / max(self.width, self.height) * 50)
            )
            img = img.resize(preview_size, Image.Resampling.LANCZOS)  # 고품질 리사이징
            img_tk = ImageTk.PhotoImage(img)  # Tkinter용 이미지 변환
            # 해상도 입력창에 원본 이미지 크기 자동 입력
            self.resolution_w_entry.delete(0, tk.END)
            self.resolution_w_entry.insert(0, self.width)
            self.resolution_h_entry.delete(0, tk.END)
            self.resolution_h_entry.insert(0, self.height)
            # 미리보기 라벨에 이미지 표시
            self.preview_image_label.config(text='', image=img_tk)
            self.preview_image_label.image = img_tk  # 참조 유지

    # Raspberry Pi 카메라로부터 사진 촬영하여 로드하는 함수
    def capture_from_camera(self):
        try:
            # 임시 파일 생성
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
                temp_filename = tmpfile.name

            camera = picamera.PiCamera()
            camera.resolution = (1024, 768)  # 필요에 따라 해상도 조절 가능
            camera.start_preview()
            time.sleep(2)  # 카메라 워밍업 시간
            camera.capture(temp_filename)
            camera.stop_preview()
            camera.close()

            # 촬영한 이미지를 파일 경로로 설정하고 GUI에 로드
            self.file_path = temp_filename
            self.file_label.config(text=os.path.basename(self.file_path))
            img = Image.open(self.file_path)
            self.width, self.height = img.size

            # 미리보기용 이미지 크기 조절 (최대 50픽셀 크기 유지)
            preview_size = (
                int(self.width / max(self.width, self.height) * 50),
                int(self.height / max(self.width, self.height) * 50)
            )
            img = img.resize(preview_size, Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            # 해상도 입력창에 원본 이미지 크기 자동 입력
            self.resolution_w_entry.delete(0, tk.END)
            self.resolution_w_entry.insert(0, self.width)
            self.resolution_h_entry.delete(0, tk.END)
            self.resolution_h_entry.insert(0, self.height)

            # 미리보기 라벨에 이미지 표시
            self.preview_image_label.config(text='', image=img_tk)
            self.preview_image_label.image = img_tk

        except Exception as e:
            messagebox.showerror("오류", f"카메라 촬영 중 오류 발생: {str(e)}")

    # GO 버튼 클릭 시 실행되는 메인 처리 함수
    def go_action(self):
        if not self.file_path:
            messagebox.showerror("오류", "이미지 파일을 먼저 선택하거나 촬영해주세요.")
            return

        file_name, file_ext = os.path.splitext(os.path.basename(self.file_path))  # 파일명과 확장자 분리
        try:
            w = int(self.var_res_width.get())  # 입력된 너비
            h = int(self.var_res_height.get())  # 입력된 높이
        except ValueError:
            messagebox.showerror("오류", "유효한 해상도 값을 입력해주세요.")
            return

        # 사용자에게 PNG 저장 위치 및 이름 선택 대화상자 표시
        output_file_path = filedialog.asksaveasfilename(
            initialfile=f"{file_name}_{w}x{h}_minecraftmap{'_noshade' if not self.var_shade.get() else ''}.png",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All Files", "*.*")],
            title="변환된 이미지 저장 위치 선택"
        )
        if not output_file_path:
            # 사용자가 저장 대화상자를 취소한 경우 처리 중단
            return

        # 스케마틱 파일명은 PNG 파일명과 동일한 폴더에 저장
        output_folder = os.path.dirname(output_file_path)
        schematic_name = f"{file_name}_{w}x{h}_pixelart"

        try:
            img = Image.open(self.file_path)  # 원본 이미지 열기
            if img.mode != 'RGBA':
                img = img.convert('RGBA')  # 투명도 처리를 위해 RGBA 모드로 변환

            # 이미지 리사이징 처리 (비율 유지 및 자르기 옵션 적용)
            if self.var_crop.get():
                width_ratio = w / self.width
                height_ratio = h / self.height
                aspect_ratio = self.width / self.height
                if width_ratio > height_ratio:
                    temp_h = int(round(w / aspect_ratio))
                    img_resized = img.resize((w, temp_h), Image.Resampling.NEAREST)
                    top = (temp_h - h) // 2
                    img_resized = img_resized.crop((0, top, w, top + h))  # 중앙 세로 자르기
                else:
                    temp_w = int(round(h * aspect_ratio))
                    img_resized = img.resize((temp_w, h), Image.Resampling.NEAREST)
                    left = (temp_w - w) // 2
                    img_resized = img_resized.crop((left, 0, left + w, h))  # 중앙 가로 자르기
            else:
                img_resized = img.resize((w, h), Image.Resampling.NEAREST)  # 단순 리사이즈

            # 투명 픽셀을 선택된 색상으로 채우기 옵션 처리
            if self.var_transparent_fill.get():
                background = Image.new('RGBA', (w, h), self.selected_color)  # 배경색 생성
                img_resized = Image.alpha_composite(background, img_resized)  # 알파 합성

            # 이미지 픽셀 색상을 마인크래프트 팔레트 색상 인덱스로 변환
            rgba_pixels = list(img_resized.getdata())  # 픽셀 데이터 리스트
            palette = extended_colors if self.var_shade.get() else base_colors  # 팔레트 선택
            tree = KDTree(np.array(palette))  # 팔레트 색상 KD트리 생성

            idx_array = []
            for r, g, b, a in rgba_pixels:
                if a == 0:  # 완전 투명 픽셀은 인덱스 0 (공기)
                    idx_array.append(0)
                else:
                    _, idx = tree.query((r, g, b))  # 가장 가까운 팔레트 색상 인덱스 찾기
                    idx_array.append(int(idx))

            # 1차원 인덱스 배열을 2차원 행렬로 변환 (이미지 크기 기준)
            idx_matrix = [idx_array[i*w:(i+1)*w] for i in range(h)]

            # 변환된 색상 인덱스 행렬을 기반으로 출력 이미지 생성 및 저장
            rgba_image = np.zeros((h, w, 4), dtype=np.uint8)  # RGBA 배열 초기화
            mask = np.array(idx_matrix) != 0  # 공기 블록 제외 마스크
            rgba_image[mask, :3] = np.array(palette)[np.array(idx_matrix)[mask]]  # 팔레트 색상 적용
            rgba_image[mask, 3] = 255  # 불투명 처리
            Image.fromarray(rgba_image, 'RGBA').save(output_file_path)  # PNG 저장

            # 마인크래프트 스케마틱 파일 생성
            schematic_path = create_schematic_from_idx_matrix(
                idx_matrix,
                output_file_path,
                schematic_name
            )

            # 성공 메시지 출력 (변환된 이미지 및 스케마틱 경로 안내)
            messagebox.showinfo("성공",
                                f"변환 완료!\n"
                                f"이미지: {os.path.abspath(output_file_path)}\n"
                                f"스케마틱: {os.path.abspath(schematic_path)}"
                                )

        except Exception as e:
            messagebox.showerror("오류", f"처리 중 오류 발생: {str(e)}")


# 프로그램 진입점 - GUI 실행
if __name__ == "__main__":
    root = tk.Tk()  # Tkinter 루트 윈도우 생성
    root.title("Minecraft 픽셀아트 변환기")  # 창 제목 설정
    root.geometry("500x600")  # 창 크기 설정
    root.bind_all("<Button-1>", lambda event: event.widget.focus_set())  # 클릭 시 포커스 설정
    app = App(root)  # App 클래스 인스턴스 생성 및 GUI 초기화
    root.mainloop()  # 이벤트 루프 시작
