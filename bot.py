import logging
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)

# ===================== НАСТРОЙКИ =====================
BOT_TOKEN = "8022396757:AAEGeWkVxynAXAcqsBXtGmWInc7AuNtKAy8"
COMPLAINTS_ID = 1068989481  # Получает жалобы и предложения
HR_ID = 7937037830          # Получает анкеты вакансий

INSTAGRAM = "https://www.instagram.com/corecl_official/"
TG_CHANNEL = "https://t.me/corecollectionuzb"
WEBSITE = "https://corecl.cc/"

# ===================== ЛОГИРОВАНИЕ =====================
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===================== СОСТОЯНИЯ АНКЕТЫ =====================
(
    VACANCY_NAME,
    VACANCY_AGE,
    VACANCY_PHONE,
    VACANCY_STUDENT,
    VACANCY_STUDENT_INFO,
    VACANCY_SHIFT,
    VACANCY_BRANCH,
    VACANCY_DURATION,
    VACANCY_PHOTO,
    VACANCY_START_DATE,
) = range(10)

# ===================== ФИЛИАЛЫ =====================
BRANCHES = [
    {
        "name_ru": "Буюк Ипак Йули (М. Горького)",
        "name_uz": "Buyuk Ipak Yo'li (M. Gorkiy)",
        "address_ru": "📍 Буюк Ипак Йули",
        "address_uz": "📍 Buyuk Ipak Yo'li",
        "hours": "🕐 10:00 – 22:00 (без выходных / har kuni)",
        "phone": "📞 +998 90-933-03-31",
        "map": "https://maps.app.goo.gl/CjPGeQWFi66Cpeiq9"
    },
    {
        "name_ru": "ТЦ Next (Бабура, 6) 3 этаж",
        "name_uz": "TC Next (Babura, 6) 3-qavat",
        "address_ru": "📍 Бабура, 6",
        "address_uz": "📍 Babura, 6",
        "hours": "🕐 10:00 – 22:00 (пт-сб до 23:00 / juma-shan 23:00 gacha)",
        "phone": "📞 +998 90-999-03-31 | 📱 @corecl_uz",
        "map": "https://maps.app.goo.gl/PBk983dG3eotGPa28"
    },
    {
        "name_ru": "ТЦ Zarafshan (Матбуотчилар, 17)",
        "name_uz": "TC Zarafshon (Matbuotchilar, 17)",
        "address_ru": "📍 ул. Матбуотчилар, 17",
        "address_uz": "📍 Matbuotchilar ko'chasi, 17",
        "hours": "🕐 10:00 – 22:00 (без выходных / har kuni)",
        "phone": "📞 +998 90-044-03-31",
        "map": "https://maps.app.goo.gl/49T23weYBBSwc7YC9"
    },
    {
        "name_ru": "ТЦ Samarkand Darvoza (Коратош, 5А) ⚠️ Реконструкция",
        "name_uz": "TC Samarqand Darvoza (Koratosh, 5A) ⚠️ Ta'mirda",
        "address_ru": "📍 ул. Коратош, 5А",
        "address_uz": "📍 Koratosh ko'chasi, 5A",
        "hours": "🕐 10:00 – 22:00 (вых. до 23:00)",
        "phone": "📞 +998 90-067-03-31",
        "map": "https://maps.app.goo.gl/mAdBMFSRLtMLw3Ft8"
    },
    {
        "name_ru": "Алайский рынок (Кашгар 4)",
        "name_uz": "Oloy bozori (Kashgar 4)",
        "address_ru": "📍 Юнусабадский район, массив Кашгар, 4",
        "address_uz": "📍 Yunusobod tumani, Kashgar massivi, 4",
        "hours": "🕐 10:00 – 20:00 (без выходных / har kuni)",
        "phone": "📞 +998 90-066-03-31",
        "map": "https://maps.app.goo.gl/wART8oQJzNgBrQsZ6"
    },
    {
        "name_ru": "Самарканд — ТЦ Makon Mall, 2 этаж",
        "name_uz": "Samarqand — TC Makon Mall, 2-qavat",
        "address_ru": "📍 ул. Шахруха Мирзы, 17",
        "address_uz": "📍 Shahruх Mirzo ko'chasi, 17",
        "hours": "🕐 10:00 – 22:00 (без выходных / har kuni)",
        "phone": "📞 +998 90-830-64-35 | 📱 @corecl_uz",
        "map": "https://maps.app.goo.gl/MeEPPjyV1LknaS7v5"
    },
    {
        "name_ru": "ТРЦ Compass (Метро Куйлюк)",
        "name_uz": "TRC Compass (Kuylyuk metro)",
        "address_ru": "📍 ТРЦ Compass, метро Куйлюк",
        "address_uz": "📍 TRC Compass, Kuylyuk metro",
        "hours": "🕐 10:00 – 22:00 (без выходных / har kuni)",
        "phone": "📞 +998 90-941-03-31",
        "map": "https://maps.app.goo.gl/MeEPPjyV1LknaS7v5"
    },
]

BRANCH_NAMES_RU = [b["name_ru"] for b in BRANCHES]
BRANCH_NAMES_UZ = [b["name_uz"] for b in BRANCHES]

# ===================== ТЕКСТЫ =====================
TEXTS = {
    "ru": {
        "welcome": "👋 Добро пожаловать в <b>Core Collection</b>!\n\nВыберите нужный раздел:",
        "return_text": (
            "🔄 <b>Условия возврата и обмена товара</b>\n\n"
            "Возврат и обмен товара в магазинах <b>Core Collection</b> возможен при сохранности "
            "товарного вида, фабричных ярлыков и неповреждённых бирок, а также при наличии "
            "товарного и кассового чека в течение <b>10 дней</b> с момента покупки в том магазине, "
            "где товар был приобретён.\n\n"
            "⚠️ <i>Скидочный товар, сумки, головные уборы, обувь и аксессуары возврату и обмену не подлежат.</i>"
        ),
        "delivery_text": (
            "🚚 <b>Условия доставки</b>\n\n"
            "Оформите доставку на сайте: <a href='https://corecl.cc/'>corecl.cc</a>\n\n"
            "<b>1. Доставка по Ташкенту</b>\n"
            "• Яндекс Доставка\n• Срок — до 2 дней\n• Оплата курьеру при получении\n\n"
            "<b>2. Доставка по регионам</b>\n"
            "• BTS почта\n• Срок — 3–5 рабочих дней\n• Оплата при получении\n\n"
            "<b>3. Экспресс-доставка (Ташкент)</b>\n"
            "• В течение 2 часов после оформления\n• Доставка в день заказа\n• Доплата за срочность при получении\n\n"
            "<b>4. Самовывоз</b>\n"
            "• Из любого филиала\n• Бесплатно ✅"
        ),
        "tracking_text": (
            "📦 <b>Отслеживание заказа</b>\n\n"
            "🔧 Функция скоро будет доступна.\n\n"
            "Мы работаем над интеграцией с EMU Delivery.\n"
            "Совсем скоро вы сможете отслеживать заказ прямо здесь!"
        ),
        "follow_text": "📲 <b>Следите за нами!</b>\n\nБудьте в курсе новинок, акций и скидок 🔥",
        "complaint_ask": "📝 <b>Жалобы и предложения</b>\n\nНапишите вашу жалобу или предложение:",
        "complaint_sent": "✅ Сообщение отправлено! Спасибо за обратную связь.",
        "phones_text": (
            "📞 <b>Контактные номера филиалов</b>\n\n"
            "🏪 Буюк Ипак Йули: +998 90-933-03-31\n"
            "🏪 ТЦ Next: +998 90-999-03-31\n"
            "🏪 ТЦ Zarafshan: +998 90-044-03-31\n"
            "🏪 ТЦ Samarkand Darvoza: +998 90-067-03-31\n"
            "🏪 Алайский (Кашгар 4): +998 90-066-03-31\n"
            "🏪 Самарканд Makon Mall: +998 90-830-64-35\n"
            "🏪 ТРЦ Compass: +998 90-941-03-31"
        ),
        "payment_text": (
            "💳 <b>Оплата заказа</b>\n\n"
            "🔧 Платёжная система Payme скоро будет подключена.\n\n"
            "Оформите заказ на сайте: <a href='https://corecl.cc/'>corecl.cc</a>"
        ),
        "branches_title": "🏪 Выберите филиал:",

        # Инфо о вакансии
        "vac_info": (
            "💼 <b>Вакансии — Core Collection</b>\n\n"
            "Здравствуйте! Спасибо за проявленный интерес к нашей вакансии.\n\n"
            "Чтобы продолжить рассмотрение вашей кандидатуры, необходимо заполнить анкету прямо здесь в боте.\n\n"
            "<b>Анкета включает:</b>\n"
            "1️⃣ Имя\n"
            "2️⃣ Возраст / Дата рождения\n"
            "3️⃣ Номер телефона\n"
            "4️⃣ Студент или нет (учебное заведение, график, курс, факультет)\n"
            "5️⃣ Смена:\n"
            "   • 1-я смена: 09:00 – 18:00\n"
            "   • 2-я смена: 14:00 – 22:00\n"
            "6️⃣ Удобные филиалы (минимум 3):\n"
            "   • ТЦ Зарафшан\n"
            "   • ст.м. Буюк Ипак Йули\n"
            "   • Алайский рынок\n"
            "   • ТРЦ Самарканд Дарвоза\n"
            "   • ТРЦ Next\n"
            "   • ТРЦ Compass\n"
            "   • г. Самарканд — Makon Mall\n"
            "7️⃣ Срок работы\n"
            "8️⃣ Фото (лицо хорошо видно)\n"
            "9️⃣ Дата начала работы\n\n"
            "Нажмите кнопку ниже, чтобы начать заполнение анкеты 👇"
        ),
        "vac_fill_btn": "📝 Заполнить анкету",

        # Анкета
        "vac_start": "💼 <b>Вакансии — Core Collection</b>\n\nЗаполним анкету по шагам!\n\nШаг 1️⃣ из 9️⃣\n<b>Введите ваше имя:</b>",
        "vac_age": "Шаг 2️⃣ из 9️⃣\n<b>Введите ваш возраст или дату рождения:</b>",
        "vac_phone": "Шаг 3️⃣ из 9️⃣\n<b>Введите ваш номер телефона:</b>",
        "vac_student_q": "Шаг 4️⃣ из 9️⃣\n<b>Вы студент?</b>",
        "vac_student_yes": "🎓 Да, студент",
        "vac_student_no": "✋ Нет, не студент",
        "vac_student_info": "Укажите одним сообщением:\n• Название учебного заведения\n• График учёбы\n• Курс и факультет",
        "vac_shift": "Шаг 5️⃣ из 9️⃣\n<b>В какую смену планируете работать?</b>",
        "vac_shift_1": "☀️ 1-я смена: 09:00 – 18:00",
        "vac_shift_2": "🌙 2-я смена: 14:00 – 22:00",
        "vac_branch": "Шаг 6️⃣ из 9️⃣\n<b>Выберите удобные филиалы (минимум 3)</b>\nНажимайте на несколько, затем ✅ Готово:",
        "vac_branch_done": "✅ Готово",
        "vac_duration": "Шаг 7️⃣ из 9️⃣\n<b>На какой срок рассматриваете работу у нас?</b>",
        "vac_photo": "Шаг 8️⃣ из 9️⃣\n<b>Отправьте ваше фото</b>\n(лицо должно быть хорошо видно):",
        "vac_start_date": "Шаг 9️⃣ из 9️⃣\n<b>С какого числа можете приступить к работе?</b>",
        "vac_sent": "✅ <b>Анкета отправлена!</b>\n\nСпасибо! Наш HR-менеджер свяжется с вами в ближайшее время. 🙌",
        "vac_cancel": "❌ Анкета отменена. Возвращаемся в главное меню.",
        "vac_cancel_btn": "❌ Отмена",
        "vac_select_min3": "⚠️ Выберите минимум 3 филиала!",
        "vac_photo_error": "⚠️ Пожалуйста, отправьте именно фото (не файл).",

        "btn_return": "🔄 Возврат и обмен",
        "btn_delivery": "🚚 Условия доставки",
        "btn_branches": "🏪 Филиалы",
        "btn_tracking": "📦 Отслеживание заказа",
        "btn_vacancy": "💼 Вакансии",
        "btn_complaint": "📝 Жалобы и предложения",
        "btn_follow": "📲 Следите за нами",
        "btn_phones": "📞 Номера телефонов",
        "btn_payment": "💳 Оплата",
        "btn_instagram": "📸 Instagram",
        "btn_telegram": "✈️ Telegram канал",
        "btn_website": "🌐 Сайт",
        "btn_back": "⬅️ Назад",
    },
    "uz": {
        "welcome": "👋 <b>Core Collection</b>ga xush kelibsiz!\n\nKerakli bo'limni tanlang:",
        "return_text": (
            "🔄 <b>Tovarni qaytarish va almashtirish shartlari</b>\n\n"
            "<b>Core Collection</b> do'konlarida tovarni qaytarish va almashtirish "
            "tovar ko'rinishi, fabrika yorliqlari va shikastlanmagan belgilar saqlanib qolgan holda, "
            "shuningdek tovar va kassa cheki mavjud bo'lganda xarid qilingan do'konda "
            "<b>10 kun</b> ichida mumkin.\n\n"
            "⚠️ <i>Chegirmali tovar, sumkalar, bosh kiyimlar, poyabzal va aksessuarlar "
            "qaytarilmaydi va almashtirilmaydi.</i>"
        ),
        "delivery_text": (
            "🚚 <b>Yetkazib berish shartlari</b>\n\n"
            "Saytda buyurtma bering: <a href='https://corecl.cc/'>corecl.cc</a>\n\n"
            "<b>1. Toshkent bo'yicha</b>\n"
            "• Yandex Delivery\n• Muddat — 2 kungacha\n• To'lov kuryerga\n\n"
            "<b>2. Hududlar bo'yicha</b>\n"
            "• BTS pochta\n• Muddat — 3–5 ish kuni\n• To'lov olganda\n\n"
            "<b>3. Ekspress (Toshkent)</b>\n"
            "• 2 soat ichida\n• Buyurtma kuni yetkaziladi\n• Qo'shimcha to'lov\n\n"
            "<b>4. O'zi olib ketish</b>\n"
            "• Istalgan filialdan\n• Bepul ✅"
        ),
        "tracking_text": (
            "📦 <b>Buyurtmani kuzatish</b>\n\n"
            "🔧 Bu funksiya tez orada ishga tushadi.\n\n"
            "EMU Delivery bilan integratsiya ustida ishlamoqdamiz!"
        ),
        "follow_text": "📲 <b>Bizni kuzating!</b>\n\nYangiliklar, aksiyalar va chegirmalardan xabardor bo'ling 🔥",
        "complaint_ask": "📝 <b>Shikoyat va takliflar</b>\n\nShikoyat yoki taklifingizni yozing:",
        "complaint_sent": "✅ Xabaringiz yuborildi! Rahmat.",
        "phones_text": (
            "📞 <b>Filiallar telefon raqamlari</b>\n\n"
            "🏪 Buyuk Ipak Yo'li: +998 90-933-03-31\n"
            "🏪 TC Next: +998 90-999-03-31\n"
            "🏪 TC Zarafshon: +998 90-044-03-31\n"
            "🏪 TC Samarqand Darvoza: +998 90-067-03-31\n"
            "🏪 Oloy (Kashgar 4): +998 90-066-03-31\n"
            "🏪 Samarqand Makon Mall: +998 90-830-64-35\n"
            "🏪 TRC Compass: +998 90-941-03-31"
        ),
        "payment_text": (
            "💳 <b>Buyurtmani to'lash</b>\n\n"
            "🔧 Payme tez orada ulanadi.\n\n"
            "Saytda buyurtma bering: <a href='https://corecl.cc/'>corecl.cc</a>"
        ),
        "branches_title": "🏪 Filialni tanlang:",

        # Инфо о вакансии
        "vac_info": (
            "💼 <b>Vakansiyalar — Core Collection</b>\n\n"
            "Salom! Bizning vakansiyamizga qiziqish bildirganingiz uchun rahmat.\n\n"
            "Nomzodingizni ko'rib chiqishni davom ettirish uchun anketani to'ldiring.\n\n"
            "<b>Anketa quyidagilarni o'z ichiga oladi:</b>\n"
            "1️⃣ Ism\n"
            "2️⃣ Yosh / Tug'ilgan sana\n"
            "3️⃣ Telefon raqam\n"
            "4️⃣ Talaba yoki yo'q (muassasa, jadval, kurs, fakultet)\n"
            "5️⃣ Smena:\n"
            "   • 1-smena: 09:00 – 18:00\n"
            "   • 2-smena: 14:00 – 22:00\n"
            "6️⃣ Qulay filiallar (kamida 3 ta):\n"
            "   • TC Zarafshon\n"
            "   • Buyuk Ipak Yo'li metrostansiyasi\n"
            "   • Oloy bozori\n"
            "   • TRC Samarqand Darvoza\n"
            "   • TRC Next\n"
            "   • TRC Compass\n"
            "   • Samarqand — Makon Mall\n"
            "7️⃣ Ishlash muddati\n"
            "8️⃣ Surat (yuz aniq ko'rinsin)\n"
            "9️⃣ Ish boshlash sanasi\n\n"
            "Anketani to'ldirish uchun tugmani bosing 👇"
        ),
        "vac_fill_btn": "📝 Anketani to'ldirish",

        # Анкета
        "vac_start": "💼 <b>Vakansiyalar — Core Collection</b>\n\nAnketani bosqichma-bosqich to'ldiramiz!\n\n1️⃣ / 9️⃣-qadam\n<b>Ismingizni kiriting:</b>",
        "vac_age": "2️⃣ / 9️⃣-qadam\n<b>Yoshingiz yoki tug'ilgan sanangizni kiriting:</b>",
        "vac_phone": "3️⃣ / 9️⃣-qadam\n<b>Telefon raqamingizni kiriting:</b>",
        "vac_student_q": "4️⃣ / 9️⃣-qadam\n<b>Siz talabamisiz?</b>",
        "vac_student_yes": "🎓 Ha, talabaman",
        "vac_student_no": "✋ Yo'q, talaba emasman",
        "vac_student_info": "Bitta xabarda yozing:\n• O'quv muassasasi nomi\n• O'qish jadvali\n• Kurs va fakultet",
        "vac_shift": "5️⃣ / 9️⃣-qadam\n<b>Qaysi smena qulay?</b>",
        "vac_shift_1": "☀️ 1-smena: 09:00 – 18:00",
        "vac_shift_2": "🌙 2-smena: 14:00 – 22:00",
        "vac_branch": "6️⃣ / 9️⃣-qadam\n<b>Qulay filiallarni tanlang (kamida 3 ta)</b>\nBir nechtasini bosing, keyin ✅ Tayyor:",
        "vac_branch_done": "✅ Tayyor",
        "vac_duration": "7️⃣ / 9️⃣-qadam\n<b>Qancha muddatga ishlashni ko'rib chiqyapsiz?</b>",
        "vac_photo": "8️⃣ / 9️⃣-qadam\n<b>SuratIngizni yuboring</b>\n(yuz aniq ko'rinsin):",
        "vac_start_date": "9️⃣ / 9️⃣-qadam\n<b>Qaysi sanadan ish boshlashingiz mumkin?</b>",
        "vac_sent": "✅ <b>Anketa yuborildi!</b>\n\nRahmat! HR menejerimiz tez orada siz bilan bog'lanadi. 🙌",
        "vac_cancel": "❌ Anketa bekor qilindi. Asosiy menyuga qaytamiz.",
        "vac_cancel_btn": "❌ Bekor qilish",
        "vac_select_min3": "⚠️ Kamida 3 ta filialni tanlang!",
        "vac_photo_error": "⚠️ Iltimos, rasm yuboring (fayl emas).",

        "btn_return": "🔄 Qaytarish va almashtirish",
        "btn_delivery": "🚚 Yetkazib berish",
        "btn_branches": "🏪 Filiallar",
        "btn_tracking": "📦 Buyurtmani kuzatish",
        "btn_vacancy": "💼 Vakansiyalar",
        "btn_complaint": "📝 Shikoyat va takliflar",
        "btn_follow": "📲 Bizni kuzating",
        "btn_phones": "📞 Telefon raqamlar",
        "btn_payment": "💳 To'lov",
        "btn_instagram": "📸 Instagram",
        "btn_telegram": "✈️ Telegram kanal",
        "btn_website": "🌐 Sayt",
        "btn_back": "⬅️ Orqaga",
    }
}

# ===================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ =====================
def get_lang(context):
    return context.user_data.get("lang", "ru")

def t(key, context):
    lang = get_lang(context)
    return TEXTS[lang].get(key, TEXTS["ru"].get(key, ""))

def main_menu_keyboard(context):
    lang = get_lang(context)
    tx = TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(tx["btn_return"], callback_data="return")],
        [InlineKeyboardButton(tx["btn_delivery"], callback_data="delivery")],
        [InlineKeyboardButton(tx["btn_branches"], callback_data="branches")],
        [InlineKeyboardButton(tx["btn_tracking"], callback_data="tracking")],
        [InlineKeyboardButton(tx["btn_vacancy"], callback_data="vacancy_info")],
        [InlineKeyboardButton(tx["btn_complaint"], callback_data="complaint")],
        [InlineKeyboardButton(tx["btn_follow"], callback_data="follow")],
        [InlineKeyboardButton(tx["btn_phones"], callback_data="phones")],
        [InlineKeyboardButton(tx["btn_payment"], callback_data="payment")],
    ])

def back_keyboard(context):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("btn_back", context), callback_data="main_menu")]
    ])

def cancel_keyboard(context):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t("vac_cancel_btn", context), callback_data="vac_cancel")]
    ])

def branch_keyboard(context):
    lang = get_lang(context)
    selected = context.user_data.get("vac_branches", [])
    names = BRANCH_NAMES_RU if lang == "ru" else BRANCH_NAMES_UZ
    keyboard = []
    for i, name in enumerate(names):
        label = f"✅ {name}" if i in selected else name
        keyboard.append([InlineKeyboardButton(label, callback_data=f"vbranch_{i}")])
    keyboard.append([InlineKeyboardButton(t("vac_branch_done", context), callback_data="vbranch_done")])
    keyboard.append([InlineKeyboardButton(t("vac_cancel_btn", context), callback_data="vac_cancel")])
    return InlineKeyboardMarkup(keyboard)

# ===================== СТАРТ / ЯЗЫК =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        ]
    ])
    await update.message.reply_text(
        "🌐 <b>Выберите язык / Tilni tanlang:</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    context.user_data["lang"] = lang
    await query.edit_message_text(
        TEXTS[lang]["welcome"],
        reply_markup=main_menu_keyboard(context),
        parse_mode="HTML"
    )

async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        t("welcome", context),
        reply_markup=main_menu_keyboard(context),
        parse_mode="HTML"
    )

# ===================== КНОПКИ МЕНЮ =====================
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "return":
        await query.edit_message_text(
            t("return_text", context), reply_markup=back_keyboard(context), parse_mode="HTML"
        )
    elif data == "delivery":
        await query.edit_message_text(
            t("delivery_text", context), reply_markup=back_keyboard(context), parse_mode="HTML"
        )
    elif data == "tracking":
        await query.edit_message_text(
            t("tracking_text", context), reply_markup=back_keyboard(context), parse_mode="HTML"
        )
    elif data == "follow":
        lang = get_lang(context)
        tx = TEXTS[lang]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(tx["btn_instagram"], url=INSTAGRAM)],
            [InlineKeyboardButton(tx["btn_telegram"], url=TG_CHANNEL)],
            [InlineKeyboardButton(tx["btn_website"], url=WEBSITE)],
            [InlineKeyboardButton(tx["btn_back"], callback_data="main_menu")],
        ])
        await query.edit_message_text(
            t("follow_text", context), reply_markup=keyboard, parse_mode="HTML"
        )
    elif data == "phones":
        await query.edit_message_text(
            t("phones_text", context), reply_markup=back_keyboard(context), parse_mode="HTML"
        )
    elif data == "payment":
        await query.edit_message_text(
            t("payment_text", context), reply_markup=back_keyboard(context), parse_mode="HTML"
        )
    elif data == "branches":
        await show_branches(query, context)
    elif data.startswith("branch_"):
        idx = int(data.split("_")[1])
        await show_branch_detail(query, context, idx)
    elif data == "complaint":
        context.user_data["awaiting_complaint"] = True
        await query.edit_message_text(
            t("complaint_ask", context), reply_markup=back_keyboard(context), parse_mode="HTML"
        )
    elif data == "vacancy_info":
        lang = get_lang(context)
        tx = TEXTS[lang]
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(tx["vac_fill_btn"], callback_data="vacancy")],
            [InlineKeyboardButton(tx["btn_back"], callback_data="main_menu")],
        ])
        await query.edit_message_text(
            t("vac_info", context), reply_markup=keyboard, parse_mode="HTML"
        )
    elif data == "main_menu":
        await main_menu_callback(update, context)

# ===================== ФИЛИАЛЫ =====================
async def show_branches(query, context):
    lang = get_lang(context)
    keyboard = []
    for i, branch in enumerate(BRANCHES):
        name = branch["name_ru"] if lang == "ru" else branch["name_uz"]
        keyboard.append([InlineKeyboardButton(f"🏪 {name}", callback_data=f"branch_{i}")])
    keyboard.append([InlineKeyboardButton(t("btn_back", context), callback_data="main_menu")])
    await query.edit_message_text(
        t("branches_title", context),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )

async def show_branch_detail(query, context, idx):
    lang = get_lang(context)
    branch = BRANCHES[idx]
    name = branch["name_ru"] if lang == "ru" else branch["name_uz"]
    address = branch["address_ru"] if lang == "ru" else branch["address_uz"]
    text = f"🏪 <b>{name}</b>\n\n{address}\n{branch['hours']}\n{branch['phone']}"
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🗺 Google Maps", url=branch["map"])],
        [InlineKeyboardButton(t("btn_back", context), callback_data="branches")],
    ])
    await query.edit_message_text(text, reply_markup=keyboard, parse_mode="HTML")

# ===================== АНКЕТА ВАКАНСИИ =====================
async def vacancy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["vacancy"] = {}
    context.user_data["vac_branches"] = []
    await query.edit_message_text(
        t("vac_start", context),
        reply_markup=cancel_keyboard(context),
        parse_mode="HTML"
    )
    return VACANCY_NAME

async def vac_get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["vacancy"]["name"] = update.message.text
    await update.message.reply_text(
        t("vac_age", context), reply_markup=cancel_keyboard(context), parse_mode="HTML"
    )
    return VACANCY_AGE

async def vac_get_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["vacancy"]["age"] = update.message.text
    await update.message.reply_text(
        t("vac_phone", context), reply_markup=cancel_keyboard(context), parse_mode="HTML"
    )
    return VACANCY_PHONE

async def vac_get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["vacancy"]["phone"] = update.message.text
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("vac_student_yes", context), callback_data="student_yes")],
        [InlineKeyboardButton(t("vac_student_no", context), callback_data="student_no")],
        [InlineKeyboardButton(t("vac_cancel_btn", context), callback_data="vac_cancel")],
    ])
    await update.message.reply_text(
        t("vac_student_q", context), reply_markup=keyboard, parse_mode="HTML"
    )
    return VACANCY_STUDENT

async def vac_student_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "student_yes":
        context.user_data["vacancy"]["is_student"] = True
        await query.edit_message_text(
            t("vac_student_info", context),
            reply_markup=cancel_keyboard(context),
            parse_mode="HTML"
        )
        return VACANCY_STUDENT_INFO
    else:
        context.user_data["vacancy"]["is_student"] = False
        context.user_data["vacancy"]["student_info"] = "—"
        context.user_data["vac_branches"] = []
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(t("vac_shift_1", context), callback_data="shift_1")],
            [InlineKeyboardButton(t("vac_shift_2", context), callback_data="shift_2")],
            [InlineKeyboardButton(t("vac_cancel_btn", context), callback_data="vac_cancel")],
        ])
        await query.edit_message_text(
            t("vac_shift", context), reply_markup=keyboard, parse_mode="HTML"
        )
        return VACANCY_SHIFT

async def vac_get_student_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["vacancy"]["student_info"] = update.message.text
    context.user_data["vac_branches"] = []
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(t("vac_shift_1", context), callback_data="shift_1")],
        [InlineKeyboardButton(t("vac_shift_2", context), callback_data="shift_2")],
        [InlineKeyboardButton(t("vac_cancel_btn", context), callback_data="vac_cancel")],
    ])
    await update.message.reply_text(
        t("vac_shift", context), reply_markup=keyboard, parse_mode="HTML"
    )
    return VACANCY_SHIFT

async def vac_shift_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    shift_map = {
        "shift_1": "1-я смена: 09:00 – 18:00",
        "shift_2": "2-я смена: 14:00 – 22:00"
    }
    context.user_data["vacancy"]["shift"] = shift_map[query.data]
    await query.edit_message_text(
        t("vac_branch", context),
        reply_markup=branch_keyboard(context),
        parse_mode="HTML"
    )
    return VACANCY_BRANCH

async def vac_branch_toggle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "vbranch_done":
        selected = context.user_data.get("vac_branches", [])
        if len(selected) < 3:
            await query.answer(t("vac_select_min3", context), show_alert=True)
            return VACANCY_BRANCH
        lang = get_lang(context)
        names = BRANCH_NAMES_RU if lang == "ru" else BRANCH_NAMES_UZ
        chosen = [names[i] for i in selected]
        context.user_data["vacancy"]["branches"] = "\n   • " + "\n   • ".join(chosen)
        await query.edit_message_text(
            t("vac_duration", context),
            reply_markup=cancel_keyboard(context),
            parse_mode="HTML"
        )
        return VACANCY_DURATION

    idx = int(query.data.split("_")[1])
    selected = context.user_data.get("vac_branches", [])
    if idx in selected:
        selected.remove(idx)
    else:
        selected.append(idx)
    context.user_data["vac_branches"] = selected
    try:
        await query.edit_message_reply_markup(reply_markup=branch_keyboard(context))
    except Exception:
        pass
    return VACANCY_BRANCH

async def vac_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["vacancy"]["duration"] = update.message.text
    await update.message.reply_text(
        t("vac_photo", context), reply_markup=cancel_keyboard(context), parse_mode="HTML"
    )
    return VACANCY_PHOTO

async def vac_get_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        await update.message.reply_text(
            t("vac_photo_error", context), reply_markup=cancel_keyboard(context)
        )
        return VACANCY_PHOTO
    context.user_data["vacancy"]["photo_id"] = update.message.photo[-1].file_id
    await update.message.reply_text(
        t("vac_start_date", context), reply_markup=cancel_keyboard(context), parse_mode="HTML"
    )
    return VACANCY_START_DATE

async def vac_get_start_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["vacancy"]["start_date"] = update.message.text
    await send_vacancy_to_hr(update, context)
    await update.message.reply_text(
        t("vac_sent", context),
        reply_markup=main_menu_keyboard(context),
        parse_mode="HTML"
    )
    return ConversationHandler.END

async def send_vacancy_to_hr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    v = context.user_data.get("vacancy", {})
    student_label = "Да ✅" if v.get("is_student") else "Нет ❌"

    text = (
        f"💼 <b>НОВАЯ АНКЕТА НА ВАКАНСИЮ</b>\n"
        f"{'━' * 25}\n\n"
        f"👤 <b>Telegram:</b> {user.full_name}\n"
        f"🔗 <b>Username:</b> @{user.username or '—'}\n"
        f"🆔 <b>ID:</b> <code>{user.id}</code>\n\n"
        f"1️⃣ <b>Имя:</b> {v.get('name', '—')}\n"
        f"2️⃣ <b>Возраст:</b> {v.get('age', '—')}\n"
        f"3️⃣ <b>Телефон:</b> {v.get('phone', '—')}\n"
        f"4️⃣ <b>Студент:</b> {student_label}\n"
        f"    <b>Инфо:</b> {v.get('student_info', '—')}\n"
        f"5️⃣ <b>Смена:</b> {v.get('shift', '—')}\n"
        f"6️⃣ <b>Филиалы:</b>{v.get('branches', '—')}\n"
        f"7️⃣ <b>Срок работы:</b> {v.get('duration', '—')}\n"
        f"9️⃣ <b>Дата начала:</b> {v.get('start_date', '—')}"
    )

    photo_id = v.get("photo_id")
    if photo_id:
        await context.bot.send_photo(
            chat_id=HR_ID,
            photo=photo_id,
            caption=text,
            parse_mode="HTML"
        )
    else:
        await context.bot.send_message(
            chat_id=HR_ID,
            text=text,
            parse_mode="HTML"
        )

async def vac_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data.pop("vacancy", None)
    context.user_data.pop("vac_branches", None)
    await query.edit_message_text(
        t("vac_cancel", context),
        reply_markup=main_menu_keyboard(context),
        parse_mode="HTML"
    )
    return ConversationHandler.END

# ===================== ЖАЛОБЫ / ОБЩИЕ СООБЩЕНИЯ =====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_complaint"):
        context.user_data["awaiting_complaint"] = False
        user = update.effective_user
        text = (
            f"📩 <b>НОВАЯ ЖАЛОБА / ПРЕДЛОЖЕНИЕ</b>\n"
            f"{'━' * 25}\n\n"
            f"👤 {user.full_name} (@{user.username or '—'})\n"
            f"🆔 ID: <code>{user.id}</code>\n\n"
            f"💬 {update.message.text}"
        )
        await context.bot.send_message(
            chat_id=COMPLAINTS_ID, text=text, parse_mode="HTML"
        )
        await update.message.reply_text(
            t("complaint_sent", context),
            reply_markup=main_menu_keyboard(context)
        )
    else:
        await update.message.reply_text(
            t("welcome", context),
            reply_markup=main_menu_keyboard(context),
            parse_mode="HTML"
        )

# ===================== ЗАПУСК =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler для анкеты вакансии
    vacancy_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(vacancy_start, pattern="^vacancy$")],
        states={
            VACANCY_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, vac_get_name)
            ],
            VACANCY_AGE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, vac_get_age)
            ],
            VACANCY_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, vac_get_phone)
            ],
            VACANCY_STUDENT: [
                CallbackQueryHandler(vac_student_choice, pattern="^student_")
            ],
            VACANCY_STUDENT_INFO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, vac_get_student_info)
            ],
            VACANCY_SHIFT: [
                CallbackQueryHandler(vac_shift_choice, pattern="^shift_")
            ],
            VACANCY_BRANCH: [
                CallbackQueryHandler(vac_branch_toggle, pattern="^vbranch_")
            ],
            VACANCY_DURATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, vac_get_duration)
            ],
            VACANCY_PHOTO: [
                MessageHandler(filters.PHOTO, vac_get_photo),
                MessageHandler(filters.TEXT & ~filters.COMMAND, vac_get_photo),
            ],
            VACANCY_START_DATE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, vac_get_start_date)
            ],
        },
        fallbacks=[
            CallbackQueryHandler(vac_cancel, pattern="^vac_cancel$"),
            CommandHandler("start", start),
        ],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(language_callback, pattern="^lang_"))
    app.add_handler(CallbackQueryHandler(main_menu_callback, pattern="^main_menu$"))
    app.add_handler(vacancy_conv)
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
