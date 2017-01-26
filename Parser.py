# -*- encoding: utf-8 -*-

import CaboCha
from mecab_token import MeCabToken
import operator
from mecab import MeCabSeparator

class CabochaParser:
    def __init__(self):
        self.parser = CaboCha.Parser()
        self.children = []
        self.parents = []  

    def parse(self, text):
        self.text = text
        self.tree = self.parser.parse(text)
        return self

    def build(self):

        id_to_chunk = {}
        chunk_id    = 0
        nodes = []
        for token_id in xrange(self.tree.size()):
           token = self.tree.token(token_id)
           mecab_token = MeCabToken(token.surface, token_feature)
            
           has_chunk = token.chunk is not None

           if has_chunk:
               id_to_chunk[chunk_id] = token.chunk
               chunk_id += 1

           nodes.append(Node(token_id, mecab_token, None))
           
        for chunk_id, chunk in id_to_chunk.items():
            pass            

    def build_from_string(self):
        '''
こんな文を想定
        * 0 5D 0/1 -0.742128
太郎	名詞,固有名詞,人名,名,*,*,太郎,タロウ,タロー
は	助詞,係助詞,*,*,*,*,は,ハ,ワ
* 1 2D 0/1 1.700175
花子	名詞,固有名詞,人名,名,*,*,花子,ハナコ,ハナコ
が	助詞,格助詞,一般,*,*,*,が,ガ,ガ
* 2 3D 0/2 1.825021
読ん	動詞,自立,*,*,五段・マ行,連用タ接続,読む,ヨン,ヨン
で	助詞,接続助詞,*,*,*,*,で,デ,デ
いる	動詞,非自立,*,*,一段,基本形,いる,イル,イル
* 3 5D 0/1 -0.742128
本	名詞,一般,*,*,*,*,本,ホン,ホン
を	助詞,格助詞,一般,*,*,*,を,ヲ,ヲ
* 4 5D 1/2 -0.742128
次	名詞,一般,*,*,*,*,次,ツギ,ツギ
郎	名詞,一般,*,*,*,*,郎,ロウ,ロー
に	助詞,格助詞,一般,*,*,*,に,ニ,ニ
* 5 -1D 0/1 0.000000
渡し	動詞,自立,*,*,五段・サ行,連用形,渡す,ワタシ,ワタシ
た	助動詞,*,*,*,特殊・タ,基本形,た,タ,タ

        '''

        chunks = self.tree.toString(CaboCha.FORMAT_LATTICE)[1:].split("\n*")
        chunk_id = chunk_parent = None
        root_chunk_id = -1

        token_id = 0
        tokens   = []
        nodes    = []

        for chunk in chunks:
            chunk_contents    = chunk.split("\n")
            chunk_information = chunk_contents[0].split()
            chunk_body        = [body.split() for body in chunk_contents[1:]]
            

            chunk_id = int(chunk_information[0])
            chunk_parent = int(chunk_information[1].replace('D',''))
            
            if chunk_parent == -1:
                root_chunk_id = chunk_id
            
            token_length = token_id + len(chunk_body)
            token_ids = range(token_id, token_length)
            token_id = token_length 


            mecab_tokens = [(tid, MeCabToken(body[0], body[1]), chunk_id, chunk_parent) 
                    for tid, body in zip(token_ids, chunk_body) if len(body) == 2]

            tokens.extend(mecab_tokens)


        token_length = len(tokens)

        for idx in range(token_length + 1) :
            current_token = tokens[idx]

            current_token_id  = current_token[0]
            current_body      = current_token[1]
            current_chunk_id  = current_token[2]
            current_parent_id = current_token[3]

            if idx + 1 == token_length:
                nodes.append(Node(current_token_id , current_body , -1, current_chunk_id))
                break


            next_token    = tokens[idx + 1]
            next_token_id = next_token[0]
            next_chunk_id = next_token[2]


            if current_chunk_id == next_chunk_id:
                node = Node(current_token_id, current_body, next_token_id, current_chunk_id)


            else:
                next_chunk_tokenids = [token[0] for token in tokens if token[2] == current_parent_id]
                next_chunk_tokenids.sort()
                next_token_id = next_chunk_tokenids[0] 
                
                node = Node(current_token_id, current_body, next_token_id, current_chunk_id)


                
            nodes.append(node)

        self.nodes = {node.id: node for node in nodes}

        def _build_children():

            # build children
            for node_id, node in self.nodes.items():
                parent_id = node.parent
                if parent_id == -1:
                    continue
                parent_node = self.nodes[parent_id]
                if parent_node.chunk_id != node.chunk_id:
                    parent_node.chunk_children.append(node.chunk_id)

                self.nodes[parent_id].children.append(node_id)

                


        _build_children()

        return self


    def search_word_to_id(self, word):
        tokens = MeCabSeparator(word).parse().convert('word')[1:-1]

        node_search_result = [node.id for node in self.nodes.values() if node.get_body('word') in tokens]

        return [node_id 
                for i, node_id in enumerate(node_search_result[:-1]) 
                if node_search_result[i+1] == node_id + 1]



    def search_partialtree(self, token, level, to='root'):
        token_ids = self.search_word_to_id(token)

        if to == 'root':
            for token_id in token_ids[:-1]:
                self.parents.append(self.nodes[token_id]) 
            return self.search_parents(token_ids[-1], level) 

        elif to == 'leaf':
            for token_id in token_ids[:-1]:
                self.children.append(self.nodes[token_id]) 
            return self.search_children(token_ids[-1], level)
    
    
    def search_children(self, token_id, chunk_level):

        if chunk_level == 0:
            self.children.sort(key=operator.attrgetter('id'))
            return self.children

        current_node = self.nodes[token_id]
        self.children.append(current_node)

        # Search chunk nodal point
        while len(current_node.chunk_children) != 0:
            next_node_id = current_node.children[0]
            current_node = self.nodes[next_node_id]
            self.children.append(current_node)
        
        for child in current_node.children:
            self.search_children(child, chunk_level - 1)


        self.children.sort(key=operator.attrgetter('id'))
        return self.children

    
    def search_parents(self, token_id, chunk_level):
        current_node = self.nodes[token_id]
        level = 0
        self.parents.append(current_node)
        

        while current_node.parent != -1:
            next_node_id = current_node.parent
            next_node    = self.nodes[next_node_id]
            if current_node.chunk_id != next_node.chunk_id:
                level += 1
                
            if level == chunk_level:
                break

            current_node = next_node
            self.parents.append(current_node)
        self.parents.sort(key=operator.attrgetter('id'))
        
        def remove_dulpicate_item_from_list(l):
            resl = [l[0]]

            for item in l[1:]:
                if resl[-1] != item:
                    resl.append(item)

            return resl
            
        self.parents = remove_dulpicate_item_from_list(self.parents)
        
        return self.parents


    def convert(self, nodes, method):
        return [node.get_body(method) for node in nodes]

       

class Node: 
    def __init__(self, id, body, parent, chunk_id):
        self.id = id
        self.body = body
        self.parent = parent
        self.children = []
        self.chunk_id = chunk_id
        self.chunk_children = []

    def is_root(self):
        return self.parent == -1
    
    def get_body(self, method):
        return self.body.get(method)

    def print_node(self):
        print '''
        ID: {}
        chunk ID: {}
        body: {}
        parent: {}
        children: {}
        chunk_children: {}
        '''.format(self.id, self.chunk_id, self.get_body('word').encode('utf-8'), self.parent, self.children, self.chunk_children)
   


def main():
    sentence = '太郎は花子が読んでいる本を二郎に渡した'
    parser   = CabochaParser()
    parser.parse(sentence).build_from_string()
    
    partial_tree = parser.search_partialtree('読んでいる',3, to='root')
    print ''.join(parser.convert(partial_tree, 'word'))

    children = parser.search_children(13,2)
    print ''.join(parser.convert(children, 'word'))
    
    parents = parser.search_parents(2,3)
    print ''.join(parser.convert(parents, 'word'))




if __name__ == '__main__':
    main()

