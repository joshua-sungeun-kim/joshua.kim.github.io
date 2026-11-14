#!/usr/bin/env python3
"""가수 이름으로 YouTube Music의 앨범을 찾아 앨범별 폴더로 다운로드한다.

사용 예:
    python album_dl.py "아이유"                 # 앨범 목록을 보고 번호로 고르기
    python album_dl.py "IU" --all               # 전부 다운로드
    python album_dl.py "IU" --all --albums-only # 정규 앨범만 (기본은 싱글/EP 포함)
    python album_dl.py "IU" --list              # 목록만 출력
"""
import argparse
import re
import sys
from pathlib import Path

from ytmusicapi import YTMusic
import yt_dlp


def clean(name: str) -> str:
    """파일/폴더 이름으로 쓸 수 없는 문자를 제거한다."""
    return re.sub(r'[\\/:*?"<>|]', "_", name).strip().rstrip(".")


def find_artists(yt: YTMusic, query: str) -> list[dict]:
    """검색된 아티스트 후보를 구독자 수/대표 앨범과 함께 보여주고 고르게 한다.

    같은 가수가 채널 여러 개로 나뉘어 있을 수 있어서 여러 개를 동시에 고를 수 있다.
    """
    results = yt.search(query, filter="artists", limit=10)
    if not results:
        sys.exit(f"'{query}' 아티스트를 찾지 못했습니다.")
    if len(results) == 1:
        return results

    print("검색된 아티스트:")
    for i, r in enumerate(results, 1):
        info = ""
        try:
            a = yt.get_artist(r["browseId"])
            titles = [x["title"] for x in (a.get("albums") or {}).get("results", [])[:3]]
            info = f"  구독자 {a.get('subscribers', '?')} | " + (", ".join(titles) or "앨범 없음")
        except Exception:
            pass
        print(f"  {i}. {r['artist']}{info}")
    pick = input("번호 선택 (여러 개면 1,2 / 기본 1): ").strip() or "1"
    idx = [int(x) for x in re.findall(r"\d+", pick)]  # 방향키 등 이상한 입력은 무시
    return [results[i - 1] for i in idx if 1 <= i <= len(results)]


def fetch_releases(yt: YTMusic, browse_id: str, include_singles: bool = True) -> list[dict]:
    artist = yt.get_artist(browse_id)
    releases = []
    sections = ["albums"] + (["singles"] if include_singles else [])
    for key in sections:
        sec = artist.get(key)
        if not sec:
            continue
        items = sec["results"]
        # 항목이 많으면 '전체 보기' 파라미터로 전부 가져온다
        if sec.get("browseId") and sec.get("params"):
            items = yt.get_artist_albums(sec["browseId"], sec["params"])
        for it in items:
            releases.append({**it, "kind": key})
    # 중복 제거
    seen, unique = set(), []
    for r in releases:
        if r["browseId"] not in seen:
            seen.add(r["browseId"])
            unique.append(r)
    return unique


def choose(releases: list[dict]) -> list[dict]:
    print("\n앨범 목록:")
    for i, r in enumerate(releases, 1):
        print(f"  {i:>2}. [{r.get('year', '----')}] {r['title']} ({r.get('type') or r['kind']})")
    raw = input("\n받을 번호 (예: 1,3,5-7 / all): ").strip().lower()
    if raw in ("all", "a"):
        return releases
    picked = set()
    for part in raw.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-")
            picked.update(range(int(a), int(b) + 1))
        elif part:
            picked.add(int(part))
    return [releases[i - 1] for i in sorted(picked) if 1 <= i <= len(releases)]


def download_album(yt: YTMusic, release: dict, artist_name: str, out_dir: Path, fmt: str):
    album = yt.get_album(release["browseId"])
    playlist_id = album.get("audioPlaylistId")
    if not playlist_id:
        print(f"  ! '{release['title']}' 재생목록을 찾지 못해 건너뜁니다.")
        return
    year = album.get("year") or release.get("year") or "0000"
    folder = out_dir / clean(artist_name) / clean(f"{year} - {album['title']}")
    folder.mkdir(parents=True, exist_ok=True)

    opts = {
        "format": "bestaudio/best",
        "outtmpl": str(folder / "%(playlist_index)02d - %(title)s.%(ext)s"),
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": fmt, "preferredquality": "0"},
            {"key": "FFmpegMetadata", "add_metadata": True},
            {"key": "EmbedThumbnail"},
        ],
        "writethumbnail": True,
        "download_archive": str(folder / ".downloaded"),  # 이어받기 / 중복 방지
        "ignoreerrors": True,
        "restrictfilenames": False,
        "windowsfilenames": True,
        "postprocessor_args": {"ffmpeg": ["-metadata", f"album={album['title']}",
                                          "-metadata", f"album_artist={artist_name}",
                                          "-metadata", f"date={year}"]},
    }
    print(f"\n▶ {album['title']} ({year}) → {folder}")
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([f"https://music.youtube.com/playlist?list={playlist_id}"])


def main():
    p = argparse.ArgumentParser(description="가수의 앨범을 YouTube Music에서 찾아 앨범별로 다운로드")
    p.add_argument("artist", help="가수 이름")
    p.add_argument("-o", "--out", default="downloads", help="저장 폴더 (기본: downloads)")
    p.add_argument("--all", action="store_true", help="물어보지 않고 전부 다운로드")
    p.add_argument("--albums-only", action="store_true", help="정규 앨범만 (기본은 싱글/EP/미니앨범 포함)")
    p.add_argument("--list", action="store_true", help="목록만 출력하고 종료")
    p.add_argument("--format", default="mp3", choices=["mp3", "m4a", "opus", "flac"],
                   help="오디오 형식 (기본: mp3)")
    args = p.parse_args()

    yt = YTMusic()
    artists = find_artists(yt, args.artist)
    if not artists:
        sys.exit("아티스트를 선택하지 않았습니다.")
    artist = artists[0]  # 폴더 이름에 쓸 대표 이름
    print(f"\n아티스트: {', '.join(a['artist'] for a in artists)}")
    releases, seen = [], set()
    for a in artists:  # 여러 채널을 고른 경우 앨범을 합치고 중복은 제거
        for r in fetch_releases(yt, a["browseId"], not args.albums_only):
            if r["browseId"] not in seen:
                seen.add(r["browseId"])
                releases.append(r)
    if not releases:
        sys.exit("앨범을 찾지 못했습니다.")

    if args.list:
        for r in releases:
            print(f"[{r.get('year', '----')}] {r['title']} ({r.get('type') or r['kind']})")
        return

    selected = releases if args.all else choose(releases)
    for r in selected:
        download_album(yt, r, artist["artist"], Path(args.out), args.format)
    print("\n완료!")


if __name__ == "__main__":
    main()
