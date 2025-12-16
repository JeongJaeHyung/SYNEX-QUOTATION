document.addEventListener('DOMContentLoaded', function() {
    const table = document.querySelector('.quotation-cover-page table tbody');
    if (!table) return;

    const rows = table.querySelectorAll('tr');

    let sectionTotal = 0;
    let grandTotal = 0;

    rows.forEach(row => {
        // Skip special rows
        if (row.classList.contains('section-title') || 
            row.classList.contains('summary-row') || 
            row.classList.contains('notes-row') ||
            row.classList.contains('section-subtitle')) {
            
            // If it's a summary row, we might need to update the total if we corrected amounts
            if (row.classList.contains('summary-row')) {
                const totalCell = row.querySelector('.total-amount');
                if (totalCell) {
                    totalCell.textContent = formatNumber(sectionTotal);
                }
                grandTotal += sectionTotal;
                sectionTotal = 0; // Reset for next section
            }
            return;
        }

        const cells = row.querySelectorAll('td');
        
        // Standard data row usually has 8 cells
        if (cells.length === 8) {
            const qtyCell = cells[3];
            const priceCell = cells[5];
            const amountCell = cells[6];
            const noteCell = cells[7];

            // 1. Make ONLY Note editable
            makeEditable(noteCell);
            
            // 2. Ensure Amount = Price * Qty (Correction on load)
            const qty = parseFloat(qtyCell.textContent.replace(/,/g, '')) || 0;
            const price = parseNumber(priceCell.textContent);
            
            // Calculate and update Amount
            const amount = Math.floor(qty * price);
            amountCell.textContent = formatNumber(amount);

            // Add to section total
            sectionTotal += amount;
        }
    });

    // Update Footer Total
    const footerTotal = document.querySelector('.quotation-cover-page tfoot .total-amount');
    if (footerTotal) {
        footerTotal.textContent = formatNumber(grandTotal);
    }

    // Make the bottom notes content editable and style it properly
    const notesContentTd = table.querySelector('td.notes-content');
    if (notesContentTd) {
        makeEditable(notesContentTd);
        notesContentTd.style.height = '150px'; 
        notesContentTd.style.verticalAlign = 'top'; 
        notesContentTd.style.padding = '10px';
    }
});

function makeEditable(element) {
    if (!element) return;
    element.setAttribute('contenteditable', 'true');
    element.style.backgroundColor = '#fffbe6'; // Light yellow to indicate editability
    
    // Optional: Visual feedback on focus
    element.addEventListener('focus', function() {
        this.style.backgroundColor = '#f0f8ff'; // Light blue
    });
    element.addEventListener('blur', function() {
        this.style.backgroundColor = '#fffbe6';
    });
}

function parseNumber(str) {
    if (!str) return 0;
    return parseInt(str.replace(/,/g, '')) || 0;
}

function formatNumber(num) {
    return num.toLocaleString('ko-KR');
}
