import datetime

from peewee import *
import os

db_name = os.path.abspath("history_data.db")
history_db = SqliteDatabase(db_name)

# Базовая модель
class BaseModel(Model):
    id = AutoField()
    class Meta:
        database = history_db

class Users(BaseModel):
    tg_id = IntegerField()

class CommandsInfo(BaseModel):
    command = CharField()
    desc = CharField()


class History(BaseModel):
    user_id = ForeignKeyField(Users, field="id") # идентификатор пользователя в таблице пользователей
    command_id = ForeignKeyField(CommandsInfo, field="id")
    search_kind = CharField() # текстовое описание причины поиска
    start_date = DateTimeField(default=datetime.datetime.now()) # дата начала поиска
    city_name = CharField(default="")
    city_id = CharField(default="")
    adults = IntegerField(default=0)
    children = CharField(default="")
    cancelled = BooleanField(default=False) # флаг отмены поиска
    user_cancel = BooleanField(default=False) # поиск прекращен пользователем.
    error_cancel = BooleanField(default=False) # поиск прекращен из-за ошибки.
    end_date = DateTimeField(null=True)



#
history_db.create_tables([Users, History, CommandsInfo])

commands_desc = [
        {
            CommandsInfo.command: "lowprice",
            CommandsInfo.desc: "топ самых дешёвых отелей в городе"
        },
        {
            CommandsInfo.command: "highprice",
            CommandsInfo.desc: "топ самых дорогих отелей в городе"
        },
        {
            CommandsInfo.command: "bestdeal",
            CommandsInfo.desc: "топ отелей, наиболее подходящих по цене и расположению от центра"
        }
    ]

CommandsInfo.insert(commands_desc).execute()