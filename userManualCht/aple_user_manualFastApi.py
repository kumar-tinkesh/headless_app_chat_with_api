# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# from aple_user_manual import EndpointRetriever  # Ensure this module is accessible
# import uvicorn

# # Initialize FastAPI app
# app = FastAPI()

# # Initialize the retriever
# text_folder_path = "/Users/macbook/Desktop/headless_app_chat_with_api/userManualCht/scraped_texts"
# retriever = EndpointRetriever(text_folder_path)
# retriever.vector_embedding()

# # Define request model
# class QueryRequest(BaseModel):
#     query: str

# @app.post("/query")
# def get_response(request: QueryRequest):
#     try:
#         response = retriever.process_query(request.query)
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.get("/")
# def root():
#     return {"message": "API is running. Send a POST request to /query with {'query': 'your question'}"}

# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=3000)


from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from aple_user_manual import EndpointRetriever  # Ensure this module is accessible
import uvicorn
from fastapi.staticfiles import StaticFiles  # Import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)
app.mount("/Users/macbook/Desktop/headless_app_chat_with_api/userManualCht/static", StaticFiles(directory="static"), name="static")

# Initialize the retriever
text_folder_path = "/Users/macbook/Desktop/headless_app_chat_with_api/userManualCht/text"
retriever = EndpointRetriever(text_folder_path)
retriever.vector_embedding()

# Load Jinja2 templates
templates = Jinja2Templates(directory="/Users/macbook/Desktop/headless_app_chat_with_api/userManualCht/templates")

# Define request model
class QueryRequest(BaseModel):
    query: str

@app.post("/query")
async def get_response(request: QueryRequest):
    try:
        response = retriever.process_query(request.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
