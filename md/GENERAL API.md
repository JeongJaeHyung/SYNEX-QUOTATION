# GENERAL API

API Status: Active
API Version: V1
날짜: 2025년 12월 26일 오전 8:27

# Contents

- General 등록
- General 목록 조회
- General 단일 조회
- General 수정
- General 삭제

---

## 1. General 등록

새로운 General(견적 프로젝트)을 등록합니다.

> Endpoint : POST /api/v1/quotation/general
> 

### Request body :

```jsx
{
  "name": "2025년 상반기 제어기 교체 사업",
  "client": "한국도로공사",
  "creator": "김철수",
  "manufacturer": "mPlus",
  "description": "기존 노후 제어기 전면 교체 건"
}
```

### Request filed:

| **Filed** | **Type** | **Not Null** | **Description** |
| --- | --- | --- | --- |
| name | varchar(100) | NN | 견적서명 |
| client | varchar(50) |  | 고객사 |
| creator | varchar(25) | NN | 작성자 |
| manufacturer | varchar(50) | NN | 장비사 |
| description | text |  | 비고 |

### Response Ex:

Response (201 Created):

```jsx
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "2025년 상반기 제어기 교체 사업",
  "client": "한국도로공사",
  "creator": "김철수",
  "manufacturer": "mPlus",
  "description": "기존 노후 제어기 전면 교체 건",
  "created_at": "2025-12-16T14:30:00.000000",
  "message": "General created successfully"
}
```

### Error:

| **Code** | **Description** |
| --- | --- |
| 422 Unprocessable Entity | 유효성 검증 실패 (필수값 누락 등) |

---

## 2. General 목록 조회

General 목록 조회와 스키마 반환을 지원합니다.

> Endpoint : GET /api/v1/quotation/general
> 

### Query Parameters:

| **Parameters** | **Type** | **Not Null** | **Description** | **Ex** |
| --- | --- | --- | --- | --- |
| include_schema | boolean |  | schema 포함 여부 | true/false |
| skip | int |  | 건너뛸 개수 | 0 |
| limit | int |  | 가져올 개수 | 100 |

### Request :

> GET /api/v1/quotation/general?include_schema=true&skip=0&limit=20
> 

### Response Ex:

Response with schema (200 OK):

```jsx
{
  "schema": {
    "name": {
      "title": "견적서명",
      "type": "string",
      "ratio": 3
    },
    "client": {
      "title": "고객사",
      "type": "string",
      "ratio": 2
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
      "ratio": 3
    }
  },
  "total": 5,
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "2025년 상반기 제어기 교체 사업",
      "client": "한국도로공사",
      "creator": "김철수",
      "manufacturer": "mPlus",
      "created_at": "2025-12-16T14:30:00.000000",
      "updated_at": "2025-12-16T14:30:00.000000",
      "description": "기존 노후 제어기 전면 교체 건"
    },
    {
      "id": "987fcdeb-51a2-43c1-z987-123456789012",
      "name": "B-Type 전광판 유지보수",
      "client": "서울시청",
      "creator": "이영희",
      "manufacturer": "mPlus",
      "created_at": "2025-12-15T09:00:00.000000",
      "updated_at": "2025-12-15T11:20:00.000000",
      "description": null
    }
  ],
  "skip": 0,
  "limit": 20
}
```

Response without schema (200 OK)

```jsx
{
  "total": 5,
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "name": "2025년 상반기 제어기 교체 사업",
      "client": "한국도로공사",
      "creator": "김철수",
      "manufacturer": "mPlus",
      "created_at": "2025-12-16T14:30:00.000000",
      "updated_at": "2025-12-16T14:30:00.000000",
      "description": "기존 노후 제어기 전면 교체 건"
    }
  ],
  "skip": 0,
  "limit": 20
}
```

---

## 3. General 단일 조회

특정 General의 상세 정보를 조회합니다. 연관된 하위 테이블(가격비교, 상세견적, 견적서) 조회 옵션을 제공합니다.

> Endpoint : GET /api/v1/quotation/general/{general_id}
> 

### Path Parameters:

| **Parameters** | **Type** | **Not Null** | **Description** | **Ex** |
| --- | --- | --- | --- | --- |
| general_id | uuid | NN | General ID | 123e4567-e89b... |

### Query Parameters:

| **Parameters** | **Type** | **Not Null** | **Description** | **Ex** |
| --- | --- | --- | --- | --- |
| include_relations | boolean |  | 연관 테이블 포함 여부 | true/false |
| include_schema | boolean |  | schema 포함 여부(relations 포함 시) | true/false |

### Request :

> GET /api/v1/quotation/general/123e4567-e89b-12d3-a456-426614174000?include_relations=true&include_schema=true
> 

### Response Ex:

Response with relations & schema (200 OK):

```jsx
{
  "general": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "name": "2025년 상반기 제어기 교체 사업",
    "client": "한국도로공사",
    "creator": "김철수",
    "manufacturer": "mPlus",
    "description": "기존 노후 제어기 전면 교체 건",
    "created_at": "2025-12-16T14:30:00.000000",
    "updated_at": "2025-12-16T14:30:00.000000"
  },
  "folders": [
	  "123e4567-e89b-12d3-a456-426614174000",
	  "adf12367-d23b-53a5-c361-521384121023",
	  "621d6891-c72f-96b4-d246-422414171230",
  ],
  "title": {
      "title": "제목",
      "type": "string",
      "ratio": 2
    },
    "updated_at": {
      "title": "최종수정일",
      "type": "datetime",
      "format": "YYYY-MM-DD HH:mm",
      "ratio": 2
    }
  }
}
```

Response basic (200 OK):

```jsx
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "2025년 상반기 제어기 교체 사업",
  "client": "한국도로공사",
  "creator": "김철수",
  "manufacturer": "mPlus",
  "description": "기존 노후 제어기 전면 교체 건",
  "created_at": "2025-12-16T14:30:00.000000",
  "updated_at": "2025-12-16T14:30:00.000000"
}
```

### Error:

| **Code** | **Description** |
| --- | --- |
| 404 Not Found | 해당 General ID를 찾을 수 없음 |

---

## 4. General 수정

General 정보를 부분 수정합니다.

> Endpoint : PUT /api/v1/quotation/general/{general_id}
> 

### Path Parameters:

| **Parameters** | **Type** | **Not Null** | **Description** | **Ex** |
| --- | --- | --- | --- | --- |
| general_id | uuid | NN | General ID | 123e4567-e89b... |

### Request body :

```jsx
{
  "client": "한국도로공사 (수정됨)",
  "description": "긴급 발주 건으로 변경"
}
```

### Request filed:

| **Filed** | **Type** | **Not Null** | **Description** |
| --- | --- | --- | --- |
| name | varchar(100) |  | 견적서명 |
| client | varchar(50) |  | 고객사 |
| creator | varchar(25) |  | 작성자 |
| description | text |  | 비고 |
| manufacture | varchar(50) |  | 장비사 |

### Response Ex:

Response (200 OK):

```jsx
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "2025년 상반기 제어기 교체 사업",
  "client": "한국도로공사 (수정됨)",
  "creator": "김철수",
  "description": "긴급 발주 건으로 변경",
  "updated_at": "2025-12-16T17:45:00.000000",
  "message": "General updated successfully"
}
```

### Error:

| **Code** | **Description** |
| --- | --- |
| 404 Not Found | 수정하려는 General이 없음 |
| 422 Unprocessable Entity | 유효성 검증 실패 |

---

## 5. General 삭제

General을 삭제합니다. (CASCADE 설정에 따라 연관된 하위 견적 데이터도 함께 삭제됩니다.)

> Endpoint : DELETE /api/v1/quotation/general/{general_id}
> 

### Path Parameters:

| **Parameters** | **Type** | **Not Null** | **Description** | **Ex** |
| --- | --- | --- | --- | --- |
| general_id | uuid | NN | General ID | 123e4567-e89b... |

### Response Ex:

Response (200 OK):

```jsx
{
  "message": "General deleted successfully",
  "deleted_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Error:

| **Code** | **Description** |
| --- | --- |
| 404 Not Found | 삭제하려는 General이 없음 |