# DETAILED API

API Status: Active
API Version: V1
날짜: 2025년 12월 26일 오전 8:49

## Contents

- Detailed 등록
- Detailed 조회

---

## 1. Detailed 등록

새로운 Parts를 등록합니다.

> Endpoint : POST /api/v1/quotation/detailed
> 

### Request body :

```json
{
  "folder_id": "4a9e6872-f4f0-4cca-8eab-af78dc3c8a7e",
  "price_compare_id": "28d6198e-cb24-4ad7-89b2-44ecf8c7a60c",
  "title": "전광판 상세 견적",
  "creator": "홍길동",
  "description": "Example\nExample\nExample"
}
```

### Request filed:

| Filed | Type | Not Null | Description |
| --- | --- | --- | --- |
| folder_id | uuid | NN | 폴더 id |
| price_compare_id | uuid | NN | 내정가견적비교서 ID |
| creator | varchar(25) | NN | 작성자 |
| description | text |  | 설명 |

### Response Ex:

Response (201 Created):

```json
{
  "detailed_id": "e8615ab6-7f33-4ec1-a13b-bfa3844fe3eb",
  "title": "전광판 상세 견적",
  "creator": "홍길동",
  "description": "Example\nExample\nExample",
  "created_at": "2025-12-17T15:40:08.627871",
  "detailed_resources": [
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "자재비",
      "minor": "전장 판넬 판금 및 명판",
      "unit": "식",
      "solo_price": 34040000,
      "compare": 1,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "자재비",
      "minor": "판넬 차단기류",
      "unit": "식",
      "solo_price": 9360000,
      "compare": 3,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "자재비",
      "minor": "판넬 기타자재",
      "unit": "식",
      "solo_price": 37838000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "자재비",
      "minor": "케이블 및 기타 잡자재",
      "unit": "식",
      "solo_price": 27760000,
      "compare": 0,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "인건비",
      "minor": "전장설계",
      "unit": "식",
      "solo_price": 18000000,
      "compare": 5,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "인건비",
      "minor": "기체배선",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "출장경비",
      "minor": "식대",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "출장경비",
      "minor": "숙박비",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "출장경비",
      "minor": "교통비",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "출장경비",
      "minor": "운송비",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
  ]
}
```

### Error:

| Code | Description |
| --- | --- |
| 404 Not Found | Maker or Category가 없음 |
| 409 Conflict | 이미 해당 부품이 등록됨 or 동일한 코드를 사용하는 부품이 있음 |
| 422 Unprocessable Entity | 유효성 검증 실패 |

---

## 2. Detailed 조회

Detailed를 조회합니다.

> Endpoint : GET /api/v1/quotation/detailed/{detailed_id}
> 

### Path Parameters:

| Parameters | Type | Not Null | Description |
| --- | --- | --- | --- |
| detailed_id | uuid | NN | 을지 ID |

### Query Parameters:

| **Parameters** | **Type** | **Not Null** | **Description** | **Ex** |
| --- | --- | --- | --- | --- |
| include_schema | boolean |  | schema 포함 여부 | true/false |

### Request :

> GET /api/v1/parts?maker_id=J012&ul=true&skip=0&limit=20
> 

### Response Ex:

Response with schema (200 OK):

```json
{
  "id": "e8615ab6-7f33-4ec1-a13b-bfa3844fe3eb",
  "title": "전광판 상세 견적",
  "creator": "홍길동",
  "description": "Example\nExample\nExample",
  "updated_at": "2025-12-09T15:47:47.198227",
  "resource_count": 10,
  "resources": {
    "schema": {
      "machine_name": {
        "title": "장비명",
        "type": "string",
        "ratio": 2
      },
      "category_major": {
        "title": "대분류",
        "type": "string",
        "ratio": 2
      },
      "category_minor": {
        "title": "중분류",
        "type": "string",
        "ratio": 2
      },
      "solo_price": {
        "title": "단가",
        "type": "integer",
        "format": "currency",
        "ratio": 2
      },
      "unit": {
        "title": "단위",
        "type": "string",
        "ratio": 1
      },
      "compare": {
        "title": "수량",
        "type": "integer",
        "ratio": 1
      },
      "subtotal": {
        "title": "견적가",
        "type": "integer",
        "format": "currency",
        "ratio": 2
      },
      "description": {
        "title": "비고",
        "type": "string",
        "format": "currency",
        "ratio": 2
      },
    },
	  "detailed_resources": [
	    {
		    "machine_name": "[TEMPLATE] mPLUS 주액기",
	      "major": "자재비",
	      "minor": "전장 판넬 판금 및 명판",
	      "unit": "식",
	      "solo_price": 34040000,
	      "compare": 1,
	      "description": ""
	    },
	    {
		    "machine_name": "[TEMPLATE] mPLUS 주액기",
	      "major": "자재비",
	      "minor": "판넬 차단기류",
	      "unit": "식",
	      "solo_price": 9360000,
	      "compare": 3,
	      "description": ""
	    },
	    {
		    "machine_name": "[TEMPLATE] mPLUS 주액기",
	      "major": "자재비",
	      "minor": "판넬 기타자재",
	      "unit": "식",
	      "solo_price": 37838000,
	      "compare": 2,
	      "description": ""
	    },
	    {
		    "machine_name": "[TEMPLATE] mPLUS 주액기",
	      "major": "자재비",
	      "minor": "케이블 및 기타 잡자재",
	      "unit": "식",
	      "solo_price": 27760000,
	      "compare": 0,
	      "description": ""
	    },
	    {
		    "machine_name": "[TEMPLATE] mPLUS 주액기",
	      "major": "인건비",
	      "minor": "전장설계",
	      "unit": "식",
	      "solo_price": 18000000,
	      "compare": 5,
	      "description": ""
	    },
	    {
		    "machine_name": "[TEMPLATE] mPLUS 주액기",
	      "major": "인건비",
	      "minor": "기체배선",
	      "unit": "식",
	      "solo_price": 120000000,
	      "compare": 2,
	      "description": ""
	    },
	    {
		    "machine_name": "[TEMPLATE] mPLUS 주액기",
	      "major": "출장경비",
	      "minor": "식대",
	      "unit": "식",
	      "solo_price": 120000000,
	      "compare": 2,
	      "description": ""
	    },
	    {
		    "machine_name": "[TEMPLATE] mPLUS 주액기",
	      "major": "출장경비",
	      "minor": "숙박비",
	      "unit": "식",
	      "solo_price": 120000000,
	      "compare": 2,
	      "description": ""
	    },
	    {
		    "machine_name": "[TEMPLATE] mPLUS 주액기",
	      "major": "출장경비",
	      "minor": "교통비",
	      "unit": "식",
	      "solo_price": 120000000,
	      "compare": 2,
	      "description": ""
	    },
	    {
		    "machine_name": "[TEMPLATE] mPLUS 주액기",
	      "major": "출장경비",
	      "minor": "운송비",
	      "unit": "식",
	      "solo_price": 120000000,
	      "compare": 2,
	      "description": ""
	    },
	  ]
  }
}
```

Response without schema (200 OK):

```json
{
  "id": "e8615ab6-7f33-4ec1-a13b-bfa3844fe3eb",
  "title": "전광판 상세 견적",
  "creator": "홍길동",
  "description": "Example\nExample\nExample",
  "updated_at": "2025-12-09T15:47:47.198227",
  "resource_count": 10,
  "detailed_resources": [
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "자재비",
      "minor": "전장 판넬 판금 및 명판",
      "unit": "식",
      "solo_price": 34040000,
      "compare": 1,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "자재비",
      "minor": "판넬 차단기류",
      "unit": "식",
      "solo_price": 9360000,
      "compare": 3,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "자재비",
      "minor": "판넬 기타자재",
      "unit": "식",
      "solo_price": 37838000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "자재비",
      "minor": "케이블 및 기타 잡자재",
      "unit": "식",
      "solo_price": 27760000,
      "compare": 0,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "인건비",
      "minor": "전장설계",
      "unit": "식",
      "solo_price": 18000000,
      "compare": 5,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "인건비",
      "minor": "기체배선",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "출장경비",
      "minor": "식대",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "출장경비",
      "minor": "숙박비",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "출장경비",
      "minor": "교통비",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "출장경비",
      "minor": "운송비",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
  ]
  "skip": 0,
  "limit": 20
}
```

---

## 3. Detailed 수정

을지 정보를 수정합니다.

> Endpoint : PUT /api/v1/quotation/detailed/{detailed_id}
> 

### Path Parameters:

| Parameters | Type | Not Null | Description |
| --- | --- | --- | --- |
| detailed_id | uuid | NN | 을지 ID |

### Request body:

```json
{
	"id": "e8615ab6-7f33-4ec1-a13b-bfa3844fe3eb",
	"title": "전광판 상세 견적",
  "creator": "홍길동",
  "description": "Example\nExample\nExample",
  "updated_at": "2025-12-09T15:47:47.198227",
  "resource_count": 10,
  "detailed_resources": [
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "자재비",
      "minor": "전장 판넬 판금 및 명판",
      "unit": "식",
      "solo_price": 34040000,
      "compare": 1,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "자재비",
      "minor": "판넬 차단기류",
      "unit": "식",
      "solo_price": 9360000,
      "compare": 3,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "자재비",
      "minor": "판넬 기타자재",
      "unit": "식",
      "solo_price": 37838000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "자재비",
      "minor": "케이블 및 기타 잡자재",
      "unit": "식",
      "solo_price": 27760000,
      "compare": 0,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "인건비",
      "minor": "전장설계",
      "unit": "식",
      "solo_price": 18000000,
      "compare": 5,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "인건비",
      "minor": "기체배선",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "출장경비",
      "minor": "식대",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "출장경비",
      "minor": "숙박비",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "출장경비",
      "minor": "교통비",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
    {
	    "machine_name": "[TEMPLATE] mPLUS 주액기",
      "major": "출장경비",
      "minor": "운송비",
      "unit": "식",
      "solo_price": 120000000,
      "compare": 2,
      "description": ""
    },
  ]
  "skip": 0,
  "limit": 20
}
```

### Request field:

| Filed | Type | Not Null | Description |
| --- | --- | --- | --- |
| title | varchar(100) |  | 제목 |
| creator | varchar(50) |  | 작성자 |
| description | text |  | 을지 |
| detailed_resources.machine_name | varchar(100) |  | [TEMPLATE] mPLUS 주액기 |
| detailed_resources.major | varchar(30) |  | 대분류 |
| detailed_resources.minor | varchar(50) |  | 소분류 |
| detailed_resources.solo_price | int |  | 내정 단가 |
| detailed_resources.unit | varchar(10) |  | 내정 단위 |
| detailed_resources.compare | int |  | 내정 수량 |
| detailed_resources.description | text |  | 비고 |

---