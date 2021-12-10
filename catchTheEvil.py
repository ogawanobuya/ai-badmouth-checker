# coding=utf-8
import collections
import os
import json
import nltk
import codecs
from requests_oauthlib import OAuth1Session
from keras.models import Sequential, load_model
from keras.preprocessing import sequence

# 認証処理
CK = 'yldk1YIA0NRsvFsCQmfGaQCgK'
CS = '8Ck4l3huZCRTscho7ctvjMvtSCZuclKM5b9obb16HVmpJz7U6M'
AT = '728509246690590720-uYedUZFbSRAYIDnCjnu1g0XLAT4PnRo'
ATS = 'tahnBJKLjbbbF6xXMvncf0qTULp3ASaYTQ2F3eNUPgfWF'
twitter = OAuth1Session(CK, CS, AT, ATS)

# ツイート検索エンドポイント
url = 'https://api.twitter.com/1.1/search/tweets.json'
# ユーザーブロックエンドポイント
url2 = 'https://api.twitter.com/1.1/blocks/create.json'
# Setting parameter
DATA_DIR = "./ai/data"
MAX_FEATURES = 2000
MAX_SENTENCE_LENGTH = 40

if os.path.exists(os.path.join(DATA_DIR, "sentence_analyzing_rnn.hdf5")):
    # Read training data and generate word2index
    maxlen = 0
    word_freqs = collections.Counter()
    with codecs.open(os.path.join(DATA_DIR, "umich-sentiment-train.txt"), "r", 'utf-8') as ftrain:
        for line in ftrain:
            label, sentence = line.strip().split("\t")
            try:
                words = nltk.word_tokenize(sentence.lower())
            except LookupError:
                print("Englisth tokenize does not downloaded. So download it.")
                nltk.download("punkt")
                words = nltk.word_tokenize(sentence.lower())
            maxlen = max(maxlen, len(words))
            for word in words:
                word_freqs[word] += 1

    vocab_size = min(MAX_FEATURES, len(word_freqs)) + 2
    word2index = {x[0]: i + 2 for i, x in enumerate(word_freqs.most_common(MAX_FEATURES))}
    word2index["PAD"] = 0
    word2index["UNK"] = 1
    # load model
    model = load_model(os.path.join(DATA_DIR, "sentence_analyzing_rnn.hdf5"))
    # エンドポイントへ渡すパラメーター
    target_account = '@downtownakasiya '  # リプライされたアカウント
    keyword = '@' + target_account + 'exclude:retweets'  # RTは除外

    params = {
        'count': 50,  # 取得するtweet数
        'q': keyword,  # 検索キーワード
    }
    req = twitter.get(url, params=params)

    if req.status_code == 200:
        res = json.loads(req.text)
        for line in res['statuses']:
            target_text = line['text'].replace(target_account, "")
            test_words = nltk.word_tokenize(target_text.lower())
            test_seqs = []
            for test_word in test_words:
                if test_word in word2index:
                    test_seqs.append(word2index[test_word])
                else:
                    test_seqs.append(word2index["UNK"])

            Xsent = sequence.pad_sequences([test_seqs], maxlen=MAX_SENTENCE_LENGTH)
            ypred = model.predict(Xsent)[0][0]
            if ypred < 0.5:  # 閾値を下回れば誹謗中傷認定する
                params2 = {'user_id': line['user']['id']}  # ブロックするユーザー
                req2 = twitter.post(url2, params=params2)

                if req2.status_code == 200:
                    print("Blocked !!")
                else:
                    print("Failed2: %d" % req2.status_code)
    else:
        print("Failed: %d" % req.status_code)
else:
    print ("AI model doesn't exist")

# 注意：Twitter APIは1週間以上前のリプを検索ヒットさせることができない
# 注意：明らかな攻撃的なリプはそもそもヒットしない
