## Authorization

- **POST** `/auth/login` **- Авторизиция**

**Body**
```
{
    "login": str,
    "password": str
}
```
**Response**
```
{
    'id': int,
    'first_name': str,
    'last_name': str,
    'father_name': str,
    'login': str,
    'role_id': int,
    'role': str,
    'token': str - Это сохранять в localStorage и в Authorization пихать
}
```
- **GET** `/auth/me` **- Инфо о пользователе по токену**

**Headers**
```
Authorization: **token**
```

**Response**
```
{
    'id': int,
    'first_name': str,
    'last_name': str,
    'father_name': str,
    'birthday': str YYYY-MM-DD,
    'login': str,
    'role_id': int,
    'role': str
}
```
- **GET** `/auth/logout` **- Выйти**

**Headers**
```
Authorization: **token**
```
**Response**
```
{
    message: str,
    resultCode: int
}
```
- **POST** `/auth/confirm-mail` **- Подтверждение почты**

**Body**
```
{
    "mail": str
}
```
**Response**
```
{
    message: str,
    resultCode: int
}
```

- **POST** `/auth/register` **- Создать аккаунт**

**(Сначала надо подтвердить почту `/auth/confirm-mail`)**

**Body**
```
{
    'login': str,
    'password': str,
    'first_name': str,
    'last_name': str,
    'father_name': str,
    'birthday': str YYYY-MM-DD,
    'email': str,
    'code': str - 6 символов от 0 до 9
}
```
**Response**
```
{
    'id': int,
    'first_name': str,
    'last_name': str,
    'father_name': str,
    'birthday': str YYYY-MM-DD,
    'login': str,
    'role_id': int,
    'role': str,
    'token':str
}
```

## Profile

- **GET** `/avatar/<user_id:int>` **- Получить аватар пользователя по ID**

**Response**
```
FILE (Render photo)
```
- **POST** `/profile/set-avatar` **- Обновить аватар**

**Headers**
```
Authorization: **token**
```
**Form-data**
```
{
    avatar: FILE
}
```
**Response**
```
{
    message: str,
    resultCode: int
}
```
- **POST** `/profile/update` **- Обновить данные профиля**

**Headers**
```
Authorization: **token**
```
**Body**
```
{
    'first_name': str,
    'last_name': str,
    'father_name' str,
    'birthday': str YYYY-MM-DD
}
```
**Response**
```
{
    message: str,
    resultCode: int
}
```
- **POST** `/profile/change_password` **- Изменить пароль**

**Headers**
```
Authorization: **token**
```
**Body**
```
{
    password_1: str,
    password_2: str
}
```
**Response**
```
{
    message: str,
    resultCode: int
}
```

- **GET** `/profile` **- Получить профиль**
**Headers**
```
Authorization: **token**
```
**Response**
```
{
    "user": {
        'id': int,
        'first_name': str,
        'last_name': str,
        'father_name': str,
        'birthday': str YYYY-MM-DD,
        'login': str,
        'role_id': int,
        'role': str
    },
    contacts: [
        {
            'id': int,
            'title': str,
            'description': str
        }
    ],
    'portfolio':[
        str
    ]
}
```

## Portfolio
- **POST** `/profile/portfolio/add` **- Добавить картинку в портфолио**

**Headers**
```
Authorization: **token**
```
**Form-data**
```
file: IMAGE
```
**Response**
```
{
    message: str,
    resultCode: int
}
```
- **POST** `/profile/portfolio/delete` **- Удалить картинку в портфолио**

**Headers**
```
Authorization: **token**
```
**Body**
```
{
    filename: str
}
```
**Response**
```
{
    message: str,
    resultCode: int
}
```
## Contacts
- **POST** `/profile/contacts/add` **- Добавить контакт**

**Headers**
```
Authorization: **token**
```
**Body**
```
{
    title: str,
    description: str
}
```
**Response**
```
{
    id: int,
    title: str,
    description: str
}
```
- **POST** `/profile/contacts/update` **- Обновить контакт**

**Headers**
```
Authorization: **token**
```
**Body**
```
{
    id: int,
    title: str,
    description: str
}
```
**Response**
```
{
    id: int,
    title: str,
    description: str
}
```
- **POST** `/profile/contacts/delete` **- Удалить контакт**

**Headers**
```
Authorization: **token**
```
**Body**
```
{
    id: int,
}
```
**Response**
```
{
    message: str,
    resultCode: int
}
```
## Users
- **GET** `/users` **- Список пользователей**

**Response**
```
[
    {
        "id": id,
        "first_name": str,
        "last_name": str,
        "father_name": str
    }
]
```
## ADMIN 
> Работает если и пользователя `role_id=1`
- **GET** `/admin/roles` **- Список ролей**

**Headers**
```
Authorization: **token**
```
**Response**
```
[
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
```
- **GET** `/admin/users` **- Список пользователей для администраторов**

**Headers**
```
Authorization: **token**
```
**Response**
```
[
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
```
- **POST** `/update_user/role` **- Обновить роль пользователю**

**Headers**
```
Authorization: **token**
```
**Body**
```
{
    'user_id': int, - тот которому мы меняем роль (можно взять из /admin/users)
    'role_id': int - ту на которую меняем (/admin/roles)
}
```




