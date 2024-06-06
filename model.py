from pydantic import BaseModel
from typing import List, Optional, Literal, Union
import datetime as dt


class Response(BaseModel):
    success: bool
    message: str


# Student
class Student(BaseModel):
    nim: int
    name: str
    tel: int
    email: str
    avatar_url: str
    address: str
    pass_hash: str


class GetAllStudentResponse(BaseModel):
    success: bool
    message: str
    mahasiswa: List[Student]


class GetStudentResponse(BaseModel):
    success: bool
    message: str
    mahasiswa: Optional[Student]


# Admin
class Admin(BaseModel):
    id: int
    name: str
    email: str
    pass_hash: str


class GetAllAdminResponse(BaseModel):
    success: bool
    message: str
    admins: List[Admin]


class GetAdminResponse(BaseModel):
    success: bool
    message: str
    admin: Optional[Admin]


# Auth
class Auth(BaseModel):
    user_type: Literal["mahasiswa", "admin"]
    user: Union[Admin, Student]


class AuthResponse(BaseModel):
    success: bool
    message: str
    auth: Optional[Auth]


# Aspiration
class Aspiration(BaseModel):
    id: int
    mahasiswa: Student
    datetime: dt.datetime
    title: str
    content: str


class GetAllAspirationResponse(BaseModel):
    success: bool
    message: str
    aspirations: List[Aspiration]


# Post
class Post(BaseModel):
    id: int
    poster: Student
    post_date: dt.datetime
    img_url: Optional[str]
    content: str
    can_comment: bool


class GetAllPostResponse(BaseModel):
    success: bool
    message: str
    posts: List[Post]


class GetPostResponse(BaseModel):
    success: bool
    message: str
    post: Optional[Post]


# Lab Post
class LabPost(BaseModel):
    id: int
    post_date: dt.datetime
    lab: Literal["magics", "sea", "rnest", "security", "evconn", "ismile"]
    img_url: Optional[str]
    content: str


class GetAllLabPostResponse(BaseModel):
    success: bool
    message: str
    lab_posts: List[LabPost]


class GetLabPostResponse(BaseModel):
    success: bool
    message: str
    lab_post: Optional[LabPost]


# Fun TK
class FunTK(BaseModel):
    id: int
    title: str
    description: str
    post_date: dt.datetime
    img_url: str
    date: dt.date
    time: dt.time
    location: str
    map_url: Optional[str]


class GetAllFunTKResponse(BaseModel):
    success: bool
    message: str
    fun_tks: List[FunTK]


class GetFunTKResponse(BaseModel):
    success: bool
    message: str
    fun_tk: Optional[FunTK]


# Academic Resource
class AcademicResource(BaseModel):
    id: int
    admin: Admin
    title: str
    url: str


class GetAllAcademicResourceResponse(BaseModel):
    success: bool
    message: str
    academic_resources: List[AcademicResource]


class GetAcademicResourceResponse(BaseModel):
    success: bool
    message: str
    academic_resource: Optional[AcademicResource]


# Comment
class Comment(BaseModel):
    id: int
    commenter: Union[Admin, Student]
    commenter_type: Literal["mahasiswa", "admin"]
    comment_date: dt.datetime
    content: str


class GetAllCommentResponse(BaseModel):
    success: bool
    message: str
    comments: Optional[List[Comment]]


class GetCommentResponse(BaseModel):
    success: bool
    message: str
    comment: Optional[Comment]


# Activity
class Activity(BaseModel):
    id: int
    post_date: dt.datetime
    title: str
    content: str
    img_url: str


class GetAllActivitiesResponse(BaseModel):
    success: bool
    message: str
    activities: List[Activity]


class GetActivityResponse(BaseModel):
    success: bool
    message: str
    activity: Optional[Activity]


# Product
class Product(BaseModel):
    id: int
    name: str
    price: int
    description: str
    img_url: str


class GetAllProductResponse(BaseModel):
    success: bool
    message: str
    products: Optional[List[Product]]


class GetProductResponse(BaseModel):
    success: bool
    message: str
    product: Optional[Product]


# Cart
class Cart(BaseModel):
    id: int
    # mahasiswa: Student
    product: Product
    quantity: int
    size: Literal["xs", "s", "m", "l", "xl", "xxl"]
    information: Optional[str]


class GetAllStudentCartResponse(BaseModel):
    success: bool
    message: str
    carts: Optional[List[Cart]]


class GetStudentCartResponse(BaseModel):
    success: bool
    message: str
    cart: Optional[Cart]


# Order
class Order(BaseModel):
    id: int
    # mahasiswa: Student
    product: Product
    quantity: int
    size: Literal["xs", "s", "m", "l", "xl", "xxl"]
    information: Optional[str]
    # transaction_id: int


class GetAllOrderResponse(BaseModel):
    success: bool
    message: str
    orders: Optional[List[Order]]


class GetOrderResponse(BaseModel):
    success: bool
    message: str
    order: Optional[Order]


# Transaction
class Transaction(BaseModel):
    id: int
    # mahasiswa: Student
    orders: List[Order]
    transaction_date: dt.datetime
    paid: bool
    completed: bool
    payment_url: str
    status: str


class GetAllTransactionResponse(BaseModel):
    success: bool
    message: str
    transactions: List[Transaction]


class GetTransactionResponse(BaseModel):
    success: bool
    message: str
    transaction: Optional[Transaction]


class AddTransactionResponse(BaseModel):
    success: bool
    message: str
    payment_url: Optional[str]
