import datetime

from peewee import *
import os

db_name = os.path.abspath("history.db")
history_db = SqliteDatabase(db_name)

class BaseModel(Model):
    id = AutoField()
    class Meta:
        database = history_db

class Users(BaseModel):
    tg_id = IntegerField()

class History(BaseModel):
    user_id = ForeignKeyField(Users, field="id") # идентификатор пользователя в таблице пользователей
    search_id = CharField() # идентификатор поиска
    search_kind = CharField() # текстовое описание причины поиска
    start_date = DateField(default=datetime.datetime.now()) # дата начала поиска
    cancelled = BooleanField(default=False) # флаг отмены поиска
    user_cancel = BooleanField(default=False) # поиск прекращен пользователем.
    error_cancel = BooleanField(default=False) # поиск прекращен из-за ошибки.

history_db.create_tables([Users, History])