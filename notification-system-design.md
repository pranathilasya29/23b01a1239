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

# Stage 4

## Problem
Currently, notifications are fetched from the database whenever a student loads a page.
With:
- 50,000 students
- 5,000,000 notifications
the database receives a large number of repeated read requests, causing:
- High database load
- Increased response time
- Poor user experience
---
## Solution 1: Redis Cache
Store recently accessed notifications in Redis.
### Flow
1. Student requests notifications.
2. Check Redis Cache.
3. If found, return cached notifications.
4. Otherwise:
   - Query database.
   - Store result in Redis.
   - Return response.
### Advantages
- Very fast reads
- Reduces database load
- Better response time
### Tradeoffs
- Additional infrastructure
- Cache invalidation complexity
- Memory consumption
---
## Solution 2: Pagination
Instead of loading all notifications:
GET /notifications?page=1&limit=20
### Advantages
- Smaller result sets
- Faster queries
- Reduced network traffic
### Tradeoffs
- Additional frontend handling
- More API requests for older notifications
---
## Solution 3: WebSocket Notifications
Instead of requesting notifications on every page load, maintain a WebSocket connection.
### Flow
1. User logs in.
2. WebSocket connection established.
3. New notifications pushed instantly.
### Advantages
- Real-time delivery
- Eliminates frequent polling
- Lower database traffic
### Tradeoffs
- More complex implementation
- Connection management required
---
## Solution 4: Read Replicas
Use:
- Primary Database for writes
- Replica Databases for reads
### Advantages
- Scales read operations
- Reduces primary database load
### Tradeoffs
- Additional infrastructure cost
- Replication lag
---
## Solution 5: Message Queue
Use Kafka or RabbitMQ.
### Flow
1. Notification created.
2. Added to queue.
3. Worker processes notification.
4. Notification delivered.
### Advantages
- Better scalability
- Handles traffic spikes
### Tradeoffs
- Increased system complexity
- Additional maintenance
---
## Recommended Architecture
1. PostgreSQL as primary database
2. Redis for caching
3. Pagination for notification APIs
4. WebSockets for real-time updates
5. Read replicas for scaling reads
This architecture minimizes database load while providing fast notification delivery and a better user experience.

# Stage 5
## Problems with Current Implementation
Current Pseudocode:
```text
function notify_all(student_ids, message):
    for student_id in student_ids:
        send_email(student_id, message)
        save_to_db(student_id, message)
        push_to_app(student_id, message)
```
### Issues
1. Sequential Processing
   - Processes one student at a time.
   - Very slow for 50,000 students.
2. No Retry Mechanism
   - Failed emails are permanently lost.
3. No Fault Tolerance
   - If the service crashes midway, notifications stop.
4. Tight Coupling
   - Email, Database, and In-App notifications are dependent on each other.
5. Poor Scalability
   - Cannot efficiently handle large notification campaigns.
---
## What Happens If Email Fails For 200 Students?
The current implementation does not provide any retry mechanism.
As a result:
- Some students receive notifications.
- Some students do not receive notifications.
- System becomes inconsistent.
Failed notifications should be retried automatically.
---
## Recommended Solution
Use:
- PostgreSQL
- Message Queue (Kafka/RabbitMQ)
- Worker Services
- Retry Queue
- Dead Letter Queue (DLQ)
---
## Why Save To Database First?
Notifications should first be saved in the database.
Benefits:
- Database becomes source of truth.
- Notifications are never lost.
- Failed deliveries can be retried.
If email is sent first and the service crashes before database storage, there will be no record of the notification.
---
## Revised Pseudocode
```text
function notify_all(student_ids, message):
    notification_id = create_notification(message)
    for student_id in student_ids:
        save_to_db(
            notification_id,
            student_id,
            status="PENDING"
        )
        publish_to_queue({
            notification_id,
            student_id,
            message
        })
worker process_notification(job):
    try:
        send_email(
            job.student_id,
            job.message
        )
        push_to_app(
            job.student_id,
            job.message
        )
        update_status(
            job.notification_id,
            job.student_id,
            "SUCCESS"
        )
    except Exception:
        retry_count += 1
        if retry_count < 3:
            send_to_retry_queue(job)
        else:
            send_to_dead_letter_queue(job)
            update_status(
                job.notification_id,
                job.student_id,
                "FAILED"
            )
```
---
## Advantages
### Reliability
- Notifications are stored before delivery.
- Failed notifications can be retried.
### Scalability
- Multiple workers can process notifications simultaneously.
### Fault Tolerance
- System can recover after crashes.
### Monitoring
Status can be tracked as:
- Pending
- Success
- Failed
---
## Tradeoffs
### Pros
- Reliable
- Scalable
- Fault tolerant
### Cons
- More infrastructure
- More complexity
- Additional maintenance

# Stage 6
## Priority Inbox Approach
Priority is determined using:
1. Notification Type Weight
   - Placement = 3
   - Result = 2
   - Event = 1
2. Recency
   - Newer notifications get higher priority.
Priority Score:
```text
(Type Weight × 100) + Recency Score
```
Notifications are sorted by priority score and the top 10 unread notifications are displayed.
## Maintaining Top 10 Efficiently
Instead of sorting all notifications every time:
- Use a Min Heap of size 10.
- Keep only the current Top 10 notifications.
- When a new notification arrives:
  - Calculate its priority score.
  - Compare with smallest item in heap.
  - Replace if score is higher.
Complexity:
- Insert: O(log 10)
- Retrieval: O(10)
This is more efficient than sorting all notifications repeatedly.