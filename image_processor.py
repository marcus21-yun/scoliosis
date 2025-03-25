import cv2
import numpy as np
from PIL import Image
import io

class ImageProcessor:
    def __init__(self):
        pass

    def process_adams_test(self, image):
        try:
            # 이미지를 OpenCV 형식으로 변환
            if isinstance(image, Image.Image):
                image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 이미지 크기 조정
            height, width = image.shape[:2]
            image = cv2.resize(image, (width, height))
            
            # 이미지 전처리
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 적응형 이진화 적용
            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 노이즈 제거
            kernel = np.ones((3,3), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            # 윤곽선 검출
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 가장 큰 윤곽선 찾기
                max_contour = max(contours, key=cv2.contourArea)
                
                # 윤곽선의 중심선 추출
                epsilon = 0.02 * cv2.arcLength(max_contour, True)
                approx = cv2.approxPolyDP(max_contour, epsilon, True)
                
                # 곡률 계산
                if len(approx) >= 3:
                    return self._calculate_curvature(approx)  # 최대값 제한 제거
            
            return None
        except Exception as e:
            print(f"Error in process_adams_test: {str(e)}")
            return None

    def process_posture(self, image):
        try:
            # 이미지를 OpenCV 형식으로 변환
            if isinstance(image, Image.Image):
                image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # 이미지 크기 조정
            height, width = image.shape[:2]
            image = cv2.resize(image, (width, height))
            
            # 이미지 전처리
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # 적응형 이진화 적용
            binary = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 노이즈 제거
            kernel = np.ones((3,3), np.uint8)
            binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
            
            # 윤곽선 검출
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 가장 큰 윤곽선 찾기
                max_contour = max(contours, key=cv2.contourArea)
                
                # 윤곽선의 경계 상자 계산
                x, y, w, h = cv2.boundingRect(max_contour)
                
                # 이미지를 4개의 영역으로 나누어 분석
                top_left = binary[y:y+h//4, x:x+w//2]
                top_right = binary[y:y+h//4, x+w//2:x+w]
                bottom_left = binary[y+3*h//4:y+h, x:x+w//2]
                bottom_right = binary[y+3*h//4:y+h, x+w//2:x+w]
                
                # 각 영역의 평균값 계산
                shoulder_diff = abs(np.mean(top_left) - np.mean(top_right)) / 255.0
                hip_diff = abs(np.mean(bottom_left) - np.mean(bottom_right)) / 255.0
                
                # 중앙선 분석
                center_line = binary[y:y+h, x+w//2-5:x+w//2+5]
                spine_alignment = np.std(center_line) / 255.0
                
                return {
                    'shoulder_difference': min(shoulder_diff, 1.0),
                    'hip_difference': min(hip_diff, 1.0),
                    'spine_alignment': min(spine_alignment, 1.0)
                }
            
            return None
        except Exception as e:
            print(f"Error in process_posture: {str(e)}")
            return None

    def _calculate_curvature(self, points):
        try:
            if len(points) < 3:
                return 0
            
            # 점들을 정렬 (y 좌표 기준)
            points = sorted(points, key=lambda p: p[0][1])
            
            # 곡률 계산
            angles = []
            max_angle = 0
            
            for i in range(len(points) - 2):
                p1 = points[i][0]
                p2 = points[i + 1][0]
                p3 = points[i + 2][0]
                
                # 두 벡터 계산
                v1 = np.array([p2[0] - p1[0], p2[1] - p1[1]])
                v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]])
                
                # 각도 계산 (라디안에서 도수로 변환)
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
                angle = np.arccos(np.clip(cos_angle, -1.0, 1.0)) * 180 / np.pi
                angles.append(angle)
                max_angle = max(max_angle, angle)
            
            # 최대 각도를 기준으로 곡률 계산 (Cobb 각도와 유사한 방식)
            # 정상: 0-10도, 경도: 10-25도, 중등도: 25-40도, 중증: 40도 이상
            normalized_curvature = max_angle / 40.0  # 40도를 기준으로 정규화
            return normalized_curvature
            
        except Exception as e:
            print(f"Error in _calculate_curvature: {str(e)}")
            return 0 
