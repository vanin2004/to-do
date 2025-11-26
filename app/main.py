
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core import settings
from app.exceptions import TodoListNotFoundException, TodoTaskNotFoundException
from app.router import router

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.app_version,
    debug=settings.debug_mode,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

@app.exception_handler(TodoListNotFoundException)
async def global_exception_handler(request: Request, exc: TodoListNotFoundException):
    return JSONResponse(
        status_code=400,
        content={
            "error": True,
            "message": "invalid todo list slug",
            "details": str(exc)
        }
    )

@app.exception_handler(TodoTaskNotFoundException)
async def todo_task_not_found_exception_handler(request: Request, exc: TodoTaskNotFoundException):
    return JSONResponse(
        status_code=400,
        content={
            "error": True,
            "message": "invalid todo task id",
            "details": str(exc)
        }
    )

app.include_router(router, prefix=settings.api_prefix)




    
    


# if __name__ == "__main__":
#     db = Database(settings.database_url)
#     with db.get_unit_of_work() as uow:
#         uow.todo_lists.create(uow.session, slug="example-slug", name="Example List", is_free=False)
#         uow.commit()