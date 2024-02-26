const searchInput = document.querySelector('.search-input');
const searchDropdown = document.querySelector('.search-dropdown');



function fetchSearchResults(searchTerm) {
  // Fetch search results from your Flask API
  fetch(`/search?q=${searchTerm}`)
    .then(response => response.json())
    .then(posts => {
      const results = posts.map(post => post.content);
      updateDropdown(results);
    })
    .catch(error => console.error('Error fetching search results:', error));
}


  // Function to update dropdown with filtered results
  function updateDropdown(results) {
    const dropdownContent = results.map(result =>
      `<div class="search-dropdown-item">${truncateText(result)}</div>`
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
    fetchSearchResults(value);
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



function truncateText(text, maxLength = 30) {
  if (text.length > maxLength) {
    return text.substring(0, maxLength - 3) + '...';
  }
  return text;
}