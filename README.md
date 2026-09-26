# 테트리스 (Python 구현)

표준 테트리스 가이드라인(SRS 회전, 7-bag 랜덤, 홀드/넥스트)을 재현하고, 로컬 랭킹 시스템을 제공하는 싱글플레이어 클래식 테트리스 게임 프로젝트입니다.

자세한 기획 내용은 [docs/PRD.md](docs/PRD.md)를 참고하세요.

## 개요

- **장르**: 낙하형 퍼즐 게임(아케이드)
- **플랫폼**: Windows/macOS/Linux, 로컬 실행 전용
- **핵심 특징**
  - SRS(Super Rotation System) 기반 회전 및 킥 테이블
  - 7-bag 랜덤 시스템, 홀드 기능, 5개 넥스트 큐
  - T-스핀, 콤보, 백투백 보너스를 포함한 점수 시스템
  - SQLite 기반 로컬 Top 10 랭킹

## 기술 스택

- Python 3.11+
- pygame (pygame-ce 권장)
- SQLite (`sqlite3` 표준 라이브러리)
- PyInstaller (배포용 단일 실행 파일)

## 프로젝트 구조 (제안)

```
pytetris/
├── main.py              # 진입점
├── game/                # 보드, 테트로미노, 점수, 레벨, 상태 관리
├── ranking/             # SQLite 랭킹 CRUD
├── ui/                  # 화면 및 렌더링
├── assets/              # 폰트, 사운드 등
└── settings.json        # 유저 설정
```

## 개발 상태

현재 기획 문서(PRD) 작성 단계이며, 구현은 아직 시작되지 않았습니다.
