import requests
import psycopg2


def get_employers(employers_names: list):
    """
    Функция для получения id компаний
    :param employers_names:
    :return: list{dict}
    """
    employers = []
    for emp_name in employers_names:
        params = {
            "text": emp_name,
            "only_with_vacancies": True,
            "per_page": 100,
        }
        response = requests.get("https://api.hh.ru/employers", params=params).json()
        for item in response["items"]:
            if emp_name == item["name"]:
                emp_dict = {"id": item["id"], "name": item["name"]}
                employers.append(emp_dict)
                break
    return employers


def get_employer_vacancies(employer_id):
    """
    Функция для получения вакансий компании
    :param employer_id:
    :return: dict
    """
    params = {
        "employer_id": employer_id,
        "area": 113,
        "per_page": 100,
    }
    response = requests.get("https://api.hh.ru/vacancies", params=params).json()
    return response


def create_database(params, db_name):
    """Создает новую базу данных."""
    conn = psycopg2.connect(dbname='postgres', **params)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE {db_name}")
    cur.execute(f"CREATE DATABASE {db_name}")
    conn.close()


def create_table_employer(params, employers):
    """ Создание таблиц в БД"""
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            for i in range(0, len(employers)):
                cur.execute(f"""
                CREATE TABLE IF NOT EXISTS employer{i + 1}(
                id serial PRIMARY KEY,
                id_employer int,
                name_employer varchar(255),
                title_vacancy varchar(255),
                city varchar(255),
                salary int,
                url_vacancy varchar(500),
                requirements text,
                responsibility text
                );
                """)


def insert_table_data(params, employer_vacancies: list[dict], table_name) -> None:
    """Добавляет данные из HH в таблицы employer1, 2 и тд """
    with psycopg2.connect(**params) as conn:
        with conn.cursor() as cur:
            for emp_vac in employer_vacancies:
                try:
                    id_employer = emp_vac['employer']['id']
                    name_employer = emp_vac['employer']['name']
                    title_vacancy = emp_vac['name']
                    city = emp_vac['area']['name']
                    salary = emp_vac['salary'].get('from')
                    url_vacancy = emp_vac['alternate_url']
                    if emp_vac['snippet']['requirement'] is None:
                        requirements = "Описание не указано"
                    else:
                        requirements = emp_vac['snippet']['requirement']
                    if emp_vac['snippet']['responsibility'] is None:
                        responsibility = "Описание не указано"
                    else:
                        responsibility = emp_vac['snippet']['responsibility']
                except AttributeError:
                    id_employer = emp_vac['employer']['id']
                    name_employer = emp_vac['employer']['name']
                    title_vacancy = emp_vac['name']
                    city = emp_vac['area']['name']
                    salary = None
                    url_vacancy = emp_vac['alternate_url']
                    if emp_vac['snippet']['requirement'] is None:
                        requirements = "Описание не указано"
                    else:
                        requirements = emp_vac['snippet']['requirement']
                    if emp_vac['snippet']['responsibility'] is None:
                        responsibility = "Описание не указано"
                    else:
                        responsibility = emp_vac['snippet']['responsibility']
                cur.execute(f"""
                INSERT INTO  {table_name}(id_employer, name_employer, title_vacancy, city, salary, url_vacancy, requirements, responsibility)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (id_employer, name_employer, title_vacancy, city, salary, url_vacancy, requirements, responsibility))
