import newspaper


# url = 'http://money.cnn.com/markets'
# url = 'http://money.cnn.com/international'
# url = 'http://cnn.com'
url = 'https://www.usatoday.com/money/'


paper = newspaper.build(url, memoize_articles=False)

for article in paper.articles:

    # article.download()
    # article.parse()

    # if isinstance(article.title, str) and len(article.title) > 1:
    print('[{} ({})--> {}'.format(article.title,
                                  len(article.title), article.url[:60]))
    print('--------------------------------')

# for category in paper.category_urls():
#     print(category)


# for fd in paper.feed_urls():
#     print(fd)


# pops = newspaper.popular_urls()

# for pop in pops:
#     print(pop)
