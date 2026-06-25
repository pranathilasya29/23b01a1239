from datetime import datetime
WEIGHTS = {
    "Placement": 3,
    "Result": 2,
    "Event": 1
}
notifications = [
    {
        "id": 1,
        "notificationType": "Placement",
        "message": "Affordmed  Hiring",
        "createdAt": "2026-06-25T10:00:00"
    },
    {
        "id": 2,
        "notificationType": "Event",
        "message": "Hackathon",
        "createdAt": "2026-06-24T10:00:00"
    },
    {
        "id": 3,
        "notificationType": "Result",
        "message": "Results Published",
        "createdAt": "2026-06-25T09:00:00"
    },
    {
        "id": 4,
        "notificationType": "Placement",
        "message": "TCS Hiring",
        "createdAt": "2026-06-25T11:00:00"
    },
    {
        "id": 5,
        "notificationType": "Event",
        "message": "Workshop",
        "createdAt": "2026-06-23T10:00:00"
    }
]
def priority_score(notification):
    created_time = datetime.fromisoformat(
        notification["createdAt"]
    )
    current_time = datetime.now()
    age_hours = (
        current_time - created_time
    ).total_seconds() / 3600
    recency_score = max(0, 100 - age_hours)
    return (
        WEIGHTS[notification["notificationType"]] * 100
        + recency_score
    )

sorted_notifications = sorted(
    notifications,
    key=priority_score,
    reverse=True
)
top_10 = sorted_notifications[:10]
print("\nTOP PRIORITY NOTIFICATIONS\n")
for n in top_10:
    print(
        f"{n['notificationType']} | "
        f"{n['message']} | "
        f"{n['createdAt']}"
    )