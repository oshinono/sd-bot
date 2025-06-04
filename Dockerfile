FROM python:3.12-alpine

WORKDIR /project

COPY pyproject.toml .

RUN pip install uv
RUN uv sync

COPY bot bot

CMD ["uv", "run", "python", "bot/main.py"]