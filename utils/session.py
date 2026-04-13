# Student ID: 24019989
# Student Name: Abdishakur Hasan
# Component: Component 2 - User Authentication, RBAC & Desktop UI Framework

class Session:
    _current_user = None

    @classmethod
    def login(cls, user):
        cls._current_user = user

    @classmethod
    def logout(cls):
        cls._current_user = None

    @classmethod
    def get_current_user(cls):
        return cls._current_user

    @classmethod
    def is_logged_in(cls):
        return cls._current_user is not None