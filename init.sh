pip install -r requirements.txt
pip install -r requirements-dev.txt
python3 -m spacy download en_core_web_sm
python3 -m nltk.downloader maxent_ne_chunker words punkt averaged_perceptron_tagger
curl -O -L http://nlp.stanford.edu/software/stanford-corenlp-latest.zip
unzip stanford-corenlp-latest.zip
