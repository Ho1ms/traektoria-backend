=== AUTH ===

- POST /auth/login - Авторизиция

json (body) = {
    "login": str,
    "password":str
}

resp => {
    'id': int,
    'first_name': str,
    'last_name': str,
    'father_name': str,
    'login': str,
    'role_id': int,
    'role': str,
    'token': str - Это сохранять в localStorage и в Authorization пихать
}

- GET /auth/me - Инфо о пользователе по токену
headers = Authorization: **token**

resp => {
    'id': int,
    'first_name': str,
    'last_name': str,
    'father_name': str,
    'login': str,
    'role_id': int,
    'role': str
}

- GET /auth/logout - Выйти
headers = Authorization: **token**

resp => {
    message: str,
    resultCode: int
}

- POST /auth/confirm-mail
body = {
    "mail": str
}

resp => {
    message: str,
    resultCode: int
}

- GET /auth/register - Создать аккаунт (Сначала надо подтвердить почту /auth/confirm-mail)
body = {
    'login': str,
    'password': str,
    'first_name': str,
    'last_name': str,
    'father_name': str,
    'birthday': str YYYY-MM-DD,
    'email': str,
    'code': str - 6 символов от 0 до 9
}

resp => {
    message: str,
    resultCode: int
}

=== PROFILE ===

- GET /profile/avatar/<user_id:int>

resp => Файлик (фото)

- POST /profile/set-avatar
headers = Authorization: **token**

form-data = {
    avatar: FILE
}

- POST /profile/update
headers = Authorization: **token**

body = {
    'first_name': str,
    'last_name': str,
    'father_name' str,
    'birthday': str YYYY-MM-DD
}

resp => {
    message: str,
    resultCode: int
}

- POST /profile/change_password
headers = Authorization: **token**

body = {
    password_1: str,
    password_2: str
}

resp => {
    message: str,
    resultCode: int
}

=== USERS ===
- GET /users

resp => [
    {
        "id": id,
        "first_name": str,
        "last_name": str,
        "father_name": str
    }
]

=== ADMIN === Работает если и юзера role_id = 1
- GET /admin/roles
headers = Authorization: **token**

resp => [
    {
        "id": 1,
        "name": "Администратор"
    },
    {
        "id": 2,
        "name": "Сотрудник поддержки"
    },
    {
        "id": 3,
        "name": "Студент"
    }
]

- GET /admin/users
headers = Authorization: **token**

resp => [
    {
        "id": int,
        "login": str,
        "first_name": str,
        "last_name": str,
        "father_name": str,
        "email": str,
        "role_id": int,
        "role": str,
        "birthday": str YYYY-MM-DD
    },
]

- POST /update_user/role
headers = Authorization: **token**

body = {
    'user_id': int, - тот которому мы меняем роль (можно взять из /admin/users)
    'role_id': int - ту на которую меняем (/admin/roles)
}




