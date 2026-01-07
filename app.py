import firebase_admin
from firebase_admin import credentials, db
import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import datetime
import pytz
import altair as alt



today_date = pytz.timezone('Asia/Kolkata').localize(
    datetime.datetime.now()
).strftime("%d %B, %Y")

firebase_secrets = dict(st.secrets["firebase"])

database_url = firebase_secrets.pop("database")

cred = credentials.Certificate(firebase_secrets)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": database_url
    })


ref = db.reference('/')


st.markdown("""
<style>
[data-testid="stContainer"] { padding: 2rem }
.stButton>button { border-radius: 8px }
</style>
""", unsafe_allow_html=True)


if "username" not in st.session_state:
    st.session_state.username = ""
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


st.markdown("# :rainbow[TaskEase]")


if not st.session_state.logged_in:
    selected = option_menu(
        None, ["Sign Up", "Log In"],
        icons=["person-plus", "box-arrow-in-right"],
        orientation="horizontal"
    )

    if selected == "Sign Up":
        st.subheader("Create Account")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Sign Up"):
            if ref.child("accounts").child(u).get() is None:
                ref.child("accounts").child(u).set({
                    "password": p,
                    "tasks": {},
                    "school": [],
                    "college": [],
                    "remember_me": "",
                    "theme": "Light"
                })
                st.session_state.username = u
                st.session_state.logged_in = True
                st.success("Account created")
                st.rerun()
            else:
                st.error("Username exists")

    if selected == "Log In":
        st.subheader("Log In")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Log In"):
            data = ref.child("accounts").child(u).get()
            if data and data["password"] == p:
                st.session_state.username = u
                st.session_state.logged_in = True
                st.success("Logged in")
                st.rerun()
            else:
                st.error("Invalid Credentials")


if st.session_state.logged_in:

    user_ref = ref.child("accounts").child(st.session_state.username)

    
    theme_colors = {
        "Light": {"bg": "#ffffff", "text": "#000000"},
        "Pink": {"bg": "#0f0f0f", "text": "#E01FC0"},
        "Blue": {"bg": "#0f0f0f", "text": "#73CCF0"},
        "Black": {"bg": "#0f0f0f", "text": "#ffffff"},
        "Yellow": {"bg": "#0f0f0f", "text": "#dad725e8"},
        "Purple": {"bg": "#0f0f0f", "text": "#a351e6ea"}
    }

    user_theme = user_ref.child("theme").get() or "Light"

    selected_theme = st.selectbox(
        "🎨 Theme",
        list(theme_colors.keys()),
        index=list(theme_colors.keys()).index(user_theme)
    )

    user_ref.child("theme").set(selected_theme)

    bg = theme_colors[selected_theme]["bg"]
    text = theme_colors[selected_theme]["text"]

    st.markdown(f"""
    <style>
    /* App background */
    .stApp {{
        background-color: {bg};
        color: {text};
    }}

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-baseweb="textarea"] > div {{
        background-color: {bg} !important;
        color: {text} !important;
        border: 1px solid {text}44 !important;
    }}
    /* Buttons & Download Buttons */
    .stButton>button, .stDownloadButton>button {{
        background-color: {bg} !important;
        color: {text} !important;
        border: 2px solid {text} !important;
        border-radius: 8px !important;
        transition: 0.3s;
    }}
    /* Tables */
    thead tr th {{
        background-color: {text} !important;
        color: {bg} !important;
    }}
    /* Force text inside expanders */
    .stExpander div {{
        color: {text} !important;
    }}
    /* Expanders & Popovers */
    .stExpander, details, div[data-testid="stPopoverBody"] {{
        background-color: {bg} !important;
        border: 1px solid {text}33 !important;
        border-radius: 8px;
    }}
    summary {{
        color: {text} !important;
        font-weight: bold;
    }}
    /* Metrics Styling */
    [data-testid="stMetric"] {{
        background-color: {bg} !important;
        border: 1px solid {text}33 !important;
        padding: 15px;
        border-radius: 10px;
    }}
    [data-testid="stMetricLabel"] > div, [data-testid="stMetricValue"] > div {{
        color: {text} !important;
    }}

    /* Dropdown text */
    div[data-baseweb="select"] span {{
        color: {text} !important;
    }}

    /* Buttons */
    button {{
        background-color: #1f2937 !important;
        color: white !important;
        border-radius: 8px !important;
    }}

    /* Expanders */
    details > summary {{
        background-color: #1f2937 !important;
        color: white !important;
        border-radius: 8px;
    }}

    /* Tables */
    thead tr th {{
        background-color: #1f2937 !important;
        color: white !important;
    }}

    tbody tr td {{
        background-color: {bg} !important;
        color: {text} !important;
    }}
    </style>
    """, unsafe_allow_html=True)


    option = option_menu(
        None,
        ["Home", "Add Task", "View Tasks", "About"],
        icons=["house", "plus-square", "list-task", "info-circle"],
        orientation="horizontal"
    )

    if option == "Home":
        st.subheader(f"👋 Welcome, {st.session_state.username}")
        st.write(today_date)
        tasks = user_ref.child("tasks").get() or {}
        total_tasks = len(tasks)
        completed, pending, overdue = 0,0,0
        
        today = datetime.date.today()

        for t in tasks.values():
            if t.get("completed"):
                completed +=1
            else:
                due = datetime.datetime.strptime(t["due_date"], "%Y-%m-%d").date()
                if due >= today:
                    pending +=1
                elif due < today:
                    overdue +=1

        completed_pct = (completed / total_tasks * 100) if total_tasks else 0
        on_time_pct = (pending / total_tasks * 100) if total_tasks else 0
        overdue_pct = (overdue/total_tasks * 100) if total tasks else 0
        with st.container(border =True):
            st.subheader("📊 Task Overview")
            st.metric("📋 Total Tasks", total_tasks,)
            with st.popover("View Breakdown"):
                c1,c2,c3 = st.columns(3)
                c1.metric("✅ Completed", completed, f"{completed_pct:.1f}%",border=True)
                c2.metric("⏳ Pending", pending, f"{on_time_pct:.1f}%", border = True)
                c3.metric("❌ Overdue", overdue, f"{overdue_pct:.1f}%", border = True)



        with st.expander("🔐 Account Settings"):
            new_pass = st.text_input("New Password", type="password")
            if st.button("Change Password"):
                user_ref.child("password").set(new_pass)
                st.success("Password updated")

            if st.button("❌ Delete Account"):
                user_ref.delete()
                st.session_state.clear()
                st.rerun()

        with st.expander("📝 Remember Me"):
            note = st.text_area(
                "Your note",
                value=user_ref.child("remember_me").get() or ""
            )
            if st.button("Save Note"):
                user_ref.child("remember_me").set(note)
                st.success("Saved")

        if st.button("Log Out"):
            st.session_state.clear()
            st.rerun()

    # -------- ADD TASK --------
    elif option == "Add Task":
        st.subheader("➕ Add Task")

        category = st.selectbox(
            "Category", ["College", "School", "Work", "Personal", "Others"]
        )

        subject = "-"
        if category in ["College", "School"]:
            sub_ref = user_ref.child(category.lower())
            subjects = sub_ref.get() or []

            subject = st.selectbox("Subject", subjects)

            with st.expander("📚 Manage Subjects"):
                new_sub = st.text_input("Add Subject")
                if st.button("Add Subject"):
                    if new_sub and new_sub not in subjects:
                        subjects.append(new_sub)
                        sub_ref.set(subjects)
                        st.rerun()

                if subjects:
                    del_sub = st.selectbox("Delete Subject", subjects)
                    if st.button("Delete Subject"):
                        subjects.remove(del_sub)
                        sub_ref.set(subjects)
                        st.rerun()

        with st.form("task_form"):
            title = st.text_input("Title")
            desc = st.text_area("Description")
            due = st.date_input("Due Date", min_value="today")
            submitted = st.form_submit_button("Add Task")

            if submitted:
                user_ref.child("tasks").push({
                    "title": title,
                    "description": desc,
                    "category": category,
                    "subject": subject,
                    "due_date": due.strftime("%Y-%m-%d"),
                    "completed": False
                })
                st.success("Task added")
                st.rerun()

    
    elif option == "View Tasks":
        st.write("📋 Tasks")

        tasks = user_ref.child("tasks").get()
        if not tasks:
            st.info("No tasks")
        else:
            today = datetime.date.today()
            rows = []

            for tid, t in tasks.items():
                due = datetime.datetime.strptime(t["due_date"], "%Y-%m-%d").date()
                done = t.get("completed", False)

                status = (
                    "✅ Completed" if done else
                    "❌ Overdue" if due < today else
                    "⏳ On Time"
                )

                rows.append([tid, t["title"], t["category"],
                             t.get("subject", "-"), t["due_date"], status])
            c1,col2 = st.columns([2,1])
            df = pd.DataFrame(
                rows,
                columns=["ID", "Title", "Category", "Subject", "Due Date", "Status"]
            )
            
            with c1:
                st.write("🔍 Search & Filter")
                search_text = st.text_input("Search by title or subject")
                filtered_df = df.copy()

                

                if search_text:
                    filtered_df = filtered_df[
                        filtered_df["Title"].str.contains(search_text, case=False, na=False) |
                        filtered_df["Subject"].str.contains(search_text, case=False, na=False)
    ]

            
            
                st.dataframe(filtered_df.drop(columns="ID"), use_container_width=True)
                task_id = st.selectbox(
                "Select Task",
                df["ID"],
                format_func=lambda x: df[df["ID"] == x]["Title"].values[0]
            )
                selected_task = tasks[task_id]

                with st.popover("🧾 Task Details"):
                    st.write(f"🆔 **Task ID:** `{task_id}`")
                    st.write(f"📌 **Title:** {selected_task['title']}")
                    st.write(f"🗂 **Category:** {selected_task['category']}")
                    st.write(f"📚 **Subject:** {selected_task.get('subject', '-')}")
                    st.write(f"📅 **Due Date:** {selected_task['due_date']}")
                    st.write(
                        f"📍 **Status:** {'Completed' if selected_task.get('completed') else 'Pending'}"
                    )
                    st.write(f"📝 **Description:** {selected_task['description']}")


                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Mark Complete"):
                        cur = tasks[task_id].get("completed", False)
                        user_ref.child("tasks").child(task_id).child("completed").set(not cur)
                        st.rerun()

                with c2:
                    if st.button("Delete Task"):
                        user_ref.child("tasks").child(task_id).delete()
                        st.rerun()

            

            analysis_df = filtered_df.copy()
            analysis_df["State"] = analysis_df["Status"].apply(
                lambda x: "Completed" if "Completed" in x else "On Time")

            analysis_df = analysis_df[
                analysis_df["Category"].isin(["School", "College", "Personal", "Work","Others"])
                        ]
            grouped = (
                analysis_df
                .groupby(["Category", "State"])
                .size()
                .reset_index(name="Count")
            )

            with col2:
                
                st.write("📚Task Analysis")
                chart = (
                alt.Chart(grouped)
                .mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                .encode(
                    x=alt.X("Category:N", title="Category"),
                    xOffset="State:N",
                    y=alt.Y("Count:Q", title="Number of Tasks"),
                    color=alt.Color(
                        "State:N",
                scale=alt.Scale(
                    domain=["Completed", "On Time"],
                    range=["#2ecc71", "#f1c40f"]
                ),
                legend=alt.Legend(title="Task Status")
            ),
            tooltip=["Category", "State", "Count"]
                    )
                    .properties(
                        width=420,
                        height=280
                    )
                )

                st.altair_chart(chart, use_container_width=False)

            


    if option == "About":
        with st.container(border = True, horizontal_alignment='distribute', vertical_alignment='distribute'):
            st.write("Yashasvi Peddintti")
            st.write("Aditi Pawar")
            st.write("Shryas Paranjape")
            st.write("Vaibhavi Patil")
            st.write("Vedika Patil")

            




