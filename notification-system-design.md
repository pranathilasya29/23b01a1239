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