# HEADER API

API Status: Active
API Version: V1
날짜: 2025년 12월 26일 오전 8:52

## Contents

- Header 등록
- Header 조회
- Header 수정

---

## 1. Header등록

새로운 갑지를 등록합니다.

> Endpoint : POST /api/v1/quotation/header
> 

### Request body :

```json
{
  "folder_id": "4a9e6872-f4f0-4cca-8eab-af78dc3c8a7e",
  "detailed_id": "28d6198e-cb24-4ad7-89b2-44ecf8c7a60c",
  "title": "mPlus 주액기",
  "creator": "홍길동",
  "client": "(주)엠플러스",
  "manufacturer": "장비사",
  "pic_name": "김중남",
  "pic_position": "이사"
}
```

### Request filed:

| Filed | Type | Not Null | Description |
| --- | --- | --- | --- |
| folder_id | uuid | NN | 폴더 id |
| detailed_id | uuid | NN | 을지 ID |
| title | varchar(100) | NN | 갑지 제목 |
| creator | varchar(25) | NN | 작성자 |
| client | varchar(50) | NN | 고객사 |
| manufacturer | varchar(50) |  | 장비사 |
| pic_name | varchar(50) | NN | 고객사 담당자명 |
| pic_position | varchar(50) | NN | 고객사 담당자 직급 |

### Response Ex:

Response (201 Created):

```json
{
  "id": "28d6198e-cb24-4ad7-89b2-44ecf8c7a60c",
  "title": "mPlus 주액기",
  "price": 634552000,
  "creator": "홍길동",
  "client": "(주)엠플러스",
  "manufacturer": "장비사",
  "pic_name": "김중남",
  "pic_position": "이사",
  "description_1": ""
  "description_2": ""
  "updated_at": "2025-12-21T16:43:56",
  "resource_count": 4,
  "header_resources": [
    {
      "machine": "[TEMPLATE] mPLUS 주액기",
      "name": "재료비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 144000000,
      "description": ""
    },
    {
      "machine": "[TEMPLATE] mPLUS 주액기",
      "name": "인건비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 435000000,
      "description": ""
    },
    {
      "machine": "주액 검사기",
      "name": "재료비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 1443000,
      "description": ""
    },
    {
      "machine": "주액 검사기",
      "name": "인건비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 231000000,
      "description": ""
    },
    {
      "machine": "경비",
      "name": "경비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 2342000,
      "description": ""
    },
    {
      "machine": "안전관리비 및 기업이윤",
      "name": "안전관리비 및 기업이윤"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 53210000,
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

## 2. Header조회

Detailed를 조회합니다.

> Endpoint : GET /api/v1/quotation/header/{header_id}
> 

### Path Parameters:

| Parameters | Type | Not Null | Description |
| --- | --- | --- | --- |
| header_id | uuid | NN | 갑지 ID |

### Query Parameters:

| **Parameters** | **Type** | **Not Null** | **Description** | **Ex** |
| --- | --- | --- | --- | --- |
| include_schema | boolean |  | schema 포함 여부 | true/false |

### Request :

> GET /api/v1/quotation/header/28d6198e-cb24-4ad7-89b2-44ecf8c7a60c?include_schema=true
> 

### Response Ex:

Response with schema (200 OK):

```json
{
  "id": "28d6198e-cb24-4ad7-89b2-44ecf8c7a60c",
  "title": "mPlus 주액기",
  "price": 634552000,
  "creator": "홍길동",
  "client": "(주)엠플러스",
  "manufacturer": "장비사",
  "pic_name": "김중남",
  "pic_position": "이사",
  "description_1": ""
  "description_2": ""
  "updated_at": "2025-12-21T16:43:56",
  "resource_count": 4,
  "resources": {
    "schema": {
      "machine": {
        "title": "장비명",
        "type": "string",
        "ratio": 2
      },
      "name": {
        "title": "품명",
        "type": "string",
        "ratio": 2
      },
      "spac": {
        "title": "규격",
        "type": "string",
        "ratio": 2
      },
      "compare": {
        "title": "수량",
        "type": "integer",
        "format": "currency",
        "ratio": 2
      },
      "unit": {
        "title": "단위",
        "type": "string",
        "ratio": 1
      },
      "solo_price": {
        "title": "단가",
        "type": "integer",
        "ratio": 1
      },
      "subtotal": {
        "title": "공급가액",
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
	  "header_resources": [
      {
	      "machine": "[TEMPLATE] mPLUS 주액기",
	      "name": "재료비"
	      "spac": "",
	      "compare": 1,
	      "unit": "원",
	      "solo_price": 144000000,
	      "description": ""
	    },
	    {
	      "machine": "[TEMPLATE] mPLUS 주액기",
	      "name": "인건비"
	      "spac": "",
	      "compare": 1,
	      "unit": "원",
	      "solo_price": 435000000,
	      "description": ""
	    },
	    {
	      "machine": "주액 검사기",
	      "name": "재료비"
	      "spac": "",
	      "compare": 1,
	      "unit": "원",
	      "solo_price": 1443000,
	      "description": ""
	    },
	    {
	      "machine": "주액 검사기",
	      "name": "인건비"
	      "spac": "",
	      "compare": 1,
	      "unit": "원",
	      "solo_price": 231000000,
	      "description": ""
	    },
	    {
	      "machine": "경비",
	      "name": "경비"
	      "spac": "",
	      "compare": 1,
	      "unit": "원",
	      "solo_price": 2342000,
	      "description": ""
	    },
	    {
	      "machine": "안전관리비 및 기업이윤",
	      "name": "안전관리비 및 기업이윤"
	      "spac": "",
	      "compare": 1,
	      "unit": "원",
	      "solo_price": 53210000,
	      "description": ""
	    },
	  ]
  }
}
```

Response without schema (200 OK):

```json
{
  "id": "28d6198e-cb24-4ad7-89b2-44ecf8c7a60c",
  "title": "mPlus 주액기",
  "price": 634552000,
  "creator": "홍길동",
  "client": "(주)엠플러스",
  "manufacturer": "장비사",
  "pic_name": "김중남",
  "pic_position": "이사",
  "description_1": ""
  "description_2": ""
  "updated_at": "2025-12-21T16:43:56",
  "resource_count": 4,
  "header_resources": [
    {
      "machine": "[TEMPLATE] mPLUS 주액기",
      "name": "재료비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 144000000,
      "description": ""
    },
    {
      "machine": "[TEMPLATE] mPLUS 주액기",
      "name": "인건비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 435000000,
      "description": ""
    },
    {
      "machine": "주액 검사기",
      "name": "재료비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 1443000,
      "description": ""
    },
    {
      "machine": "주액 검사기",
      "name": "인건비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 231000000,
      "description": ""
    },
    {
      "machine": "경비",
      "name": "경비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 2342000,
      "description": ""
    },
    {
      "machine": "안전관리비 및 기업이윤",
      "name": "안전관리비 및 기업이윤"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 53210000,
      "description": ""
    },
  ]
}
```

---

## 3. Header수정

갑지 정보를 수정합니다.

> Endpoint : PUT /api/v1/quotation/header/{header_id}
> 

### Path Parameters:

| Parameters | Type | Not Null | Description |
| --- | --- | --- | --- |
| header_id | uuid | NN | 갑지 ID |

### Request body:

```json
{
  "id": "28d6198e-cb24-4ad7-89b2-44ecf8c7a60c",
  "title": "mPlus 주액기",
  "price": 634552000,
  "creator": "홍길동",
  "client": "(주)엠플러스",
  "manufacturer": "장비사",
  "pic_name": "김중남",
  "pic_position": "이사",
  "description_1": ""
  "description_2": ""
  "updated_at": "2025-12-21T16:43:56",
  "resource_count": 4,
  "header_resources": [
      {
      "machine": "[TEMPLATE] mPLUS 주액기",
      "name": "재료비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 144000000,
      "description": ""
    },
    {
      "machine": "[TEMPLATE] mPLUS 주액기",
      "name": "인건비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 435000000,
      "description": ""
    },
    {
      "machine": "경비",
      "name": "경비"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 2342000,
      "description": ""
    },
    {
      "machine": "안전관리비 및 기업이윤",
      "name": "안전관리비 및 기업이윤"
      "spac": "",
      "compare": 1,
      "unit": "원",
      "solo_price": 53210000,
      "description": ""
    },
  ]
}
```

### Request field:

| Filed | Type | Not Null | Description |
| --- | --- | --- | --- |
| title | varchar(100) |  | 갑지 제목 |
| creator | varchar(25) |  | 작성자 |
| client | varchar(50) |  | 고객사 |
| manufacturer | varchar(50) |  | 장비사 |
| pic_name | varchar(50) |  | 고객사 담당자명 |
| pic_position | varchar(50) |  | 고객사 담당자 직급 |
| header_resources.machine | varchar(100) |  | 장비명 |
| header_resources.name | varchar(100) |  | 품목명 |
| header_resources.spac | varchar(50) |  | 규격 |
| header_resources.compare | int |  | 수량 |
| header_resources.unit | varchar(10) |  | 단위 |
| header_resources.solo_price | int |  | 단가 |
| header_resources.description | text |  | 비고 |

---