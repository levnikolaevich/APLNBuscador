import gradio as gr
from rag import RagFAISS
from chat_llm import Chat
import tracemalloc
import time
import os

tracemalloc.start()

global rag_faiss, chat_llm, chat_history, isInited
rag_faiss = None
chat_llm = None
chat_history = []
isInited = False

def initialize_global_variables():
    print("initialize_global_variables started")
    global rag_faiss, chat_llm

    if rag_faiss is None:
        rag_faiss = initialize_text_processing()

    if chat_llm is None:
        chat_llm = Chat()

    print("initialize_global_variables finished")


def initialize_text_processing(modelST_id='avsolatorio/GIST-small-Embedding-v0'):
    """
    Initializes text processing by creating a FAISS index from PDF files in the given folder.

    Args:
        modelST_id (str): name of the model for SentenceTransformer

    Returns:
        RagFAISS: An initialized instance of the RagFAISS class.
    """
    rag_faiss_db = RagFAISS(modelST_id)
    text2vec = rag_faiss_db.extract_text_to_paragraphs()
    rag_faiss_db.read_or_create_faiss_index(text2vec)
    return rag_faiss_db


def execute_text(rag_faiss_db, query):
    """
    Executes a text query using the given RagFAISS instance.

    Args:
        rag_faiss_db (RagFAISS): The initialized RagFAISS instance.
        query (str): The text query to process.
    """
    D, I, RAG_context = rag_faiss_db.search(query)
    print(I)
    print(D)
    print(RAG_context)

def chat_with_ai(query):
    global rag_faiss, chat_llm, chat_history
    context = ""

    D, I, RAG_context = rag_faiss.search(query, k=3)
    context_str = "\n".join(RAG_context)

    context += "\n\nSite content:\n"
    context += "\n\n" + context_str + "\n"

    final_prompt = f"Based on your knowledge and the following detailed context, please provide a comprehensive answer:\n\nCONTEXT:\n{context}\n\nQUESTION:\n{query}"
    print("final_prompt:")
    print(final_prompt)
    start_time = time.time()
    response = chat_llm.get_answer(final_prompt, 200)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to get the response: {elapsed_time} seconds")

    chat_history.append("\n Q: " + query)
    chat_history.append("\n A: " + response)
    chat_history.append("\n ------------------------")

    output = ''
    for sentence in chat_history:
        output += sentence
    return output


def get_website_context(site_url):
    context = ""

    return context

def main():
    with gr.Blocks() as buscador:
        gr.Markdown("Crawl website")
        with gr.Row():
            with gr.Column():
                link = gr.Textbox(
                    label="Enter link to website: (ex. https://www.ua.es/ )")
                with gr.Column():
                    submit_button_yt = gr.Button("Download audio")
                    # Process the YouTube link when the submit button is clicked.
                    response = gr.Textbox(label="Video info:", interactive=False, lines=1)
                    submit_button_yt.click(fn=get_website_context, inputs=[link], outputs=[response])

        gr.Markdown("Chat with Website Content")
        with gr.Row():
            with gr.Column():
                query = gr.Textbox(label="Enter your query:")
                submit_button = gr.Button("To ask")
                response = gr.Textbox(label="Chat History:", interactive=False, lines=10)
                # Process the user query when the submit button is clicked.
                submit_button.click(fn=chat_with_ai, inputs=[query], outputs=[response])

    buscador.launch()


if __name__ == '__main__':
    if not isInited:
        initialize_global_variables()
        isInited = True

    main()
