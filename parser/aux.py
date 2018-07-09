import MySQLdb
import configparser
from nltk.corpus import stopwords
from nltk import sent_tokenize, ne_chunk, ne_chunk_sents, pos_tag, word_tokenize
from nltk import PorterStemmer


def savePage(filename, content):
    try:
        fl = open(filename, 'w')
        fl.writelines(content)
        fl.close
        result = True
    except:
        result = False

    return result


def measureCorpus(text):
    sentenses = sent_tokenize(text)
    words = word_tokenize(text)

    return [sentenses, words]


def filterText(text, stemmed=False):
    if stemmed:
        porter = PorterStemmer()

    # remove stopwords and useless words
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(text)

    valuable_words = []
    for wrd in words:
        if len(wrd) > 3 and not wrd in stop_words:
            if stemmed:
                valuable_words.append(porter.stem(wrd.lower()))
            else:
                valuable_words.append(wrd.lower())

    return valuable_words


def createSummary(text_title, text, ratio):

    # filter title
    filtered_title = filterText(text_title, True)

    # build stemmed -> frequency table
    stemmed_frquency_table = {}

    valuable_words = filterText(text, True)

    for wrd in valuable_words:

        if wrd in stemmed_frquency_table:
            stemmed_frquency_table[wrd] += 1
        else:
            stemmed_frquency_table[wrd] = 1

    # assign score to each sentence
    sentenses = sent_tokenize(text)
    sentense_scoreboard = []
    total_score = 0

    for sentense in sentenses:
        sentense_score = 0
        sentense_words = filterText(sentense, True)
        for sentense_word in sentense_words:
            sentense_score += stemmed_frquency_table[sentense_word]
            if sentense_word in filtered_title:
                sentense_score += 10

        sentense_scoreboard.append(list([sentense, sentense_score]))
        total_score += sentense_score

    # calculate average sentense score
    # and determine score threshold
    average_score = int(total_score / len(sentense_scoreboard))
    score_mutator = int(average_score * 0.6)
    reduced_text = ''

    sentense_counter = 0

    for sent in sentense_scoreboard:
        if sent[1] >= average_score + score_mutator:
            sentense_counter += 1
            outputx = sent[0]
            # reduced_text += outputx.replace('\n', '<br>')
            reduced_text += outputx

    return reduced_text


def getSentiment(text, pos_keys, neg_keys):
    results = {}
    positive_keys = 0
    negative_keys = 0
    text_size = 0

    try:
        filtered_text = filterText(text, False)
        text_size = len(filtered_text)

        for wrd in filtered_text:
            if wrd in pos_keys:
                positive_keys += 1

            if wrd in neg_keys:
                negative_keys += 1

        percentage_positive = (positive_keys / text_size) / 100
        percentage_negative = (negative_keys / text_size) / 100

        results['positive'] = positive_keys
        results['positive_percentage'] = percentage_positive
        results['negative'] = negative_keys
        results['negative_percentage'] = percentage_negative
        results['text_size'] = text_size
    except:
        results['positive'] = 0
        results['positive_percentage'] = 0
        results['negative'] = 0
        results['negative_percentage'] = 0
        results['text_size'] = 0
    return results


def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))

    return entity_names


def NE_extract(text):
    sentences = sent_tokenize(text)
    tokenized_sentences = [word_tokenize(sentence) for sentence in sentences]
    tagged_sentences = [pos_tag(sentence) for sentence in tokenized_sentences]
    chunked_sentences = ne_chunk_sents(tagged_sentences, binary=True)

    entity_names = []
    for tree in chunked_sentences:
        entity_names.extend(extract_entity_names(tree))

    return set(entity_names)


def removeQuotes(text):
    quotes = ['\'', '"', '\n']
    for quote in quotes:
        text = text.replace(quote, '')

    return text
