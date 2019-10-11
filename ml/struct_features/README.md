# Social / structural feature extraction

## Usage

    # Test queries
    python3 f_extractor.py db_uri user password
    # E.g.: python3 f_extractor.py bolt://localhost:7687 neo4j neo4j

## Usage (FeatureExtractor class)

    # Init fx
    from f_extractor import FeatureExtractor as FX
    fx = FX(db_uri, username, password)

    # All ancestors
    fx.get_thread(comment_name)

    # Brothers with previous 'created_utc'
    fx.get_brothers(comment_name)

    # Comments of a link with depth=0
    fx.get_link_children(link_id)

    # User infos: n_comments, n_score, n_gilded
    fx.get_user_info(author)

