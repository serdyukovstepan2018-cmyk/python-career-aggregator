# vacancy_checker.py
import requests
from mysql_database import SessionLocal, Vacancy
from datetime import datetime, timedelta

def check_vacancy_active(link):
    """Проверяет, активна ли вакансия"""
    try:
        response = requests.get(link, timeout=10)
        if response.status_code == 404:
            return False
        if "hh.ru" in link and "вакансия не найдена" in response.text.lower():
            return False
        if "career.habr.com" in link and "вакансия не найдена" in response.text.lower():
            return False       
        return True
    except Exception as e:
        print(f"❌ Ошибка проверки вакансии {link}: {e}")
        return False

def cleanup_old_vacancies():
    """Помечает неактуальные вакансии"""
    session = SessionLocal()
    
    # Вакансии, которые давно не обновлялись (старше 7 дней)
    old_vacancies = session.query(Vacancy).filter(
        Vacancy.updated_at < datetime.now() - timedelta(days=7),
        Vacancy.is_active == True
    ).all()
    
    print(f"Проверяем {len(old_vacancies)} вакансий на актуальность...")
    
    deactivated_count = 0
    for vacancy in old_vacancies:
        if not check_vacancy_active(vacancy.link):
            vacancy.is_active = False
            vacancy.updated_at = datetime.now()
            print(f"❌ Деактивирована: {vacancy.title}")
            deactivated_count += 1
        else:
            # Обновляем время проверки
            vacancy.updated_at = datetime.now()
            print(f"✅ Активна: {vacancy.title}")
    
    session.commit()
    session.close()
    print(f"Деактивировано {deactivated_count} вакансий")

def check_specific_vacancy(vacancy_id):
    """Проверяет конкретную вакансию по ID"""
    session = SessionLocal()
    vacancy = session.query(Vacancy).filter(Vacancy.id == vacancy_id).first()
    
    if vacancy:
        is_active = check_vacancy_active(vacancy.link)
        vacancy.is_active = is_active
        vacancy.updated_at = datetime.now()
        session.commit()
        print(f"🔍 Вакансия {vacancy_id}: {'✅ Активна' if is_active else '❌ Неактивна'}")
    else:
        print(f"❌ Вакансия {vacancy_id} не найдена")
    
    session.close()

if __name__ == "__main__":
    print("Запуск проверки актуальности вакансий...")
    cleanup_old_vacancies()