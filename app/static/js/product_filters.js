// Store the original product list when the page loads
  const originalProducts = Array.from(document.querySelectorAll('.product-card-container'));

  // Function to apply all filters and sorting
  function applyFilters() {
    const priceFilter = document.getElementById('price-filter').value;
    const expiryFilter = document.getElementById('expiry-filter').value;
    const locationFilter = document.getElementById('location-filter').value;

    // Start with a copy of the original list
    let filteredProducts = [...originalProducts];

    // Apply filters
    filteredProducts = filteredProducts.filter(card => {
      const price = parseFloat(card.getAttribute('data-price'));
      const expiry = new Date(card.getAttribute('data-expiry'));
      const location = card.getAttribute('data-location');

      let showCard = true;

      // Expiry filter logic
      if (expiryFilter === 'soon' && expiry.getTime() > Date.now()) {
        showCard = false;
      }
      if (expiryFilter === 'later' && expiry.getTime() < Date.now()) {
        showCard = false;
      }

      // Location filter logic
      if (locationFilter !== 'all' && location !== locationFilter) {
        showCard = false;
      }

      return showCard;
    });

    // Sort by price if applicable
    if (priceFilter === 'low-to-high') {
      filteredProducts.sort((a, b) => {
        const priceA = parseFloat(a.getAttribute('data-price'));
        const priceB = parseFloat(b.getAttribute('data-price'));
        return priceA - priceB; // Ascending order
      });
    } else if (priceFilter === 'high-to-low') {
      filteredProducts.sort((a, b) => {
        const priceA = parseFloat(a.getAttribute('data-price'));
        const priceB = parseFloat(b.getAttribute('data-price'));
        return priceB - priceA; // Descending order
      });
    }

    // Clear the current product list and append the filtered and sorted products
    const productList = document.getElementById('product-list');
    productList.innerHTML = ''; // Clear existing products

    filteredProducts.forEach(card => {
      productList.appendChild(card); // Append the filtered and sorted cards
    });
  }