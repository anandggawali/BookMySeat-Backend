def serialize_mongo(document):

    if document and "_id" in document:
        del document["_id"]

    return document


def serialize_mongo_list(documents):

    return [
        serialize_mongo(doc)
        for doc in documents
    ]