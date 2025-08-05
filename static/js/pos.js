// POS JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize POS system
    initializePOS();
});

function initializePOS() {
    // Add event listeners
    document.addEventListener('keydown', handleKeyboardShortcuts);

    // Auto-focus search input
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        searchInput.focus();
    }
}

function handleKeyboardShortcuts(event) {
    // F1 - Focus search
    if (event.key === 'F1') {
        event.preventDefault();
        document.querySelector('input[name="search"]').focus();
    }

    // F2 - Clear cart
    if (event.key === 'F2') {
        event.preventDefault();
        clearCart();
    }

    // F3 - Process sale
    if (event.key === 'F3') {
        event.preventDefault();
        if (!document.getElementById('checkout-btn').disabled) {
            processCheckout();
        }
    }

    // ESC - Clear search
    if (event.key === 'Escape') {
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) {
            searchInput.value = '';
            searchInput.focus();
        }
    }
}

function showNotification(message, type = 'success') {
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

function formatCurrency(amount) {
    return `₹${parseFloat(amount).toFixed(2)}`;
}

function playSound(type) {
    // Add beep sounds for better UX
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();

    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);

    if (type === 'success') {
        oscillator.frequency.value = 800;
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.3);
    } else if (type === 'error') {
        oscillator.frequency.value = 400;
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    }

    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.3);
}