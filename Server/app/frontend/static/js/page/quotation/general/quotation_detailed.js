// quotation_comparison.js
// 견적 비교 ?이지??금액 ?동 계산 기능

document.addEventListener('DOMContentLoaded', function() {

    const table = document.querySelector('.comparison-table tbody');
    if (!table) {
        return;
    }

    const rows = table.querySelectorAll('tr');

    const markupInput = document.getElementById('markup-rate');

    // ?자 ?싱 ?수 (?표 ?거)
    function parseNumber(text) {
        if (!text || text.trim() === '' || text === '-') return 0;
        return parseInt(text.replace(/,/g, '')) || 0;
    }

    // ?자 ?맷???수 (?표 추?)
    function formatNumber(num) {
        if (num === 0) return '';
        return num.toLocaleString('ko-KR');
    }

    // 견적가 업데이트 함수
    function updateEstimates() {
        const rate = parseFloat(markupInput.value) || 0;
        const multiplier = 1 + (rate / 100);
        let isTravelSection = false; // 출장 경비 섹션 여부

        rows.forEach((row) => {
            const cells = row.querySelectorAll('td');
            
            // 카테고리 확인 (rowspan이 있는 첫 번째 셀)
            const hasCategoryCell = cells.length === 11;
            if (hasCategoryCell && cells[0].classList.contains('category-cell')) {
                const categoryName = cells[0].textContent.trim();
                if (categoryName.includes('출장') && categoryName.includes('경비')) {
                    isTravelSection = true;
                } else {
                    isTravelSection = false;
                }
            }

            // 데이터 행 처리
            const offset = hasCategoryCell ? 1 : 0;

            const internalQtyIdx = 1 + offset;
            const internalPriceIdx = 3 + offset;
            
            const estimateQtyIdx = 5 + offset;
            const estimatePriceIdx = 7 + offset;
            const estimateAmountIdx = 8 + offset;

            if (cells.length < 10) return;

            const internalQtyCell = cells[internalQtyIdx];
            const internalPriceCell = cells[internalPriceIdx];
            
            const estimateQtyCell = cells[estimateQtyIdx];
            const estimatePriceCell = cells[estimatePriceIdx];
            const estimateAmountCell = cells[estimateAmountIdx];

            if (internalQtyCell && internalPriceCell && estimatePriceCell && estimateAmountCell) {
                // 견적 단가 셀을 수정 가능하도록 설정
                if (estimatePriceCell.getAttribute('contenteditable') !== 'true') {
                    estimatePriceCell.setAttribute('contenteditable', 'true');
                    estimatePriceCell.style.backgroundColor = '#fffbe6';
                    estimatePriceCell.style.cursor = 'text';

                    estimatePriceCell.addEventListener('input', function() {
                        this.dataset.manual = 'true';
                        
                        const currentPrice = parseNumber(this.textContent);
                        const currentQty = parseNumber(estimateQtyCell.textContent) || parseNumber(internalQtyCell.textContent);
                        
                        if (currentQty > 0) {
                            const currentAmount = currentQty * currentPrice;
                            estimateAmountCell.textContent = formatNumber(currentAmount);
                        }
                        
                        calculateSubtotals();
                    });
                }

                const internalQty = parseNumber(internalQtyCell.textContent);
                const internalPrice = parseNumber(internalPriceCell.textContent);
                const estimateQty = parseNumber(estimateQtyCell.textContent);
                const initialEstimatePrice = parseNumber(estimatePriceCell.textContent);

                // 수량 결정 (견적 수량 우선)
                const finalQty = estimateQty > 0 ? estimateQty : internalQty;

                if (finalQty > 0) {
                    let finalPrice = 0;

                    // 단가 결정 로직
                    if (estimatePriceCell.dataset.manual === 'true') {
                        // 1. 수동 입력 값
                        finalPrice = parseNumber(estimatePriceCell.textContent);
                    } else if (internalPrice > 0) {
                        // 2. 내정가 기반 자동 계산
                        const effectiveMultiplier = isTravelSection ? 1 : multiplier;
                        finalPrice = Math.round(internalPrice * effectiveMultiplier);
                        estimatePriceCell.textContent = formatNumber(finalPrice);
                    } else if (initialEstimatePrice > 0) {
                        // 3. 내정가는 없지만 견적가가 있는 경우 (예: 운송비)
                        finalPrice = initialEstimatePrice;
                    }

                    // 금액 계산 및 업데이트
                    if (finalPrice > 0) {
                        const amount = finalQty * finalPrice;
                        estimateAmountCell.textContent = formatNumber(amount);
                    }

                    // 견적 수량 동기화 (내정가에는 있고 견적가에 없는 경우)
                    if (estimateQtyCell && (!estimateQtyCell.textContent || estimateQtyCell.textContent.trim() === '')) {
                         estimateQtyCell.textContent = internalQtyCell.textContent;
                    }
                }
            }
        });
        
        calculateSubtotals();
    }

    // 초기화 및 이벤트 리스너
    if (markupInput) {
        markupInput.addEventListener('input', updateEstimates);
    }

    // ??을 ?회?면??금액 계산
    rows.forEach((row, index) => {
        const cells = row.querySelectorAll('td');

        // rowspan???는 ?인지 ?인 (? 개수가 11개면 category-cell ?음)
        const hasCategoryCell = cells.length === 11;

        let offset = 0;
        if (hasCategoryCell) {
            offset = 1; // 카테고리 ????으??덱?? 1 ?로 밀?
        }

        // ?정가: 구분, ?량, ?위, ??, 금액
        // 견적가: ?량, ?위, ??, 금액
        const itemIdx = 0 + offset;
        const internalQtyIdx = 1 + offset;
        const internalUnitIdx = 2 + offset;
        const internalPriceIdx = 3 + offset;
        const internalAmountIdx = 4 + offset;

        // 내정가 금액 초기 계산 (한 번만 실행하면 됨)
        if (cells.length >= 10) {
            const internalQty = cells[internalQtyIdx];
            const internalPrice = cells[internalPriceIdx];
            const internalAmount = cells[internalAmountIdx];

             if (internalQty && internalPrice && internalAmount) {
                const qty = parseNumber(internalQty.textContent);
                const price = parseNumber(internalPrice.textContent);

                if (qty > 0 && price > 0) {
                    const amount = qty * price;
                    internalAmount.textContent = formatNumber(amount);
                }
            }
        }
    });

    // 페이지 로드 시 초기 계산 실행
    updateEstimates();

    // ?계/?계 ??계산 (subtotal-row, total-row, final-total-row)
    function calculateSubtotals() {
        let currentCategoryStartIndex = -1;
        let internalSum = 0;
        let estimateSum = 0;
        const subtotalBreakdown = {};

        rows.forEach((row, index) => {
            const cells = row.querySelectorAll('td');
            if (cells.length < 5) return;

            // 카테고리 ?작 감? (category-row)
            if (row.classList.contains('category-row')) {
                currentCategoryStartIndex = index;
                internalSum = 0;
                estimateSum = 0;
            }

            // ?반 ?이????(?량*?? ?는 ??
            if (!row.classList.contains('subtotal-row') &&
                !row.classList.contains('total-row') &&
                !row.classList.contains('final-total-row') &&
                !row.classList.contains('pjt-manager-row') &&
                !row.classList.contains('management-row') &&
                !row.classList.contains('exclude-from-subtotal') &&
                currentCategoryStartIndex >= 0) {

                // rowspan 고려???덱??(? 11개면 category-cell ?음)
                const hasCategoryCell = cells.length === 11;
                const offset = hasCategoryCell ? 1 : 0;

                const internalAmountIdx = 4 + offset;
                const estimateAmountIdx = 8 + offset;

                if (cells[internalAmountIdx]) {
                    const internalAmount = parseNumber(cells[internalAmountIdx].textContent);
                    if (internalAmount > 0) {
                        internalSum += internalAmount;
                    }
                }

                if (cells[estimateAmountIdx]) {
                    const estimateAmount = parseNumber(cells[estimateAmountIdx].textContent);
                    if (estimateAmount > 0) {
                        estimateSum += estimateAmount;
                    }
                }
            }

            // ?계 ??
            if (row.classList.contains('subtotal-row')) {

                let internalSubtotalIdx, estimateSubtotalIdx, differenceIdx;

                // ? 개수가 11개면 ??칸씩 ?로 (PJT Manager??출장 경비 ?계)
                if (cells.length === 11) {
                    internalSubtotalIdx = 5;
                    estimateSubtotalIdx = 9;
                    differenceIdx = 10;
                } else {
                    // ?반 ?계 (10??)
                    internalSubtotalIdx = 4;
                    estimateSubtotalIdx = 8;
                    differenceIdx = 9;
                }

                if (cells[internalSubtotalIdx] && cells[internalSubtotalIdx].classList.contains('subtotal-cell')) {
                    cells[internalSubtotalIdx].textContent = formatNumber(internalSum);
                }
                if (cells[estimateSubtotalIdx] && cells[estimateSubtotalIdx].classList.contains('subtotal-cell')) {
                    cells[estimateSubtotalIdx].textContent = formatNumber(estimateSum);
                }
                if (cells[differenceIdx] && cells[differenceIdx].classList.contains('difference-cell')) {
                    const diff = estimateSum - internalSum;
                    cells[differenceIdx].textContent = formatNumber(diff);
                }
                const subtotalType = row.dataset.subtotalType;
                if (subtotalType) {
                    subtotalBreakdown[subtotalType] = {
                        internal: internalSum,
                        estimate: estimateSum
                    };
                }


                // 리셋
                currentCategoryStartIndex = -1;  // 카테고리 ?덱?도 리셋
                internalSum = 0;
                estimateSum = 0;
            }
        });

        // ?체 ?계 계산 (total-row)
        let totalInternalSum = 0;
        let totalEstimateSum = 0;

        rows.forEach((row) => {
            if (row.classList.contains('subtotal-row')) {
                const cells = row.querySelectorAll('td');
                let internalIdx = 4;
                let estimateIdx = 8;

                // 칸 개수가 11개인 경우 (PJT Manager, 출장비 등) 인덱스 조정
                if (cells.length === 11) {
                    internalIdx = 5;
                    estimateIdx = 9;
                }

                if (cells[internalIdx]) {
                    const val = parseNumber(cells[internalIdx].textContent);
                    totalInternalSum += val;
                }
                if (cells[estimateIdx]) {
                    const val = parseNumber(cells[estimateIdx].textContent);
                    totalEstimateSum += val;
                }
            }
        });

        // total-row 업데이트
        rows.forEach((row) => {
            if (row.classList.contains('total-row')) {
                const cells = row.querySelectorAll('td');
                // cells[0]: Sub Total (colspan=5) -> Covers Category, Item, Int Qty, Int Unit, Int Price
                // cells[1]: Internal Amount Total (Total Cell) -> Aligns with Internal Amount
                // cells[2]: Estimate Qty (Empty)
                // cells[3]: Estimate Unit (Empty)
                // cells[4]: Estimate Price (Empty)
                // cells[5]: Estimate Amount Total (Total Cell) -> Aligns with Estimate Amount
                // cells[6]: Difference (Difference Cell) -> Aligns with Note/Difference

                if (cells.length >= 6) {
                    if (cells[1]) {
                        cells[1].textContent = formatNumber(totalInternalSum);
                    }
                    if (cells[5]) {
                        cells[5].textContent = formatNumber(totalEstimateSum);
                    }
                    if (cells[6]) {
                        cells[6].textContent = formatNumber(totalEstimateSum - totalInternalSum);
                    }
                }
            }
        });

        // final-total-row ?데?트 (관리비 ?함)
        let finalInternalTotal = totalInternalSum;
        let finalEstimateTotal = totalEstimateSum;

        // 관리비 ?산
        rows.forEach((row) => {
            if (row.classList.contains('management-row')) {
                const cells = row.querySelectorAll('td');
                // management-row??rowspan ?음 (? 11??는 10?
                const hasCategoryCell = cells.length === 11;
                const offset = hasCategoryCell ? 1 : 0;
                const estimateIdx = 8 + offset;

                if (cells[estimateIdx]) {
                    const estimateAmount = parseNumber(cells[estimateIdx].textContent);
                    if (estimateAmount > 0) {
                        finalEstimateTotal += estimateAmount;
                    }
                }
            }
        });

        // final-total-row 업데이트
        rows.forEach((row) => {
            if (row.classList.contains('final-total-row')) {
                const cells = row.querySelectorAll('td');
                if (cells.length >= 6) {
                    if (cells[1]) {
                        cells[1].textContent = formatNumber(finalInternalTotal);
                    }
                    if (cells[5]) {
                        cells[5].textContent = formatNumber(finalEstimateTotal);
                    }
                    if (cells[6]) {
                        cells[6].textContent = formatNumber(finalEstimateTotal - finalInternalTotal);
                    }
                }
            }
        });

        // 이익률 계산 및 표시 (markup-row)
        const markupRow = table.querySelector('.markup-row');
        if (markupRow) {
            // Cell 0: Spacer (colspan=9)
            // Cell 1: Margin Value (.margin-cell)
            // Cell 2: Label (.markup-cell)
            
            const spacerCell = markupRow.cells[0];
            const marginCell = markupRow.querySelector('.margin-cell');
            const labelCell = markupRow.querySelector('.markup-cell');

            if (spacerCell) spacerCell.textContent = ''; // Clear spacer

            if (marginCell) {
                marginCell.style.textAlign = 'right';
                marginCell.style.paddingRight = '10px';
                marginCell.style.fontWeight = 'bold';
                marginCell.style.color = '#e74c3c'; // Point color

                if (finalEstimateTotal > 0) {
                    const margin = (1 - (finalInternalTotal / finalEstimateTotal)) * 100;
                    marginCell.textContent = margin.toFixed(0) + ' %';
                } else {
                    marginCell.textContent = '0 %';
                }
            }

            if (labelCell) {
                labelCell.textContent = '이익률';
                labelCell.style.textAlign = 'center';
            }
        }
    }

    // 비고란 수정 가능하도록 설정
    function makeNotesEditable() {
        rows.forEach((row) => {
            // 계산 행 제외
            if (row.classList.contains('subtotal-row') ||
                row.classList.contains('total-row') ||
                row.classList.contains('final-total-row') ||
                row.classList.contains('markup-row')) {
                return;
            }

            const cells = row.querySelectorAll('td');
            if (cells.length > 0) {
                const lastCell = cells[cells.length - 1];
                // 마지막 셀이 비고란인지 확인 (difference-cell 클래스가 없는지 확인)
                if (!lastCell.classList.contains('difference-cell')) {
                    if (lastCell.getAttribute('contenteditable') !== 'true') {
                        lastCell.setAttribute('contenteditable', 'true');
                        // 시각적 피드백 (선택 사항)
                        lastCell.addEventListener('focus', function() {
                            this.style.backgroundColor = '#f0f8ff';
                        });
                        lastCell.addEventListener('blur', function() {
                            this.style.backgroundColor = '';
                        });
                    }
                }
            }
        });

        // 하단 특이사항 영역 수정 가능 설정
        const notesContent = document.querySelector('.notes-content');
        if (notesContent) {
            notesContent.setAttribute('contenteditable', 'true');
            // 스타일 적용 (편집 가능함을 나타냄)
            notesContent.style.backgroundColor = '#fffbe6'; 
            notesContent.style.padding = '10px';
            notesContent.style.border = '1px solid #ddd';
            notesContent.style.borderRadius = '4px';
            notesContent.style.minHeight = '50px'; // 최소 높이 확보
        }
    }

    makeNotesEditable();

    calculateSubtotals();
});