#!/data/data/com.termux/files/usr/bin/bash
# Termux 처음 설치한 상태에서 한 번만 실행하면 되는 설정 스크립트.
#   bash termux-setup.sh
# 끝나면 `album "가수 이름"` 으로 바로 사용할 수 있다. (여러 번 실행해도 안전)
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "==> 1/4 패키지 설치 (python, ffmpeg)"
pkg update -y
pkg install -y python ffmpeg git

echo "==> 2/4 폰 저장소 접근 권한"
if [ ! -d "$HOME/storage/music" ]; then
    termux-setup-storage || true
    echo "    화면에 권한 팝업이 뜨면 '허용'을 눌러 주세요."
    for _ in $(seq 1 60); do
        [ -d "$HOME/storage/music" ] && break
        sleep 1
    done
fi
if [ ! -d "$HOME/storage/music" ]; then
    echo "!! 저장소 권한이 허용되지 않았습니다. 'termux-setup-storage'를 실행하고 허용한 뒤 이 스크립트를 다시 실행해 주세요."
    exit 1
fi

echo "==> 3/4 파이썬 라이브러리 설치 (yt-dlp, ytmusicapi)"
pip install -U yt-dlp ytmusicapi

echo "==> 4/4 'album' 명령어 만들기"
cat > "$PREFIX/bin/album" <<EOF
#!/data/data/com.termux/files/usr/bin/bash
# 다운로드 중 화면이 꺼져도 끊기지 않도록 wakelock을 켠다
termux-wake-lock 2>/dev/null || true
trap 'termux-wake-unlock 2>/dev/null || true' EXIT
# 저장 위치 기본값은 폰의 Music 폴더. 뒤에 -o 를 직접 주면 그쪽이 우선한다.
python "$DIR/album_dl.py" -o "\$HOME/storage/music" "\$@"
EOF
chmod +x "$PREFIX/bin/album"

cat <<'MSG'

설정 완료!

사용법:
  album "가수 이름"            목록을 보고 번호로 골라서 받기
  album "가수 이름" --all      전부 받기
  album "가수 이름" --list     목록만 보기
  album --help                 모든 옵션

받은 파일은 폰의 Music 폴더(내장 메모리/Music/가수/연도 - 앨범/)에 저장됩니다.
MSG
