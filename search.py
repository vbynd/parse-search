from elasticsearch import Elasticsearch
from beautifultable import BeautifulTable
from wiki_ru_wordnet import WikiWordnet
import json
import conf
from enum import IntEnum


class SearchOption(IntEnum):
    AUTHOR = 1
    TAG = 2
    TITLE = 3
    ALL_FIELDS = 4


class Searcher:
    def __init__(self):
        self.es = Elasticsearch()
        self.ww = WikiWordnet()
        self.data_path = conf.data_path
        self.index_name = 'poems'

    def create_index(self):
        self.es.indices.create(
            index=self.index_name,
            body={
                'settings': {
                    'number_of_shards': 1,
                    'number_of_replicas': 0,
                    'analysis': {
                        'filter': {
                            'ru_stop': {
                                'type': 'stop',
                                'stopwords': '_russian_'
                            }
                        },
                        'analyzer': {
                            'default': {
                                'char_filter': ['html_strip'],
                                'tokenizer': 'standard',
                                'filter': ['lowercase', 'ru_stop']
                            }
                        }
                    }
                }
            },
            ignore=400
        )

    def add_to_index(self):
        with open(self.data_path, 'r') as input_stream:
            data = json.loads(input_stream.read())
            print(data)
            k = 1
            for item in data:
                self.es.index(index=self.index_name, id=k, body=item)
                k += 1

    def add_synonyms(self, query):
        tmp_list = list()
        result_tokens = self.es.indices.analyze(index=self.index_name, body={
            'analyzer': 'default',
            'text': [query]
        })
        for token in result_tokens['tokens']:
            tmp_list.append(token['token'])
            syn_sets = self.ww.get_synsets(token['token'])
            if syn_sets:
                for synonym in syn_sets[0].get_words():
                    word = synonym.lemma()
                    if tmp_list.count(word) == 0:
                        tmp_list.append(word)
        return ' '.join(tmp_list)

    def find_by(self, find_option, query):
        if find_option == SearchOption.AUTHOR:
            fields_list = ['author']
        if find_option == SearchOption.TAG:
            fields_list = ['tag']
        elif find_option == SearchOption.TITLE:
            fields_list = ['title']
        elif find_option == SearchOption.ALL_FIELDS:
            fields_list = ['author', 'tag', 'title']

        query_body = {
            'query': {
                'bool': {
                    'should': [
                        {
                            'multi_match': {
                                'query': query,
                                'analyzer': 'default',
                                'fields': fields_list,
                            }
                        },
                    ],
                }
            }
        }
        return self.es.search(index='poems', body=query_body)

    def clear(self):
        for key in self.es.indices.get_alias().keys():
            self.es.indices.delete(index=key)


if __name__ == '__main__':
    searcher = Searcher()
    searcher.create_index()
    searcher.add_to_index()

    option = '-1'
    while option != '0':
        option = int(input('\nВыполнить поиск по:'
                           '\n1 - автору'
                           '\n2 - тегу'
                           '\n3 - названию'
                           '\n4 - по всем полям'
                           '\n0 - завершить работу'
                           '\nВаш выбор: '))

        if option == 0:
            searcher.clear()
            exit(0)
        elif option in [1, 2, 3, 4]:
            new_query = searcher.add_synonyms(input('\nВведите фразу для поиска: '))
            print(f'\nВыполяется поиск по данным словам: {new_query}')
            result = searcher.find_by(option, new_query)

            hits_len = len(result['hits']['hits'])
            print('Всего совпадений:', hits_len)
            if hits_len > 0:
                table = BeautifulTable(maxwidth=1000)
                table.set_style(BeautifulTable.STYLE_BOX)

                for i in range(hits_len):
                    table.rows.append([i + 1,
                                       result['hits']['hits'][i]['_score'],
                                       result['hits']['hits'][i]['_source']['author'],
                                       result['hits']['hits'][i]['_source']['tag'],
                                       result['hits']['hits'][i]['_source']['title'],
                                       result['hits']['hits'][i]['_source']['href']])
                table.columns.header = ["№", "Score", "Author", "tag", "title","URL"]
                print(table)
        else:
            print('\nВведён некорректный режим работы!')
