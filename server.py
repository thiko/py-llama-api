import logging as log

from fastapi import FastAPI

from llama import LlamaQuestionnaire

app = FastAPI()
llama_api = LlamaQuestionnaire()


@app.get("/gpt")
async def ask_gpt(question: str):
    log.info("Got question: " + question)
    return llama_api.ask_gpt(question)
