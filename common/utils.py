from types import SimpleNamespace
from collections import defaultdict
from .models import Mark


def get_student_activities(user_profile):
    """
    Given a UserProfile `user_profile`, returns a list of SimpleNamespace objects,
    one per activity that the student has a mark for. Each namespace has attributes:
      - activity_category: ActivityCategory instance or activity_type string
      - mark:              the Mark instance
      - subject:           the Subject instance
      - max_score:         Decimal max_score for that activity
    """
    # Fetch all Mark records for this student, including related Activity, Subject, and Category
    student_marks = Mark.objects.filter(student=user_profile).select_related(
        "activity__subject", "activity__activity_category"
    )

    activities_info = []
    for mark in student_marks:
        activity = mark.activity
        # Use the category FK if set, otherwise fall back to the old activity_type field
        activity_category = activity.activity_category or activity.activity_type

        activities_info.append(
            SimpleNamespace(
                activity_category=activity_category,
                mark=mark,
                subject=activity.subject,
                max_score=activity.max_score,
            )
        )

    return activities_info


def get_student_activities_by_category(user_profile, activity_category):
    """
    Given a UserProfile `user_profile` and an ActivityCategory instance `activity_category`,
    return a list of dicts—one per activity in that category which this student has a mark for.
    Each dict contains:
      - 'student':           the UserProfile
      - 'mark':              the Mark instance
      - 'subject':           the Subject instance
      - 'max_score':         Decimal max_score for that activity
      - 'activity_category': the ActivityCategory instance
    """
    # pull all marks for this student in activities of the given category
    student_marks = Mark.objects.filter(
        student=user_profile, activity__activity_category=activity_category
    ).select_related("activity__subject")

    for mark in student_marks:
        print(mark)

    results = []
    for mark in student_marks:
        activity = mark.activity
        results.append(
            {
                "student": user_profile,
                "mark": mark,
                "subject": activity.subject,
                "max_score": activity.max_score,
                "activity_category": activity_category,
            }
        )

    return results
