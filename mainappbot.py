import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, ConversationHandler, Filters, CallbackContext

# Константы для работы с Google Sheets
GOOGLE_SHEETS_FILE = "Your google sheet name"
GOOGLE_SHEETS_WORKSHEET = "worksheet name"


# Функция для записи данных в Google Sheets
# Сначала нужно будет в google cloud получить данные о проекте и api в виде json
def save_to_google_sheets(data):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('xxxxxxxx.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEETS_FILE).worksheet(GOOGLE_SHEETS_WORKSHEET)
    sheet.append_row(data)


# Состояния для обработки разговора
MENU, FIO, POSITION, REQUEST = range(4)


def start(update: Update, _: CallbackContext) -> int:

    # Создаем кнопки для меню
    keyboard = [
        [KeyboardButton("Предложение")],
        [KeyboardButton("Помощь")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)

    # Отправляем сообщение с приветствием и кнопками меню
    update.message.reply_text("Здравствуйте! Мы очень рады новым предложениям по применению ИИ для автоматизации "
                              "рабочих процессов.",
                              reply_markup=reply_markup)

    return MENU


def cancel(update: Update, _: CallbackContext) -> int:
    # Обработчик команды /cancel, вызывается при отмене текущего действия
    update.message.reply_text("Отменено.")
    return start(update, _)


def menu(update: Update, _: CallbackContext) -> int:
    # Обработчик для отображения меню и перехода к соответствующим действиям
    if update.message.text == "Заявка":
        update.message.reply_text("Напишите свое ФИО:")
        return FIO
    elif update.message.text == "Помощь":
        update.message.reply_text("Если у вас возникли вопросы, вы можете связаться с нами по номеру  "
                                  "+79999999999")
        return MENU
    else:
        update.message.reply_text("Неверный выбор. Пожалуйста, используйте кнопки меню.")
        return MENU


def get_fio(update: Update, _: CallbackContext) -> int:
    # Обработчик для получения ФИО от пользователя
    _.user_data['fio'] = update.message.text
    update.message.reply_text("Отлично! Теперь укажите свою должность:")
    return POSITION


def get_position(update: Update, _: CallbackContext) -> int:
    # Обработчик для получения должности от пользователя
    _.user_data['position'] = update.message.text
    update.message.reply_text("Хорошо! Теперь напишите свое предложение (максимально подробно):")
    return REQUEST


def get_request(update: Update, _: CallbackContext) -> int:
    # Обработчик для получения заявки от пользователя и записи данных в Google Sheets
    fio = _.user_data.get('fio')
    position = _.user_data.get('position')
    request = update.message.text
    save_to_google_sheets([fio, position, request])

    update.message.reply_text("Спасибо за предложение! Мы свяжемся с вами, если понадобится дополнительная информация.")
    update.message.reply_text("Всегда будем рады новым предложениям. Следующее предложение можно отправить, выбравь в "
                              "пункт меню кнопку 'Предожение'")
    return MENU


def main():
    # Инициализация бота и диспетчера
    updater = Updater("You telegram bot token")
    dispatcher = updater.dispatcher

    # Создание обработчика диалога (ConversationHandler) для меню и заявок
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MENU: [MessageHandler(Filters.text & ~Filters.command, menu)],
            FIO: [MessageHandler(Filters.text & ~Filters.command, get_fio)],
            POSITION: [MessageHandler(Filters.text & ~Filters.command, get_position)],
            REQUEST: [MessageHandler(Filters.text & ~Filters.command, get_request)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    # Добавление обработчика диалога в диспетчер
    dispatcher.add_handler(conv_handler)

    # Запуск бота и ожидание входящих сообщений
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
