# StudLabs API

Postman-коллекция для работы с API тестового задания StudLabs.  
[Ссылка на коллекцию Postman](https://postman.co/workspace/My-Workspace~9a4584af-7291-4211-80bc-5fbe5db99042/collection/31974596-2261464e-1272-45e4-9e38-8d9443f7ca80?action=share&creator=31974596)

---
## Start
```bash
git clone https://github.com/mm-shkurin/studlabs.forms
```
```bash
python -m venv venv
```
```bash
venv\Scripts\activate
```
```bash
pip install -r requirements.txt
```
```bash
python manage.py makemigrations
```
```bash
python manage.py migrate
```
```bash
python manage.py runserver #wsgi
```
```bash
uvicorn LabForm.asgi:application --reload #uvicorn
```
---
## Docker
```bash
docker-compose up --build
```
---
## Функциональность
- Регистрация и подтверждение email
- Авторизация через JWT (access/refresh токены)
- Управление профилем пользователя
- CRUD операции для форм
- Отправка ответов на формы (доступно без авторизации)
- Статистика ответов в процентах

---

## Эндпоинты API

### Auth
- **POST /user/register/**  
  Регистрация нового пользователя.  
  *Токен не требуется*

- **POST /user/auth/jwt/create/**  
  Получение access и refresh токенов.  
  *Токен не требуется*

- **POST /user/confirm-email/**  
  Подтверждение email.  
  *Токен не требуется*

---

### User
- **GET /user/me/**  
  Получение профиля пользователя и краткой статистики.  
  *Требуется токен*

---

### Form
- **POST /labform/**  
  Создание новой формы.  
  *Требуется токен*

- **GET /labform/list/**  
  Список всех форм пользователя.  
  *Требуется токен*

- **GET /labform/{form_id}/**  
  Просмотр конкретной формы.  
  *Требуется токен*

- **PATCH /labform/{form_id}/**  
  Обновление формы.  
  *Требуется токен*

- **DELETE /labform/{form_id}/**  
  Удаление формы.  
  *Требуется токен*

- **GET /labform/{form_id}/stats/**  
  Статистика ответов в процентах.  
  *Требуется токен*

---

### Respons
- **POST /labform/{form_id}/responses/**  
  Отправить ответ на форму.  
  *Токен не требуется*
---
### Swagger
- **GET /swagger/**  
  Открыть swagger.  
  *Токен не требуется*
