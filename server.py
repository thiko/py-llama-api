import logging as log
from enum import Enum

from fastapi import FastAPI, Query

from llama import LlamaQuestionnaire

app = FastAPI(
    title="LLAMA Index API Wrapper for simple document based use-cases",
    description="Builds an index based on a given directory and provides a simple-to-use endpoint to \
     query the content of these using GPT 3.5",
    version="0.0.1",
    contact={
        "name": "Me!",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)
llama_api = LlamaQuestionnaire()


class IndexOperation(str, Enum):
    RECREATE = "RECREATE"


@app.get("/gpt", description="Ask a question to GPT")
async def ask_gpt(question: str):
    global llama_api
    log.info("Got question: " + question)
    return llama_api.ask_gpt(question)


@app.post("/gpt/index", description="Perform operations on the current index")
async def person_index_operation(operation: IndexOperation = Query(...)):
    global llama_api
    if operation == IndexOperation.RECREATE:
        log.info("going to recreate index")
        llama_api.delete_index()
        llama_api = LlamaQuestionnaire()
        return {"success:true"}
    else:
        raise ValueError(
            "No handling for operation implemented: %s" % operation
        )
