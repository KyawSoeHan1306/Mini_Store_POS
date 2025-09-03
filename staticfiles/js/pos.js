// static/js/pos.js
document.addEventListener('DOMContentLoaded', function() {
    // Elements
    var productSearch = document.getElementById('product-search');
    var searchButton = document.getElementById('search-button');
    var categoryButtons = document.querySelectorAll('.category-btn');
    var productItems = document.querySelectorAll('.product-item');
    var cartItems = document.getElementById('cart-items');
    var clearCartBtn = document.getElementById('clear-cart');
    var checkoutBtn = document.getElementById('checkout-btn');
    var modal = document.getElementById('checkout-modal');
    var closeModal = document.querySelector('.close');
    var cancelSale = document.getElementById('cancel-sale');
    var completeSale = document.getElementById('complete-sale');
    var subtotalEl = document.getElementById('subtotal');
    var discountEl = document.getElementById('discount');
    var discountTypeEl = document.getElementById('discount-type');
    var taxEl = document.getElementById('tax');
    var totalEl = document.getElementById('total');
    var modalTotalItems = document.getElementById('modal-total-items');
    var modalSubtotal = document.getElementById('modal-subtotal');
    var modalDiscount = document.getElementById('modal-discount');
    var modalTax = document.getElementById('modal-tax');
    var modalTotal = document.getElementById('modal-total');
    var customerName = document.getElementById('customer-name');
    var customerPhone = document.getElementById('customer-phone');
    var paymentMethod = document.getElementById('payment-method');
    var cashPaymentDetails = document.getElementById('cash-payment-details');
    var amountPaid = document.getElementById('amount-paid');
    var changeAmount = document.getElementById('change-amount');
    var loadingOverlay = document.getElementById('loading-overlay');

    // Cart state
    var cart = [];
    var subtotal = 0;
    var discount = 0;
    var tax = 0;
    var total = 0;

    // Filter products by category
    for (var i = 0; i < categoryButtons.length; i++) {
        categoryButtons[i].addEventListener('click', function() {
            var categoryId = this.getAttribute('data-category');
            
            // Update active button
            for (var j = 0; j < categoryButtons.length; j++) {
                categoryButtons[j].classList.remove('active');
            }
            this.classList.add('active');
            
            // Filter products
            for (var k = 0; k < productItems.length; k++) {
                if (categoryId === 'all' || productItems[k].getAttribute('data-category') === categoryId) {
                    productItems[k].style.display = 'block';
                } else {
                    productItems[k].style.display = 'none';
                }
            }
        });
    }

    // Search products
    searchButton.addEventListener('click', searchProducts);
    productSearch.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchProducts();
        }
    });

    function searchProducts() {
        var query = productSearch.value.toLowerCase().trim();
        
        if (query === '') {
            for (var i = 0; i < productItems.length; i++) {
                productItems[i].style.display = 'block';
            }
            return;
        }
        
        for (var j = 0; j < productItems.length; j++) {
            var name = productItems[j].getAttribute('data-name').toLowerCase();
            if (name.includes(query)) {
                productItems[j].style.display = 'block';
            } else {
                productItems[j].style.display = 'none';
            }
        }
    }

    // Add product to cart
    for (var i = 0; i < productItems.length; i++) {
        productItems[i].addEventListener('click', function() {
            var productId = this.getAttribute('data-product-id');
            var name = this.getAttribute('data-name');
            var price = parseFloat(this.getAttribute('data-price'));
            var stock = parseInt(this.getAttribute('data-stock'));
            
            addToCart(productId, name, price, stock);
        });
    }

    // Add to cart function
    function addToCart(productId, name, price, stock) {
        var existingItem = null;
        for (var i = 0; i < cart.length; i++) {
            if (cart[i].productId === productId) {
                existingItem = cart[i];
                break;
            }
        }
        
        if (existingItem) {
            if (existingItem.quantity < stock) {
                existingItem.quantity += 1;
                updateCartUI();
            } else {
                alert('Cannot add more of this product. Stock limit reached.');
            }
        } else {
            cart.push({
                productId: productId,
                name: name,
                price: price,
                quantity: 1,
                stock: stock
            });
            updateCartUI();
        }
    }

    // Update cart UI
    function updateCartUI() {
        // Clear cart display
        cartItems.innerHTML = '';
        
        if (cart.length === 0) {
            cartItems.innerHTML = '<div class="empty-cart-message">Cart is empty</div>';
            subtotal = 0;
        } else {
            subtotal = 0;
            
            // Add items to cart
            for (var i = 0; i < cart.length; i++) {
                var item = cart[i];
                var itemTotal = item.price * item.quantity;
                subtotal += itemTotal;
                
                var cartItem = document.createElement('div');
                cartItem.className = 'cart-item';
                cartItem.innerHTML = 
                    '<div class="cart-item-info">' +
                        '<div class="cart-item-title">' + item.name + '</div>' +
                        '<div class="cart-item-price">$' + item.price.toFixed(2) + ' × ' + item.quantity + ' = $' + itemTotal.toFixed(2) + '</div>' +
                    '</div>' +
                    '<div class="cart-item-controls">' +
                        '<div class="quantity-control">' +
                            '<button class="quantity-btn minus" data-id="' + item.productId + '">-</button>' +
                            '<input type="number" class="quantity-input" value="' + item.quantity + '" min="1" max="' + item.stock + '" data-id="' + item.productId + '">' +
                            '<button class="quantity-btn plus" data-id="' + item.productId + '">+</button>' +
                        '</div>' +
                        '<div class="remove-item" data-id="' + item.productId + '"><i class="fas fa-trash"></i></div>' +
                    '</div>';
                
                cartItems.appendChild(cartItem);
                
                // Add event listeners to controls (using closure to capture the correct item)
                (function(itemId, maxStock) {
                    var minusBtn = cartItem.querySelector('.minus');
                    var plusBtn = cartItem.querySelector('.plus');
                    var quantityInput = cartItem.querySelector('.quantity-input');
                    var removeBtn = cartItem.querySelector('.remove-item');
                    
                    minusBtn.addEventListener('click', function() {
                        var currentItem;
                        for (var j = 0; j < cart.length; j++) {
                            if (cart[j].productId === itemId) {
                                currentItem = cart[j];
                                break;
                            }
                        }
                        updateItemQuantity(itemId, currentItem.quantity - 1);
                    });
                    
                    plusBtn.addEventListener('click', function() {
                        var currentItem;
                        for (var j = 0; j < cart.length; j++) {
                            if (cart[j].productId === itemId) {
                                currentItem = cart[j];
                                break;
                            }
                        }
                        
                        if (currentItem.quantity < maxStock) {
                            updateItemQuantity(itemId, currentItem.quantity + 1);
                        } else {
                            alert('Cannot add more of this product. Stock limit reached.');
                        }
                    });
                    
                    quantityInput.addEventListener('change', function() {
                        var newQuantity = parseInt(this.value);
                        if (isNaN(newQuantity) || newQuantity < 1) {
                            newQuantity = 1;
                        } else if (newQuantity > maxStock) {
                            newQuantity = maxStock;
                            alert('Quantity adjusted to maximum available stock.');
                        }
                        this.value = newQuantity;
                        updateItemQuantity(itemId, newQuantity);
                    });
                    
                    removeBtn.addEventListener('click', function() {
                        removeItemFromCart(itemId);
                    });
                })(item.productId, item.stock);
            }
        }
        
        // Update summary
        updateSummary();
    }

    // Update item quantity
    function updateItemQuantity(productId, newQuantity) {
        for (var i = 0; i < cart.length; i++) {
            if (cart[i].productId === productId) {
                if (newQuantity < 1) {
                    removeItemFromCart(productId);
                } else {
                    cart[i].quantity = newQuantity;
                    updateCartUI();
                }
                break;
            }
        }
    }

    // Remove item from cart
    function removeItemFromCart(productId) {
        var newCart = [];
        for (var i = 0; i < cart.length; i++) {
            if (cart[i].productId !== productId) {
                newCart.push(cart[i]);
            }
        }
        cart = newCart;
        updateCartUI();
    }

    // Clear cart
    clearCartBtn.addEventListener('click', function() {
        if (cart.length > 0 && confirm('Are you sure you want to clear the cart?')) {
            cart = [];
            updateCartUI();
        }
    });

    // Update summary calculations
    function updateSummary() {
        // Calculate discount
        var discountValue = parseFloat(discountEl.value) || 0;
        var discountType = discountTypeEl.value;
        
        if (discountType === 'percentage') {
            discount = (subtotal * discountValue) / 100;
        } else {
            discount = discountValue;
        }
        
        // Calculate tax (0% for now, can be adjusted)
        tax = 0;
        
        // Calculate total
        total = subtotal - discount + tax;
        
        // Update display
        subtotalEl.textContent = '$' + subtotal.toFixed(2);
        taxEl.textContent = '$' + tax.toFixed(2);
        totalEl.textContent = '$' + total.toFixed(2);
    }

    // Discount and tax change events
    discountEl.addEventListener('input', updateSummary);
    discountTypeEl.addEventListener('change', updateSummary);

    // Show checkout modal
    checkoutBtn.addEventListener('click', function() {
        if (cart.length === 0) {
            alert('Please add items to cart before checkout.');
            return;
        }
        
        // Calculate total items
        var totalItems = 0;
        for (var i = 0; i < cart.length; i++) {
            totalItems += cart[i].quantity;
        }
        
        // Update modal details
        modalTotalItems.textContent = totalItems;
        modalSubtotal.textContent = '$' + subtotal.toFixed(2);
        modalDiscount.textContent = '$' + discount.toFixed(2);
        modalTax.textContent = '$' + tax.toFixed(2);
        modalTotal.textContent = '$' + total.toFixed(2);
        
        // Reset fields
        customerName.value = '';
        customerPhone.value = '';
        paymentMethod.value = 'cash';
        amountPaid.value = '';
        changeAmount.value = '';
        
        // Show/hide payment details
        togglePaymentDetails();
        
        // Show modal
        modal.style.display = 'block';
    });

    // Close modal
    closeModal.addEventListener('click', function() {
        modal.style.display = 'none';
    });
    
    cancelSale.addEventListener('click', function() {
        modal.style.display = 'none';
    });

    // Handle payment method change
    paymentMethod.addEventListener('change', togglePaymentDetails);
    
    function togglePaymentDetails() {
        if (paymentMethod.value === 'cash') {
            cashPaymentDetails.style.display = 'block';
        } else {
            cashPaymentDetails.style.display = 'none';
        }
    }

    // Calculate change
    amountPaid.addEventListener('input', function() {
        var paid = parseFloat(this.value) || 0;
        var change = paid - total;
        
        if (change >= 0) {
            changeAmount.value = '$' + change.toFixed(2);
        } else {
            changeAmount.value = 'Insufficient amount';
        }
    });

    // Complete sale
    completeSale.addEventListener('click', function() {
        if (cart.length === 0) {
            alert('Cart is empty. Cannot complete sale.');
            return;
        }
        
        if (paymentMethod.value === 'cash') {
            var paid = parseFloat(amountPaid.value) || 0;
            if (paid < total) {
                alert('Insufficient payment amount.');
                return;
            }
        }
        
        // Show loading overlay
        loadingOverlay.style.display = 'flex';
        
        // Prepare data for API
        var saleData = {
            items: [],
            customer_name: customerName.value.trim(),
            customer_phone: customerPhone.value.trim(),
            payment_method: paymentMethod.value,
            discount_amount: discount
        };
        
        // Add items to sale data
        for (var i = 0; i < cart.length; i++) {
            saleData.items.push({
                product_id: cart[i].productId,
                quantity: cart[i].quantity
            });
        }
        
        // Call API to process sale
        fetch('/api/process-sale/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(saleData)
        })
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            loadingOverlay.style.display = 'none';
            
            if (data.success) {
                // Reset cart
                cart = [];
                updateCartUI();
                
                // Close modal
                modal.style.display = 'none';
                
                // Show success message
                alert('Sale completed successfully!\nInvoice #: ' + data.invoice_number + '\nAmount: $' + data.final_amount);
                
                // Redirect to receipt
                window.open('/receipt/' + data.sale_id + '/', '_blank');
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(function(error) {
            loadingOverlay.style.display = 'none';
            alert('An error occurred while processing the sale. Please try again.');
            console.error('Error:', error);
        });
    });

    // Get CSRF token from cookies
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Close modal when clicking outside
    window.addEventListener('click', function(event) {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Initialize
    updateCartUI();
});