FROM alpine

RUN apk add --no-cache openjdk8
COPY ./ /app
WORKDIR /app/
RUN rm setup.cfg
RUN apk update  && apk add  --no-cache --update curl zip make automake python3 python3-dev freetype-dev py3-pip libffi-dev openssl-dev openssh-client && apk add --no-cache --virtual .build-deps gcc g++ musl-dev
RUN curl -O -L http://nlp.stanford.edu/software/stanford-corenlp-latest.zip
RUN unzip stanford-corenlp-latest.zip
RUN pip3 install  --upgrade pip
RUN pip3 install cython
RUN pip3 install --no-cache-dir -r requirements.txt
RUN apk del .build-deps gcc g++ musl-dev
RUN python3 -m spacy download en_core_web_sm && python3 -m nltk.downloader maxent_ne_chunker words punkt averaged_perceptron_tagger
CMD ["python3", "app.py"]
