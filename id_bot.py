import asyncio
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums import ChatType, ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    Message,
    User,
    Chat,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.utils.formatting import (
    Bold, Code, Text, as_section, as_list, as_key_value
)
from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")




logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

router = Router()




def format_user_info(user: User) -> str:
    """Foydalanuvchi haqida chiroyli formatdagi ma'lumot."""
    premium = "⭐ Ha" if getattr(user, "is_premium", False) else "❌ Yo'q"
    bot_flag = "🤖 Ha" if user.is_bot else "👤 Yo'q"
    lang = user.language_code or "Noma'lum"

    username_line = f"@{user.username}" if user.username else "Yo'q"
    full_name = user.full_name or "—"
    first = user.first_name or "—"
    last = user.last_name or "Yo'q"

    return (
        "👤 <b>FOYDALANUVCHI MA'LUMOTLARI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n"
        f"📛 <b>To'liq ism:</b> {full_name}\n"
        f"🔤 <b>Ism:</b> {first}\n"
        f"🔤 <b>Familiya:</b> {last}\n"
        f"🔗 <b>Username:</b> {username_line}\n"
        f"🌐 <b>Til:</b> {lang}\n"
        f"⭐ <b>Premium:</b> {premium}\n"
        f"🤖 <b>Bot:</b> {bot_flag}\n"
        f"🔗 <b>Havola:</b> <a href='tg://user?id={user.id}'>Profil</a>"
    )


def format_chat_info(chat: Chat) -> str:
    """Chat haqida ma'lumot."""
    chat_type_map = {
        "private": "🔒 Shaxsiy",
        "group": "👥 Guruh",
        "supergroup": "🏢 Supergruuh",
        "channel": "📢 Kanal",
    }
    chat_type = chat_type_map.get(chat.type, chat.type)
    username_line = f"@{chat.username}" if getattr(chat, "username", None) else "Yo'q"
    title = getattr(chat, "title", None) or getattr(chat, "full_name", "—")

    return (
        "💬 <b>CHAT MA'LUMOTLARI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>\n"
        f"📌 <b>Nomi:</b> {title}\n"
        f"📂 <b>Turi:</b> {chat_type}\n"
        f"🔗 <b>Username:</b> {username_line}"
    )


def format_message_info(message: Message) -> str:
    """Xabar haqida texnik ma'lumot."""
    date_str = message.date.strftime("%Y-%m-%d %H:%M:%S UTC") if message.date else "—"
    forward_info = "✅ Ha" if message.forward_origin else "❌ Yo'q"

    msg_type = "📄 Matn"
    if message.photo:
        msg_type = "🖼 Rasm"
    elif message.video:
        msg_type = "🎬 Video"
    elif message.audio:
        msg_type = "🎵 Audio"
    elif message.document:
        msg_type = "📎 Fayl"
    elif message.sticker:
        msg_type = "🎭 Stiker"
    elif message.voice:
        msg_type = "🎙 Ovozli xabar"
    elif message.video_note:
        msg_type = "📹 Video xabar (doira)"
    elif message.location:
        msg_type = "📍 Joylashuv"
    elif message.contact:
        msg_type = "📞 Kontakt"
    elif message.poll:
        msg_type = "📊 So'rovnoma"
    elif message.animation:
        msg_type = "🎞 GIF"

    return (
        "📨 <b>XABAR MA'LUMOTLARI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>Xabar ID:</b> <code>{message.message_id}</code>\n"
        f"📅 <b>Vaqt:</b> {date_str}\n"
        f"📦 <b>Turi:</b> {msg_type}\n"
        f"↩️ <b>Forward:</b> {forward_info}"
    )


def main_keyboard() -> InlineKeyboardMarkup:
    """Asosiy inline tugmalar."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🆔 Mening ID", callback_data="my_id"),
            InlineKeyboardButton(text="📊 Bot haqida", callback_data="bot_info"),
        ],
        [
            InlineKeyboardButton(text="📖 Yordam", callback_data="help"),
        ],
    ])




@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    """
    /start — foydalanuvchini kutib olish va uning to'liq ma'lumotlarini ko'rsatish.
    """
    user = message.from_user
    chat = message.chat

    greeting = (
        f"👋 <b>Salom, {user.first_name}!</b>\n\n"
        "Men — <b>Info Bot</b> 🤖\n"
        "Xabar yuborganlarning ID va boshqa ma'lumotlarini ko'rsataman.\n\n"
        "Quyida <b>siz haqingizda</b> ma'lumotlar:\n\n"
        f"{format_user_info(user)}\n\n"
        f"{format_chat_info(chat)}"
    )

    await message.answer(
        greeting,
        parse_mode=ParseMode.HTML,
        reply_markup=main_keyboard(),
        disable_web_page_preview=True,
    )
    logger.info(f"START | User: {user.id} ({user.full_name}) | Chat: {chat.id}")


@router.message(Command("id"))
async def cmd_id(message: Message):
    """/id — faqat ID larni tez ko'rsatish."""
    user = message.from_user
    chat = message.chat

    text = (
        "🆔 <b>ID MA'LUMOTLARI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 <b>Sizning ID:</b> <code>{user.id}</code>\n"
        f"💬 <b>Chat ID:</b> <code>{chat.id}</code>\n"
        f"📨 <b>Xabar ID:</b> <code>{message.message_id}</code>"
    )
    if message.reply_to_message and message.reply_to_message.from_user:
        replied_user = message.reply_to_message.from_user
        text += (
            f"\n\n↩️ <b>Reply qilingan foydalanuvchi:</b>\n"
            f"👤 ID: <code>{replied_user.id}</code>\n"
            f"📛 Ism: {replied_user.full_name}"
        )
    await message.answer(text, parse_mode=ParseMode.HTML)


@router.message(Command("info"))
async def cmd_info(message: Message):
    """/info — to'liq ma'lumot, reply qilingan foydalanuvchi haqida ham."""
    user = message.from_user
    chat = message.chat

    parts = [
        format_user_info(user),
        "",
        format_chat_info(chat),
        "",
        format_message_info(message),
    ]

    if message.reply_to_message:
        reply = message.reply_to_message
        parts.append("")
        parts.append("↩️ <b>REPLY QILINGAN XABAR</b>")
        parts.append("━━━━━━━━━━━━━━━━━━━━━━━━")
        if reply.from_user:
            parts.append(format_user_info(reply.from_user))
        parts.append(format_message_info(reply))

    await message.answer(
        "\n".join(parts),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


@router.message(Command("chatid"))
async def cmd_chatid(message: Message):
    """/chatid — joriy chat ID."""
    await message.answer(
        f"💬 <b>Chat ID:</b> <code>{message.chat.id}</code>",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """/help — buyruqlar ro'yxati."""
    text = (
        "📖 <b>BUYRUQLAR RO'YXATI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "/start — Botni ishga tushirish, o'z ma'lumotlarini ko'rish\n"
        "/id — Tez ID ko'rsatish (reply bilan boshqasini ham)\n"
        "/info — To'liq texnik ma'lumot\n"
        "/chatid — Chat ID ni ko'rsatish\n"
        "/help — Ushbu yordam\n\n"
        "💡 <b>Qo'shimcha imkoniyatlar:</b>\n"
        "• Istalgan xabarni forward qiling — asl yuboruvchi ma'lumoti + profiliga havola\n"
        "• Foydalanuvchi <b>ID sini yuboring</b> (masalan: <code>123456789</code>) — kim ekanligini ko'rish\n"
        "• /info buyrug'ini reply bilan ishlating — o'sha foydalanuvchi haqida ma'lumot"
    )
    await message.answer(text, parse_mode=ParseMode.HTML)



@router.message(F.forward_origin)
async def handle_forward(message: Message):
    """Forward xabarlar — FAQAT asl yuboruvchi ma'lumoti."""
    from aiogram.types import (
        MessageOriginUser,
        MessageOriginHiddenUser,
        MessageOriginChat,
        MessageOriginChannel,
    )

    origin = message.forward_origin

    if isinstance(origin, MessageOriginUser):
        fu = origin.sender_user
        premium = "⭐ Ha" if getattr(fu, "is_premium", False) else "❌ Yo'q"
        bot_flag = "🤖 Ha" if fu.is_bot else "👤 Yo'q"
        username_line = f"\n🔗 <b>Username:</b> @{fu.username}" if fu.username else ""
        last_name = f" {fu.last_name}" if fu.last_name else ""
        date_str = origin.date.strftime("%Y-%m-%d %H:%M UTC") if origin.date else "—"

        text = (
            "📤 <b>FORWARD — YUBORUVCHI MA'LUMOTLARI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>ID:</b> <code>{fu.id}</code>\n"
            f"📛 <b>To'liq ism:</b> {fu.first_name}{last_name}\n"
            f"🌐 <b>Til:</b> {fu.language_code or 'Nomalum'}\n"
            f"⭐ <b>Premium:</b> {premium}\n"
            f"🤖 <b>Bot:</b> {bot_flag}"
            f"{username_line}\n"
            f"🔗 <b>Profil:</b> <a href='tg://user?id={fu.id}'>Profilga o'tish</a>\n"
            f"📅 <b>Xabar sanasi:</b> {date_str}"
        )

    elif isinstance(origin, MessageOriginHiddenUser):
        text = (
            "📤 <b>FORWARD — YUBORUVCHI MA'LUMOTLARI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🕵️ <b>Ism:</b> {origin.sender_user_name}\n"
            "⚠️ <b>Bu foydalanuvchi o'z profilini yashirgan</b>\n"
            "🔒 ID va boshqa ma'lumotlar mavjud emas"
        )

    elif isinstance(origin, MessageOriginChat):
        chat = origin.sender_chat
        username_line = f"\n🔗 <b>Username:</b> @{chat.username}" if getattr(chat, "username", None) else ""
        date_str = origin.date.strftime("%Y-%m-%d %H:%M UTC") if origin.date else "—"
        text = (
            "📤 <b>FORWARD — GURUH MA'LUMOTLARI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 <b>Nomi:</b> {chat.title}\n"
            f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>"
            f"{username_line}\n"
            f"📅 <b>Xabar sanasi:</b> {date_str}"
        )

    elif isinstance(origin, MessageOriginChannel):
        chat = origin.chat
        username_line = f"\n🔗 <b>Username:</b> @{chat.username}" if getattr(chat, "username", None) else ""
        channel_link = f"\n🔗 <b>Kanal havolasi:</b> <a href='https://t.me/{chat.username}'>Kanalga o'tish</a>" if getattr(chat, "username", None) else ""
        post_id = f"\n📌 <b>Post ID:</b> <code>{origin.message_id}</code>" if origin.message_id else ""
        date_str = origin.date.strftime("%Y-%m-%d %H:%M UTC") if origin.date else "—"
        text = (
            "📤 <b>FORWARD — KANAL MA'LUMOTLARI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📢 <b>Nomi:</b> {chat.title}\n"
            f"🆔 <b>Chat ID:</b> <code>{chat.id}</code>"
            f"{username_line}"
            f"{channel_link}"
            f"{post_id}\n"
            f"📅 <b>Xabar sanasi:</b> {date_str}"
        )

    else:
        text = "⚠️ Forward ma'lumotini aniqlab bo'lmadi."

    await message.answer(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@router.message(F.text & ~F.text.startswith("/") & ~F.text.regexp(r"^\d{5,12}$"))
async def handle_text(message: Message):
    """Oddiy matn xabari — yuboruvchi haqida ma'lumot."""
    user = message.from_user
    if not user:
        return
    text = (
        f"{format_user_info(user)}\n\n"
        f"{format_message_info(message)}"
    )
    await message.answer(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@router.message(F.text.regexp(r"^\d{5,12}$"))
async def handle_id_lookup(message: Message, bot: Bot):
    """Foydalanuvchi ID yuborilsa — profil havolasini ko'rsatish."""
    user_id = int(message.text.strip())

    try:
        member = await bot.get_chat(user_id)
        name = getattr(member, "full_name", None) or getattr(member, "title", "Noma'lum")
        username_line = f"\n🔗 <b>Username:</b> @{member.username}" if getattr(member, "username", None) else ""
        chat_type = getattr(member, "type", "—")

        text = (
            "🔍 <b>ID BO'YICHA QIDIRUV</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            f"📛 <b>Ism:</b> {name}\n"
            f"📂 <b>Turi:</b> {chat_type}"
            f"{username_line}\n"
            f"🔗 <b>Profil:</b> <a href='tg://user?id={user_id}'>Profilga o'tish</a>"
        )
    except Exception:
        text = (
            "🔍 <b>ID BO'YICHA QIDIRUV</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
            "⚠️ <b>Ma'lumot topilmadi</b>\n"
            "Bu foydalanuvchi botga yozmagan yoki mavjud emas.\n\n"
            f"🔗 <b>Profil havolasi:</b> <a href='tg://user?id={user_id}'>Profilga o'tish</a>"
        )

    await message.answer(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@router.message(F.photo | F.video | F.audio | F.document | F.sticker |
                F.voice | F.video_note | F.location | F.contact |
                F.poll | F.animation)
async def handle_media(message: Message):
    """Media xabarlar — yuboruvchi haqida ma'lumot."""
    user = message.from_user
    if not user:
        return
    text = (
        f"{format_user_info(user)}\n\n"
        f"{format_message_info(message)}"
    )
    await message.answer(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)



@router.callback_query(F.data == "my_id")
async def callback_my_id(callback: CallbackQuery):
    user = callback.from_user
    await callback.answer(
        f"Sizning ID: {user.id}",
        show_alert=True,
    )


@router.callback_query(F.data == "bot_info")
async def callback_bot_info(callback: CallbackQuery, bot: Bot):
    info = await bot.get_me()
    text = (
        "🤖 <b>BOT MA'LUMOTLARI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 <b>Bot ID:</b> <code>{info.id}</code>\n"
        f"📛 <b>Ismi:</b> {info.full_name}\n"
        f"🔗 <b>Username:</b> @{info.username}\n"
        f"⚙️ <b>Framework:</b> aiogram 3.x\n"
        f"📅 <b>Vaqt:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}"
    )
    await callback.message.answer(text, parse_mode=ParseMode.HTML)
    await callback.answer()


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    await callback.answer()
    text = (
        "📖 <b>BUYRUQLAR</b>\n\n"
        "/start — Boshlash\n"
        "/id — ID ko'rsatish\n"
        "/info — To'liq ma'lumot\n"
        "/chatid — Chat ID\n"
        "/help — Yordam\n\n"
        "💡 Istalgan xabar yuboring — yuboruvchi haqida ma'lumot olasiz!"
    )
    await callback.message.answer(text, parse_mode=ParseMode.HTML)



async def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("❌ BOT_TOKEN o'rnatilmagan! .env faylida yoki muhit o'zgaruvchisida kiriting.")
        return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    bot_info = await bot.get_me()
    logger.info(f"✅ Bot ishga tushdi: @{bot_info.username} (ID: {bot_info.id})")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("🛑 Bot to'xtatildi.")


if __name__ == "__main__":
    asyncio.run(main())