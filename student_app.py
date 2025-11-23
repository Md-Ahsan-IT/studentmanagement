import streamlit as st
import pandas as pd
import json
import os
import re
from typing import List, Optional

# Student Class
class Student:
    def __init__(self, student_id, name, age, grade, email, performance):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade
        self.email = email
        self.performance = performance
    
    def to_dict(self):
        return {
            'student_id': self.student_id,
            'name': self.name,
            'age': self.age,
            'grade': self.grade,
            'email': self.email,
            'performance': self.performance
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            student_id=data['student_id'],
            name=data['name'],
            age=data['age'],
            grade=data['grade'],
            email=data['email'],
            performance=data['performance']
        )

# Student Manager Class
class StudentManager:
    def __init__(self, data_file='students.json'):
        self.data_file = data_file
        self.students = []
        self.load_students()
    
    def load_students(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as file:
                    data = json.load(file)
                    self.students = [Student.from_dict(student_data) for student_data in data]
            except:
                self.students = []
        else:
            self.students = []
    
    def save_students(self):
        with open(self.data_file, 'w') as file:
            json.dump([student.to_dict() for student in self.students], file, indent=2)
    
    def add_student(self, student):
        if any(s.student_id == student.student_id for s in self.students):
            return False
        self.students.append(student)
        self.save_students()
        return True
    
    def update_student(self, student_id, **kwargs):
        for student in self.students:
            if student.student_id == student_id:
                for key, value in kwargs.items():
                    if hasattr(student, key):
                        setattr(student, key, value)
                self.save_students()
                return True
        return False
    
    def delete_student(self, student_id):
        initial_count = len(self.students)
        self.students = [s for s in self.students if s.student_id != student_id]
        if len(self.students) < initial_count:
            self.save_students()
            return True
        return False
    
    def get_all_students(self):
        return self.students
    
    def search_students(self, query):
        query = query.lower()
        return [s for s in self.students if query in s.name.lower() or query in s.email.lower()]
    
    def filter_students(self, grade=None, min_age=None, max_age=None, performance=None):
        filtered = self.students
        if grade:
            filtered = [s for s in filtered if s.grade == grade]
        if min_age is not None:
            filtered = [s for s in filtered if s.age >= min_age]
        if max_age is not None:
            filtered = [s for s in filtered if s.age <= max_age]
        if performance:
            filtered = [s for s in filtered if s.performance.lower() == performance.lower()]
        return filtered
    
    def generate_student_id(self):
        if not self.students:
            return "STU001"
        numbers = []
        for student in self.students:
            try:
                num = int(student.student_id[3:])
                numbers.append(num)
            except:
                continue
        next_num = max(numbers) + 1 if numbers else 1
        return f"STU{next_num:03d}"

# Main Application
def main():
    st.set_page_config(
        page_title="Student Management System",
        page_icon="🎓",
        layout="wide"
    )
    
    st.title("🎓 Student Management System")
    st.markdown("---")
    
    manager = StudentManager()
    
    # Navigation
    st.sidebar.title("Navigation")
    app_mode = st.sidebar.selectbox(
        "Choose Operation",
        ["View All Students", "Add Student", "Update Student", "Delete Student", "Search & Filter"]
    )
    
    # Validation functions
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_grade(grade):
        pattern = r'^[1-9][0-9]?[A-Z]$'
        return re.match(pattern, grade.upper()) is not None
    
    if app_mode == "View All Students":
        st.header("👥 All Students")
        students = manager.get_all_students()
        if students:
            student_data = []
            for student in students:
                student_data.append({
                    'Student ID': student.student_id,
                    'Name': student.name,
                    'Age': student.age,
                    'Grade': student.grade,
                    'Email': student.email,
                    'Performance': student.performance
                })
            df = pd.DataFrame(student_data)
            st.dataframe(df, use_container_width=True)
            
            # Statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", len(students))
            with col2:
                excellent_count = len([s for s in students if s.performance == "Excellent"])
                st.metric("Excellent", excellent_count)
            with col3:
                avg_age = sum(s.age for s in students) / len(students) if students else 0
                st.metric("Average Age", f"{avg_age:.1f}")
            with col4:
                grades = len(set(s.grade for s in students))
                st.metric("Different Grades", grades)
        else:
            st.info("No students found in the system. Add some students to get started!")
    
    elif app_mode == "Add Student":
        st.header("➕ Add New Student")
        with st.form("add_student_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Full Name*", placeholder="Enter student's full name")
                age = st.number_input("Age*", min_value=5, max_value=100, value=18)
                email = st.text_input("Email*", placeholder="student@example.com")
            with col2:
                grade = st.text_input("Grade*", placeholder="e.g., 10A, 11B")
                performance = st.selectbox(
                    "Performance*",
                    ["Excellent", "Good", "Average", "Needs Improvement"]
                )
            submitted = st.form_submit_button("Add Student")
            if submitted:
                errors = []
                if not name.strip():
                    errors.append("Name is required")
                if age < 5 or age > 100:
                    errors.append("Age must be between 5 and 100")
                if not validate_email(email):
                    errors.append("Valid email is required")
                if not validate_grade(grade):
                    errors.append("Grade must be in format like '10A', '11B'")
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    student_id = manager.generate_student_id()
                    new_student = Student(student_id, name.strip(), int(age), grade.upper(), email.strip(), performance)
                    if manager.add_student(new_student):
                        st.success(f"✅ Student added successfully! Student ID: {student_id}")
                    else:
                        st.error("❌ Failed to add student.")
    
    elif app_mode == "Update Student":
        st.header("✏️ Update Student Information")
        students = manager.get_all_students()
        if not students:
            st.info("No students available to update.")
        else:
            student_options = {f"{s.student_id}: {s.name}": s for s in students}
            selected_option = st.selectbox("Select Student to Update", options=list(student_options.keys()))
            if selected_option:
                selected_student = student_options[selected_option]
                with st.form("update_student_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        new_name = st.text_input("Full Name*", value=selected_student.name)
                        new_age = st.number_input("Age*", min_value=5, max_value=100, value=selected_student.age)
                        new_email = st.text_input("Email*", value=selected_student.email)
                    with col2:
                        new_grade = st.text_input("Grade*", value=selected_student.grade)
                        new_performance = st.selectbox(
                            "Performance*",
                            ["Excellent", "Good", "Average", "Needs Improvement"],
                            index=["Excellent", "Good", "Average", "Needs Improvement"].index(selected_student.performance)
                        )
                    submitted = st.form_submit_button("Update Student")
                    if submitted:
                        errors = []
                        if not new_name.strip():
                            errors.append("Name is required")
                        if new_age < 5 or new_age > 100:
                            errors.append("Age must be between 5 and 100")
                        if not validate_email(new_email):
                            errors.append("Valid email is required")
                        if not validate_grade(new_grade):
                            errors.append("Grade must be in format like '10A', '11B'")
                        if errors:
                            for error in errors:
                                st.error(error)
                        else:
                            update_data = {
                                'name': new_name.strip(),
                                'age': int(new_age),
                                'grade': new_grade.upper(),
                                'email': new_email.strip(),
                                'performance': new_performance
                            }
                            if manager.update_student(selected_student.student_id, **update_data):
                                st.success("✅ Student updated successfully!")
                            else:
                                st.error("❌ Failed to update student.")
    
    elif app_mode == "Delete Student":
        st.header("🗑️ Delete Student")
        students = manager.get_all_students()
        if not students:
            st.info("No students available to delete.")
        else:
            student_options = {f"{s.student_id}: {s.name}": s.student_id for s in students}
            selected_option = st.selectbox("Select Student to Delete", options=list(student_options.keys()))
            if selected_option:
                st.warning(f"⚠️ You are about to delete: **{selected_option}**")
                if st.button("Confirm Delete", type="primary"):
                    student_id = student_options[selected_option]
                    if manager.delete_student(student_id):
                        st.success("✅ Student deleted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete student.")
    
    elif app_mode == "Search & Filter":
        st.header("🔍 Search & Filter Students")
        col1, col2 = st.columns([2, 1])
        with col1:
            search_query = st.text_input("Search by name or email", placeholder="Enter search term...")
        with col2:
            performance_filter = st.selectbox("Filter by Performance", ["All", "Excellent", "Good", "Average", "Needs Improvement"])
        
        col3, col4, col5 = st.columns(3)
        with col3:
            grade_filter = st.text_input("Filter by Grade", placeholder="e.g., 10A")
        with col4:
            min_age = st.number_input("Min Age", min_value=5, max_value=100, value=5)
        with col5:
            max_age = st.number_input("Max Age", min_value=5, max_value=100, value=100)
        
        filtered_students = manager.get_all_students()
        if search_query:
            filtered_students = manager.search_students(search_query)
        performance_val = performance_filter if performance_filter != "All" else None
        grade_val = grade_filter.upper() if grade_filter.strip() else None
        filtered_students = manager.filter_students(grade_val, min_age, max_age, performance_val)
        
        st.subheader("📊 Filtered Results")
        if filtered_students:
            student_data = []
            for student in filtered_students:
                student_data.append({
                    'Student ID': student.student_id,
                    'Name': student.name,
                    'Age': student.age,
                    'Grade': student.grade,
                    'Email': student.email,
                    'Performance': student.performance
                })
            df = pd.DataFrame(student_data)
            st.dataframe(df, use_container_width=True)
            st.metric("Filtered Students", len(filtered_students))
        else:
            st.info("No students found matching your criteria.")

if __name__ == "__main__":
    main()
