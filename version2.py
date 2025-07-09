import streamlit as st
import pandas as pd
from io import BytesIO

st.title("🔍 Employee–Project Matching App")

# Upload files
employee_file = st.file_uploader("📁 Upload Employee CSV", type=["csv"])
project_file = st.file_uploader("📁 Upload Project Excel", type=["xlsx"])

if employee_file and project_file:
    try:
        # Load files
        employee_df = pd.read_csv(employee_file, encoding="latin1")
        project_df = pd.read_excel(project_file)

        # Fill missing values
        employee_df.fillna("", inplace=True)
        project_df.fillna("", inplace=True)

        # Create employee profile for keyword matching
        employee_df["profile"] = (
            employee_df["Tools"].astype(str) + " " +
            employee_df["Experience"].astype(str) + " " +
            employee_df["Languages"].astype(str)
        )

        # Combine project requirements
        project_df["requirements"] = (
            project_df["Tools (e.g. Power BI, Jira)"].astype(str) + " " +
            project_df["Skills Required (e.g. Risk Management, Data Analysis, Data Visualization )"].astype(str) + " " +
            project_df["Langauages proficiency required (e.g. Python, Java)"].astype(str)
        )

        # Match percentage function
        def calculate_match_percent(profile, requirement):
            profile_words = set(profile.lower().split())
            requirement_words = set(requirement.lower().split())
            if not requirement_words:
                return 0.0
            return round(100 * len(profile_words & requirement_words) / len(requirement_words), 2)

        # Process matches
        results = []
        for _, project in project_df.iterrows():
            for _, emp in employee_df.iterrows():
                match_pct = calculate_match_percent(emp["profile"], project["requirements"])
                if match_pct > 0:
                    assignment_status = emp["Are you currently\u00a0 assigned to a project?"].strip().lower()
                    results.append({
                        "Project Name": project["Project Name"],
                        "Employee Name": emp["Name1"],
                        "Email": emp["Email"],
                        "Matching %": match_pct,
                        "Availability": emp["Availability"],
                        "Project Assignment": emp["Are you currently\u00a0 assigned to a project?"],
                        "Role": emp["Role"],
                        "Tools": emp["Tools"],
                        "Languages": emp["Languages"],
                        "Assigned Flag": 1 if assignment_status == "yes" else 0
                    })

        # Convert and sort: Unassigned → Name → Matching %
        result_df = pd.DataFrame(results)
        result_df = result_df.sort_values(
            by=["Assigned Flag", "Employee Name", "Matching %"],
            ascending=[True, True, False]
        )

        result_df.drop(columns=["Assigned Flag"], inplace=True)

        if result_df.empty:
            st.warning("No matches found above 0%. Try updating employee/project data.")
        else:
            st.success("✅ Matching complete and sorted (Unassigned → Name → Match %)")
            st.dataframe(result_df)

            # Download option
            def to_excel(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Matches")
                return output.getvalue()

            st.download_button(
                label="📥 Download Results as Excel",
                data=to_excel(result_df),
                file_name="employee_project_matches_sorted.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error: {e}")
