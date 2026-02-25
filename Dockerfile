FROM python:3.14

WORKDIR /divifilter

COPY . /divifilter

RUN pip install -r /divifilter/requirements.txt

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl --fail http://localhost/health || exit 1

ENTRYPOINT ["uvicorn", "dividend_stocks_filterer.app:app", "--host", "0.0.0.0", "--port", "80", "--workers", "4"]
