import typer
import uvicorn

import crawler
import data_consumer

app = typer.Typer()


@app.command("crawl")
def crawl():
    print("Starting crawler from command line")
    crawler.start()


@app.command("data_consume")
def data_generator_function():
    print("Starting data consumer from command line")
    data_consumer.start()


@app.command("serve")
def serve():
    print("Starting FastAPI server")
    uvicorn.run("server.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    app()
