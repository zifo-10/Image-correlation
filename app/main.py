from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.client.database import Database
from app.exceptions.custom_exception import CustomException, CustomHTTPException
from app.routes.file_routes import router

app = FastAPI(title="Zedny API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Global Exception Handlers
@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.exception_type or "CustomException",
            "detail": exc.detail,
            "additional_info": exc.additional_info,
        },
    )


@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.exception_type or "CustomHTTPException",
            "detail": exc.detail,
            "additional_info": exc.additional_info,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # Catch-all for unexpected errors
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "detail": str(exc),
        },
    )
app.include_router(router)

# ✅ Initialize DB
db = Database()

# @app.on_event("startup")
# async def on_startup():
#     await db.create_tables()
