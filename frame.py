import cv2
import numpy as np
import os
from PIL import Image

def process_image(input_path, output_path):
    # 이미지 읽기
    image = cv2.imread(input_path)
    if image is None:
        print(f"Error: 이미지를 로드할 수 없습니다: {input_path}")
        return

    # --- 1. 마젠타 사각형 영역 마스크 생성 ---
    # BGR을 HSV로 변환하여 색상 범위로 마젠타 감지
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # 포토샵의 마젠타 (R:255, G:0, B:255)는 HSV에서 H가 300도에 해당. OpenCV에서는 H/2 이므로 150.
    lower_magenta = np.array([145, 50, 50])
    upper_magenta = np.array([155, 255, 255])
    magenta_area_mask = cv2.inRange(hsv, lower_magenta, upper_magenta)

    # --- 2. 배경 검은색 마스크 생성 ---
    # 이미지의 모든 검은색 픽셀 찾기
    lower_black = np.array([0, 0, 0])
    upper_black = np.array([0, 0, 0])
    black_pixels_mask = cv2.inRange(image, lower_black, upper_black)

    # 마젠타 사각형 바깥의 검은색만 '배경'으로 정의
    background_black_mask = cv2.bitwise_and(black_pixels_mask, cv2.bitwise_not(magenta_area_mask))

    # --- 3. 배경 검은색을 제외한 모든 영역 찾기 ---
    # 배경 검은색 마스크를 반전시켜 캐릭터 셀 영역을 얻음
    content_mask = cv2.bitwise_not(background_black_mask)

    # --- 4. 컨투어를 찾아 프레임 그리기 ---
    # 캐릭터 셀 영역의 컨투어 찾기
    contours, _ = cv2.findContours(content_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    output_image = image.copy()
    min_area = 500 # 너무 작은 노이즈 영역은 제외
    padding = 1  # 각 방향으로 1픽셀씩 안으로 줄이기
    for contour in contours:
        if cv2.contourArea(contour) > min_area:
            x, y, w, h = cv2.boundingRect(contour)
            # 축소된 사각형 계산 (각 면에서 padding만큼 안쪽으로)
            new_x = x + padding
            new_y = y + padding
            new_w = w - 2 * padding
            new_h = h - 1 * padding
            # 안전 처리: new_w 또는 new_h가 작아지면 원래 크기를 사용
            if new_w <= 0 or new_h <= 0:
                # 축소 후 유효하지 않으면 원래 바운딩 박스를 그림
                cv2.rectangle(output_image, (x, y), (x + w, y + h), (0, 255, 0), 1)
            else:
                cv2.rectangle(output_image, (new_x, new_y), (new_x + new_w, new_y + new_h), (0, 255, 0), 1)

    # 결과 이미지 저장
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, output_image)
    print(f"처리된 이미지가 저장되었습니다: {output_path}")

def get_frame_list(image_name):
    frame_list = []  # 리스트 초기화
    image = cv2.imread(image_name)
    if image is None:
        print("이미지를 불러올 수 없습니다. 파일 경로를 확인하세요.")
        return

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # 초록색의 HSV 범위 정의
    lower_green = np.array([35, 100, 100])
    upper_green = np.array([85, 255, 255])

    mask = cv2.inRange(hsv, lower_green, upper_green)

    # 윤곽선 찾기
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # 이미지 높이
    img_height = image.shape[0]

    # 찾은 윤곽선을 기반으로 프레임 정보 저장
    for contour in contours:
        # 윤곽선을 감싸는 최소 사각형 계산
        x, y, w, h = cv2.boundingRect(contour)

        # 영역 내에서 세로 초록색 선을 찾아 분할
        region_mask = mask[y:y+h, x:x+w]
        vertical_projection = np.sum(region_mask, axis=0)

        # 높이의 80% 이상이 초록색인 경우 분할선으로 간주
        split_threshold = h * 255 * 0.8
        split_points = [0] + [i for i, val in enumerate(vertical_projection) if val >= split_threshold] + [w]

        # 중복 제거 및 정렬
        split_points = sorted(list(set(split_points)))

        # 분할점을 기준으로 프레임 생성
        for i in range(len(split_points) - 1):
            start_x = split_points[i]
            end_x = split_points[i+1]

            # 분할된 영역의 너비가 5픽셀 이상인 경우에만 추가 (작은 노이즈 제거)
            if end_x - start_x > 5:
                new_w = end_x - start_x
                new_x = x + start_x

                # 좌하단 y좌표 계산
                bottom_left_y = img_height - (y + h)

                # frame_list에 추가
                frame_list.append([new_x, bottom_left_y + 1, new_w, h])
    # y 좌표 기준으로 정렬 (위에서 아래로), 그 다음 x 좌표 기준으로 정렬 (왼쪽에서 오른쪽으로)
    #frame_list.sort(key=lambda frame: (-(frame[1] + frame[3]), frame[0]))
    #return frame_list

    # 정렬 규칙:
    # - 프레임 박스 위치 판단은 '좌하 (left_x, bottom_y)' 좌표를 사용
    # - 화면의 왼쪽-상단 프레임이 인덱스 0, 오른쪽-하단이 마지막이 되도록 정렬
    # 구현 방법:
    # 1) bottom_y(좌하의 y)가 큰 값이 위쪽이므로, bottom_y 내림차순으로 예비 정렬
    # 2) 같은 행으로 간주되는 프레임들은 bottom_y 차이가 작음(row_tolerance)
    # 3) 각 행 내부는 left_x 오름차순 정렬
    if not frame_list:
        return frame_list

    # 1) 예비 정렬: bottom_y 내림차순(위->아래), left_x 오름차순(왼->오)
    frame_list.sort(key=lambda f: (-f[1], f[0]))

    # 2) 행 그룹화 (bottom_y 차이가 작으면 같은 행)
    rows = []
    row_tolerance = 10  # 필요 시 조정
    for f in frame_list:
        left_x, bottom_y, w, h = f
        if not rows:
            rows.append([f])
            continue
        last_row = rows[-1]
        avg_bottom = sum(r[1] for r in last_row) / len(last_row)
        if abs(bottom_y - avg_bottom) <= row_tolerance:
            last_row.append(f)
        else:
            rows.append([f])

    # 3) 각 행 내부 정렬(왼->오) 후 평탄화
    sorted_list = []
    for row in rows:
        row.sort(key=lambda r: r[0])
        sorted_list.extend(row)

    return sorted_list

def change_color(input_path, output_path):
    img = Image.open(input_path).convert('RGBA')

    # 픽셀 데이터 가져오기
    pixels = img.load()

    width, height = img.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            # 마젠타색(255, 0, 255)이거나 검정색(10, 10, 10)으로 변경
            if r == 255 and g == 0 and b == 255:
                pixels[x, y] = (255, 255, 255, 1)
    # 새 파일로 저장
    img.save(output_path)

# 프레임별 번호 매기기
def annotate_frames(input_path: str, output_path: str, start_index: int = 0,
                    font_scale: float = 0.5, padding: int = 2) -> bool:
    """
    input_path의 프레임 리스트를 불러와 각 프레임 좌상단에 번호를 붙여 output_path로 저장.
    반환값: 저장 성공 True, 실패 False
    """
    img = cv2.imread(input_path)
    if img is None:
        print("이미지를 불러올 수 없습니다:", input_path)
        return False

    frames = get_frame_list(input_path)
    if not frames:
        # 프레임이 없으면 원본을 그대로 저장
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cv2.imwrite(output_path, img)
        return True

    h_img = img.shape[0]
    font = cv2.FONT_HERSHEY_SIMPLEX
    thickness = 1

    for idx, (left_x, bottom_y, w, h) in enumerate(frames, start=start_index):
        top_y = int(h_img - (bottom_y + h))
        x = int(left_x)
        y = int(top_y)

        text = str(idx)
        (tw, th) = cv2.getTextSize(text, font, font_scale, thickness)[0]
        tx = x + padding
        ty = y + th + padding

        # 배경 사각형(가독성)
        cv2.rectangle(img, (tx - padding, ty - th - padding), (tx + tw + padding, ty + padding), (0, 0, 0), cv2.FILLED)
        # 텍스트(흰색)
        cv2.putText(img, text, (tx, ty), font, font_scale, (255, 255, 255), thickness, cv2.LINE_AA)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    cv2.imwrite(output_path, img)
    return True


if __name__ == "__main__":
    input_file = "CharacterSpriteSheet_Origin/Neo Geo _ NGCD - The King of Fighters '98 - Fighters - Kim.png"
    output_file = "CharacterSpriteSheet_Modified/Kim_frame_box.png"
    output_file_alpha = "CharacterSpriteSheet_Modified/Kim_frames_alpha1.png"
    change_color(input_file, output_file_alpha)
    process_image(input_file, output_file)
