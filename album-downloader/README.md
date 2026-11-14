# album-downloader

가수 이름을 입력하면 YouTube Music에서 앨범 목록을 찾고, 앨범별 폴더로 오디오를 내려받는 CLI입니다.

## 안드로이드(Termux)에서 한 번에 설정

Termux를 처음 설치한 상태에서 아래 세 줄만 실행하면 됩니다.

```bash
pkg install -y git
git clone https://github.com/joshua-sungeun-kim/joshua.kim.github.io.git
bash joshua.kim.github.io/album-downloader/termux-setup.sh
```

중간에 저장소 접근 권한 팝업이 뜨면 **허용**을 누르세요. 끝나면 어디서든 이렇게 쓰면 됩니다.

```bash
album "가수 이름"           # 목록을 보고 번호로 골라서 받기
album "가수 이름" --all     # 전부 받기
```

받은 파일은 폰의 `Music/가수/연도 - 앨범/` 폴더에 저장됩니다.
코드가 업데이트되면 `cd ~/joshua.kim.github.io && git pull`로 갱신하세요.

## 직접 설치하기(PC 등)

```bash
pip install -r requirements.txt
# ffmpeg 필요: brew install ffmpeg / sudo apt install ffmpeg
```

## 사용법

```bash
python album_dl.py "아이유"              # 목록 확인 후 번호로 선택 (예: 1,3,5-7)
python album_dl.py "IU" --all            # 전체 앨범 다운로드
python album_dl.py "IU" --all --albums-only  # 정규 앨범만 (기본은 싱글/EP/미니앨범 포함)
python album_dl.py "IU" --list           # 목록만 보기
python album_dl.py "IU" -o ~/Music --format m4a
```

## 저장 구조

```
downloads/
└── IU/
    └── 2017 - Palette/
        ├── 01 - 팔레트.mp3
        ├── 02 - ...
        └── .downloaded     # 이어받기용 기록
```

곡 제목, 앨범명, 앨범 아티스트, 연도, 커버 이미지가 태그로 들어갑니다.
중간에 끊겨도 같은 명령을 다시 실행하면 받은 곡은 건너뜁니다.

## 참고

- 개인 소장용 사용을 전제로 합니다. 저작권법과 YouTube 약관을 확인하고 사용하세요.
- 앨범이 안 나오면 영문/한글 이름을 바꿔서 검색해 보세요.
