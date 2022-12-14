import os

import bson
from dotenv import load_dotenv
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL") or "mongodb://localhost:27017/myDatabase"

client = MongoClient(DATABASE_URL)
db = client.myDatabase


class Templates:
    """Templates Model"""

    def __init__(self):
        return

    def create(self, template_name="", subject="", body="", user_id=""):
        """Create a new template"""
        template = self.get_by_user_id_and_template_name(user_id, template_name)
        if template:
            return
        new_template = db.templates.insert_one(
            {"template_name": template_name, "body": body, "subject": subject, "user_id": user_id}
        )
        return self.get_by_id(new_template.inserted_id)

    def get_all(self):
        """Get all templates"""
        templates = db.templates.find()
        return [{**template, "_id": str(template["_id"])} for template in templates]

    def get_by_id(self, book_id):
        """Get a template by id"""
        template = db.templates.find_one({"_id": bson.ObjectId(book_id)})
        if not template:
            return
        template["_id"] = str(template["_id"])
        return template

    def get_by_user_id(self, user_id):
        """Get all templates created by a user"""
        templates = db.templates.find({"user_id": user_id})
        return [{**template, "_id": str(template["_id"])} for template in templates]

    def get_by_user_id_and_template_name(self, user_id, template_name):
        """Get a template given its template_name and author"""
        template = db.templates.find_one({"user_id": user_id, "template_name": template_name})
        if not template:
            return
        template["_id"] = str(template["_id"])
        return template

    def update(self, book_id, template_name="", body="", subject="", user_id=""):
        """Update a template"""
        data = {}
        if template_name:
            data["template_name"] = template_name
        if body:
            data["body"] = body
        if subject:
            data["subject"] = subject

        template = db.templates.update_one({"_id": bson.ObjectId(book_id)}, {"$set": data})
        template = self.get_by_id(book_id)
        return template

    def delete(self, book_id):
        """Delete a template"""
        template = db.templates.delete_one({"_id": bson.ObjectId(book_id)})
        return template

    def delete_by_user_id(self, user_id):
        """Delete all templates created by a user"""
        template = db.templates.delete_many({"user_id": bson.ObjectId(user_id)})
        return template


class User:
    """User Model"""

    def __init__(self):
        return

    def create(self, first_name="", last_name="", email="", password=""):
        """Create a new user"""
        user = self.get_by_email(email)
        if user:
            return
        new_user = db.users.insert_one(
            {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "password": self.encrypt_password(password),
                "active": True,
            }
        )
        return self.get_by_id(new_user.inserted_id)

    def get_all(self):
        """Get all users"""
        users = db.users.find({"active": True})
        return [{**user, "_id": str(user["_id"])} for user in users]

    def get_by_id(self, user_id):
        """Get a user by id"""
        user = db.users.find_one({"_id": bson.ObjectId(user_id), "active": True})
        if not user:
            return
        user["_id"] = str(user["_id"])
        user.pop("password")
        return user

    def get_by_email(self, email):
        """Get a user by email"""
        user = db.users.find_one({"email": email, "active": True})
        if not user:
            return
        user["_id"] = str(user["_id"])
        return user

    def update(self, user_id, first_name="", last_name=""):
        """Update a user"""
        data = {}
        if first_name:
            data["first_name"] = first_name
            data["last_name"] = last_name
        user = db.users.update_one({"_id": bson.ObjectId(user_id)}, {"$set": data})
        user = self.get_by_id(user_id)
        return user

    def delete(self, user_id):
        """Delete a user"""
        Templates().delete_by_user_id(user_id)
        user = db.users.delete_one({"_id": bson.ObjectId(user_id)})
        user = self.get_by_id(user_id)
        return user

    def disable_account(self, user_id):
        """Disable a user account"""
        user = db.users.update_one({"_id": bson.ObjectId(user_id)}, {"$set": {"active": False}})
        user = self.get_by_id(user_id)
        return user

    def encrypt_password(self, password):
        """Encrypt password"""
        return generate_password_hash(password)

    def login(self, email, password):
        """Login a user"""
        user = self.get_by_email(email)
        if not user or not check_password_hash(user["password"], password):
            return
        user.pop("password")
        return user
