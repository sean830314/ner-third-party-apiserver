import copy
import os
import re
from itertools import groupby

import nltk
import spacy
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from stanfordcorenlp import StanfordCoreNLP

from data import get_pid_data


class NerTagger:
    def __init__(self):
        self._stanford_corenlp = StanfordCoreNLP(
            "{}/{}".format(os.getcwd(), "stanford-corenlp-4.2.0")
        )
        self._azure_key = os.getenv("AZURE_KEY")
        self._azure_endpoint = os.getenv("AZURE_ENDPOINT")

    def group_chunk(self, texts):
        results = list()
        for tag, chunk in groupby(texts, lambda x: x[1]):
            if tag != "O":
                tuple_item = (" ".join(w for w, t in chunk), tag)
                results.append(tuple_item)
        return results

    def parse_document(self, document):
        document = re.sub("\n", " ", document)
        if isinstance(document, str):
            document = document
        else:
            raise ValueError("Document is not string!")
        document = document.strip()
        sentences = nltk.sent_tokenize(document)
        sentences = [sentence.strip() for sentence in sentences]
        return sentences

    def authenticate_client(self):
        ta_credential = AzureKeyCredential(self._azure_key)
        text_analytics_client = TextAnalyticsClient(
            endpoint=self._azure_endpoint, credential=ta_credential
        )
        return text_analytics_client

    def azure_entity_recognition(self, client, paragraph):
        try:
            documents = [paragraph]
            result = client.recognize_entities(documents=documents)[0]
            response = {"organization": [], "date": [], "address": []}
            print("Named Entities:\n")
            for entity in result.entities:
                if entity.category == "Organization":
                    r = entity.text
                    # r = {
                    #     "text": entity.text,
                    #     "score": round(entity.confidence_score, 2),
                    # }
                    response["organization"].append(r)
                if entity.category == "DateTime":
                    response["date"].append(entity.text)
                if entity.category == "Address":
                    response["address"].append(entity.text)
                print(
                    "\tText: \t",
                    entity.text,
                    "\tCategory: \t",
                    entity.category,
                    "\tSubCategory: \t",
                    entity.subcategory,
                    "\tConfidence Score: \t",
                    round(entity.confidence_score, 2),
                    "\tOffset: \t",
                    entity.offset,
                    "\n",
                )
                print("---" * 10)
            return response
        except Exception as err:
            print("Encountered exception. {}".format(err))
            return {}

    def spacy_entity_recognition(self, paragraph):
        """
        CARDINAL, DATE, EVENT, FAC, GPE, LANGUAGE, LAW, LOC, MONEY, NORP, ORDINAL, ORG, PERCENT, PERSON, PRODUCT, QUANTITY, TIME, WORK_OF_ART
        """
        try:
            response = {"organization": [], "date": [], "address": []}
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(paragraph)
            named_entities = []
            for ent in doc.ents:
                named_entities.append((ent.text, ent.label_))
                # get unique named entities
                named_entities = list(set(named_entities))
            print("Origin Spacy entities")
            print(named_entities)
            for item in named_entities:
                if item[1] == "ORG" or item[1] == "PERSON":
                    r = item[0]
                    response["organization"].append(r)
                if item[1] == "DATE":
                    response["date"].append(item[0])
                if item[1] == "LOC" or item[1] == "GPE":
                    response["address"].append(item[0])
            return response
        except Exception as err:
            print("Encountered exception. {}".format(err))
            return {}

    def nltk_entity_recognition(self, paragraph):
        try:
            response = {"organization": [], "date": [], "address": []}
            sentences = self.parse_document(paragraph)
            tokenized_sentences = [
                nltk.word_tokenize(sentence) for sentence in sentences
            ]
            # tag sentences and use nltk's Named Entity Chunker
            tagged_sentences = [
                nltk.pos_tag(sentence) for sentence in tokenized_sentences
            ]
            ne_chunked_sents = [nltk.ne_chunk(tagged) for tagged in tagged_sentences]
            # extract all named entities
            named_entities = []
            for ne_tagged_sentence in ne_chunked_sents:
                for tagged_tree in ne_tagged_sentence:
                    # extract only chunks having NE labels
                    print("===" * 100)
                    print(tagged_tree)
                    if hasattr(tagged_tree, "label"):
                        entity_name = " ".join(
                            c[0] for c in tagged_tree.leaves()
                        )  # get NE name
                        entity_type = tagged_tree.label()  # get NE category
                        named_entities.append((entity_name, entity_type))
            print("Origin Spacy entities")
            print(named_entities)
            for item in named_entities:
                if item[1] == "ORGANIZATION" or item[1] == "PERSON":
                    response["organization"].append(item[0])
                if item[1] == "GPE" or item[1] == "LOCATION":
                    response["address"].append(item[0])
                if item[1] == "DATE" or item[1] == "TIME":
                    response["date"].append(item[0])
            return response
        except Exception as err:
            print("Encountered exception. {}".format(err))
            return {}

    def stanford_corenlp_entity_recognition(self, paragraph):
        """
        (PERSON, LOCATION, ORGANIZATION, MISC), numerical (MONEY, NUMBER, ORDINAL, PERCENT) and temporal (DATE, TIME, DURATION, SET) entities (12 classes).
        """
        try:
            response = {"organization": [], "date": [], "address": []}
            result = self._stanford_corenlp.ner(paragraph)
            print("Origin Spacy entities")
            print(result)
            named_entities = self.group_chunk(result)
            print("Group Chunk entities")
            print(named_entities)
            for item in named_entities:
                if item[1] == "ORGANIZATION" or item[1] == "PERSON":
                    response["organization"].append(item[0])
                if (
                    item[1] == "GPE"
                    or item[1] == "LOCATION"
                    or item[1] == "NUMBER"
                    or item[1] == "CITY"
                ):
                    response["address"].append(item[0])
                if item[1] == "DATE" or item[1] == "TIME":
                    response["date"].append(item[0])
            return response
        except Exception as err:
            print("Encountered exception. {}".format(err))
            return {}

    def predict(self, model_type, paragraph):
        response = {}
        response["ner"] = list()
        if model_type == "Azure":
            client = self.authenticate_client()
            result = self.azure_entity_recognition(client, paragraph)
            result["model"] = model_type
            response["ner"].append(result)
        if model_type == "Spacy":
            result = self.spacy_entity_recognition(paragraph)
            result["model"] = model_type
            response["ner"].append(result)
        if model_type == "NLTK":
            result = self.nltk_entity_recognition(paragraph)
            result["model"] = model_type
            response["ner"].append(result)
        if model_type == "Stanford_CoreNLP":
            result = self.stanford_corenlp_entity_recognition(paragraph)
            result["model"] = model_type
            response["ner"].append(result)
        if model_type == "All":
            client = self.authenticate_client()
            result = self.azure_entity_recognition(client, paragraph)
            result["model"] = "Azure"
            response["ner"].append(result)
            result = self.spacy_entity_recognition(paragraph)
            result["model"] = "Spacy"
            response["ner"].append(result)
            result = self.nltk_entity_recognition(paragraph)
            result["model"] = "NLTK"
            response["ner"].append(result)
            result = self.stanford_corenlp_entity_recognition(paragraph)
            result["model"] = "Stanford_CoreNLP"
            response["ner"].append(result)
        return response

    def predict_by_models(self, pid):
        response = list()
        print(pid, type(pid))
        data = get_pid_data()
        paragraph = data[pid]["paragraph"]
        result = copy.deepcopy(data[pid]["target"])
        result["model"] = "Target"
        response.append(result)
        client = self.authenticate_client()
        result = self.azure_entity_recognition(client, paragraph)
        result["model"] = "Azure"
        response.append(result)
        result = self.spacy_entity_recognition(paragraph)
        result["model"] = "Spacy"
        response.append(result)
        result = self.nltk_entity_recognition(paragraph)
        result["model"] = "NLTK"
        response.append(result)
        result = self.stanford_corenlp_entity_recognition(paragraph)
        result["model"] = "Stanford_CoreNLP"
        response.append(result)
        from tomark import Tomark

        markdown = Tomark.table(response)
        print(markdown)
        response = {"data": response}
        return response
