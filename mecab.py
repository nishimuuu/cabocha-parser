# -*-coding: utf-8 -*-
__author__ = 'nishimuuu'

import sys, os

sys_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(sys_path)
import MeCab
import numpy as np

print sys.path
from inspect import getargspec
from mecab_token import MeCabToken
import re

# write code here...

class MeCabSeparator:
  stop_words = ['これ', 'それ', 'あれ', 'この', 'その', 'あの', 'ここ', 'そこ', 'あそこ', 'こちら', 'どこ', 'だれ', 'なに', 'なん',
                '何', 'です', 'あります', 'おります',
                'います', 'は', 'が', 'の', 'に', 'を', 'で', 'え', 'から',
                'まで', 'より', 'も', 'どの', 'と', 'し', 'それで', 'しかし']
  patUrl = re.compile("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+")
  patXml = re.compile("<(\".*?\"|\'.*?\'|[^\'\"])*?>")
  sep = '[!-/:-@[-`{-~、◞⤴○▿゚д◟。♡٩ωو°！？（）〈〉【】『』／≦＜＼≧＞≪≫《》∀〔〕━──\n¥〜∵∴́ ❤⇒→⇔\│←↑↓┃★☆「」・♪～〓◆◇■□▽△▲●〇▼◎．”“※♥́́́]'

  def __init__(self, description):
    # type:: unicode
    self.description = description
    self.temp_filter = None

  def parse(self):
    mb = MeCab.Tagger('mecabrc')


    ######################################
    #### Encode
    if isinstance(self.description, unicode):
      target_text = self.description.encode('utf-8')
    else:
      target_text = self.description
    ######################################

    res = mb.parseToNode(target_text)
    # pos_count:: parts of speech's count
    pos_count = {}
    words = {}
    documents = {}
    s = {}
    sentence_array = []
    sentence_length = 0
    tokens = []
    mecab_result = []
    while (res):

      token = MeCabToken(res.surface, res.feature)
      mecab_result.append(token)
      word = token.get_word()
      pos = token.get_pos()

      if (word in self.stop_words or pos == 'BOS/EOS'):
        res = res.next
        continue
      if (word == '。'):
        sentence_array.append(sentence_length)
        documents[u'sentences_count'] = documents.get(u'sentences_count', 0) + 1
        sentence_length = 0
      else:
        sentence_length += 1

        ######################################
        #### Decode
      word = word.decode('utf-8')
      pos = pos.decode('utf-8')
      ######################################

      pos_count[pos] = pos_count.get(pos, 0) + 1
      words[word] = words.get(word, 0) + 1
      tokens.append(word)
      documents[u'word_count'] = documents.get(u'word_count', 0) + 1
      res = res.next

    if (len(sentence_array) != 0):
      s['min'] = min(sentence_array)
      s['max'] = max(sentence_array)
      s['mean'] = np.mean(sentence_array)
      documents['sentence_stats'] = s

    self.pos_count = pos_count
    self.words = words
    self.documents = documents
    self.tokens = tokens
    self.mecab_result = mecab_result
    return self

  def select(self,
             word=None,
             pos=None,
             pos_detail=None,
             pos_detail2=None,
             pos_detail3=None,
             conjugate=None,
             conjugate_fmt=None,
             surface_base=None,
             reading=None,
             pronounce=None,
             ):
    return self.filter(remove=False,
                       word=word,
                       pos=pos,
                       pos_detail=pos_detail,
                       pos_detail2=pos_detail2,
                       pos_detail3=pos_detail3,
                       conjugate=conjugate,
                       conjugate_fmt=conjugate_fmt,
                       surface_base=surface_base,
                       reading=reading,
                       pronounce=pronounce)

  def reject(self,
             word=None,
             pos=None,
             pos_detail=None,
             pos_detail2=None,
             pos_detail3=None,
             conjugate=None,
             conjugate_fmt=None,
             surface_base=None,
             reading=None,
             pronounce=None,
             ):
    return self.filter(remove=True,
                       word=word,
                       pos=pos,
                       pos_detail=pos_detail,
                       pos_detail2=pos_detail2,
                       pos_detail3=pos_detail3,
                       conjugate=conjugate,
                       conjugate_fmt=conjugate_fmt,
                       surface_base=surface_base,
                       reading=reading,
                       pronounce=pronounce)

  def filter(self,
             remove=True,
             word=None,
             pos=None,
             pos_detail=None,
             pos_detail2=None,
             pos_detail3=None,
             conjugate=None,
             conjugate_fmt=None,
             surface_base=None,
             reading=None,
             pronounce=None,
             ):
    tokens = self._get_current_filter()

    arg_list = getargspec(self.filter)[0][2::]
    invoke_list = [arg for arg in arg_list if not eval(arg) is None]
    if remove:
      for invoke in invoke_list:
        tokens = [token for token in tokens if getattr(token, 'get_' + invoke)() not in eval(invoke)]
    else:
      for invoke in invoke_list:
        tokens = [token for token in tokens if getattr(token, 'get_' + invoke)() in eval(invoke)]

    self.temp_filter = tokens

    return self

  def replace(self, invoke_target, replace_from, replace_target, replace_to):
    tokens = self._get_current_filter()
    tokens = [self._get_token_after_change_attribute(token, replace_target, replace_to)
              if getattr(token, 'get_' + invoke_target)() == replace_from
              else token
              for token in tokens]

    self.temp_filter = tokens
    return self

  def _get_token_after_change_attribute(self, token, key, value):
    setattr(token, key, value)
    return token

  def convert(self, invoke_method, convert_utf8=True):
    tokens = self._get_current_filter()
    tokens = [getattr(token, 'get_' + invoke_method)()
              if hasattr(token, 'get_' + invoke_method)
              else ''
              for token in tokens]

    if convert_utf8:
      tokens = [token.decode('utf-8') for token in tokens]
    return tokens

  def get_temp_filter(self):
    return self.temp_filter

  def words(self):
    return self.words

  def description(self):
    return self.description

  def pos_count(self):
    return self.pos_count

  def documents(self):
    return self.documents

  def tokens(self):
    return self.tokens

  def toDict(self):
    ret = {}
    ret[u'words'] = self.words
    ret[u'pos_count'] = self.pos_count
    ret[u'documents'] = self.documents
    return ret

  def _get_current_filter(self):
    if self.get_temp_filter() is None:
      tokens = self.get_mecab_result()
    else:
      tokens = self.get_temp_filter()
    return tokens

  def get_mecab_result(self):
    return self.mecab_result


if __name__ == '__main__':
  description = u'全ての単語は、いずれかの品詞に所属すると考えられる。だが、実際にどの品詞に含まれるかと問われれば、分類に悩むことも多い。そのため現在では認知心理学の意味研究からプロトタイプという考え方が導入されて説明されている。'
  mecab = MeCabSeparator(description)
  mecab.parse()
  f = mecab.reject(word=['hoge']).select(pos=['名詞', '形容詞']).replace('pos_detail2', '組織', 'word', '***')

  tokens = f.convert('word')
  for w in tokens:
    print w, type(w)


