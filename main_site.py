# main_site.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from mysql_database import SessionLocal, Vacancy
from collections import Counter

app = FastAPI(title="Python Вакансии")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Главная страница сайта"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/stats")
async def get_stats():
    """Статистика для сайта"""
    try:
        session = SessionLocal()
        # ФИЛЬТРУЕМ ТОЛЬКО АКТИВНЫЕ ВАКАНСИИ
        vacancies = session.query(Vacancy).filter(Vacancy.is_active == True).all()
        
        if not vacancies:
            return {
                "total_vacancies": 0,
                "with_salary": 0,
                "top_companies": [],
                "top_technologies": []
            }
        
        vacancies_with_salary = [v for v in vacancies if v.salary]
        company_counts = Counter(v.company for v in vacancies)
        top_companies = company_counts.most_common(5)
        
        # Анализ технологий
        technologies = {
            'Python': 0, 'Django': 0, 'Flask': 0, 'FastAPI': 0, 
            'PostgreSQL': 0, 'MySQL': 0, 'Docker': 0, 'Git': 0,
            'Linux': 0, 'REST': 0, 'SQL': 0, 'JavaScript': 0
        }
        
        for vacancy in vacancies:
            text = f"{vacancy.title} {vacancy.company}".lower()
            for tech in technologies:
                if tech.lower() in text:
                    technologies[tech] += 1
        
        popular_tech = {tech: count for tech, count in technologies.items() if count > 0}
        sorted_tech = sorted(popular_tech.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_vacancies": len(vacancies),
            "with_salary": len(vacancies_with_salary),
            "top_companies": [{"company": c, "count": n} for c, n in top_companies],
            "top_technologies": [{"tech": tech, "count": count} for tech, count in sorted_tech]
        }
    
    except Exception as e:
        return {"error": f"Database error: {e}"}
    
    finally:
        session.close()

@app.get("/search")
async def search_vacancies(q: str = ""):
    """Поиск вакансий для сайта"""
    try:
        session = SessionLocal()
        # ФИЛЬТРУЕМ ТОЛЬКО АКТИВНЫЕ ВАКАНСИИ
        query = session.query(Vacancy).filter(Vacancy.is_active == True)
        
        if q:
            results = query.filter(Vacancy.title.ilike(f"%{q}%")).limit(20).all()
        else:
            results = query.limit(10).all()
            
        vacancies_list = []
        for v in results:
            vacancies_list.append({
                "title": v.title,
                "company": v.company,
                "salary": v.salary,
                "link": v.link
            })
            
        return vacancies_list
    
    except Exception as e:
        return {"error": f"Database error: {e}"}
    
    finally:
        session.close()

@app.get("/vacancies")
async def get_vacancies():
    try:
        session = SessionLocal()
        # ФИЛЬТРУЕМ ТОЛЬКО АКТИВНЫЕ ВАКАНСИИ
        vacancies = session.query(Vacancy).filter(Vacancy.is_active == True).all()
        return vacancies
    
    except Exception as e:
        return {"error": f"Database error: {e}"}
    
    finally:
        session.close()

@app.get("/vacancies/search")
async def search_vacancies_api(keyword: str = None, company: str = None, limit: int = 50):
    try:
        session = SessionLocal()
        # ФИЛЬТРУЕМ ТОЛЬКО АКТИВНЫЕ ВАКАНСИИ
        query = session.query(Vacancy).filter(Vacancy.is_active == True)
        
        if keyword:
            query = query.filter(Vacancy.title.ilike(f"%{keyword}%"))
        if company:
            query = query.filter(Vacancy.company.ilike(f"%{company}%"))
            
        results = query.limit(limit).all()
        return results
    
    except Exception as e:
        return {"error": f"Database error: {e}"}
    
    finally:
        session.close()