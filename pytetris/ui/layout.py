"""렌더링 관련 레이아웃/색상 상수(게임 로직 상수와 분리).

전체 톤: 차분하고 몽글몽글한 파스텔 힐링 무드.
"""

CELL_SIZE = 30
CELL_PADDING = 3  # 블록 사이 여백 -> 칸이 서로 붙지 않고 개별 젤리처럼 보이게
BLOCK_RADIUS = 10  # 블록 모서리를 크게 둥글림(마시멜로 느낌)
PANEL_RADIUS = 18  # 보드/패널 바깥 테두리도 부드럽게

BOARD_VISIBLE_ROWS = 20
BOARD_COLS = 10

PLAYFIELD_MARGIN = 24
SIDE_PANEL_WIDTH = 200

PLAYFIELD_PX_WIDTH = CELL_SIZE * BOARD_COLS
PLAYFIELD_PX_HEIGHT = CELL_SIZE * BOARD_VISIBLE_ROWS

WINDOW_WIDTH = PLAYFIELD_MARGIN * 3 + PLAYFIELD_PX_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = PLAYFIELD_MARGIN * 2 + PLAYFIELD_PX_HEIGHT

# 완전한 검정 대신 아주 어두운 웜그레이 톤
BG_COLOR = (35, 34, 38)
BOARD_BG_COLOR = (46, 45, 50)
PANEL_BG_COLOR = (46, 45, 50)

# 그리드는 아주 은은하게(강한 선 없음)
GRID_LINE_COLOR = (58, 57, 63)

TEXT_COLOR = (226, 221, 214)  # 완전한 흰색 대신 살짝 톤 다운된 웜화이트
TEXT_MUTED_COLOR = (160, 156, 150)
HIGHLIGHT_COLOR = (247, 214, 178)  # 파스텔 골드(팝업 텍스트용, 쨍한 노랑 대신)
