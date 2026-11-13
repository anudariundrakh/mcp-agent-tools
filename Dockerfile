FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e '.[dev]'
RUN python -m src.init_db
EXPOSE 8501
CMD ["python", "-m", "streamlit", "run", "src/app.py", "--server.address=0.0.0.0", "--server.port=8501"]
