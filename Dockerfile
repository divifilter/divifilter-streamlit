FROM python:3.14

WORKDIR /divifilter

COPY . /divifilter

RUN pip install -r /divifilter/requirements.txt

EXPOSE 80

HEALTHCHECK CMD curl --fail http://localhost/health

ENTRYPOINT ["uvicorn", "dividend_stocks_filterer.app:app", "--host", "0.0.0.0", "--port", "80"]
