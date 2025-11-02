from flask import render_template, redirect, url_for, flash, request , Blueprint , send_file
from app import db
from app.models import Issue , Machine , User
from .forms import IssueForm
from flask_login import current_user
from sqlalchemy import or_
from app.utils import export_to_pdf

issues = Blueprint('issues', __name__, template_folder='templates/auth')

@issues.route('/issues/export/pdf')
def export_issues_pdf():
    issues = Issue.query.all()
    headers = ["#", "Title", "Machine", "User", "Date", "Status"]
    rows = [
        [
            i + 1,
            issue.title,
            issue.machine.name,
            issue.author.username if issue.author else "—",
            issue.created_at.strftime("%Y-%m-%d"),
            issue.status.capitalize() if hasattr(issue, "status") else "—"
        ]
        for i, issue in enumerate(issues)
    ]
    return export_to_pdf("🧾 Maintenance Issues Report", headers, rows, "issues_report.pdf")


@issues.route("/issues")
def issues_list():
    search_query = request.args.get('q', '').strip()
    date_filter = request.args.get('date', '').strip()

    query = Issue.query.join(Issue.machine).join(User) # join Machine table

    if search_query:
        query = query.filter(
            or_(
                Issue.title.ilike(f"%{search_query}%"),
                Machine.name.ilike(f"%{search_query}%"),
                User.username.ilike(f"%{search_query}%")
            )
        )

    if date_filter:
        query = query.filter(Issue.created_at.like(f"%{date_filter}%"))

    issues = query.all()
    return render_template("issues/issues.html", issues=issues)

@issues.route("/issues/new", methods=["GET", "POST"])
def new_issue():
   
    form = IssueForm()
    form.machine_name.choices = [(m.id, m.name) for m in Machine.query.all()]
   
    if form.validate_on_submit():
        issue = Issue(
            title=form.title.data,
            description=form.description.data,
            solution=form.solution.data,
            machine_id = form.machine_name.data,
            author = current_user
        )
        db.session.add(issue)
        db.session.commit()
        flash("Issue added successfully!", "success")
        return redirect(url_for("issues.issues_list"))
    return render_template("issues/add_issue.html", form=form, title="New Issue")

@issues.route("/issues/<int:issue_id>")
def issue_detail(issue_id):
    issue = Issue.query.get_or_404(issue_id)  # returns 404 if not found
    return render_template("issues/issue_details.html", issue=issue)



@issues.route("/issues/<int:issue_id>/edit", methods=["GET", "POST"])
def edit_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    form = IssueForm(obj=issue)
    form.machine_name.choices = [(m.id, m.name) for m in Machine.query.all()]
    if form.validate_on_submit():
        issue.title = form.title.data
        issue.description = form.description.data
        issue.solution = form.solution.data
        issue.machine_name = form.machine_name.data
        db.session.commit()
        flash("Issue updated successfully!", "success")
        return redirect(url_for("issues.issues_list"))
    print(form.errors)
    return render_template("issues/add_issue.html", form=form, title="Edit Issue")

@issues.route("/issues/<int:issue_id>/delete", methods=["POST"])
def delete_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    db.session.delete(issue)
    db.session.commit()
    flash("Issue deleted successfully!", "danger")
    return redirect(url_for("issues.issues_list"))
