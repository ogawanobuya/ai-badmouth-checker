## Twitter API x LSTMで作る誹謗中傷撃退プログラム

Twitter APIとLSTM(自然言語を扱うことに優れたAIモデル)とWord2vecを組み合わせてアカウントに悪質メッセージをリプライしてくるユーザを自動でブロックするプログラムを作りました。

#### 技術的特徴
- LSTMによる文章のPositive・Negative分類実装
- テキストデータをベクトルデータにする部分をWord2vecで実装
- Twitter APIを用いてリプライ限定でRTを除外した投稿を見つける高度な検索を実現
