import logging
import os
from typing import List

from decouple import config
from langchain import OpenAI
from llama_index import (
    GPTSimpleVectorIndex,
    LLMPredictor,
    PromptHelper,
    SimpleDirectoryReader,
)
from llama_index.response.schema import Response, SourceNode
from pydantic import BaseModel

from data_provider import LlamaDataProvider, LocalDataProvider, S3DataProvider

os.environ["OPENAI_API_KEY"] = config("OPENAI_API_KEY")

max_input_size = 4096
num_output = 2000
max_chunk_overlap = 20
chunk_size_limit = 600

# text-davinci-003 offers the most tokens (around 4k)
llm_predictor = LLMPredictor(
    llm=OpenAI(
        temperature=0.5, model_name="text-davinci-003", max_tokens=num_output
    )
)
prompt_helper = PromptHelper(
    max_input_size,
    num_output,
    max_chunk_overlap,
    chunk_size_limit=chunk_size_limit,
)


class LlamaQuestionnaire:
    index: GPTSimpleVectorIndex = None

    def __init__(self):
        self.data_provider: LlamaDataProvider = self.__get_data_provider()
        self.index = self.__load_index_from_data_provider()

    def ask_gpt(self, question: str):
        if self.index is None:
            raise Exception("Unable to work with null index")

        result = self.index.query(question, response_mode="compact")
        try:
            return GptResponse.from_response(result)
        except Exception:
            logging.error(
                'Unable to parse result "%s"' % result, exc_info=True
            )
            raise

    def delete_index(self):
        self.data_provider.delete_index()

    def __get_data_provider(self) -> LlamaDataProvider:
        data_provider_config = config(
            "DATA_PROVIDER", default="local", cast=str
        )

        is_s3_provider = (
            data_provider_config != None
            and data_provider_config.lower() == "s3"
        )

        if is_s3_provider:
            return S3DataProvider()

        return LocalDataProvider()

    # Newer version still have bugs when counting the token.
    # service_context = ServiceContext.from_defaults(
    #   llm_predictor=llm_predictor, prompt_helper=prompt_helper)
    # index = GPTSimpleVectorIndex.from_documents(documents,
    #   service_context=service_context)
    def __load_index_from_data_provider(self) -> GPTSimpleVectorIndex:
        index = self.data_provider.get_index_file()
        if self.index is not None:
            return index

        documents = self.data_provider.get_data_directory()
        logging.info("Create index from stored documents")
        index = GPTSimpleVectorIndex(
            documents,
            llm_predictor=llm_predictor,
            prompt_helper=prompt_helper,
        )
        self.data_provider.save_index(index)
        return index


class GptSource(BaseModel):
    source_text: str
    doc_id: str
    similarity: float

    @staticmethod
    def from_source_node(source_node: SourceNode):
        return GptSource(
            source_text=source_node.source_text,
            doc_id=source_node.doc_id,
            similarity=source_node.similarity,
        )


class GptResponse(BaseModel):
    summary: str
    sources: List[GptSource]

    @staticmethod
    def from_response(response: Response):
        sources: List[GptSource] = []
        for element in response.source_nodes:
            sources.append(GptSource.from_source_node(element))

        return GptResponse(summary=response.response, sources=sources)
