# habr_parser.py
import requests
from bs4 import BeautifulSoup
import time
from mysql_database import SessionLocal, Vacancy
from datetime import datetime  # ← ДОБАВИЛИ ИМПОРТ

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def check_habr_access():
    """Проверяет доступность Habr Career"""
    try:
        response = requests.get("https://career.habr.com/vacancies", headers=headers, timeout=10)
        return response.status_code == 200
    except:
        return False

def parse_habr_vacancies():
    url = "https://career.habr.com/vacancies?q=python&type=all"
    
    print("=== ПАРСИМ HABR CAREER ===")
    
    # Проверяем доступность
    if not check_habr_access():
        print("❌Habr Career недоступен")
        return
    
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        vacancies = soup.find_all('div', class_='vacancy-card__info')
        
        session = SessionLocal()
        saved_count = 0
        updated_count = 0
        skipped_count = 0
        
        for vacancy in vacancies:
            try:
                title_elem = vacancy.find('a', class_='vacancy-card__title-link')
                title = title_elem.text.strip() if title_elem else "Не указано"
                
                company_elem = vacancy.find('div', class_='vacancy-card__company')
                company = company_elem.text.strip() if company_elem else "Не указано"
                
                salary_elem = vacancy.find('div', class_='basic-salary')
                salary = salary_elem.text.strip() if salary_elem else "Не указана"
                
                if title_elem and title_elem.has_attr('href'):
                    link = "https://career.habr.com" + title_elem['href']
                else:
                    link = "Нет ссылки"
                
                # ПРОВЕРЯЕМ ДУБЛИКАТЫ
                existing = session.query(Vacancy).filter(Vacancy.link == link).first()
                if existing:
                    existing.title = title
                    existing.company = company
                    existing.salary = salary
                    existing.is_active = True
                    existing.updated_at = datetime.now()
                    print(f"🔄 Обновлена: {title}")
                    updated_count += 1
                else:
                    # добавляем новую вакансию
                    new_vacancy = Vacancy(
                        title=title,
                        company=company,
                        salary=salary,
                        link=link,
                        description="",
                        is_active=True,  
                        updated_at=datetime.now()
                    )
                    session.add(new_vacancy)
                    print(f"✅ Добавлена: {title}")
                    saved_count += 1
                
                time.sleep(0.2)
                
            except Exception as e:
                print(f"❌ Ошибка в вакансии: {e}")
                continue
        
        session.commit()
        session.close()
        print(f"=== ДОБАВЛЕНО: {saved_count}, ОБНОВЛЕНО: {updated_count}, ПРОПУЩЕНО: {skipped_count} ===")
        
    except Exception as e:
        print(f"❌ Общая ошибка: {e}")

if __name__ == "__main__":
    parse_habr_vacancies()