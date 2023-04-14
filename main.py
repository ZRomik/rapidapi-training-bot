from setups import bot, dp
from aiogram.utils import executor
import logging
import sys

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
        # filename="debug.log",
        # filemode="w",
        # encoding="utf-8",
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
            skip_updates=True
        )

if __name__ == "__main__":
    main()