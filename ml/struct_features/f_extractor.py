from py2neo import Graph, Path



class FeatureExtractor(object):

    def __init__(self, uri, passw=None):
        self.g = Graph(uri, password=passw)

    def get_thread(self, comment_name):
        cursor = self.g.run(
            " MATCH p=(:Commentaire {nom: {cname}})-[:Parent*]->(:Post)"
            " RETURN NODES(p)",
            cname = comment_name)
        return [n['nom'] for n in cursor.evaluate()]

    def get_brothers(self, comment_name):
        cursor = self.g.run(
            " MATCH (c1:Commentaire {nom: {cname}})-[:Parent]->()<-[:Parent]-(c2:Commentaire)"
            " WHERE c1.creation > c2.creation"
            " RETURN c2.nom AS name",
            cname = comment_name)
        return [d['name'] for d in cursor.data()]

    def get_link_children(self, link_id):
        cursor = self.g.run(
            " MATCH (c:Commentaire)-[:Parent]->(:Post {nom: {lid}})"
            " RETURN c.nom AS name",
            lid = link_id)
        return [d['name'] for d in cursor.data()]

    def get_user_info(self, author):
        cursor = self.g.run(
            " MATCH (u:Auteur {nom_auteur: {author}})-[:ACree]->(c:Commentaire)"
            " RETURN COUNT(c) AS n_comments, SUM(c.score) AS n_score, SUM(c.gilded) AS n_gilded",
            author = author)
        return cursor.data()[0]


    def get_all_threads(self):
        cursor = self.g.run("MATCH p=(:Commentaire)-[:Parent*]->(:Post)"
                            "RETURN NODES(p)")
        return [n['nom'] for n in cursor.evaluate()]

    


if __name__ == "__main__":

    # Read command-line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Extract features from the Neo4j database")
    parser.add_argument('uri', type=str, help="URI of the database")
    parser.add_argument('passw', type=str, help="Password of the database")

    args = parser.parse_args()


    # Sample queries
    cname = 't1_cqunfnx'
    linkid = 't3_34gb9e'
    author = 'ICDT'
    
    fx = FeatureExtractor(args.uri, args.passw)
    print(fx.get_thread(cname))
    print(fx.get_brothers(cname))
    print(fx.get_link_children(linkid))
    print(fx.get_user_info(author))
