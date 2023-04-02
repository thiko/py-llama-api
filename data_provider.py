import logging
import os
from abc import ABC, abstractmethod
from typing import List

from decouple import config
from llama_index import Document, GPTSimpleVectorIndex, SimpleDirectoryReader

from s3_bucket import S3Bucket


class LlamaDataProvider(ABC):
    def __init__(self) -> None:
        super().__init__()
        self.index_file = config("INDEX_FILE")
        self.data_directory = config("LOAD_DIR")
        logging.info(
            'Use data directory: "%s" and index file: "%s"'
            % (self.data_directory, self.index_file)
        )

    @abstractmethod
    def get_index_file(self) -> GPTSimpleVectorIndex:
        pass

    @abstractmethod
    def get_data_directory(self) -> List[Document]:
        pass

    @abstractmethod
    def save_index(self, index: GPTSimpleVectorIndex) -> None:
        pass

    @abstractmethod
    def delete_index(self) -> None:
        pass


class LocalDataProvider(LlamaDataProvider):
    # overwrites
    def get_index_file(self) -> GPTSimpleVectorIndex:
        if not os.path.exists(self.index_file):
            return None

        logging.info("Load index from storage %s" % self.index_file)
        return GPTSimpleVectorIndex.load_from_disk(self.index_file)

    # overwrites
    def get_data_directory(self) -> List[Document]:
        if not os.path.exists(self.data_directory):
            logging.warning(
                "Unable to load data directory - is does not exists: %s "
                % self.data_directory
            )
            return List()

        return SimpleDirectoryReader(self.data_directory).load_data()

    # overwrites
    def save_index(self, index: GPTSimpleVectorIndex) -> None:
        index.save_to_disk(self.index_file)

    def delete_index(self) -> None:
        os.remove(self.index_file)
        logging.info("Index %s deleted " % self.index_file)


class S3DataProvider(LlamaDataProvider):
    def __init__(self) -> None:
        super().__init__()
        self.s3 = S3Bucket(config("S3_BUCKET_NAME"))

    # overwrites
    def get_index_file(self) -> GPTSimpleVectorIndex:
        local_filepath = os.path.join("/tmp", self.index_file)
        if self.s3.download_file(self.index_file, local_filepath):
            return GPTSimpleVectorIndex.load_from_disk(local_filepath)

        return None

    # overwrites
    def get_data_directory(self) -> List[Document]:
        local_datapath = os.path.join("/tmp", self.index_file)

        self.s3.download_s3_folder(self.data_directory, local_datapath)
        return SimpleDirectoryReader(local_datapath).load_data()

    # overwrites
    def delete_index(self) -> None:
        self.s3.remove_file(self.index_file)
        raise Exception("S3 Data Provider is not implemented yet")
