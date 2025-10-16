import cv2
import numpy as np
import os

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

if __name__ == "__main__":
    input_file = "CharacterSpriteSheet_Origin/Neo Geo _ NGCD - The King of Fighters '98 - Fighters - Kim.png"
    output_file = "CharacterSpriteSheet_Modified/Kim_frame_box.png"
    process_image(input_file, output_file)
