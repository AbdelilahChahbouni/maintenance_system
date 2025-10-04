from flask import render_template, redirect, url_for, flash, request , Blueprint
from app import db
from app.models import Issue
from .forms import IssueForm


issues = Blueprint('issues', __name__, template_folder='templates/auth')

@issues.route("/issues")
def issues_list():
    all_issues = Issue.query.all()
    return render_template("issues/issues.html", issues=all_issues)

@issues.route("/issues/<int:issue_id>")
def issue_detail(issue_id):
    issue = Issue.query.get_or_404(issue_id)  # returns 404 if not found
    return render_template("issues/issue_details.html", issue=issue)


@issues.route("/issues/new", methods=["GET", "POST"])
def new_issue():
    print("befor")
    form = IssueForm()
    print('ok')
    if form.validate_on_submit():
        issue = Issue(
            title=form.title.data,
            description=form.description.data,
            solution=form.solution.data,
            machine_name = form.machine_name.data
        )
        db.session.add(issue)
        db.session.commit()
        flash("Issue added successfully!", "success")
        return redirect(url_for("issues.issues_list"))
    return render_template("issues/add_issue.html", form=form, title="New Issue")

@issues.route("/issues/<int:issue_id>/edit", methods=["GET", "POST"])
def edit_issue(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    form = IssueForm(obj=issue)
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
