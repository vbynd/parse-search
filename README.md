# parser-search
Parser and search for culture.ru
# Парсинг
Для парсинга использовалась библиотека BeautifulSoup. 
Для запуска парсера запустите файл parser.py, результат парсинга вы можете найти в файле poems.json.
# Поиск
Для поиска использовалась библиотека Elasticsearch.
Для запуска поиска необходимо установить серверную часть ElasticSearch по ссылке (https://www.elastic.co/downloads/elasticsearch) и запустить файл ./elasticsearch-7.10.2/bin/elasticsearch.bat. Далее указать путь к файлу poems.json в файле conf.py. Далее запустить search.py
# Оценка качества ранжирования
Оценки качества ранжирования для разных запросов приведены по ссылке (https://docs.google.com/spreadsheets/d/1iQd_AyfbPea1trMmFoDMRVXr_IYDWtDM96Dy5X5Ek7c/edit?usp=sharing)
