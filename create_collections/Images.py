# Import necessary libraries
import weaviate
import weaviate.classes as wvc
from weaviate.util import generate_uuid5
from weaviate import WeaviateClient
from weaviate.collections.classes.batch import BatchObjectReturn
import base64
from pathlib import Path
from scripts.get_metadata import createFileRecords 


def define_collection_images(client: WeaviateClient, collection_name: str = 'images') -> bool:
    """
    Define a collection for images in Weaviate.

    Args:
        client (WeaviateClient): The Weaviate client.
        collection_name (str, optional): The name of the collection. Defaults to 'images'.

    Returns:
        bool: True if collection creation is successful, otherwise False.
    """
    client.collections.create(
        name=collection_name,
        description="Image collection",
        vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_bind(
            image_fields=[wvc.config.Multi2VecField(name='image', weight=0.95)],
            vectorize_collection_name=False),
        generative_config=wvc.config.Configure.Generative.openai(),
        properties=[
            wvc.Property(
                name="image",
                data_type=wvc.config.DataType.BLOB,
            ),
            wvc.Property(
                name="filename",
                data_type=wvc.config.DataType.TEXT,
                skip_vectorization=True,  # Not vectorizing for demonstrative purposes
            ),
            wvc.Property(
                name="date_created",
                data_type=wvc.config.DataType.DATE,
            ),
            wvc.Property(
                name="date_modified",
                data_type=wvc.config.DataType.DATE,
            ),
            wvc.Property(
                name="file_size",
                data_type=wvc.config.DataType.TEXT,
            ),
            wvc.Property(
                name="author",
                data_type=wvc.config.DataType.TEXT,
            ),
        ],
    )
    return True


def import_data_images(client: WeaviateClient, collection_name: str = 'images') -> BatchObjectReturn:
    """
    Import image data into the specified collection in Weaviate.

    Args:
        client (WeaviateClient): The Weaviate client.
        collection_name (str, optional): The name of the collection. Defaults to 'images'.

    Returns:
        BatchObjectReturn: The response object containing information about the import process.
    """
    mm_coll = client.collections.get(collection_name)
    imgdir = Path("data/images")

    data_objs = list()

    for f in imgdir.glob("*.jpg"):
        b64img = base64.b64encode(f.read_bytes()).decode()
        meta_data = createFileRecords(f)

        data_props = {
            "image": b64img,
            "filename": f.name,
            "date_created": meta_data['Creation Date'].isoformat(),
            "date_modified": meta_data['Modified Date'].isoformat(),
            "file_size": meta_data['Size (KB)'],
            "author": '0'
        }

        data_obj = wvc.data.DataObject(
            properties=data_props, uuid=generate_uuid5(f.name)
        )
        data_objs.append(data_obj)

    insert_response = mm_coll.data.insert_many(data_objs)

    print(f"{len(insert_response.all_responses)} insertions complete.")
    print(f"{len(insert_response.errors)} errors within.")
    if insert_response.has_errors:
        for e in insert_response.errors:
            print(e)

    return insert_response


# def define_collection_images(client: WeaviateClient, collection_name: str = 'images') -> bool:
#     client.collections.create(
#         name=collection_name,
#         description="Image collection",
#         vectorizer_config=wvc.config.Configure.Vectorizer.multi2vec_clip(
#             image_fields=[wvc.config.Multi2VecField(name='image', weight=0.95)],
#             text_fields=[wvc.config.Multi2VecField(name='filedesc', weight=0.05)],
#             vectorize_collection_name=False
#         ),
#         generative_config=wvc.config.Configure.Generative.openai(),
#         properties=[
#             wvc.Property(
#                 name="image",
#                 data_type=wvc.config.DataType.BLOB,
#             ),
#             wvc.Property(
#                 name="filename",
#                 data_type=wvc.config.DataType.TEXT,
#                 skip_vectorization=True,  # Not vectorizing for demonstrative purposes
#             ),
#             wvc.Property(
#                 name="filedesc",
#                 data_type=wvc.config.DataType.TEXT,
#                 skip_vectorization=True,  # Not vectorizing for demonstrative purposes
#             ),
#         ],
#     )
#     return True