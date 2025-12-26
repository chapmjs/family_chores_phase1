"""
Family Chores App - Phase 1
Streamlit application with MySQL backend
"""

import streamlit as st
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import datetime, date, timedelta
import os
from PIL import Image
import io

# Page configuration
st.set_page_config(
    page_title="Family Chores Tracker",
    page_icon="🏠",
    layout="wide"
)

# Database connection configuration
# Update these with your actual database credentials
DB_CONFIG = {
    'host': 'localhost',  # or your MySQL server host
    'database': 'family_chores',
    'user': 'your_username',  # Update this
    'password': 'your_password'  # Update this
}

# You can also use environment variables for security:
# DB_CONFIG = {
#     'host': os.getenv('DB_HOST', 'localhost'),
#     'database': os.getenv('DB_NAME', 'family_chores'),
#     'user': os.getenv('DB_USER'),
#     'password': os.getenv('DB_PASSWORD')
# }

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL database: {e}")
        return None

def get_all_people():
    """Get all family members"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM people ORDER BY name")
            people = cursor.fetchall()
            return people
        finally:
            conn.close()
    return []

def get_all_chores():
    """Get all chores"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM chores ORDER BY room, task")
            chores = cursor.fetchall()
            return chores
        finally:
            conn.close()
    return []

def get_assignments_for_date(target_date):
    """Get all assignments for a specific date with completion status"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 
                    a.id as assignment_id,
                    c.id as chore_id,
                    c.room,
                    c.task,
                    c.estimated_time,
                    p.name as assigned_to,
                    p.id as person_id,
                    CASE WHEN comp.id IS NOT NULL THEN 1 ELSE 0 END as is_completed,
                    comp.completed_datetime,
                    comp.actual_minutes,
                    comp.photo_filename
                FROM assignments a
                JOIN chores c ON a.chore_id = c.id
                JOIN people p ON a.person_id = p.id
                LEFT JOIN completions comp ON a.id = comp.assignment_id
                WHERE a.assigned_date = %s
                ORDER BY c.room, c.task
            """
            cursor.execute(query, (target_date,))
            assignments = cursor.fetchall()
            return assignments
        finally:
            conn.close()
    return []

def assign_chore(chore_id, person_id, assigned_date):
    """Assign a chore to a person for a specific date"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Check if assignment already exists
            cursor.execute(
                "SELECT id FROM assignments WHERE chore_id = %s AND assigned_date = %s",
                (chore_id, assigned_date)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing assignment
                cursor.execute(
                    "UPDATE assignments SET person_id = %s WHERE chore_id = %s AND assigned_date = %s",
                    (person_id, chore_id, assigned_date)
                )
            else:
                # Insert new assignment
                cursor.execute(
                    "INSERT INTO assignments (chore_id, person_id, assigned_date) VALUES (%s, %s, %s)",
                    (chore_id, person_id, assigned_date)
                )
            conn.commit()
            return True
        except Error as e:
            st.error(f"Error assigning chore: {e}")
            return False
        finally:
            conn.close()
    return False

def copy_previous_day_assignments(from_date, to_date):
    """Copy all assignments from one day to another"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Delete any existing assignments for the target date
            cursor.execute("DELETE FROM assignments WHERE assigned_date = %s", (to_date,))
            
            # Copy assignments from previous date
            query = """
                INSERT INTO assignments (chore_id, person_id, assigned_date)
                SELECT chore_id, person_id, %s
                FROM assignments
                WHERE assigned_date = %s
            """
            cursor.execute(query, (to_date, from_date))
            conn.commit()
            return cursor.rowcount
        except Error as e:
            st.error(f"Error copying assignments: {e}")
            return 0
        finally:
            conn.close()
    return 0

def mark_chore_complete(assignment_id, actual_minutes, photo_data=None, photo_filename=None):
    """Mark a chore as complete"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            
            # Save photo if provided
            saved_filename = None
            if photo_data and photo_filename:
                # Create uploads directory if it doesn't exist
                os.makedirs("chore_photos", exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                saved_filename = f"{timestamp}_{photo_filename}"
                filepath = os.path.join("chore_photos", saved_filename)
                
                with open(filepath, "wb") as f:
                    f.write(photo_data)
            
            # Insert completion record
            cursor.execute(
                """INSERT INTO completions (assignment_id, actual_minutes, photo_filename)
                   VALUES (%s, %s, %s)""",
                (assignment_id, actual_minutes, saved_filename)
            )
            conn.commit()
            return True
        except Error as e:
            st.error(f"Error marking chore complete: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_assignment(assignment_id):
    """Delete a chore assignment"""
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM assignments WHERE id = %s", (assignment_id,))
            conn.commit()
            return True
        except Error as e:
            st.error(f"Error deleting assignment: {e}")
            return False
        finally:
            conn.close()
    return False

# Main App
def main():
    st.title("🏠 Family Chores Tracker - Phase 1")
    
    # Sidebar navigation
    page = st.sidebar.radio("Navigation", 
                           ["📋 Assign Chores", 
                            "✅ Complete Chores",
                            "📊 View Assignments",
                            "⚙️ Manage Chores"])
    
    if page == "📋 Assign Chores":
        assign_chores_page()
    elif page == "✅ Complete Chores":
        complete_chores_page()
    elif page == "📊 View Assignments":
        view_assignments_page()
    elif page == "⚙️ Manage Chores":
        manage_chores_page()

def assign_chores_page():
    """Page for assigning chores to family members"""
    st.header("📋 Assign Chores")
    
    # Date selector
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        selected_date = st.date_input("Select Date", value=date.today())
    
    with col2:
        if st.button("Copy from Previous Day"):
            previous_date = selected_date - timedelta(days=1)
            count = copy_previous_day_assignments(previous_date, selected_date)
            if count > 0:
                st.success(f"Copied {count} assignments from {previous_date}")
                st.rerun()
            else:
                st.warning(f"No assignments found for {previous_date}")
    
    with col3:
        if st.button("Clear All Today's Assignments"):
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM assignments WHERE assigned_date = %s", (selected_date,))
                    conn.commit()
                    st.success("All assignments cleared!")
                    st.rerun()
                finally:
                    conn.close()
    
    # Get all chores and people
    chores = get_all_chores()
    people = get_all_people()
    
    if not chores or not people:
        st.warning("Please ensure chores and family members are loaded in the database.")
        return
    
    # Get existing assignments for the date
    existing_assignments = get_assignments_for_date(selected_date)
    assignment_dict = {a['chore_id']: a['person_id'] for a in existing_assignments}
    
    st.subheader(f"Assign Chores for {selected_date}")
    
    # Group chores by room
    chores_by_room = {}
    for chore in chores:
        room = chore['room']
        if room not in chores_by_room:
            chores_by_room[room] = []
        chores_by_room[room].append(chore)
    
    # Create assignment interface
    people_names = [p['name'] for p in people]
    people_dict = {p['name']: p['id'] for p in people}
    
    changes_made = False
    
    for room, room_chores in sorted(chores_by_room.items()):
        with st.expander(f"🏠 {room} ({len(room_chores)} tasks)", expanded=True):
            for chore in room_chores:
                col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
                
                with col1:
                    st.write(f"**{chore['task']}**")
                
                with col2:
                    current_person = None
                    if chore['id'] in assignment_dict:
                        current_person_id = assignment_dict[chore['id']]
                        for p in people:
                            if p['id'] == current_person_id:
                                current_person = p['name']
                                break
                    
                    assigned_to = st.selectbox(
                        "Assign to",
                        ["Unassigned"] + people_names,
                        index=people_names.index(current_person) + 1 if current_person else 0,
                        key=f"assign_{chore['id']}_{selected_date}"
                    )
                
                with col3:
                    st.write(f"{chore['estimated_time']} min")
                
                with col4:
                    if assigned_to != "Unassigned":
                        if st.button("Save", key=f"save_{chore['id']}_{selected_date}"):
                            person_id = people_dict[assigned_to]
                            if assign_chore(chore['id'], person_id, selected_date):
                                st.success("✓")
                                changes_made = True
    
    if changes_made:
        st.rerun()

def complete_chores_page():
    """Page for marking chores as complete"""
    st.header("✅ Complete Chores")
    
    # Date selector
    selected_date = st.date_input("Select Date", value=date.today())
    
    # Get assignments for the date
    assignments = get_assignments_for_date(selected_date)
    
    if not assignments:
        st.info(f"No chores assigned for {selected_date}")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        filter_person = st.selectbox("Filter by Person", 
                                     ["All"] + sorted(list(set([a['assigned_to'] for a in assignments]))))
    with col2:
        show_completed = st.checkbox("Show Completed", value=True)
    
    # Filter assignments
    filtered_assignments = assignments
    if filter_person != "All":
        filtered_assignments = [a for a in filtered_assignments if a['assigned_to'] == filter_person]
    if not show_completed:
        filtered_assignments = [a for a in filtered_assignments if not a['is_completed']]
    
    # Display assignments
    st.subheader(f"Chores for {selected_date}")
    
    incomplete_count = sum(1 for a in assignments if not a['is_completed'])
    complete_count = len(assignments) - incomplete_count
    st.write(f"**Progress:** {complete_count}/{len(assignments)} completed")
    
    # Group by room
    assignments_by_room = {}
    for assignment in filtered_assignments:
        room = assignment['room']
        if room not in assignments_by_room:
            assignments_by_room[room] = []
        assignments_by_room[room].append(assignment)
    
    for room, room_assignments in sorted(assignments_by_room.items()):
        with st.expander(f"🏠 {room}", expanded=True):
            for assignment in room_assignments:
                if assignment['is_completed']:
                    st.success(f"✅ **{assignment['task']}** - {assignment['assigned_to']} - " +
                             f"Completed in {assignment['actual_minutes']} min")
                    if assignment['photo_filename']:
                        photo_path = os.path.join("chore_photos", assignment['photo_filename'])
                        if os.path.exists(photo_path):
                            st.image(photo_path, width=200)
                else:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{assignment['task']}** - Assigned to: {assignment['assigned_to']} " +
                               f"(est. {assignment['estimated_time']} min)")
                    
                    # Completion form
                    with st.form(f"complete_{assignment['assignment_id']}"):
                        col_a, col_b, col_c = st.columns([2, 2, 1])
                        
                        with col_a:
                            actual_minutes = st.number_input(
                                "Actual minutes",
                                min_value=1,
                                value=assignment['estimated_time'],
                                key=f"min_{assignment['assignment_id']}"
                            )
                        
                        with col_b:
                            photo = st.file_uploader(
                                "Upload photo (optional)",
                                type=['png', 'jpg', 'jpeg'],
                                key=f"photo_{assignment['assignment_id']}"
                            )
                        
                        with col_c:
                            submitted = st.form_submit_button("✓ Done")
                        
                        if submitted:
                            photo_data = None
                            photo_filename = None
                            if photo:
                                photo_data = photo.read()
                                photo_filename = photo.name
                            
                            if mark_chore_complete(assignment['assignment_id'], 
                                                  actual_minutes, 
                                                  photo_data, 
                                                  photo_filename):
                                st.success("Chore marked as complete!")
                                st.rerun()

def view_assignments_page():
    """Page for viewing assignments summary"""
    st.header("📊 View Assignments")
    
    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", value=date.today())
    
    # Get assignments for date range
    conn = get_db_connection()
    if not conn:
        st.error("Could not connect to database")
        return
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                a.assigned_date,
                c.room,
                c.task,
                p.name as assigned_to,
                c.estimated_time,
                CASE WHEN comp.id IS NOT NULL THEN 'Complete' ELSE 'Incomplete' END as status,
                comp.actual_minutes
            FROM assignments a
            JOIN chores c ON a.chore_id = c.id
            JOIN people p ON a.person_id = p.id
            LEFT JOIN completions comp ON a.id = comp.assignment_id
            WHERE a.assigned_date BETWEEN %s AND %s
            ORDER BY a.assigned_date DESC, c.room, c.task
        """
        cursor.execute(query, (start_date, end_date))
        results = cursor.fetchall()
        
        if results:
            df = pd.DataFrame(results)
            
            # Summary statistics
            st.subheader("Summary")
            col1, col2, col3 = st.columns(3)
            
            total_tasks = len(df)
            completed_tasks = len(df[df['status'] == 'Complete'])
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            col1.metric("Total Tasks", total_tasks)
            col2.metric("Completed", completed_tasks)
            col3.metric("Completion Rate", f"{completion_rate:.1f}%")
            
            # Detailed table
            st.subheader("Detailed View")
            st.dataframe(df, use_container_width=True)
            
            # Download option
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"chore_assignments_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )
        else:
            st.info(f"No assignments found between {start_date} and {end_date}")
    
    finally:
        conn.close()

def manage_chores_page():
    """Admin page for managing the chore master list"""
    st.header("⚙️ Manage Chores")
    
    tab1, tab2, tab3 = st.tabs(["View All Chores", "Add New Chore", "Manage People"])
    
    with tab1:
        st.subheader("All Chores")
        chores = get_all_chores()
        if chores:
            df = pd.DataFrame(chores)
            st.dataframe(df[['room', 'task', 'frequency', 'estimated_time']], use_container_width=True)
        else:
            st.info("No chores in database")
    
    with tab2:
        st.subheader("Add New Chore")
        with st.form("add_chore"):
            room = st.text_input("Room")
            task = st.text_input("Task")
            frequency = st.selectbox("Frequency", 
                                    ["Daily", "Weekly", "Monthly", "Semi-annually", "Annual", "Summer-weekly"])
            estimated_time = st.number_input("Estimated Time (minutes)", min_value=1, value=10)
            
            if st.form_submit_button("Add Chore"):
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO chores (room, task, frequency, estimated_time) VALUES (%s, %s, %s, %s)",
                            (room, task, frequency, estimated_time)
                        )
                        conn.commit()
                        st.success("Chore added successfully!")
                    except Error as e:
                        st.error(f"Error adding chore: {e}")
                    finally:
                        conn.close()
    
    with tab3:
        st.subheader("Family Members")
        people = get_all_people()
        if people:
            for person in people:
                st.write(f"• {person['name']}")
        
        st.subheader("Add New Family Member")
        with st.form("add_person"):
            name = st.text_input("Name")
            if st.form_submit_button("Add Person"):
                conn = get_db_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO people (name) VALUES (%s)", (name,))
                        conn.commit()
                        st.success(f"{name} added successfully!")
                    except Error as e:
                        st.error(f"Error adding person: {e}")
                    finally:
                        conn.close()

if __name__ == "__main__":
    main()
