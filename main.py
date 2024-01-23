from fastapi import FastAPI

# Create an instance of the FastAPI class
app = FastAPI()

# Define a simple route
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# Additional routes can be added here

# Example of using a path parameter
@app.get("/items/{item_id}")
def read_item(item_id: int, query_param: str = None):
    return {"item_id": item_id, "query_param": query_param}
