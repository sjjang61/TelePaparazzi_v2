from modules.telegram.Telegram import Telegram

async def list_ids():
    api_id = '2442467'
    api_hash = '00807ca58c9293bf4dd7c0bfd58031d1'

   # client = TelegramClient('session', api_id, api_hash)
   # await client.start()
   # async for dlg in client.iter_dialogs():
    #    if dlg.name == "제우스봇":  # 표시 이름
    #        print("ID:", dlg.entity.id)
    #await client.disconnect()



if __name__ == "__main__":
    telegram = Telegram()
    telegram.Update()
    #asyncio.run(list_ids())



