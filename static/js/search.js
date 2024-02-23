const searchInput = document.querySelector('.search-input');
const searchDropdown = document.querySelector('.search-dropdown');

  // Dummy data for demonstration
  const dummyData = [
    "Apple",
    "Banana",
    "Orange",
    "Pineapple",
    "Grapes",
    "Watermelon",
    "Mango",
    "Peach"
  ];
function filterData(value) {
    return dummyData.filter(item =>
      item.toLowerCase().includes(value.toLowerCase())
    );
  }

  // Function to update dropdown with filtered results
  function updateDropdown(results) {
    const dropdownContent = results.map(result =>
      `<div class="search-dropdown-item">${result}</div>`
    ).join('');
    searchDropdown.innerHTML = dropdownContent;
    searchDropdown.style.display = results.length ? '' : 'none';
  }

  // Event listener for input keyup
  searchInput.addEventListener('keyup', function() {
    const value = this.value.trim();
    if (value === '') {
      searchDropdown.style.display = 'none';
      return;
    }
    const filteredData = filterData(value);
    updateDropdown(filteredData);
  });

  // Event listener to handle clicks on dropdown items
  searchDropdown.addEventListener('click', function(e) {
    if (e.target.classList.contains('search-dropdown-item')) {
      searchInput.value = e.target.textContent;
      searchDropdown.style.display = 'none';
    }
  });

  // Close dropdown when clicking outside
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.search-container')) {
      searchDropdown.style.display = 'none';
    }
  });