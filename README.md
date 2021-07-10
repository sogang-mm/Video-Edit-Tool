# Video-Edit-Tool
##### 비디오 변형 도구 

### requirements
* FFMPEG 4.3.1
* requirements.txt
 
### 프로그램 설치 및 실행 방법
- [다운로드](https://github.com/sogang-mm/Video-Edit-Tool/releases)
- 소스 실행
```
git clone https://github.com/sogang-mm/Video-Edit-Tool.git
cd Video-Edit-Tool
pip install -r requirements.txt
python main.py
```

### 사용법

<p align="center">
<img src="https://i.imgur.com/HKRNtxe.jpeg" width="320">
<img src="https://i.imgur.com/f3H1J0U.gif" width="320">
</p>

1. 비디오/디렉토리 선택, 삭제, 초기화
2. 적용할 변형 선택 및 저장/불러오기
3. 단일 비디오/모든 비디오에 변형 적용, ffmpeg 명령어 출력


### Command Line Interface 

```
python transform_videos.py <비디오> <save 디렉토리> <transform.json> <suffix> 
```
##### Windows 
```
transform_videos.exe <비디오> <save 디렉토리> <transform.json> <suffix> 
```