# auto_parser.py
import schedule
import time
from hh_parser_with_descriptions import parse_hh_vacancies
import atexit
import os
from datetime import datetime 

PID_FILE = "parser.pid"

def check_already_running():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            old_pid = f.read().strip()
        try:
            os.kill(int(old_pid), 0)
            print("❌ Парсер уже запущен!")
            exit(1)
        except:
            os.remove(PID_FILE)
    
    with open(PID_FILE, 'w') as f:
        f.write(str(os.getpid()))

def cleanup():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def daily_parsing():
    """Ежедневный парсинг HH.ru"""
    print(f"\n{time.strftime('%Y-%m-%d %H:%M:%S')} - ЗАПУСК ПАРСИНГА HH.RU")
    
    try:
        print("🔍 Парсим HH.ru...")
        parse_hh_vacancies()
        print("✅ Парсинг завершен!")
        
    except Exception as e:
        print(f"❌ Ошибка парсинга: {e}")

def main():
    """Основная функция с расписанием"""
    check_already_running()
    atexit.register(cleanup)
    
    print("АВТОПАРСЕР HH.RU ЗАПУЩЕН")
    print("Расписание: каждый день в 09:00")
    
    # Настраиваем расписание
    schedule.every().day.at("09:00").do(daily_parsing)
    
    # ТЕСТОВЫЙ ЗАПУСК ТОЛЬКО ЕСЛИ СЕГОДНЯ ЕЩЕ НЕ ПАРСИЛИ
    current_hour = datetime.now().hour
    if current_hour >= 9:  
        print("Запускаем парсинг...")
        daily_parsing()
    else:
        print("Ждем 09:00 для первого парсинга...")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("🛑 Остановка парсера...")

if __name__ == "__main__":
    main()
