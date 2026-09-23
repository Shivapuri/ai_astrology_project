/**
 * Astra UI Drag & Resize Primitives
 * 
 * Reusable pointer-based dragging and resizing helpers for modal cards,
 * floating windows, and inspection overlays.
 */

function makeDraggable(cardElement, handleElement, options = {}) {
    if (!cardElement || !handleElement) return null;

    let isDragging = false;
    let startX = 0, startY = 0;
    let origLeft = 0, origTop = 0;

    const ignoreSelector = options.ignoreSelector || 'button, select, input, a, .floating-nav-pill, .close-btn, .btn-pill';
    const minLeft = options.minLeft !== undefined ? options.minLeft : 10;
    const minTop = options.minTop !== undefined ? options.minTop : 10;

    function onPointerDown(e) {
        if (e.button !== undefined && e.button !== 0) return;
        if (e.target.closest(ignoreSelector)) return;

        isDragging = true;
        const clientX = e.clientX !== undefined ? e.clientX : (e.touches && e.touches[0].clientX);
        const clientY = e.clientY !== undefined ? e.clientY : (e.touches && e.touches[0].clientY);
        startX = clientX;
        startY = clientY;

        const rect = cardElement.getBoundingClientRect();
        origLeft = rect.left;
        origTop = rect.top;

        cardElement.style.left = origLeft + 'px';
        cardElement.style.top = origTop + 'px';
        handleElement.style.cursor = 'grabbing';

        document.addEventListener('mousemove', onPointerMove);
        document.addEventListener('mouseup', onPointerUp);
        document.addEventListener('touchmove', onPointerMove, { passive: false });
        document.addEventListener('touchend', onPointerUp);
    }

    function onPointerMove(e) {
        if (!isDragging) return;
        if (e.cancelable && e.type === 'touchmove') e.preventDefault();

        const clientX = e.clientX !== undefined ? e.clientX : (e.touches && e.touches[0].clientX);
        const clientY = e.clientY !== undefined ? e.clientY : (e.touches && e.touches[0].clientY);

        const dx = clientX - startX;
        const dy = clientY - startY;

        let newLeft = origLeft + dx;
        let newTop = origTop + dy;

        const maxLeft = window.innerWidth - (options.boundaryMarginRight || 120);
        const maxTop = window.innerHeight - (options.boundaryMarginBottom || 50);
        newLeft = Math.max(minLeft, Math.min(maxLeft, newLeft));
        newTop = Math.max(minTop, Math.min(maxTop, newTop));

        cardElement.style.left = newLeft + 'px';
        cardElement.style.top = newTop + 'px';

        if (typeof options.onDrag === 'function') {
            options.onDrag(newLeft, newTop);
        }
    }

    function onPointerUp() {
        if (!isDragging) return;
        isDragging = false;
        handleElement.style.cursor = 'grab';
        document.removeEventListener('mousemove', onPointerMove);
        document.removeEventListener('mouseup', onPointerUp);
        document.removeEventListener('touchmove', onPointerMove);
        document.removeEventListener('touchend', onPointerUp);

        if (typeof options.onDragEnd === 'function') {
            options.onDragEnd();
        }
    }

    handleElement.addEventListener('mousedown', onPointerDown);
    handleElement.addEventListener('touchstart', onPointerDown, { passive: true });

    return {
        destroy() {
            handleElement.removeEventListener('mousedown', onPointerDown);
            handleElement.removeEventListener('touchstart', onPointerDown);
        }
    };
}

function makeResizable(cardElement, gripElement, options = {}) {
    if (!cardElement || !gripElement) return null;

    let isResizing = false;
    let startX = 0, startY = 0;
    let origWidth = 0, origHeight = 0;

    const minWidth = options.minWidth || 360;
    const minHeight = options.minHeight || 220;

    function onResizeDown(e) {
        if (e.button !== undefined && e.button !== 0) return;
        isResizing = true;
        const clientX = e.clientX !== undefined ? e.clientX : (e.touches && e.touches[0].clientX);
        const clientY = e.clientY !== undefined ? e.clientY : (e.touches && e.touches[0].clientY);
        startX = clientX;
        startY = clientY;

        origWidth = cardElement.offsetWidth;
        origHeight = cardElement.offsetHeight;

        document.addEventListener('mousemove', onResizeMove);
        document.addEventListener('mouseup', onResizeUp);
        document.addEventListener('touchmove', onResizeMove, { passive: false });
        document.addEventListener('touchend', onResizeUp);
        e.preventDefault();
        e.stopPropagation();
    }

    function onResizeMove(e) {
        if (!isResizing) return;
        if (e.cancelable && e.type === 'touchmove') e.preventDefault();

        const clientX = e.clientX !== undefined ? e.clientX : (e.touches && e.touches[0].clientX);
        const clientY = e.clientY !== undefined ? e.clientY : (e.touches && e.touches[0].clientY);

        const dx = clientX - startX;
        const dy = clientY - startY;

        const maxWidth = window.innerWidth - 20;
        const maxHeight = window.innerHeight - 20;

        const newWidth = Math.max(minWidth, Math.min(maxWidth, origWidth + dx));
        const newHeight = Math.max(minHeight, Math.min(maxHeight, origHeight + dy));

        cardElement.style.width = newWidth + 'px';
        cardElement.style.height = newHeight + 'px';

        if (typeof options.onResize === 'function') {
            options.onResize(newWidth, newHeight);
        }
    }

    function onResizeUp() {
        if (!isResizing) return;
        isResizing = false;
        document.removeEventListener('mousemove', onResizeMove);
        document.removeEventListener('mouseup', onResizeUp);
        document.removeEventListener('touchmove', onResizeMove);
        document.removeEventListener('touchend', onResizeUp);

        if (typeof options.onResizeEnd === 'function') {
            options.onResizeEnd();
        }
    }

    gripElement.addEventListener('mousedown', onResizeDown);
    gripElement.addEventListener('touchstart', onResizeDown, { passive: false });

    return {
        destroy() {
            gripElement.removeEventListener('mousedown', onResizeDown);
            gripElement.removeEventListener('touchstart', onResizeDown);
        }
    };
}

// Global initialization helpers for existing modals / floating windows
function initFloatingWindowDrag() {
    const card = document.getElementById('widgetMaximizeCard');
    const header = document.getElementById('widgetMaximizeHeader');
    if (!card || !header) return;

    makeDraggable(card, header);

    header.addEventListener('dblclick', (e) => {
        if (e.target.closest('button, select, input, a, .floating-nav-pill')) return;
        if (typeof window.toggleFloatingCollapse === 'function') {
            window.toggleFloatingCollapse();
        }
    });
}

function initFloatingWindowResize() {
    const card = document.getElementById('widgetMaximizeCard');
    const grip = document.getElementById('floatingCornerGrip');
    if (!card || !grip) return;

    makeResizable(card, grip, { minWidth: 360, minHeight: 220 });
}

function initMaximizeChartDrag() {
    const card = document.getElementById('maximizeChartCard');
    const header = document.getElementById('maximizeChartHeader');
    if (!card || !header) return;

    makeDraggable(card, header);
}

function initMaximizeChartResize() {
    const card = document.getElementById('maximizeChartCard');
    const grip = document.getElementById('maximizeCornerGrip');
    if (!card || !grip) return;

    makeResizable(card, grip, { minWidth: 360, minHeight: 360 });
}

// Attach to window
if (typeof window !== 'undefined') {
    window.makeDraggable = makeDraggable;
    window.makeResizable = makeResizable;
    window.initFloatingWindowDrag = initFloatingWindowDrag;
    window.initFloatingWindowResize = initFloatingWindowResize;
    window.initMaximizeChartDrag = initMaximizeChartDrag;
    window.initMaximizeChartResize = initMaximizeChartResize;
}
