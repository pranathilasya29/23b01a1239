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

# Stage 3
## Query Analysis
### Existing Query
```sql
SELECT *
FROM notifications
WHERE studentID = 1042
AND isRead = false
ORDER BY createdAt DESC;
```
### Is this Query Accurate?
Yes, the query is functionally correct because it retrieves all unread notifications for a specific student and orders them by creation time in descending order.
However, it is not efficient for large datasets.
---
## Why is this Query Slow?
The database contains:
- 50,000 students
- 5,000,000 notifications
Without proper indexing, the database performs a full table scan to find matching records.
The query performs:
1. Filtering by studentID
2. Filtering by isRead
3. Sorting by createdAt DESC
For millions of records this becomes expensive.
### Computation Cost
Without Index:
O(N)
where N = 5,000,000 rows
The database may need to scan most rows before sorting.
---
## Optimization
Create a Composite Index
```sql
CREATE INDEX idx_notifications_student_read_created
ON notifications(studentID, isRead, createdAt DESC);
```
### Optimized Query
```sql
SELECT *
FROM notifications
WHERE studentID = 1042
AND isRead = FALSE
ORDER BY createdAt DESC;
```
### Cost After Indexing
Index Lookup:
O(log N)
Result Retrieval:
O(K)
where K is the number of matching notifications.
This is significantly faster than a full table scan.
---
## Should We Add Indexes on Every Column?
No.
Adding indexes on every column is not a good practice.
### Reasons
1. Increased Storage Usage
2. Slower Insert Operations
3. Slower Update Operations
4. Slower Delete Operations
5. Many indexes may never be used
### Best Practice
Create indexes only on:
- Frequently searched columns
- Join columns
- Sorting columns
- Foreign key columns
---
## Query to Find Students Who Received Placement Notifications in Last 7 Days
```sql
SELECT DISTINCT studentID
FROM notifications
WHERE notificationType = 'Placement'
AND createdAt >= NOW() - INTERVAL '7 days';
```
### Explanation
- Filters Placement notifications.
- Retrieves notifications created in the last 7 days.
- Returns unique student IDs.