# Preconditions

TODO: Separate index filename and path could be useful (s3)
TODO: Separate data directory and path could be useful (s3)

Environment variables:
- INDEX_FILE: Fullpath of the desired index file. Will be created if necessary.
- LOAD_DIR: Directory of all input documents (word, pdf, csv, ...)
- OPENAI_API_KEY: Your Open API key.

- DATA_PROVIDER: Optional; Either s3 or local (default)
- S3_BUCKET_NAME: Mandatory when working with S3 as data provider

# Run
Dev: `uvicorn server:app --reload`

# Test it
`curl http://127.0.0.1:8000/gpt\?question\=whatever` (pipe it to `jq` make it readable :-)

`curl -X POST http://127.0.0.1:8000/gpt\/index?operation\=RECREATE` (pipe it to `jq` make it readable :-)

# API Spec
Default Swagger-UI: http://127.0.0.1:8000/docs
Alternative provided by ReDoc: http://127.0.0.1:8000/redoc