import sys, pygame

def rgb565_to_rgb888(color_565):
    """実機用のRGB565形式(16bit)を、Pygame表示用のRGB888(24bit)へ1ビットの狂いもなく変換する"""
    r = ((color_565 >> 11) & 0x1F) * 255 // 31
    g = ((color_565 >> 5) & 0x3F) * 255 // 63
    b = (color_565 & 0x1F) * 255 // 31
    return (r, g, b)

# --- 1. 定数・ベースカラー定義 (RGB) ---
BG_COLOR = (32, 16, 48)        # 夜空のベースとなる深い紫
WHITE = (255, 255, 255)
GRAY = (80, 80, 80)

# 木・金 / 土・日用のカラー（後半戦用）
L_GRN, GRN, D_GRN, BRN, SKIN = (170, 240, 0), (0, 200, 80), (0, 90, 40), (140, 90, 50), (200, 160, 110)
GLD, MID_YEL, BRZ = (255, 215, 0), (200, 160, 0), (128, 96, 0)
SUN_RED, SAT_BLU, EBICHA = (255, 32, 32), (32, 112, 255), (100, 30, 40)

# --- 2. 実機用RGB565パレットデータ（1文字も削られないように厳重展開） ---
MON_565 = [0x0020, 0x0861, 0x18C3, 0x0861, 0x45B8, 0x2186, 0x1166, 0x573E, 0x0000, 0x579F, 0x3473, 0x465B, 0x577F, 0x577F, 0x057C, 0x0041, 0x4F3F, 0x473F, 0x471F, 0x1A29, 0x0841, 0x369E, 0x3EDE, 0x0841, 0x10A2, 0x18E3, 0x230E, 0x1945]
MON_PALETTE_RGB = [rgb565_to_rgb888(c) for c in MON_565]

TUE_565 = [0x0000, 0xFF3A, 0xFDD1, 0xFC05, 0xFD0B, 0xFB60, 0xFFFF]
TUE_PALETTE_RGB = [rgb565_to_rgb888(c) for c in TUE_565]

WED_565 = [0x0000, 0xFF3A, 0xFDD1, 0xFC05, 0xFD0B, 0xFB60, 0xFFFF]
WED_PALETTE_RGB = [rgb565_to_rgb888(c) for c in WED_565]

# --- 3. 2次元配列配置データ（システムの間引きバグを回避するため1行のロング文字列で記述し、内部展開） ---
# あなたの指定データおよびファイル1〜3のドットを1マスも落とさず文字化

STR_MON = "0001020300040500" + "0001020300060705" + "000102030008090a" + "00010203000b0c0a" + "00010203000d0e04" + "0f01020610111213" + "141516160e161714" + "1819051a1b181818"
STR_TUE = "00000000" + "00000000" + "00000100" + "00000203" + "03000001" + "04020303" + "00040202" + "03030505"
STR_WED = "00000000" + "00000100" + "00000203" + "03000001" + "04020303" + "00040202" + "03030505" + "00050305"

STR_THU = "00122300" + "01223330" + "02223330" + "00045000" + "00034000" + "00033000"
STR_FRI = "00333300" + "03121220" + "03222220" + "00222220" + "00222220" + "00000000"
STR_SAT = "00033000" + "02222200" + "11222211" + "00222200" + "00033000" + "00000000"
STR_SUN = "00000000" + "00333300" + "03322330" + "03211230" + "21111112" + "41414141"

def parse_to_pixels(day_idx):
    data_str = [STR_MON, STR_TUE, STR_WED, STR_THU, STR_FRI, STR_SAT, STR_SUN][day_idx]
    pixels = []
    
    if day_idx == 0:
        # 月曜日用の2桁16進数（00〜1b）デコード処理
        for r in range(8):
            row = []
            for c in range(8):
                idx = (r * 8 + c) * 2
                row.append(int(data_str[idx:idx+2], 16))
            pixels.append(row)
    else:
        # それ以外の曜日用の1桁デコード処理
        num_rows = len(data_str) // 8
        for r in range(num_rows):
            row = []
            for c in range(8):
                row.append(int(data_str[r * 8 + c]))
            pixels.append(row)
    return pixels

ICONS = {
    0: {"palette": MON_PALETTE_RGB, "pixels": parse_to_pixels(0), "width": 8, "y_offset": 0},
    1: {"palette": TUE_PALETTE_RGB, "pixels": parse_to_pixels(1), "width": 8, "y_offset": 0}, 
    2: {"palette": WED_PALETTE_RGB, "pixels": parse_to_pixels(2), "width": 8, "y_offset": 0},
    3: {"palette": [BG_COLOR, L_GRN, GRN, D_GRN, BRN, SKIN], "pixels": parse_to_pixels(3), "width": 8, "y_offset": 1},
    4: {"palette": [BG_COLOR, WHITE, GLD, MID_YEL, BRZ], "pixels": parse_to_pixels(4), "width": 8, "y_offset": 1},
    5: {"palette": [BG_COLOR, WHITE, SAT_BLU, GRAY], "pixels": parse_to_pixels(5), "width": 8, "y_offset": 1},
    6: {"palette": [BG_COLOR, WHITE, SUN_RED, GRAY, EBICHA], "pixels": parse_to_pixels(6), "width": 8, "y_offset": 1}
}

def main():
    pygame.init()
    SCALE, V_WIDTH, V_HEIGHT = 4, 56, 8
    virtual_screen = pygame.Surface((V_WIDTH, V_HEIGHT))
    display_screen = pygame.display.set_mode((V_WIDTH * SCALE, V_HEIGHT * SCALE))
    pygame.display.set_caption("Icon Dot-Art Studio (Mon-Sun)")
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
        virtual_screen.fill(BG_COLOR)
        
        current_x = 0
        for i in range(7):
            icon_data = ICONS[i]
            y_off = icon_data["y_offset"]
            for r, row in enumerate(icon_data["pixels"]):
                for c, p_val in enumerate(row):
                    if p_val > 0 and p_val < len(icon_data["palette"]):
                        virtual_screen.set_at((current_x + c, r + y_off), icon_data["palette"][p_val])
            current_x += icon_data["width"]

        pygame.transform.scale(virtual_screen, (V_WIDTH * SCALE, V_HEIGHT * SCALE), display_screen)
        pygame.display.flip()
        clock.tick(10)

if __name__ == "__main__": main()
