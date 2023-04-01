import os
from typing import List

from llama_index import GPTSimpleVectorIndex, SimpleDirectoryReader, LLMPredictor, PromptHelper  # , ServiceContext
from langchain import OpenAI
import logging
from decouple import config
from llama_index.response.schema import SourceNode, Response
from pydantic import BaseModel

os.environ['OPENAI_API_KEY'] = config("OPENAI_API_KEY")

max_input_size = 4096
num_output = 2000
max_chunk_overlap = 20
chunk_size_limit = 600

# text-davinci-003 offers the most tokens (around 4k)
llm_predictor = LLMPredictor(llm=OpenAI(temperature=0.5, model_name="text-davinci-003", max_tokens=num_output))
prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap, chunk_size_limit=chunk_size_limit)


class LlamaQuestionnaire:
    index = None

    def __init__(self):

        index_file = config('INDEX_FILE')
        data_directory = config('LOAD_DIR')
        logging.info('Use data directory: "%s" and index file: "%s"' % (data_directory, index_file))

        # Newer version still have bugs when counting the token.
        # service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)
        # index = GPTSimpleVectorIndex.from_documents(documents, service_context=service_context)
        if os.path.exists(index_file):
            self.index = GPTSimpleVectorIndex.load_from_disk(index_file)
        else:
            documents = SimpleDirectoryReader(data_directory).load_data()
            self.index = GPTSimpleVectorIndex(documents, llm_predictor=llm_predictor, prompt_helper=prompt_helper)
            self.index.save_to_disk(index_file)

    def ask_gpt(self, question: str):
        if self.index is None:
            raise Exception("Unable to work with null index")

        result = self.index.query(question, response_mode="compact")
        try:
            return GptResponse.from_response(result)
        except Exception as exception:
            logging.error('Unable to parse result "%s"' % result, exc_info=True)
            raise


class GptSource(BaseModel):
    source_text: str
    doc_id: str
    similarity: float

    @staticmethod
    def from_source_node(source_node: SourceNode):
        return GptSource(source_text=source_node.source_text,
                         doc_id=source_node.doc_id,
                         similarity=source_node.similarity)


class GptResponse(BaseModel):
    summary: str
    sources: List[GptSource]

    @staticmethod
    def from_response(response: Response):
        sources: List[GptSource] = []
        for element in response.source_nodes:
            sources.append(GptSource.from_source_node(element))

        return GptResponse(summary=response.response,
                           sources=sources)
