import streamlit as st
import pandas as pd
import re
from services.manager import StudentManager

class StudentManagementUI:
    def __init__(self):
        self.manager = StudentManager()
        self.setup_page()
    
    def setup_page(self):
        """Configure the Streamlit page"""
        st.set_page_config(
            page_title="Student Management System",
            page_icon="🎓",
            layout="wide"
        )
        
        st.title("🎓 Student Management System")
        st.markdown("---")
    
    def validate_email(self, email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_age(self, age):
        """Validate age (5-100)"""
        try:
            age_int = int(age)
            return 5 <= age_int <= 100
        except ValueError:
            return False
    
    def validate_grade(self, grade):
        """Validate grade format (e.g., 10A, 11B)"""
        pattern = r'^[1-9][0-9]?[A-Z]$'
        return re.match(pattern, grade.upper()) is not None
    
    def show_add_student_form(self):
        """Display form to add new student"""
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
                # Validation
                errors = []
                if not name.strip():
                    errors.append("Name is required")
                if not self.validate_age(age):
                    errors.append("Age must be between 5 and 100")
                if not self.validate_email(email):
                    errors.append("Valid email is required")
                if not self.validate_grade(grade):
                    errors.append("Grade must be in format like '10A', '11B'")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    # Generate student ID and add student
                    student_id = self.manager.generate_student_id()
                    from models.student import Student
                    new_student = Student(
                        student_id=student_id,
                        name=name.strip(),
                        age=int(age),
                        grade=grade.upper(),
                        email=email.strip(),
                        performance=performance
                    )
                    
                    if self.manager.add_student(new_student):
                        st.success(f"✅ Student added successfully! Student ID: {student_id}")
                    else:
                        st.error("❌ Failed to add student. Student ID might already exist.")
    
    def show_update_student_form(self):
        """Display form to update student information"""
        st.header("✏️ Update Student Information")
        
        # Student selection
        students = self.manager.get_all_students()
        if not students:
            st.info("No students available to update.")
            return
        
        student_options = {f"{s.student_id}: {s.name}": s for s in students}
        selected_option = st.selectbox(
            "Select Student to Update",
            options=list(student_options.keys()),
            key="update_select"
        )
        
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
                    # Validation
                    errors = []
                    if not new_name.strip():
                        errors.append("Name is required")
                    if not self.validate_age(new_age):
                        errors.append("Age must be between 5 and 100")
                    if not self.validate_email(new_email):
                        errors.append("Valid email is required")
                    if not self.validate_grade(new_grade):
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
                        
                        if self.manager.update_student(selected_student.student_id, **update_data):
                            st.success("✅ Student updated successfully!")
                        else:
                            st.error("❌ Failed to update student.")
    
    def show_delete_student_form(self):
        """Display form to delete student"""
        st.header("🗑️ Delete Student")
        
        students = self.manager.get_all_students()
        if not students:
            st.info("No students available to delete.")
            return
        
        student_options = {f"{s.student_id}: {s.name}": s.student_id for s in students}
        selected_option = st.selectbox(
            "Select Student to Delete",
            options=list(student_options.keys()),
            key="delete_select"
        )
        
        if selected_option:
            st.warning(f"⚠️ You are about to delete: **{selected_option}**")
            
            if st.button("Confirm Delete", type="primary"):
                student_id = student_options[selected_option]
                if self.manager.delete_student(student_id):
                    st.success("✅ Student deleted successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to delete student.")
    
    def show_search_filter_section(self):
        """Display search and filter functionality"""
        st.header("🔍 Search & Filter Students")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input("Search by name or email", placeholder="Enter search term...")
        
        with col2:
            performance_filter = st.selectbox(
                "Filter by Performance",
                ["All", "Excellent", "Good", "Average", "Needs Improvement"]
            )
        
        col3, col4, col5 = st.columns(3)
        with col3:
            grade_filter = st.text_input("Filter by Grade", placeholder="e.g., 10A")
        with col4:
            min_age = st.number_input("Min Age", min_value=5, max_value=100, value=5)
        with col5:
            max_age = st.number_input("Max Age", min_value=5, max_value=100, value=100)
        
        # Apply filters
        filtered_students = self.manager.get_all_students()
        
        if search_query:
            filtered_students = self.manager.search_students(search_query)
        
        # Apply additional filters
        performance_val = performance_filter if performance_filter != "All" else None
        grade_val = grade_filter.upper() if grade_filter.strip() else None
        
        filtered_students = self.manager.filter_students(
            grade=grade_val,
            min_age=min_age,
            max_age=max_age,
            performance=performance_val
        )
        
        return filtered_students
    
    def display_students_table(self, students):
        """Display students in a table format"""
        if not students:
            st.info("No students found matching your criteria.")
            return
        
        # Convert to DataFrame for better display
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
        
        # Display statistics
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
    
    def run(self):
        """Main application runner"""
        # Sidebar navigation
        st.sidebar.title("Navigation")
        app_mode = st.sidebar.selectbox(
            "Choose Operation",
            ["View All Students", "Add Student", "Update Student", "Delete Student", "Search & Filter"]
        )
        
        st.sidebar.markdown("---")
        st.sidebar.info(
            "**Student Management System**\n\n"
            "Manage student records with full CRUD operations, search, and filtering capabilities."
        )
        
        # Main content based on selection
        if app_mode == "View All Students":
            st.header("👥 All Students")
            students = self.manager.get_all_students()
            self.display_students_table(students)
            
        elif app_mode == "Add Student":
            self.show_add_student_form()
            
        elif app_mode == "Update Student":
            self.show_update_student_form()
            
        elif app_mode == "Delete Student":
            self.show_delete_student_form()
            
        elif app_mode == "Search & Filter":
            filtered_students = self.show_search_filter_section()
            st.subheader("📊 Filtered Results")
            self.display_students_table(filtered_students)

# Run the application
if __name__ == "__main__":
    ui = StudentManagementUI()
    ui.run()