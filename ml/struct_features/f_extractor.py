"""
FeatureExtractor class

A FeatureExtractor instance maintains a connection to the neo4j database
in order to provide structural features on-the-fly.
"""
from py2neo import Graph


class FeatureExtractor(object):

    def __init__(self, uri, user='neo4j', passw='neo4j'):
        self.g = Graph(uri, user=user, password=passw)



    def get_thread(self, comment_name):
        """Comments of the ascending thread (path from comment_name to link_id)
        using the parent_id relation."""
        
        cursor = self.g.run(
            " MATCH p=(:Commentaire {nom: {cname}})-[:Parent*]->(:Post)"
            " RETURN NODES(p)",
            cname = comment_name)
        return [n['nom'] for n in cursor.evaluate()]



    def get_brothers(self, comment_name):
        """Comments with the same parent_id and a lower created_utc than the given comment"""

        cursor = self.g.run(
            " MATCH (c1:Commentaire {nom: {cname}})-[:Parent]->()<-[:Parent]-(c2:Commentaire)"
            " WHERE c1.creation > c2.creation"
            " RETURN c2.nom AS name",
            cname = comment_name)
        return [d['name'] for d in cursor.data()]



    def get_link_children(self, link_id):
        """Comments which have the given link as parent_id"""

        cursor = self.g.run(
            " MATCH (c:Commentaire)-[:Parent]->(:Post {nom: {lid}})"
            " RETURN c.nom AS name",
            lid = link_id)
        return [d['name'] for d in cursor.data()]



    def get_user_info(self, author):
        """Number of comments, cumulative score and number of gilded comments
        for the given author"""

        cursor = self.g.run(
            " MATCH (u:Auteur {nom_auteur: {author}})-[:ACree]->(c:Commentaire)"
            " RETURN COUNT(c) AS n_comments, SUM(c.score) AS n_score, SUM(c.gilded) AS n_gilded",
            author = author)
        return cursor.data()[0]

    

    def execute(self, cypher_query, **kwargs):
        """Execute a cypher query"""

        cursor = self.g.run(cypher_query, **kwargs)
        return cursor.data()

    


if __name__ == "__main__":

    # Example run

    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Example run of the neo4j feature extractor")
    parser.add_argument('uri', type=str, help="DB's URI (eg. bolt://localhost:7687)")
    parser.add_argument('user', type=str, help="User name")
    parser.add_argument('passw', type=str, help="Password")

    args = parser.parse_args()


    # Sample queries
    cname = 't1_cqunfnx'
    linkid = 't3_34gb9e'
    author = 'ICDT'
    
    fx = FeatureExtractor(args.uri, args.user, args.passw)

    print()
    print("fx.get_thread('%s') ="%(cname),
          fx.get_thread(cname))
    print()
    print("fx.get_brothers('%s') ="%(cname),
          fx.get_brothers(cname))
    print()
    print("fx.get_link_children('%s') ="%(linkid),
          fx.get_link_children(linkid))
    print()
    print("fx.get_user_info('%s') ="%(author),
          fx.get_user_info(author))
    print()
    print("fx.execute('MATCH (s:Subreddit) RETURN id(s), s.nom LIMIT 5') = ",
          fx.execute('MATCH (s:Subreddit) RETURN id(s), s.nom LIMIT 5'))

