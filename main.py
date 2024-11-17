import typer

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


if __name__ == "__main__":
    app()
