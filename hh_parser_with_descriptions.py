# hh_parser_with_descriptions.py
import requests
import time
import random
import re
from mysql_database import SessionLocal, Vacancy
from datetime import datetime  

def parse_hh_vacancies():
    queries = [
        "Python разработчик",
        "Python developer", 
        "Django разработчик",
        "FastAPI разработчик",
        "Flask разработчик",
        "Backend Python",
        "Data Scientist Python",
        "ML engineer Python"
    ]
    
    print("=== ПАРСИМ HH.RU ===")
    
    total_added = 0
    total_updated = 0
    
    for query in queries:
        print(f"🔍 Ищем: {query}")
        
        try:
            session = SessionLocal()
            query_added = 0
            query_updated = 0
            
            params = {
                "text": query,  
                "area": 1,
                "per_page": 20,
                "page": 0
            }
            
            for page in range(0, 2):
                params["page"] = page
                
                response = requests.get("https://api.hh.ru/vacancies", params=params)
                data = response.json()
                
                if not data["items"]:
                    break
                
                page_added = 0
                page_updated = 0
                for item in data["items"]:
                    try:
                        # ПРОВЕРЯЕМ ДУБЛИКАТ
                        existing = session.query(Vacancy).filter(Vacancy.link == item["alternate_url"]).first()
                        if existing:
                            existing.title = item["name"]
                            existing.company = item["employer"]["name"]
                            existing.salary = parse_salary(item.get("salary"))
                            existing.is_active = True 
                            existing.updated_at = datetime.now()
                            session.commit()
                            print(f"Обновлена: {item['name'][:50]}...")
                            page_updated += 1
                            query_updated += 1
                            total_updated += 1
                        else:
                            # добавление новой вакансии
                            description = get_vacancy_description(item["url"])
                            vacancy = Vacancy(
                                title=item["name"],
                                company=item["employer"]["name"],
                                salary=parse_salary(item.get("salary")),
                                link=item["alternate_url"],
                                description=description,
                                is_active=True,  
                                updated_at=datetime.now()
                            )
                            session.add(vacancy)
                            session.commit()
                            print(f"✅ Добавлена: {item['name'][:50]}...")
                            page_added += 1
                            query_added += 1
                            total_added += 1
                            
                    except Exception as e:
                        print(f"❌ Ошибка в вакансии: {e}")
                        session.rollback()
                        continue
                    
                    time.sleep(0.3)
                
                print(f"   Страница {page+1}: +{page_added} новых, {page_updated} обновлено")
                
                if page_added == 0 and page_updated == 0:
                    break
                    
                time.sleep(1)
            
            session.close()
            print(f"📊 По запросу '{query}': +{query_added} новых, {query_updated} обновлено")
            
        except Exception as e:
            print(f"❌ Ошибка в запросе '{query}': {e}")
            continue
    
    print(f"=== ИТОГО: {total_added} НОВЫХ, {total_updated} ОБНОВЛЕНО ===")

def get_vacancy_description(vacancy_url):
    try:
        response = requests.get(vacancy_url)
        data = response.json()
        description = re.sub('<[^<]+?>', '', data["description"])
        return description[:1000]#огр, чтобы занимать меньше места в базе
    except Exception as e:
        return ""

def parse_salary(salary_data):
    if not salary_data:
        return None
    if salary_data["from"] and salary_data["to"]:
        return f"{salary_data['from']} - {salary_data['to']} {salary_data['currency']}"
    elif salary_data["from"]:
        return f"от {salary_data['from']} {salary_data['currency']}"
    elif salary_data["to"]:
        return f"до {salary_data['to']} {salary_data['currency']}"
    return None

if __name__ == "__main__":
    parse_hh_vacancies()