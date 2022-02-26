import sys
import requests
import time

import pygame
from pygame.locals import *

# 設定
FONT = "C:\Windows\Fonts\msjhbd.ttc"
ALBUMART = "albumart.jpg"
VOLUMIO_IP = "http://volumio.local"

# pygame 初期設定
pygame.init()
screen = pygame.display.set_mode((400, 310))
pygame.display.set_caption("Now Plaing")
font1 = pygame.font.Font(FONT, 20)
font2 = pygame.font.Font(FONT, 14)

# Volumioで再生中の情報を取得
def volumio_nowplaying():
    base_url = f'{VOLUMIO_IP}/api/v1/getState'
    url = f'{base_url}'
    r = requests.get(url)
    print(url, r)
    
    if r.status_code != 200:
        return None

    return r.json()

def download_image(url, file_name=ALBUMART):
    try:
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(r.content)
        return r.status_code
    except:
        return -1

def main():
    # 曲名とアーティストを描画
    def draw_song_data():
        text = font1.render(song_title, True, (220, 220, 220))
        screen.blit(text, [10, 2])
        text = font2.render(f'{song_artist} / {song_album}', True, (120, 120, 120))
        screen.blit(text, [12, 27])
    def draw_albumart():
        #### get image
        url = song_albumart
        if url[:9] == "/albumart":
            url = f'{VOLUMIO_IP}{url}'
        print(url)
        if download_image(url) == 200:
            img = pygame.image.load(ALBUMART)
            w, h = img.get_rect().size
            new_w = 250
            new_h = int(new_w / w * h)
            print(w,h,new_w,new_h)
            img2 = pygame.transform.smoothscale(img, (new_w, new_h))
            screen.blit(img2, [75, 50])

    last_song_title = None # １つ前の再生曲名
    get_count = 0 # 曲を取得する時間のカウンタ

    while True:
        # イベントを処理
        for event in pygame.event.get():
            if event.type == QUIT:  # 閉じるボタンが押されたら終了
                pygame.quit()
                sys.exit()

        # 再生中の曲を取得 (Volumioの負荷を考慮して5秒に1回)
        if get_count == 0:
            r = volumio_nowplaying()
            ### stop/pause 対応 2021-10-26
            if r["status"] == "play":
                song_title = r["title"]
                song_artist = r["artist"]
                song_album = r["album"]
                song_albumart = r["albumart"]
            else:
                song_title = r["status"]
                song_artist = ""
                song_album = ""
                song_albumart = ""
            get_count = 50 # 50 x 0.1 sec = 5秒
        else:
            get_count = get_count - 1

        # 曲が変わった時だけ画面更新
        if last_song_title != song_title:
            screen.fill((0, 0 ,0))
            print(song_title)
            draw_song_data()
            draw_albumart()
            pygame.display.update()
            last_song_title = song_title

        time.sleep(0.1)

if __name__ == '__main__':
    main()