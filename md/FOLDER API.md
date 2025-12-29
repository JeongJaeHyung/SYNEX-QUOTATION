# FOLDER API

API Status: SOON
API Version: V1
날짜: 2025년 12월 26일 오전 8:52

## Contents

- Folder 등록
- Folder 조회

---

## 1. Folder 등록

새로운 Folder를 등록합니다.

> Endpoint : POST /api/v1/quotation/folder
> 

### Request body :

```json
{
  "general_id": "4a9e6872-f4f0-4cca-8eab-af78dc3c8a7e",
  "title": "1차 총안"
}
```

### Request filed:

| Filed | Type | Not Null | Description |
| --- | --- | --- | --- |
| general_id | uuid | NN | 견적서(일반) id |
| title | varchar(50) | NN | 제목 |

### Response Ex:

Response (201 Created):

```json
{
  "id": "6s4e6872-h6f3-1fda-8eab-hf68dc3c8n5q",
  "title": "1차 총안",
  "created_at": "2025-12-17T15:40:08.627871"
}
```

### Error:

| Code | Description |
| --- | --- |
| 409 Conflict | 이미 있음 |
| 422 Unprocessable Entity | 유효성 검증 실패 |

---

## 2. Folder 조회

Folder를 조회합니다.

> Endpoint : GET /api/v1/quotation/folder/{folder_id}
> 

### Path Parameters:

| Parameters | Type | Not Null | Description |
| --- | --- | --- | --- |
| folder_id  | uuid | NN       | 폴더 ID     |

### Query Parameters:

| **Parameters** | **Type** | **Not Null** | **Description** | **Ex** |
| --- | --- | --- | --- | --- |
| include_schema | boolean |  | schema 포함 여부 | true/false |

### Request :

> GET /api/v1/quotation/folder/e8615ab6-7f33-4ec1-a13b-bfa3844fe3eb?include_schema=true
> 

### Response Ex:

Response with schema (200 OK):

```json
{
  "schema": {
    "table_name": {
      "title": "유형",
      "type": "string",
      "ratio": 2
    },
    "title": {
      "title": "제목",
      "type": "string",
      "ratio": 3
    },
    "creator": {
      "title": "작성자",
      "type": "string",
      "ratio": 1
    },
    "updated_at": {
      "title": "최종수정일",
      "type": "datetime",
      "format": "YYYY-MM-DD HH:mm",
      "ratio": 2
    },
    "description": {
      "title": "비고",
      "type": "string",
      "ratio": 2
    }
  },
  "id": "e8615ab6-7f33-4ec1-a13b-bfa3844fe3eb",
  "title": "1차 총안",
  "updated_at": "2025-12-09T15:47:47.198227",
  "resource_count": 3,
  "resources": [
    {
      "table_name": "내정가 비교",
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "납품품목 내정가견적비교",
      "creator": "김철수",
      "updated_at": "2025-12-16T15:00:00.000000",
      "description": "A사/B사 단가 비교"
    },
    {
      "table_name": "견적서(을지)",
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "납품품목 을지",
      "creator": "김철수",
      "updated_at": "2025-12-16T15:00:00.000000",
      "description": "최종 을지"
    },
    {
      "table_name": "견적서",
      "id": "770e8400-e29b-41d4-a716-996655441111",
      "title": "제어기 78개소",
      "creator": "박민수",
      "updated_at": "2025-12-16T16:20:00.000000",
      "description": "최종 제출용 견적서"
    }
  ]
}
```

Response without schema (200 OK):

```json
{
  "id": "e8615ab6-7f33-4ec1-a13b-bfa3844fe3eb",
  "title": "1차 총안",
  "updated_at": "2025-12-09T15:47:47.198227",
  "resource_count": 3,
  "resources": [
    {
      "table_name": "내정가 비교",
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "납품품목 내정가견적비교",
      "creator": "김철수",
      "updated_at": "2025-12-16T15:00:00.000000",
      "description": "A사/B사 단가 비교"
    },
    {
      "table_name": "견적서(을지)",
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "title": "납품품목 을지",
      "creator": "김철수",
      "updated_at": "2025-12-16T15:00:00.000000",
      "description": "최종 을지"
    },
    {
      "table_name": "견적서",
      "id": "770e8400-e29b-41d4-a716-996655441111",
      "title": "제어기 78개소",
      "creator": "박민수",
      "updated_at": "2025-12-16T16:20:00.000000",
      "description": "최종 제출용 견적서"
    }
  ]
}
```

---

## 3. Folder수정

을지 정보를 수정합니다.

> Endpoint : PUT /api/v1/quotation/folder/{folder_id}
> 

### Path Parameters:

| Parameters | Type | Not Null | Description |
| --- | --- | --- | --- |
| folder_id | uuid | NN | 폴더 ID |

### Request body:

```json
{
  "title": "1차 총안"
}
```

### Request field:

| Filed | Type | Not Null | Description |
| --- | --- | --- | --- |
| title | varchar(100) |  | 제목 |

---