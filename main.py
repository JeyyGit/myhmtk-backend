from fastapi import FastAPI, Depends
from fastapi.responses import RedirectResponse
# from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware

from routes.route_auth import auth_router
from routes.route_student import student_router
from routes.route_cart import cart_router
from routes.route_order import order_router
from routes.route_admin import admin_router
from routes.route_post import post_router
from routes.route_lab_post import lab_post_router
from routes.route_aspiration import aspiration_router
from routes.route_fun_tk import fun_tk_router
from routes.route_academic_resource import academic_resource_router
from routes.route_product import product_router
from routes.reset_password import reset_pw_router

from util import bearer_scheme, MyHMTKMiddleware

app = FastAPI()

app.add_middleware(MyHMTKMiddleware, fastapi_app=app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.tokens = []

@app.get('/')
async def root():
    return RedirectResponse('/docs')


app.include_router(auth_router, dependencies=[Depends(bearer_scheme)])
app.include_router(admin_router, dependencies=[Depends(bearer_scheme)])
app.include_router(student_router, dependencies=[Depends(bearer_scheme)])
app.include_router(cart_router, dependencies=[Depends(bearer_scheme)])
app.include_router(order_router, dependencies=[Depends(bearer_scheme)])
app.include_router(post_router, dependencies=[Depends(bearer_scheme)])
app.include_router(lab_post_router, dependencies=[Depends(bearer_scheme)])
# app.include_router(aspiration_router, dependencies=[Depends(bearer_scheme)])
app.include_router(fun_tk_router, dependencies=[Depends(bearer_scheme)])
app.include_router(academic_resource_router, dependencies=[Depends(bearer_scheme)])
app.include_router(product_router, dependencies=[Depends(bearer_scheme)])

app.include_router(reset_pw_router)