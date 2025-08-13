from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import os
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuizStates(StatesGroup):
    waiting_for_quiz_id = State()
    waiting_for_answer = State()

load_dotenv()

bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
dp = Dispatcher()

API_URL = 'http://localhost:5000/api'

def get_quiz(quiz_id: int) -> dict | None:
    """Получить квиз по ID.
    Args:
        quiz_id (int): ID квиза
    Returns:
        dict | None: Данные квиза или None при ошибке
    """
    try:
        response = requests.get(f"{API_URL}/quizzes/{quiz_id}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error getting quiz {quiz_id}: {e}")
        return None

def create_attempt(quiz_id: int, user_id: int) -> dict | None:
    """Создать новую попытку прохождения квиза.
    Args:
        quiz_id (int): ID квиза
        user_id (int): ID пользователя
    Returns:
        dict | None: Данные созданной попытки или None при ошибке
    """
    try:
        response = requests.post(
            f"{API_URL}/attempts",
            json={'quiz_id': quiz_id, 'user_id': user_id}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error creating attempt: {e}")
        return None

def submit_answer(attempt_id: int, question_id: int, answer_data: dict) -> dict | None:
    """Отправить ответ на вопрос на сервер.
    Args:
        attempt_id (int): ID попытки
        question_id (int): ID вопроса
        answer_data (dict): Данные ответа
    Returns:
        dict | None: Данные ответа или None при ошибке
    """
    try:
        response = requests.post(
            f"{API_URL}/attempts/{attempt_id}/answers",
            json={'question_id': question_id, **answer_data}
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error submitting answer: {e}")
        return None

def complete_attempt(attempt_id: int) -> dict | None:
    """Завершить попытку прохождения квиза.
    Args:
        attempt_id (int): ID попытки
    Returns:
        dict | None: Данные завершённой попытки или None при ошибке
    """
    try:
        response = requests.post(f"{API_URL}/attempts/{attempt_id}/complete")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Error completing attempt: {e}")
        return None

def get_attempt(attempt_id: int) -> dict | None:
    """Получить данные о попытке прохождения.
    Args:
        attempt_id (int): ID попытки
    Returns:
        dict | None: Данные попытки или None при ошибке
    """
    response = requests.get(f"{API_URL}/attempts/{attempt_id}")
    return response.json() if response.status_code == 200 else None

def get_next_question(attempt_id: int) -> dict | None:
    """Получить следующий вопрос для попытки.
    Args:
        attempt_id (int): ID попытки
    Returns:
        dict | None: Данные вопроса или None если вопросы закончились
    """
    attempt = get_attempt(attempt_id)
    if not attempt:
        return None
        
    quiz = get_quiz(attempt['quiz_id'])
    if not quiz or 'questions' not in quiz:
        return None
        
    answered_ids = [a['question_id'] for a in attempt.get('answers', [])]
    for question in quiz['questions']:
        if question['id'] not in answered_ids:
            return question
    return None

async def send_question(chat_id: int, question: dict, state: FSMContext):
    """Отправить вопрос пользователю и обновить локальное состояние.
    Args:
        chat_id (int): ID чата
        question (dict): Данные вопроса
        state (FSMContext): Контекст состояния
    """
    if question['question_type'] == 'text':
        await bot.send_message(
            chat_id, 
            f"Вопрос:\n{question['text']}\n\nОтправьте текстовый ответ"
        )
    elif question['question_type'] == 'option':
        builder = InlineKeyboardBuilder()
        for option in question.get('options', []):
            builder.add(types.InlineKeyboardButton(
                text=option['text'],
                callback_data=f"answer_{option['id']}"
            ))
        builder.adjust(1)
        await bot.send_message(
            chat_id,
            f"Вопрос:\n{question['text']}",
            reply_markup=builder.as_markup()
        )
    await state.update_data(current_question=question)

@dp.message(Command('start'))
async def start(message: types.Message):
    """Обработчик команды /start."""
    await message.answer("Привет! Я бот для проведения квизов. Чтобы начать квиз, введите команду /start_quiz и укажите ID квиза.")

@dp.message(Command('help'))
async def help(message: types.Message):
    """Обработчик команды /help."""
    await message.answer("/start - базовая информация\n/start_quiz - начало опроса\n/cancel - отмена прохождения квиза")

@dp.message(Command('start_quiz'))
async def start_quiz(message: types.Message, state: FSMContext):
    """Обработчик команды /start_quiz."""
    await message.answer("Введите ID квиза, который вы хотите начать:")
    await state.set_state(QuizStates.waiting_for_quiz_id)

@dp.message(QuizStates.waiting_for_quiz_id)
async def handle_quiz_id(message: types.Message, state: FSMContext):
    """Обработчик ввода ID квиза."""
    try:
        quiz_id = int(message.text)
    except ValueError:
        await message.answer("Неверный формат ID. Пожалуйста, введите число.")
        return
    
    quiz = get_quiz(quiz_id)
    if not quiz:
        await message.answer("Квиз с таким ID не найден.")
        await state.clear()
        return
    
    attempt = create_attempt(quiz_id, message.from_user.id)
    if not attempt:
        await message.answer("Ошибка при создании попытки. Попробуйте позже.")
        await state.clear()
        return
    
    question = get_next_question(attempt['id'])
    if not question:
        await message.answer("В этом квизе нет вопросов.")
        await state.clear()
        return
    
    await state.update_data(
        quiz_id=quiz_id,
        attempt_id=attempt['id']
    )
    await message.answer(f"Начало квиза: {quiz['title']}\n")
    await send_question(message.chat.id, question, state)
    await state.set_state(QuizStates.waiting_for_answer)

@dp.message(Command('cancel'))
async def cancel_quiz(message: types.Message, state: FSMContext):
    """Обработчик отмены квиза."""
    if current_state := await state.get_state():
        data = await state.get_data()
        if 'attempt_id' in data:
            complete_attempt(data['attempt_id'])
        await state.clear()
        await message.answer("Квиз отменен.")

@dp.message(QuizStates.waiting_for_answer)
async def handle_text_answer(message: types.Message, state: FSMContext):
    """Обработчик текстового ответа на вопрос."""
    data = await state.get_data()
    current_question = data.get('current_question')
    
    if current_question['question_type'] == 'option':
        await message.answer("Выберите вариант ответа.")
        return
    
    submit_answer(
        data['attempt_id'],
        current_question['id'],
        {'answer_text': message.text}
    )
    
    if next_question := get_next_question(data['attempt_id']):
        await send_question(message.chat.id, next_question, state)
    else:
        complete_attempt(data['attempt_id'])
        await message.answer("Квиз завершен!")
        await state.clear()

@dp.callback_query(QuizStates.waiting_for_answer, types.F.data.startswith("answer_"))
async def handle_option_answer(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора варианта ответа."""
    data = await state.get_data()
    current_question = data.get('current_question')
    option_id = int(callback.data.split("_")[1])
    
    submit_answer(
        data['attempt_id'],
        current_question['id'],
        {'answer_text': str(option_id)}
    )
    await callback.message.edit_reply_markup(reply_markup=None)

    if next_question := get_next_question(data['attempt_id']):
        await send_question(callback.message.chat.id, next_question, state)
    else:
        complete_attempt(data['attempt_id'])
        await callback.message.answer("Квиз завершен!")
        await state.clear()

async def main():
    """Запуск бота."""
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())