from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, InputMediaVideo
from asgiref.sync import sync_to_async

from bot_core.utils import is_near_school
from main.models import User, UserMedia
from bot_core.states import Registration, Browsing

from bot_core.keyboards import *

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext, force_registration: bool = False):
    await state.clear()

    if not force_registration:
        user = await sync_to_async(User.objects.filter(telegram_id=str(message.from_user.id)).first)()
        if user and user.is_active:
            await message.answer(
                f"С возвращением, {user.name}! 👋\nРад тебя видеть снова.",
                reply_markup=get_main_menu_kb(is_active=user.is_active)
            )
            await state.set_state(Browsing.viewing_profiles)
            return

    text = (
        f"Йоу! {message.from_user.first_name}, это **Коннект 82**. 👫\n\n"
        f"На связи вся школа. Начнем заполнять анкету?\n"
        f"Для начала, кто ты?"
    )

    await message.answer(text, reply_markup=get_gender_kb(), parse_mode="Markdown")
    await state.set_state(Registration.gender)


@router.message(F.text == "Заполнить заново 📝")
async def restart_reg(message: types.Message, state: FSMContext):
    await cmd_start(message, state, force_registration=True)


@router.message(Registration.gender)
async def process_gender(message: types.Message, state: FSMContext):
    gender_map = {"Я парень 👦": "M", "Я девушка 👧": "F"}
    val = gender_map.get(message.text)

    if not val:
        return await message.answer("Выбери вариант на кнопках ниже!")

    await state.update_data(gender=val)
    await message.answer("А кто тебе интересен?", reply_markup=get_search_gender_kb())
    await state.set_state(Registration.search_gender)


@router.message(Registration.search_gender)
async def process_search_gender(message: types.Message, state: FSMContext):
    search_map = {"Парни 👦": "M", "Девушки 👧": "F", "Все равно 🤝": "O"}
    val = search_map.get(message.text)

    if not val:
        return await message.answer("Воспользуйся кнопками!")

    await state.update_data(search_gender=val)
    await message.answer(f"Как тебя зовут?",
                         reply_markup=get_name_kb(message.from_user.first_name))
    await state.set_state(Registration.name)


@router.message(Registration.name)
async def process_name(message: types.Message, state: FSMContext):
    if "Оставить как в ТГ" in message.text:
        name = message.from_user.first_name
    else:
        name = message.text

    await state.update_data(name=name)
    await message.answer(f"Приятно познакомиться, {name}! Сколько тебе лет?",
                         reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(Registration.age)


@router.message(Registration.age)
async def process_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("Введи возраст цифрами!")

    age = int(message.text)
    if not (12 <= age <= 100):
        return await message.answer("Введи реальный возраст (от 12 лет)")

    await state.update_data(age=age)

    await message.answer(
        "Подтверди, что ты из нашей школы. Отправь свою геолокацию (кнопка ниже).",
        reply_markup=get_location_kb()
    )
    await state.set_state(Registration.location)


@router.message(Registration.location, F.location)
async def process_location(message: types.Message, state: FSMContext):
    lat = message.location.latitude
    lon = message.location.longitude

    if is_near_school(lat, lon):
        await state.update_data(lat=str(lat), long=str(lon))
        await message.answer(
            "Проверка пройдена! ✅ Теперь расскажи немного о себе (текстом):",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.set_state(Registration.bio)
    else:
        await message.answer(
            "Извини, бро, но ты слишком далеко от школы. ⛔️ Бот только для своих.",
            reply_markup=get_location_kb()
        )


@router.message(Registration.bio)
async def process_bio(message: types.Message, state: FSMContext):
    await state.update_data(bio=message.text)

    await message.answer(
        "Отлично! Теперь пришли мне одно или несколько фото (или видео). "
        "Когда закончишь, нажми кнопку ниже 👇",
        reply_markup=get_finish_media_kb()
    )
    await state.set_state(Registration.media)


@router.message(Registration.media)
async def process_media_upload(message: types.Message, state: FSMContext):
    if message.text == "Готово ✅":
        return await finish_registration(message, state)

    data = await state.get_data()
    media_list = data.get("media_list", [])
    MAX_MEDIA = 3
    new_media = None

    if message.photo:
        new_media = {"type": "P", "id": message.photo[-1].file_id}

    elif message.video:
        new_media = {"type": "V", "id": message.video.file_id}

    elif message.animation:
        new_media = {"type": "V", "id": message.animation.file_id}

    elif message.video_note:
        return await message.answer("Извини, кружочки нельзя добавить в анкету. Пришли обычное фото или видео!")

    if new_media:
        media_list.append(new_media)
        await state.update_data(media_list=media_list)

        current_count = len(media_list)

        if current_count >= MAX_MEDIA:
            await message.answer(f"✅ Добавлено {current_count} из {MAX_MEDIA}. Сохраняю...")
            return await finish_registration(message, state)
        else:
            await message.answer(
                f"Принято! ({current_count}/{MAX_MEDIA})\n"
                "Пришли еще или нажми 'Готово ✅'",
                reply_markup=get_finish_media_kb()
            )
    else:
        await message.answer(
            "Бро, пришли фото или видео. Другие форматы не подходят.",
            reply_markup=get_finish_media_kb()
        )


@router.message(Registration.media, F.text == "Готово ✅")
async def finish_registration(message: types.Message, state: FSMContext):
    data = await state.get_data()
    media_list = data.get("media_list", [])

    if not media_list:
        return await message.answer("Нужно прислать хотя бы одно фото или видео!")

    def save_user_and_media():
        user, _ = User.objects.update_or_create(
            telegram_id=str(message.from_user.id),
            defaults={
                'username': message.from_user.username or "",
                'name': data.get('name'),
                'age': data.get('age'),
                'gender': data.get('gender'),
                'search_gender': data.get('search_gender'),
                'lat': data.get('lat'),
                'long': data.get('long'),
                'bio': data.get('bio', "Нет описания"),
                'is_active': True
            }
        )
        UserMedia.objects.filter(user=user).delete()
        for item in media_list:
            UserMedia.objects.create(
                user=user,
                media_id=item["id"],
                media_type=item["type"]
            )
        return user

    user = await sync_to_async(save_user_and_media)()

    await message.answer("Сохраняю анкету... ⏳", reply_markup=types.ReplyKeyboardRemove())

    await state.clear()

    await message.answer("Вот так выглядит твоя анкета:")
    await show_my_profile(message, state)

    await state.set_state(Browsing.viewing_profiles)

# =============================================================
#  Моя анкета

@router.message(F.text == "👤 Моя анкета")
async def show_my_profile(message: types.Message, state: FSMContext):
    user = await sync_to_async(User.objects.filter(telegram_id=str(message.from_user.id)).first)()
    if not user:
        return await message.answer("Анкета не найдена. Нажми /start")

    if not user.is_active:
        return await message.answer(
            "Твоя анкета сейчас **скрыта**. 🙈\nДругие пользователи её не видят.",
            reply_markup=get_main_menu_kb(is_active=False),
            parse_mode="Markdown"
        )

    media_objects = await sync_to_async(list)(UserMedia.objects.filter(user=user))

    caption = (
        f"**{user.name}, {user.age}**\n"
        f"📍 Рядом со школой\n\n"
        f"{user.bio}"
    )

    if not media_objects:
        return await message.answer(caption, reply_markup=get_main_menu_kb(), parse_mode="Markdown")

    if len(media_objects) == 1:
        m = media_objects[0]
        if m.media_type == "P":
            return await message.answer_photo(m.media_id, caption=caption, parse_mode="Markdown", reply_markup=get_main_menu_kb())
        else:
            return await message.answer_video(m.media_id, caption=caption, parse_mode="Markdown", reply_markup=get_main_menu_kb())

    media_group = []
    for i, m in enumerate(media_objects):
        item_caption = caption if i == 0 else None
        if m.media_type == "P":
            media_group.append(InputMediaPhoto(media=m.media_id, caption=item_caption, parse_mode="Markdown"))
        else:
            media_group.append(InputMediaVideo(media=m.media_id, caption=item_caption, parse_mode="Markdown"))

    try:
        await message.answer_media_group(media=media_group)
        await message.answer("Выше твоя анкета 👆", reply_markup=get_main_menu_kb())
    except Exception as e:
        await message.answer(f"Ошибка отображения анкеты. Попробуй обновить фото.\n\n{caption}",
                             reply_markup=get_main_menu_kb(), parse_mode="Markdown")


@router.message(F.text.in_({"Скрыть анкету 🚫", "Опубликовать анкету ✅"}))
async def toggle_profile_active(message: types.Message):
    user = await sync_to_async(User.objects.filter(telegram_id=str(message.from_user.id)).first)()

    if not user:
        return

    new_status = not user.is_active
    user.is_active = new_status
    await sync_to_async(user.save)()

    if new_status:
        text = "Твоя анкета снова в строю! 🚀 Теперь её видят другие ученики."
    else:
        text = "Анкета скрыта. 🔒 Тебя больше не будут встречать в поиске, но и ты не сможешь смотреть других."

    await message.answer(text, reply_markup=get_main_menu_kb(is_active=new_status))

@router.message(F.text == "Заполнить заново 📝")
async def restart_reg(message: types.Message, state: FSMContext):
    await cmd_start(message, state)