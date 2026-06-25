# Stage 1- Notification System Design
## Core Actions
1. Get Notifications
2. Get Notification By ID
3. Create Notification
4. Mark Notification As Read
5. Mark All Notifications As Read
6. Delete Notification
7. Real-Time Notifications
---
## Get Notifications

### Endpoint

GET /api/v1/notifications

### Headers

Authorization: Bearer <token>

### Response

```json
{
  "success": true,
  "data": [
    {
      "id": "1239",
      "title": "Placement Drive",
      "message": "Affordmed recruitment starts tomorrow ",
      "category": "PLACEMENT",
      "isRead": false,
      "createdAt": "2026-06-25T10:00:00Z"
    }
  ]
}
```
---
## Get Notification By ID

GET /api/v1/notifications/{id}
---
## Create Notification
POST /api/v1/notifications
### Request
```json
{
  "title": "Exam Results",
  "message": "Results are published",
  "category": "RESULT"
}
```
### Response
```json
{
  "success": true,
  "message": "Notification Created"
}
```
---
## Mark Notification As Read
PATCH /api/v1/notifications/{id}/read
### Response
```json
{
  "success": true,
  "message": "Notification marked as read"
}
```
---
## Mark All Notifications As Read
PATCH /api/v1/notifications/read-all
---
## Delete Notification
DELETE /api/v1/notifications/{id}
---
## Real-Time Notifications
### WebSocket Endpoint
ws://localhost:8000/ws/notifications
### Event
```json
{
  "event": "notification_created",
  "data": {
    "id": "123",
    "title": "Hackathon",
    "message": "Hackathon starts tomorrow"
  }
}
```

# Stage 2
## Database Selection
Recommended Database: PostgreSQL
### Why PostgreSQL?
1. Supports ACID transactions.
2. Reliable for notification systems.
3. Supports indexing for fast retrieval.
4. Scales well with large datasets.
5. Supports JSON fields if needed.
---
## Database Schema
### Users Table
| Column | Type | Description |
|----------|---------|-------------|
| id | UUID | Primary Key |
| name | VARCHAR(100) | User Name |
| email | VARCHAR(255) | Email Address |
| created_at | TIMESTAMP | Creation Time |

### Notifications Table

| Column | Type | Description |
|----------|---------|-------------|
| id | UUID | Primary Key |
| title | VARCHAR(255) | Notification Title |
| message | TEXT | Notification Content |
| category | VARCHAR(50) | Placement/Event/Result |
| created_at | TIMESTAMP | Creation Time |

### User_Notifications Table

| Column | Type | Description |
|----------|---------|-------------|
| id | UUID | Primary Key |
| user_id | UUID | Foreign Key |
| notification_id | UUID | Foreign Key |
| is_read | BOOLEAN | Read Status |
| read_at | TIMESTAMP | Read Timestamp |

---
## SQL Queries
### Create Notification
INSERT INTO notifications
(title, message, category)
VALUES
('Placement Drive',
 'Infosys recruitment starts tomorrow',
 'PLACEMENT');
---
### Get Notifications
SELECT n.id,
       n.title,
       n.message,
       un.is_read
FROM notifications n
JOIN user_notifications un
ON n.id = un.notification_id
WHERE un.user_id = :user_id
ORDER BY n.created_at DESC;
---
### Get Notification By ID
SELECT *
FROM notifications
WHERE id = :notification_id;
---
### Mark Notification As Read
UPDATE user_notifications
SET is_read = TRUE,
    read_at = NOW()
WHERE notification_id = :notification_id
AND user_id = :user_id;
---
### Mark All Notifications As Read
UPDATE user_notifications
SET is_read = TRUE,
    read_at = NOW()
WHERE user_id = :user_id;
---
### Delete Notification
DELETE FROM notifications
WHERE id = :notification_id;
---
## Potential Challenges
### 1. Large Number of Notifications
Problem:
Millions of notifications can slow queries.
Solution:
- Add indexes on user_id and created_at.
- Use pagination.
---
### 2. High Read Traffic
Problem:
Users frequently check notifications.
Solution:
- Use Redis caching.
- Cache recent notifications.
---
### 3. Real-Time Delivery
Problem:
Large number of WebSocket connections.
Solution:
- Use Redis Pub/Sub.
- Use message queues.
---
### 4. Database Growth
Problem:
Storage size increases over time.
Solution:
- Archive old notifications.
- Partition tables by date.