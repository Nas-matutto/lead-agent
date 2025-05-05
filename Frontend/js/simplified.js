// API URL - Change this to match your server
const API_URL = 'http://127.0.0.1:8080/api';

// Simple helper for logging
function log(message, data) {
  console.log(`[Lead Agent] ${message}`, data || '');
}

// Wait for page to fully load
document.addEventListener('DOMContentLoaded', function() {
  log('Page loaded, setting up handlers');
  
  // Setup tab switching
const tabLinks = document.querySelectorAll('.tab-link');
const tabContents = document.querySelectorAll('.tab-content');

tabLinks.forEach(link => {
  link.addEventListener('click', function(e) {
    e.preventDefault();
    
    // Remove active class from all tabs
    tabLinks.forEach(tab => tab.classList.remove('active', 'border-indigo-500', 'text-indigo-600'));
    tabLinks.forEach(tab => tab.classList.add('border-transparent', 'text-gray-500'));
    
    // Add active class to current tab
    this.classList.add('active', 'border-indigo-500', 'text-indigo-600');
    this.classList.remove('border-transparent', 'text-gray-500');
    
    // Hide all tab contents
    tabContents.forEach(content => {
      content.style.display = 'none';
    });
    
    // Show current tab content
    const tabName = this.getAttribute('data-tab');
    const tabContent = document.getElementById(tabName + '-tab');
    if (tabContent) {
      tabContent.style.display = 'block';
    }
  });
});

// Make sure only the product tab is visible initially
document.addEventListener('DOMContentLoaded', function() {
  // Hide all tabs except product tab
  tabContents.forEach(content => {
    if (content.id !== 'product-tab') {
      content.style.display = 'none';
    }
  });
});
  
  // 1. Product Analysis Button
  const analyzeButton = document.getElementById('analyze-button');
  
  if (analyzeButton) {
    log('Found analyze button, adding click handler');
    
    analyzeButton.addEventListener('click', function() {
      log('Analyze button clicked');
      
      const description = document.getElementById('product-description').value;
      
      if (!description) {
        alert('Please enter a product description');
        return;
      }
      
      // Show loading state
      analyzeButton.disabled = true;
      analyzeButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Analyzing...';
      
      // Log the API call
      log('Calling API with data', { description });
      
      // Make the API call
      fetch(`${API_URL}/analyze-product`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ description })
      })
      .then(response => {
        log('API response status', response.status);
        
        if (!response.ok) {
          throw new Error(`API returned status ${response.status}`);
        }
        
        return response.json();
      })
      .then(data => {
        log('API returned data', data);
        
        // Hide product form
        document.getElementById('product-form').style.display = 'none';
        
        // Show analysis results
        const resultsSection = document.getElementById('analysis-results');
        if (resultsSection) {
          // Update the analysis results
          updateAnalysisResults(resultsSection, data);
          resultsSection.style.display = 'block';
        } else {
          throw new Error('Analysis results section not found');
        }
      })
      .catch(error => {
        log('Error occurred', error);
        alert(`Error: ${error.message}`);
      })
      .finally(() => {
        // Reset button state
        analyzeButton.disabled = false;
        analyzeButton.innerHTML = '<i class="fas fa-magic mr-2"></i> Analyze Product';
      });
    });
  } else {
    log('ERROR: Analyze button not found', null);
  }
  
  // Back button
  const backButton = document.querySelector('#analysis-results button[data-action="back"]');
  if (backButton) {
    backButton.addEventListener('click', function() {
      // Hide analysis results
      document.getElementById('analysis-results').style.display = 'none';
      
      // Show product form
      document.getElementById('product-form').style.display = 'block';
    });
  }
  
  const generateLeadsButton = document.querySelector('#analysis-results button[data-action="generate"]');
if (generateLeadsButton) {
  generateLeadsButton.addEventListener('click', function() {
    // Hide product tab content
    document.getElementById('product-tab').style.display = 'none';
    
    // Show leads tab content
    document.getElementById('leads-tab').style.display = 'block';
    
    // Update the active tab indicator
    document.querySelectorAll('.tab-link').forEach(tab => {
      tab.classList.remove('active', 'border-indigo-500', 'text-indigo-600');
      tab.classList.add('border-transparent', 'text-gray-500');
    });
    
    const leadsTabLink = document.querySelector('.tab-link[data-tab="leads"]');
    leadsTabLink.classList.add('active', 'border-indigo-500', 'text-indigo-600');
    leadsTabLink.classList.remove('border-transparent', 'text-gray-500');
  });
}
});

// Function to update analysis results
function updateAnalysisResults(container, data) {
  try {
    // Target Audience Title & Description
    const audienceHeading = container.querySelector('.bg-gray-50 h4');
    const audienceDesc = container.querySelector('.bg-gray-50 p');
    
    if (audienceHeading && audienceDesc) {
      audienceHeading.textContent = data.target_audience.title || 'Target Audience';
      audienceDesc.textContent = data.target_audience.description || 'No description available';
    }
    
    // Info Fields
    const fields = container.querySelectorAll('.bg-indigo-50 p');
    if (fields.length >= 4) {
      fields[0].textContent = data.target_audience.industry || 'N/A';
      fields[1].textContent = data.target_audience.company_size || 'N/A';
      fields[2].textContent = data.target_audience.role || 'N/A';
      fields[3].textContent = data.target_audience.pain_point || 'Workflow Inefficiency';
    }
    
    // Markets
    const marketsList = container.querySelector('ul');
    if (marketsList && data.markets && data.markets.length > 0) {
      marketsList.innerHTML = '';
      
      data.markets.slice(0, 3).forEach((market, index) => {
        marketsList.innerHTML += `
          <li class="flex">
            <span class="bg-indigo-100 text-indigo-800 rounded-full h-6 w-6 flex items-center justify-center font-semibold mr-2">${index + 1}</span>
            <div>
              <h4 class="font-bold">${market.name || 'Market'}</h4>
              <p class="text-gray-600 text-sm">${market.description || 'No description'}</p>
            </div>
          </li>
        `;
      });
    }
    
    // Locations
    const locationsContainer = container.querySelector('div.mt-6 > div.flex.flex-col');
    if (locationsContainer && data.ideal_locations && data.ideal_locations.length > 0) {
      locationsContainer.innerHTML = '';
      
      data.ideal_locations.slice(0, 10).forEach(location => {
        locationsContainer.innerHTML += `
          <div class="bg-gray-100 p-2 rounded-md">
            <span class="font-medium">${location.country_region || 'Location'}</span>
            <p class="text-sm text-gray-600">${location.reason || 'No reason provided'}</p>
          </div>
        `;
      });
    }
  } catch (error) {
    console.error('Error updating analysis results:', error);
  }
}