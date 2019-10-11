import lucene
from org.apache.lucene.analysis.core import KeywordAnalyzer, WhitespaceAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser



def escape_lucene_special_chars(string):
    for c in ['//', '+', '-', '&&', '||', '!', '(', ')', '{', '}', '[', ']',
              '^', '"', '~', '*', '?', ':', '/']:
        string = string.replace(c, ' ')
    return string




def user_profile(searcher, author):
    """Builds an user profile {comments, links, subreddits}"""

    analyzer = WhitespaceAnalyzer()
    query = QueryParser("author", analyzer).parse('"%s"'%author)
    scoreDocs = searcher.search(query, 1000).scoreDocs

    profile = {'comments': set(), 'links': set(), 'subreddits': set()}
    for sd in scoreDocs:
        doc = searcher.doc(sd.doc)
        profile['comments'].add(doc.get('name'))
        profile['links'].add(doc.get('link_id'))
        profile['subreddits'].add(doc.get('subreddit'))

    return profile

def reformulate_query(initial_query, searcher, analyzer, user_name):
    """reformulate query using profile similarity"""
    
    profile = user_profile(searcher, user_name)

    weights = [1, 0.05, 0.03, 0.02]

    command = '(%s)^%d'%(escape_lucene_special_chars(initial_query), weights[0])

    # Vocabulary of his own comments
    kws = " ".join(profile['comments'])
    if len(kws.replace(' ','')) > 1:
        q_comm = QueryParser("name", analyzer).parse(kws)
        scoreDocs = searcher.search(q_comm, 1000).scoreDocs
        w_comm = " ".join([searcher.doc(sd.doc).get('body') for sd in scoreDocs])
        command = '(%s)^0.05'%(escape_lucene_special_chars(w_comm), weights[1])

    # Vocabulary of the links he posts on
    kws = " ".join(profile['links'])
    if len(kws.replace(' ','')) > 0:
        q_link = QueryParser("link_id", analyzer).parse(" ".join(profile['links']))
        scoreDocs = searcher.search(q_link, 1000).scoreDocs
        w_link = " ".join([searcher.doc(sd.doc).get('body') for sd in scoreDocs])
        command = '(%s)^0.03'%(escape_lucene_special_chars(w_link), weights[2])

    # Vocabulary of the subreddit he posts on
    kws = " ".join(profile['subreddits'])
    if len(kws.replace(' ','')) > 0:
        q_subr = QueryParser("subreddit", analyzer).parse(" ".join(profile['subreddits']))
        scoreDocs = searcher.search(q_link, 1000).scoreDocs
        w_subr = " ".join([searcher.doc(sd.doc).get('body') for sd in scoreDocs])
        command = '(%s)^0.01'%(escape_lucene_special_chars(w_subr), weights[3])



    # Reformulated query. Weights are not justified
    reformulated_query = QueryParser("body", analyzer).parse(command)
    return reformulated_query
