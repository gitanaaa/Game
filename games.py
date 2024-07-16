import pygame
from pygame.locals import *
import sys

img_bg = pygame.image.load("fild_image2.jpg")

bg_y = 0

def main():
    global bg_y

    pygame.init()
    pygame.display.set_caption("トロッコゲーム")
    screen = pygame.display.set_mode((800,400))
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        bg_y = (bg_y+1.25)%400
        screen.blit(img_bg,[0,bg_y-400])
        screen.blit(img_bg,[0,bg_y])

        pygame.display.update()
        clock.tick()

                # 終了用のイベント処理
        for event in pygame.event.get():
            if event.type == QUIT:          # 閉じるボタンが押されたとき
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:       # キーを押したとき
                if event.key == K_ESCAPE:   # Escキーが押されたとき
                    pygame.quit()
                    sys.exit()
if __name__ == "__main__":
    main()
