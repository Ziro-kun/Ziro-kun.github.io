---
title: "Computer Vision 실습_카드 색깔 분류하기"
description: "Computer Vision 실습기 입니다."
pubDate: "2025-12-18"
tags: ["AI", "Computer Vision", "ROI", "matplotlib", "opencv", "python"]
category: "데이터 & ML"
---

### 도전과제 3: 빨간색과 녹색 마커를 사용하여 다양한 색상의 카드를 만들고, 특정 색상의 카드가 제시될 때마다 컴퓨터가 인식하도록 할 수 있습니까?

힌트: 먼저 제작한 카드의 사진을 몇 장 찍은 다음 간단한 이미지 처리를 사용하여 카드의 색상 패턴을 분석합니다. 필요한 경우 다양한 색상 공간을 탐색합니다. 이 시스템이 조명 조건의 변화에 어떻게 영향을 받는지 살펴보십시오.

---
그러니까.. 학원에 빨간색과 녹색 마카를 가지고 가서 카드를 만든 다음 사진을 찍어서 올리고 이게 빨간 카드냐 파란 카드냐를 판단하게 시키라는거죠...?

![](https://velog.velcdn.com/images/applez/post/132c7b0c-4e9c-42ec-9a31-9f41379e3c2d/image.png)

?????????


---

아무튼 그래서 이걸 어떻게 해결할까 고민하다가 

1️⃣ 구글에서 카드 여러개를 한곳에 모은 이미지를 찾은 다음 
2️⃣ 어제 오늘 배운 ROI, contouring, Mask 등을 활용해서 카드 이미지를 나눈 다음 
3️⃣ RGB 함량(?)을 추출하는 방식으로 접근해보기로 했습니다.

# 1. 이미지 불러오기

제가 사용한 이미지는 아래에 있는 카드 판매 사이트에서 가져왔습니다. 

![](https://velog.velcdn.com/images/applez/post/ea7c470c-1b69-4e17-a36a-1dc3dce9e3ab/image.jpg)

(이미지 출처 : https://www.cheonyu.com/product/view.html?qIDX=47022)

```python
import cv2              # OpenCV 라이브러리 가져오기
import numpy as np      # Numpy 라이브러리 가져오기
import sys
import matplotlib.pyplot as plt # Matplotlib 가져오기

img_bgr = cv2.imread("card.jpg")  # 작업 폴더 기준
if img_bgr is None:
    raise FileNotFoundError("card.jpg를 찾지 못했습니다. 작업 폴더 경로를 확인해주세요.")

img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

plt.figure(figsize=(6,6))
plt.imshow(img_rgb)
plt.title("Original")
plt.axis("off")
plt.show()

print("shape:", img_bgr.shape)  # (H, W, 3)
```
맥북 에어 m4를 구매한 후 작업 환경이 맥북으로 바뀌어서 새로운 습관이 생겼습니다. 외부 소스를 불러왔을때 제대로 작업하고 있는지 확인하기 위해 print를 하거나 .shape을 찍어보는 버릇입니다.

어제부터 OpenCV와 Matplotlib을 활용해서 컴퓨터 비전 기술 기반의 이미지 처리 연습을 해보는 중인데요.

OpenCV는 내부적으로 이미지를 BGR 순서로 처리하는 반면, Matplotlib을 비롯한 대부분의 시각화 도구는 RGB 순서를 전제로 하기 때문에 OpenCV에서 불러온 이미지를 Matplotlib으로 정확히 표시하려면 COLOR_BGR2RGB 변환이 필요합니다.

왜 그런 선택(?)을 했나 찾아봤는데 OpenCV는 성능과 기존 영상 처리 시스템과의 호환성을 이유로 이미지를 BGR 순서로 로딩하고, Matplotlib은 RGB를 표준으로 사용한다고 합니다.
따라서 OpenCV에서 불러온 이미지를 Matplotlib으로 정확히 시각화하기 위해서는 cv2.COLOR_BGR2RGB 변환을 통해 색상 채널 순서를 맞춰주어야 하는거죠.

저는 당연히 RGB가 표준일거라 생각했는데 좀 의외였습니다.

```
shape: (640, 640, 3)
```
640*640에 RGB 3채널짜리 이미지가 로딩되었습니다.

# 2. 이미지 인식시키기

이제 이 이미지를 컴퓨터에게 보여주고(?) 어떤 구조인지 알아내게 하는 작업을 진행해보겠습니다.

```python
img = cv2.imread("card.jpg")
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

H, W, _ = img.shape

rows = 4
cols = 3

card_h = H // rows
card_w = W // cols

rois = []

for r in range(rows):
    for c in range(cols):
        y1 = r * card_h
        y2 = (r + 1) * card_h
        x1 = c * card_w
        x2 = (c + 1) * card_w

        roi = img[y1:y2, x1:x2]
        rois.append((r, c, roi))
```
이를 위해 ROI(Region of Interest, 관심 영역) 기법을 활용할건데요. (투자대비 수익률 아닙니다.) 이미지나 영상 내에서 사용자가 특정 처리를 하거나 분석하고 싶은 중요한 부분을 의미하며, 사각형, 원형 등으로 지정해 해당 영역만 효율적으로 분석하여 시간과 데이터 양을 줄이고 정확도를 높이는 데 사용합니다.

OpenCV 같은 라이브러리에서는 image[y:y+h, x:x+w]와 같이 좌표와 크기를 이용해 관심 영역을 추출하고, 이 영역에 필터링, 객체 검출 등 특정 연산을 적용할 수 있습니다.

지금 이미지에 보이는 흰색 margin을 기준으로 이미지를 분리하고, 카드 하나하나의 좌표(시작부분-끝부분)를 판단하여 12개의 카드를 모두 구분지을 수 있게 해보는 것이라고 일단 저는 그렇게 이해하였습니다. 그 과정을 컴퓨터한테 반복하라고 시킨겁니다.

```python
plt.figure(figsize=(6,8))
for i, (r, c, roi) in enumerate(rois, 1):
    plt.subplot(4, 3, i)
    plt.imshow(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
    plt.axis("off")
    plt.title(f"{i}")
plt.tight_layout()
plt.show()
```
그 작업이 끝나면 분류한 카드 위에 카드번호를 타이틀로 달아서 총 12개의 카드에 넘버링을 하라고 지시하였습니다. 이미지를 출력해보니 다음과 같이 나오는 것을 확인하였습니다.

![](https://velog.velcdn.com/images/applez/post/4244cf68-f85a-486b-a65f-92c91478d188/image.png)

뭔가 좀 엉성하긴 한데 생각보다 훌륭하게 알아서 잘 구분을 지었네요.

# 3. 색깔 비율 판별하기

이제 각 카드 ROI에서 RGB가 아닌 HSV 기반으로 “빨강/초록 비율”로 카드 색 판단을 시켜볼겁니다. 참고로 빨강은 HSV에서 2구간(0~10, 170~180) 입니다.
```python
def red_green_ratio(roi_bgr):
    hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)

    lower_g = np.array([35, 50, 50])
    upper_g = np.array([85, 255, 255])
    mask_g = cv2.inRange(hsv, lower_g, upper_g)

    lower_r1 = np.array([0, 70, 50])
    upper_r1 = np.array([10, 255, 255])
    lower_r2 = np.array([170, 70, 50])
    upper_r2 = np.array([180, 255, 255])
    mask_r = cv2.inRange(hsv, lower_r1, upper_r1) | \
             cv2.inRange(hsv, lower_r2, upper_r2)

    total = roi_bgr.shape[0] * roi_bgr.shape[1]
    return cv2.countNonZero(mask_r)/total, cv2.countNonZero(mask_g)/total
 ```
 색 비율을 잘 판단했는지 결과를 보겠습니다.
 
 ```python
 for i, (r, c, roi) in enumerate(rois, 1):
    r_ratio, g_ratio = red_green_ratio(roi)
    print(f"Card {i:02d} | R:{r_ratio:.2f}, G:{g_ratio:.2f}")
```
아마 출력형식은 카드 + 카드숫자 | 빨강비율, 초록비율 로 나올겁니다.
```
Card 01 | R:0.42, G:0.02
Card 02 | R:0.11, G:0.44
Card 03 | R:0.66, G:0.00
Card 04 | R:0.12, G:0.42
Card 05 | R:0.57, G:0.03
Card 06 | R:0.17, G:0.34
Card 07 | R:0.58, G:0.00
Card 08 | R:0.14, G:0.42
Card 09 | R:0.45, G:0.03
Card 10 | R:0.11, G:0.47
Card 11 | R:0.47, G:0.12
Card 12 | R:0.19, G:0.33
```
어떤가요? 컴퓨터가 잘 인식한 것 같나요? 저는 나름 나쁘지 않다고 생각했습니다. 여기에 새로운 이미지를 불러와서 같은 포멧으로 만드는 과정을 거친 다음 판단하게 하는 과정이라든지, 웹캠으로 카드 이미지를 들면 캡쳐해서 포멧팅 한 다음 판별하게 하는 과정을 추가하고 싶었으나, 아직 수련이 부족하여 이 정도로 마무리하였습니다.

컴퓨터 비전 매우 재밌군요. 아직 제가 손코딩을 직접 하기엔 무리가 있지만 바이브코딩으로 개념 익히고 코드 하나하나 뜯어보는 맛이 있습니다. 이제 본격적인 딥러닝 객체탐지로 넘어가면 비명을 지르게 될지도 모르지만 기대가 됩니다.
