#!/usr/bin/env python
"""Script to check database contents for courses and user assignments."""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('APP_MODE', 'local')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'silicon._microservices.admin.settings')
django.setup()

from silicon.knowledge.models import Course, School
from silicon.user.models import CustomUser

print("=" * 60)
print("DATABASE CHECK - Courses and User Assignments")
print("=" * 60)

print("\nCOURSES:")
print("-" * 60)
courses = Course.objects.all()
if courses:
    for course in courses:
        print(f"  ID: {course.id}")
        print(f"  Name: {course.name}")
        print(f"  Code: {course.course_code}")
        print(f"  Active: {course.is_active}")
        print(f"  School: {course.school.name}")
        print(f"  Created by: {course.created_by.username if course.created_by else 'None'}")
        print()
else:
    print("  No courses found")

print("\nUSERS:")
print("-" * 60)
users = CustomUser.objects.all()
for user in users:
    print(f"  ID: {user.id}")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Is Staff: {user.is_staff}")
    print(f"  Is Superuser: {user.is_superuser}")
    
    # Get assigned courses
    all_courses = list(user.my_courses.all())
    active_courses = list(user.my_courses.filter(is_active=True).all())
    
    print(f"  Total Assigned Courses: {len(all_courses)}")
    print(f"  Active Assigned Courses: {len(active_courses)}")
    
    if all_courses:
        print("  Assigned Courses:")
        for course in all_courses:
            status = "[ACTIVE]" if course.is_active else "[INACTIVE]"
            print(f"    - {course.name} ({status})")
    else:
        print("  No courses assigned")
    print()

print("\nMANY-TO-MANY RELATIONSHIPS:")
print("-" * 60)
from django.db import connection
cursor = connection.cursor()

# Find the ManyToMany table name
# Django creates: <app>_<model>_<field>
table_name = "user_customuser_my_courses"
try:
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    if rows:
        print(f"  Table: {table_name}")
        print(f"  Total mappings: {len(rows)}")
        for row in rows:
            user_id = row[0]
            course_id = row[1]
            try:
                user = CustomUser.objects.get(id=user_id)
                course = Course.objects.get(id=course_id)
                print(f"    User '{user.username}' (ID:{user_id}) <-> Course '{course.name}' (ID:{course_id}) [Active: {course.is_active}]")
            except Exception as e:
                print(f"    User ID:{user_id} <-> Course ID:{course_id} [Error: {e}]")
    else:
        print(f"  Table {table_name} exists but is empty")
except Exception as e:
    print(f"  Error accessing table {table_name}: {e}")
    print("  Trying to find table name...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%course%'")
    tables = cursor.fetchall()
    print(f"  Found tables: {[t[0] for t in tables]}")

print("\n" + "=" * 60)
print("Check complete!")
print("=" * 60)

