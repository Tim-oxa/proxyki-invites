from datetime import datetime, UTC, timedelta
from aiogram.filters import Command
from aiogram import Router, Bot
from aiogram.types import *
from database import db
from config import *


rt = Router()


@rt.message(Command("start"))
async def start(message: Message, bot: Bot):
    user = await db["users"].find_one({"id": message.from_user.id})
    if user is None:
        invite_link = await bot.create_chat_invite_link(
            chat_id=GROUP_ID,
            name=str(message.from_user.id) + datetime.now(UTC).strftime("_%d-%m-%Y"),
            expire_date=timedelta(days=30),
            member_limit=1
        )
        await db["users"].insert_one({
            "id": message.from_user.id,
            "username": message.from_user.username,
            "first_name": message.from_user.first_name,
            "last_name": message.from_user.last_name,
            "invite_link": invite_link.invite_link,
            "link_date": datetime.now(UTC)
        })
        text = "Твоя ссылка для приглашения 1 нового участника создана и будет действовать 30 дней. Новая ссылка будет доступна по истечению срока действия текущей. Сгенерировать её можно будет командой /start"
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Скопировать ссылку", copy_text=CopyTextButton(text=invite_link.invite_link))]
        ])
        await message.answer(text, reply_markup=kb)
    else:
        now = datetime.now(UTC)
        if now - user["link_date"] > timedelta(days=30):
            invite_link = await bot.create_chat_invite_link(
                chat_id=GROUP_ID,
                name=str(message.from_user.id) + datetime.now(UTC).strftime("_%d-%m-%Y"),
                expire_date=timedelta(days=30),
                member_limit=1
            )
            await db["users"].replace_one({
                "id": message.from_user.id,
                "username": message.from_user.username,
                "first_name": message.from_user.first_name,
                "last_name": message.from_user.last_name,
                "invite_link": invite_link.invite_link,
                "link_date": datetime.now(UTC)
            })
            text = "Твоя ссылка для приглашения 1 нового участника создана и будет действовать 30 дней. Новая ссылка будет доступна по истечению срока действия текущей. Сгенерировать её можно будет командой /start"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Скопировать ссылку", copy_text=CopyTextButton(text=invite_link.invite_link))]
            ])
            await message.answer(text, reply_markup=kb)
        elif user["invite_link"] is None:
            next_date: datetime = user["link_date"] + timedelta(days=30)
            text = "По твоей ссылке уже кто-то зашёл. Ты сможешь создать новую " + next_date.strftime("%d-%m-%Y") + " с помощью команды /start"
            await message.answer(text)
        else:
            link_date: datetime = user["link_date"]
            text = f"Твоя ссылка для приглашения 1 нового участника создана и будет действовать до {link_date.strftime('%d-%m-%Y')}. Новая ссылка будет доступна по истечению срока действия текущей. Сгенерировать её можно будет командой /start"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Скопировать ссылку", copy_text=CopyTextButton(text=user["invite_link"]))]
            ])
            await message.answer(text, reply_markup=kb)


@rt.chat_member()
async def new_chat_member(event: ChatMemberUpdated, bot: Bot):
    if event.old_chat_member.status in ("left", "kicked") and event.new_chat_member.status == "member":
        user = await db["users"].find_one({"invite_link": event.invite_link})
        if user:
            await db["users"].update_one({"id": user["id"]}, {
                "$set": {
                    "invite_link": None
                }
            })
            text = f"По твоей ссылке зашёл пользователь @{event.new_chat_member.user.username} ({event.new_chat_member.user.id})"
            await bot.send_message(user["id"], text)
