import streamlit as st
import streamlit.components.v1 as components
from google import genai
from PIL import Image
import json
import smtplib
import re

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# CHANGE: Import the Gemini prompt from prompts.py.
# WHY: Keeps the AI instructions separate from the Streamlit app code.
from prompts import DEADLINE_PROMPT


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Deadline Tracker",
    page_icon="📚",
    layout="centered"
)


# ============================================================
# SESSION STATE
# ============================================================

# CHANGE: Store extracted deadlines in session state.
# WHY: Streamlit reruns the app whenever a button is clicked.
# This keeps the extracted data available for the email button.
if "deadline_data" not in st.session_state:
    st.session_state.deadline_data = None


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)


# ============================================================
# GMAIL CONFIGURATION
# ============================================================

GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"].strip()

GMAIL_APP_PASSWORD = (
    st.secrets["GMAIL_APP_PASSWORD"]
    .strip()
    .replace(" ", "")
)


# ============================================================
# EMAIL VALIDATION
# ============================================================

def is_valid_email(email):
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return re.fullmatch(pattern, email) is not None


# ============================================================
# APP TITLE
# ============================================================

st.title("📚 AI Deadline Tracker")

st.write(
    "Upload your syllabus, timetable, assignment sheet, "
    "or academic document to extract important deadlines."
)


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload your academic document",
    type=["jpg", "jpeg", "png"]
)


# ============================================================
# STUDENT EMAIL
# ============================================================

recipient_email = st.text_input(
    "Student Email",
    placeholder="student@example.com"
).strip()


# ============================================================
# DISPLAY UPLOADED IMAGE
# ============================================================

image = None

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(
        image,
        caption="Uploaded Academic Document",
        use_container_width=True
    )


# ============================================================
# EXTRACT DEADLINES BUTTON
# ============================================================

if st.button("Extract Deadlines"):

    # CHANGE: Clear previous extraction before analyzing a new file.
    # WHY: Prevents old deadlines from appearing when the new
    # document contains no deadlines.
    st.session_state.deadline_data = None

    if uploaded_file is None:

        st.warning(
            "Please upload an academic document."
        )

    elif not recipient_email:

        st.warning(
            "Please enter the student's email address."
        )

    elif not is_valid_email(recipient_email):

        st.warning(
            "Please enter a valid email address."
        )

    else:

        with st.spinner(
            "Analyzing your document with Gemini..."
        ):

            try:

                # ====================================================
                # GEMINI VISION EXTRACTION
                # ====================================================

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=[
                        DEADLINE_PROMPT,
                        image
                    ]
                )


                # ====================================================
                # CONVERT GEMINI RESPONSE TO PYTHON DICTIONARY
                # ====================================================

                deadline_data = json.loads(
                    response.text
                )


                # CHANGE: Save extraction result in session state.
                # WHY: The result must survive Streamlit reruns.
                st.session_state.deadline_data = deadline_data


                # ====================================================
                # SHOW SUCCESS ONLY IF DEADLINES EXIST
                # ====================================================

                # CHANGE: Success message is displayed only when
                # at least one deadline was actually extracted.
                # WHY: Avoids incorrectly saying "successfully extracted"
                # when the document contains no deadlines.
                if deadline_data.get("deadlines"):

                    st.success(
                        "✅ Deadlines extracted successfully!"
                    )


            except json.JSONDecodeError:

                st.error(
                    "❌ Gemini returned invalid JSON. Please try again."
                )

            except Exception as e:

                st.error(
                    f"❌ Something went wrong: {e}"
                )


# ============================================================
# GET SAVED DEADLINE DATA
# ============================================================

# CHANGE: Read the saved result from session state.
# WHY: Allows the deadline table and email functionality
# to continue working after Streamlit reruns.
deadline_data = st.session_state.deadline_data


# ============================================================
# DISPLAY DEADLINES
# ============================================================

if deadline_data is not None:

    deadlines = deadline_data.get(
        "deadlines",
        []
    )


    # ========================================================
    # DEADLINES FOUND
    # ========================================================

    if deadlines:

        st.subheader(
            "📅 Extracted Academic Deadlines"
        )


        # ====================================================
        # CREATE TABLE ROWS
        # ====================================================

        rows = ""

        for deadline in deadlines:

            date_time = deadline.get(
                "date_time",
                "Not specified"
            )

            task_event = deadline.get(
                "task_event",
                "Not specified"
            )

            subject_course = deadline.get(
                "subject_course",
                "Not specified"
            )

            deadline_type = deadline.get(
                "type",
                "Other"
            )

            additional_notes = deadline.get(
                "additional_notes",
                "Not specified"
            )


            rows += f"""
            <tr>
                <td>{date_time}</td>
                <td>{task_event}</td>
                <td>{subject_course}</td>
                <td>{deadline_type}</td>
                <td>{additional_notes}</td>
            </tr>
            """


        # ====================================================
        # HTML TABLE
        # ====================================================

        deadline_table = f"""
        <style>

            body {{
                margin: 0;
                padding: 0;
                background-color: #ffffff;
                font-family: Arial, sans-serif;
            }}

            .table-container {{
                width: 100%;
                overflow-x: auto;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background-color: #ffffff;
                color: #222222;
            }}

            th {{
                background-color: #1976D2;
                color: #ffffff;
                padding: 10px;
                border: 1px solid #dddddd;
                text-align: left;
                font-size: 14px;
            }}

            td {{
                background-color: #ffffff;
                color: #222222;
                padding: 10px;
                border: 1px solid #dddddd;
                font-size: 13px;
            }}

            tr:nth-child(even) td {{
                background-color: #f7f7f7;
            }}

        </style>

        <div class="table-container">

            <table>

                <thead>

                    <tr>
                        <th>Date / Time</th>
                        <th>Task / Event</th>
                        <th>Subject / Course</th>
                        <th>Type</th>
                        <th>Additional Notes</th>
                    </tr>

                </thead>

                <tbody>

                    {rows}

                </tbody>

            </table>

        </div>
        """


        # ====================================================
        # DISPLAY TABLE
        # ====================================================

        components.html(
            deadline_table,
            height=400,
            scrolling=True
        )


        # ====================================================
        # EMAIL SECTION
        # ====================================================

        st.markdown("---")

        st.subheader(
            "📧 Send Deadline Digest"
        )

        st.write(
            f"Recipient: **{recipient_email}**"
        )


        # ====================================================
        # SEND EMAIL BUTTON
        # ====================================================

        if st.button("📧 Send Deadline Digest"):

            if not recipient_email:

                st.warning(
                    "Please enter the student's email address."
                )

            elif not is_valid_email(recipient_email):

                st.warning(
                    "Please enter a valid email address."
                )

            else:

                try:

                    with st.spinner(
                        "Sending deadline digest..."
                    ):

                        # ============================================
                        # CREATE EMAIL
                        # ============================================

                        email = MIMEMultipart(
                            "alternative"
                        )

                        email["Subject"] = (
                            "Your Academic Deadline Digest"
                        )

                        email["From"] = GMAIL_ADDRESS

                        email["To"] = recipient_email


                        # ============================================
                        # CREATE EMAIL TABLE ROWS
                        # ============================================

                        email_rows = ""

                        for deadline in deadlines:

                            date_time = deadline.get(
                                "date_time",
                                "Not specified"
                            )

                            task_event = deadline.get(
                                "task_event",
                                "Not specified"
                            )

                            subject_course = deadline.get(
                                "subject_course",
                                "Not specified"
                            )

                            deadline_type = deadline.get(
                                "type",
                                "Other"
                            )

                            additional_notes = deadline.get(
                                "additional_notes",
                                "Not specified"
                            )


                            email_rows += f"""
                            <tr>

                                <td style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    {date_time}
                                </td>

                                <td style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    {task_event}
                                </td>

                                <td style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    {subject_course}
                                </td>

                                <td style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    {deadline_type}
                                </td>

                                <td style="
                                    padding:10px;
                                    border:1px solid #ddd;
                                ">
                                    {additional_notes}
                                </td>

                            </tr>
                            """


                        # ============================================
                        # PROFESSIONAL EMAIL HTML
                        # ============================================

                        html_body = f"""
                        <html>

                        <body style="
                            font-family:Arial,sans-serif;
                            background-color:#f5f7fa;
                            padding:20px;
                        ">

                            <div style="
                                max-width:800px;
                                margin:auto;
                                background-color:white;
                                padding:25px;
                                border-radius:10px;
                            ">

                                <h2 style="
                                    color:#1976D2;
                                ">
                                    📚 Academic Deadline Digest
                                </h2>

                                <p>
                                    Hello,
                                </p>

                                <p>
                                    Here are the important academic
                                    deadlines extracted from your
                                    uploaded document.
                                </p>

                                <table style="
                                    width:100%;
                                    border-collapse:collapse;
                                    background-color:white;
                                ">

                                    <thead>

                                        <tr style="
                                            background-color:#1976D2;
                                            color:white;
                                        ">

                                            <th style="
                                                padding:10px;
                                                border:1px solid #ddd;
                                            ">
                                                Date / Time
                                            </th>

                                            <th style="
                                                padding:10px;
                                                border:1px solid #ddd;
                                            ">
                                                Task / Event
                                            </th>

                                            <th style="
                                                padding:10px;
                                                border:1px solid #ddd;
                                            ">
                                                Subject / Course
                                            </th>

                                            <th style="
                                                padding:10px;
                                                border:1px solid #ddd;
                                            ">
                                                Type
                                            </th>

                                            <th style="
                                                padding:10px;
                                                border:1px solid #ddd;
                                            ">
                                                Additional Notes
                                            </th>

                                        </tr>

                                    </thead>

                                    <tbody>

                                        {email_rows}

                                    </tbody>

                                </table>

                                <p style="
                                    margin-top:20px;
                                    color:#555;
                                ">
                                    This deadline digest was generated
                                    using the AI Deadline Tracker.
                                </p>

                                <p>
                                    Stay organized and don't miss
                                    your important academic deadlines.
                                </p>

                            </div>

                        </body>

                        </html>
                        """


                        # ============================================
                        # ATTACH HTML EMAIL
                        # ============================================

                        email.attach(
                            MIMEText(
                                html_body,
                                "html"
                            )
                        )


                        # ============================================
                        # CONNECT TO GMAIL
                        # ============================================

                        with smtplib.SMTP_SSL(
                            "smtp.gmail.com",
                            465,
                            timeout=30
                        ) as server:

                            server.login(
                                GMAIL_ADDRESS,
                                GMAIL_APP_PASSWORD
                            )

                            server.send_message(
                                email
                            )


                    # ================================================
                    # EMAIL SUCCESS
                    # ================================================

                    st.success(
                        f"✅ Deadline digest sent successfully "
                        f"to {recipient_email}"
                    )

                    st.info(
                        "If you don't see it in the inbox, "
                        "please check the Spam/Junk folder."
                    )


                # ================================================
                # GMAIL AUTHENTICATION ERROR
                # ================================================

                except smtplib.SMTPAuthenticationError as e:

                    st.error(
                        "❌ Gmail authentication failed."
                    )

                    st.code(
                        str(e)
                    )


                # ================================================
                # SMTP ERROR
                # ================================================

                except smtplib.SMTPException as e:

                    st.error(
                        "❌ Gmail SMTP error."
                    )

                    st.code(
                        str(e)
                    )


                # ================================================
                # GENERAL EMAIL ERROR
                # ================================================

                except Exception as e:

                    st.error(
                        "❌ Email could not be sent."
                    )

                    st.code(
                        str(e)
                    )


    # ========================================================
    # NO DEADLINES FOUND
    # ========================================================

    else:

        # CHANGE: This is now the ONLY place where the
        # no-deadline message is displayed.
        # WHY: Prevents duplicate messages.
        st.info(
            "ℹ️ No academic deadlines were found "
            "in the provided image."
        )