# PRICE_COMPARE API

API Status: Active
API Version: V1
날짜: 2025년 12월 26일 오전 7:47

# Contents

- Price compare 등록
- Price compare 조회
- Price compare 수정

---

## 1. Price compare 등록

새로운 Price compare(내정가견적비교서)를 등록합니다.

> Endpoint : POST /api/v1/quotation/price_compare
> 

### Request body :

```jsx
{
  "folder_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "의정부 설치, 전광판제어기",
  "creator": "홍길동",
  "description": "의정부에 설치할 전광판제어기 입니다.",
  "machine_count": 2,
	"machine_ids": [
      "987fcdeb-51a2-43c1-z987-123456789012",
      "123e4567-e89b-43c1-z987-426614174000"
  ],
}
```

### Request field:

| **Filed** | **Type** | **Not Null** | **Description** |
| --- | --- | --- | --- |
| folder_id | uuid | NN | 폴더 id |
| title | varchar(100) | NN | 제목 |
| creator | varchar(25) | NN | 작성자 |
| description | text |  | 작성자 |
| machines, machine_id | uuid | NN | 장비 견적서 id |

### Response Ex:

Response (201 Created):

```jsx
{
  "id": "517e4567-51a2-43c1-z987-123412784212",
  "title": "의정부 설치, 전광판제어기",
  "creator": "김철수",
  "description": "기존 노후 제어기 전면 교체 건",
  "created_at": "2025-12-16T14:30:00.000000",
  "price_compare_resources": [
	  {
		  "major": "자재비",
		  "minor": "부품비",
		  "cost_solo_price": 28000,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 29400,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "자재비",
		  "minor": "전장 판넬 판금 및 명판",
		  "cost_solo_price": 3150000,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 3307500,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "자재비",
		  "minor": "케이블 및 기타 잡자재",
		  "cost_solo_price": 1,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 1,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "자재비",
		  "minor": "판넬 기타자재",
		  "cost_solo_price": 90000,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 94500,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "자재비",
		  "minor": "판넬 주요자재",
		  "cost_solo_price": 1,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 1,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "자재비",
		  "minor": "판넬 차단기류",
		  "cost_solo_price": 80000,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 84000,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "인건비",
		  "minor": "전장설계",
		  "cost_solo_price": 200000,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 210000,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "인건비",
		  "minor": "운영PC 셋업",
		  "cost_solo_price": 350000,
		  "cost_unit": "ea",
		  "cost_compare": 10,
		  "quotation_solo_price": 367500,
		  "quotation_unit": "ea",
		  "quotation_compare": 10,
		  "upper": 5,
		  "description": ""
	  }
  ]
}
```

### Error:

| **Code** | **Description** |
| --- | --- |
| 404 Not Found | 입력한 `general_id` 또는 `machine_id`가 DB에 존재하지 않음 |
| 409 Conflict | 해당 General ID로 이미 생성된 비교견적서가 존재함 (1:1 관계일 경우) |
| 422 Validation Error | 필수 필드 누락 또는 UUID 형식 오류 |

---

## 2. Price compare 조회

Price compare 조회와 스키마 반환을 지원합니다.

> Endpoint : GET /api/v1/quotation/price_compare/{price_compare_id}
> 

### Path Parameters:

| Parameters | Type | Not Null | Description |
| --- | --- | --- | --- |
| price_compare_id | uuid | NN | 내정가견적비교서 ID |

### Query Parameters:

| **Parameters** | **Type** | **Not Null** | **Description** | **Ex** |
| --- | --- | --- | --- | --- |
| include_schema | boolean |  | schema 포함 여부 | true/false |

### Request :

> GET /api/v1/quotation/price_compare/{price_compare_id}?include_schema=true
> 

### Response Ex:

Response with schema (200 OK):

```jsx
{
  "id": "517e4567-51a2-43c1-z987-123412784212",
  "title": "의정부 설치, 전광판제어기",
  "creator": "홍길동",
  "description": "의정부에 설치할 전광판제어기 입니다.",
  "updated_at": "2025-12-09T15:47:47.198227",
  "resource_count": 8,
  "resources": {
    "schema": {
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
      "cost_solo_price": {
        "title": "내정 단가",
        "type": "integer",
        "format": "currency",
        "ratio": 2
      },
      "cost_unit": {
        "title": "내정 단위",
        "type": "string",
        "ratio": 1
      },
      "cost_compare": {
        "title": "내정 수량",
        "type": "integer",
        "ratio": 1
      },
      "cost_subtotal": {
        "title": "내정가",
        "type": "integer",
        "format": "currency",
        "ratio": 2
      },"quotation_solo_price": {
        "title": "견적 단가",
        "type": "integer",
        "format": "currency",
        "ratio": 2
      },
      "quotation_unit": {
        "title": "견적 단위",
        "type": "string",
        "ratio": 1
      },
      "quotation_compare": {
        "title": "견적 수량",
        "type": "integer",
        "ratio": 1
      },
      "quotation_subtotal": {
        "title": "견적가",
        "type": "integer",
        "format": "currency",
        "ratio": 2
      },
      "upper": {
        "title": "상승반영",
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
	  "price_compare_resources": [
		  {
			  "major": "자재비",
			  "minor": "부품비",
			  "cost_solo_price": 28000,
			  "cost_unit": "ea",
			  "cost_compare": 1,
			  "quotation_solo_price": 29400,
			  "quotation_unit": "ea",
			  "quotation_compare": 1,
			  "upper": 5,
			  "description": ""
		  },
		  {
			  "major": "자재비",
			  "minor": "전장 판넬 판금 및 명판",
			  "cost_solo_price": 3150000,
			  "cost_unit": "ea",
			  "cost_compare": 1,
			  "quotation_solo_price": 3307500,
			  "quotation_unit": "ea",
			  "quotation_compare": 1,
			  "upper": 5,
			  "description": ""
		  },
		  {
			  "major": "자재비",
			  "minor": "케이블 및 기타 잡자재",
			  "cost_solo_price": 1,
			  "cost_unit": "ea",
			  "cost_compare": 1,
			  "quotation_solo_price": 1,
			  "quotation_unit": "ea",
			  "quotation_compare": 1,
			  "upper": 5,
			  "description": ""
		  },
		  {
			  "major": "자재비",
			  "minor": "판넬 기타자재",
			  "cost_solo_price": 90000,
			  "cost_unit": "ea",
			  "cost_compare": 1,
			  "quotation_solo_price": 94500,
			  "quotation_unit": "ea",
			  "quotation_compare": 1,
			  "upper": 5,
			  "description": ""
		  },
		  {
			  "major": "자재비",
			  "minor": "판넬 주요자재",
			  "cost_solo_price": 1,
			  "cost_unit": "ea",
			  "cost_compare": 1,
			  "quotation_solo_price": 1,
			  "quotation_unit": "ea",
			  "quotation_compare": 1,
			  "upper": 5,
			  "description": ""
		  },
		  {
			  "major": "자재비",
			  "minor": "판넬 차단기류",
			  "cost_solo_price": 80000,
			  "cost_unit": "ea",
			  "cost_compare": 1,
			  "quotation_solo_price": 84000,
			  "quotation_unit": "ea",
			  "quotation_compare": 1,
			  "upper": 5,
			  "description": ""
		  },
		  {
			  "major": "인건비",
			  "minor": "전장설계",
			  "cost_solo_price": 200000,
			  "cost_unit": "ea",
			  "cost_compare": 1,
			  "quotation_solo_price": 210000,
			  "quotation_unit": "ea",
			  "quotation_compare": 1,
			  "upper": 5,
			  "description": ""
		  },
		  {
			  "major": "인건비",
			  "minor": "운영PC 셋업",
			  "cost_solo_price": 350000,
			  "cost_unit": "ea",
			  "cost_compare": 10,
			  "quotation_solo_price": 367500,
			  "quotation_unit": "ea",
			  "quotation_compare": 10,
			  "upper": 5,
			  "description": ""
		  }
	  ]
  }
}
```

Response without schema (200 OK)

```jsx
{
  "id": "517e4567-51a2-43c1-z987-123412784212",
  "title": "의정부 설치, 전광판제어기",
  "creator": "홍길동",
  "description": "의정부에 설치할 전광판제어기 입니다.",
  "updated_at": "2025-12-09T15:47:47.198227",
  "resource_count": 8,
  "price_compare_resources": [
	  {
		  "major": "자재비",
		  "minor": "부품비",
		  "cost_solo_price": 28000,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 28000,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "자재비",
		  "minor": "전장 판넬 판금 및 명판",
		  "cost_solo_price": 3150000,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 3150000,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "자재비",
		  "minor": "케이블 및 기타 잡자재",
		  "cost_solo_price": 1,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 1,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "자재비",
		  "minor": "판넬 기타자재",
		  "cost_solo_price": 90000,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 90000,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "자재비",
		  "minor": "판넬 주요자재",
		  "cost_solo_price": 1,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 1,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "자재비",
		  "minor": "판넬 차단기류",
		  "cost_solo_price": 80000,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 80000,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "인건비",
		  "minor": "전장설계",
		  "cost_solo_price": 200000,
		  "cost_unit": "ea",
		  "cost_compare": 1,
		  "quotation_solo_price": 200000,
		  "quotation_unit": "ea",
		  "quotation_compare": 1,
		  "upper": 5,
		  "description": ""
	  },
	  {
		  "major": "인건비",
		  "minor": "운영PC 셋업",
		  "cost_solo_price": 350000,
		  "cost_unit": "ea",
		  "cost_compare": 10,
		  "quotation_solo_price": 350000,
		  "quotation_unit": "ea",
		  "quotation_compare": 10,
		  "upper": 5,
		  "description": ""
	  }
  ]
}
```

---

## 3. Price compare 수정

장비 견적서 정보 및/또는 구성 부품을 수정합니다.

> Endpoint : PUT /api/v1/quotation/price_compare/{price_compare_id}
> 

### Path Parameters:

| Parameters | Type | Not Null | Description |
| --- | --- | --- | --- |
| price_compare_id | uuid | NN | 내정가견적비교서 ID |

### Request body:

```json
{
  "creator": "홍길동",
  "title": "의정부 설치, 전광판제어기",
  "description": "의정부에 설치할 전광판제어기 입니다. (수정됨)",
  "machine_ids": [
      "987fcdeb-51a2-43c1-z987-123456789012",
      "123e4567-e89b-43c1-z987-426614174000"
  ],
  "price_compare_resources": [
      {
          "major": "자재비",
          "minor": "부품비",
          "cost_solo_price": 28000,
          "cost_unit": "ea",
          "cost_compare": 1,
          "quotation_solo_price": 30240,
          "quotation_unit": "ea",
          "quotation_compare": 1,
          "upper": 8,
          "description": ""
      },
      {
          "major": "자재비",
          "minor": "전장 판넬 판금 및 명판",
          "cost_solo_price": 3150000,
          "cost_unit": "ea",
          "cost_compare": 1,
          "quotation_solo_price": 3622500,
          "quotation_unit": "ea",
          "quotation_compare": 1,
          "upper": 15,
          "description": "15% 추가"
      }
      // ... 나머지 항목들 (기존 DB에 있던 내용이라도 유지하려면 다시 보내야 함)
  ]
}
```

### Request field:

| Filed | Type | Not Null | Description |
| --- | --- | --- | --- |
| title | varchar(100) |  |  |
| creator | varchar(50) |  | 작성자 |
| description | text |  | 내정가견적비교서 비고 |
| price_compare_resources.major | varchar(30) |  | 대분류 |
| price_compare_resources.minor | varchar(50) |  | 소분류 |
| price_compare_resources.cost_solo_price | int |  | 내정 단가 |
| price_compare_resources.cost_unit | varchar(10) |  | 내정 단위 |
| price_compare_resources.cost_compare | int |  | 내정 수량 |
| price_compare_resources.quotation_solo_price | int |  | 견적 단가 |
| price_compare_resources.quotation_unit | varchar(10) |  | 견적 단위 |
| price_compare_resources.quotation_compare | int |  | 견적 수량 |
| price_compare_resources.upper | int |  | 상승 반영 |
| price_compare_resources.description | text |  | 비고 |

### Error:

| **Code** | **Description** |
| --- | --- |
| 404 Not Found | 수정하려는 `price_compare_id`가 없음 |
| 400 Bad Request | 계산 로직 오류 (예: 견적가가 원가보다 터무니없이 낮음 등 비즈니스 로직) |