from setups import bot, dp, Users, History
from aiogram.utils import executor
import logging
import sys
import handers
from helpers import get_user_id, add_new_search

async def on_startup(_):
    logger = logging.getLogger(__name__)
    logger.info(
        "Бот запущен."
    )

async def on_shutdown(_):
    logger = logging.getLogger(__name__)
    logger.info(
        "Бот остановлен."
    )


def main():
    # настройка логгера.
    logging.basicConfig(
        datefmt="%d.%m.%Y : %H:%M:%S",
        level=logging.INFO,
        handlers= [
            logging.FileHandler(
                filename="debug.log",
                encoding="utf-8",
                mode="w"
            ),
            logging.StreamHandler(sys.stdout)
        ],
        format="%(levelname)s : %(asctime)s : %(name)s : %(message)s"
    )
    # запуск бота.
    if dp:
        executor.start_polling(
            dispatcher=dp,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            timeout=3,
            skip_updates=True,

        )

if __name__ == "__main__":
    main()