import asyncio
from create_bot import bot, dp
from handlers.start import start_router
from handlers.manipulate_players import player_handler

async def main():
    dp.include_routers(start_router, player_handler)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())