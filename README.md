# SPIMEX ETL Parser

ETL-пайплайн для загрузки и обработки бюллетеней торгов биржи SPIMEX с сохранением данных в PostgreSQL.

Пайплайн реализован в двух вариантах:
- Sync (последовательный)
- Async (параллельный)

---

## Архитектура пайплайна

Последовательность обработки данных:

- Download (загрузка файлов)
- Parse (парсинг PDF/Excel)
- Save (сохранение в PostgreSQL)

---

## Стек технологий

- Python 3.14  
- asyncpg
- psycopg3 
- SQLAlchemy 2.x
- asyncpg / SQLAlchemy async
- httpx
- asyncio
- pandas
- pdfplumber
- xlrd
- BeautifulSoup4 
- pydantic
- pydantic-settings
- typer 
- rich 

---

## Сравнение Sync vs Async

| Этап            | Sync     | Async    | Speedup |
|----------------|----------|----------|---------|
| Download files  | 49.78s   | 20.79s   | 2.39x   |
| Parse data      | 2.27s    | 2.26s    | 1.00x   |
| Load to DB      | 2.54s    | 1.13s    | 2.25x   |
| **Total**       | **54.60s** | **24.20s** | **2.26x** |

---

## Быстрый старт (Docker)

### 1. Сборка контейнеров

```bash
1. docker compose build

2. Конфигурация окружения
cp .env.example .env

3. Запуск PostgreSQL
docker compose up -d postgres

4. Инициализация базы данных
docker compose run --rm backend init-db

5. Запуск
```

#### Sync:
```bash
docker compose run --rm backend run-sync --pages 10
```

#### Async:
```bash
docker compose run --rm backend run-async --pages 10
```

#### Benchmark:
```bash
docker compose run --rm backend benchmark --pages 10
```

