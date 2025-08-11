// API URL - Change this to match your server
const API_URL = '/api';

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
        if (content) {
          content.style.display = 'none';
        }
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
  tabContents.forEach(content => {
    if (content && content.id !== 'product-tab') {
      content.style.display = 'none';
    }
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
        const productForm = document.getElementById('product-form');
        if (productForm) {
          productForm.style.display = 'none';
        }
        
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
      const resultsSection = document.getElementById('analysis-results');
      if (resultsSection) {
        resultsSection.style.display = 'none';
      }
      
      // Show product form
      const productForm = document.getElementById('product-form');
      if (productForm) {
        productForm.style.display = 'block';
      }
    });
  }
  
  // 2. Generate Leads Button
  const generateLeadsButton = document.querySelector('#analysis-results button[data-action="generate"]');
  if (generateLeadsButton) {
    generateLeadsButton.addEventListener('click', function() {
      log('Generate Leads button clicked');
      
      // Get the target audience from the analysis results
      const targetAudienceHeading = document.querySelector('#analysis-results .bg-gray-50 h4');
      const targetAudienceDesc = document.querySelector('#analysis-results .bg-gray-50 p');
      
      if (!targetAudienceHeading || !targetAudienceDesc) {
        alert('Could not find target audience data');
        return;
      }
      
      const targetAudience = {
        title: targetAudienceHeading.textContent,
        description: targetAudienceDesc.textContent
      };
      
      log('Target audience:', targetAudience);
      
      // Show loading state
      generateLeadsButton.disabled = true;
      generateLeadsButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Generating...';
      
      // Call the API to find leads
      fetch(`${API_URL}/find-leads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ target_audience: targetAudience, count: 10 })
      })
      .then(response => {
        log('API response status:', response.status);
        if (!response.ok) {
          throw new Error(`API returned status ${response.status}`);
        }
        return response.json();
      })
      .then(leads => {
        log('Received leads:', leads);

        if (!Array.isArray(leads)) {
            console.error("API returned non-array response:", leads);
            // Convert to array if possible
            if (leads && typeof leads === 'object') {
              leads = [leads];
            } else {
              leads = [];
            }
          }
        
        try {
          // Try to update tab display safely
          const tabs = document.querySelectorAll('.tab-content');
          if (tabs.length > 0) {
            // Hide all tabs
            tabs.forEach(tab => {
              if (tab) tab.style.display = 'none';
            });
          }
          
          // Try to show leads tab
          const leadsTab = document.getElementById('leads-tab');
          if (leadsTab) {
            leadsTab.style.display = 'block';
          } else {
            console.error("Could not find leads-tab element");
          }
          
          // Update active tab indicator
          const tabLinks = document.querySelectorAll('.tab-link');
          if (tabLinks.length > 0) {
            // Remove active class from all tabs
            tabLinks.forEach(tab => {
              if (tab) {
                tab.classList.remove('active', 'border-indigo-500', 'text-indigo-600');
                tab.classList.add('border-transparent', 'text-gray-500');
              }
            });
            
            // Add active class to leads tab
            const leadsTabLink = document.querySelector('.tab-link[data-tab="leads"]');
            if (leadsTabLink) {
              leadsTabLink.classList.add('active', 'border-indigo-500', 'text-indigo-600');
              leadsTabLink.classList.remove('border-transparent', 'text-gray-500');
            } else {
              console.error("Could not find leads tab link");
            }
          }
          
          // Update the leads table with the results
          updateLeadsTable(leads);
        } catch (error) {
          console.error("Error updating UI:", error);
          alert("Error updating UI. Please check the console for details.");
        }
      })
      .catch(error => {
        console.error("Error finding leads:", error);
        alert(`Error finding leads: ${error.message}`);
      })
      .finally(() => {
        // Reset button state
        generateLeadsButton.disabled = false;
        generateLeadsButton.innerHTML = '<i class="fas fa-users mr-2"></i> Generate Leads';
      });
    });
  }
  
  // Set up select all checkbox functionality
  setupSelectAllCheckbox();
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
      
      // Filter to ensure only industry-related markets
      const filteredMarkets = data.markets.filter(market => 
        market.name && 
        !market.name.includes(',') && // Filter out location-like entries with commas
        !/^\d+%/.test(market.name) && // Filter out percentage-based entries
        !/^[A-Z]{2}$/.test(market.name) // Filter out 2-letter country codes
      );
      
      filteredMarkets.slice(0, 3).forEach((market, index) => {
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
    
    // Locations or Keywords
    const locationsContainer = container.querySelector('div.mt-6 > div.flex.flex-col');
    if (locationsContainer) {
      locationsContainer.innerHTML = '';
      
      // Add a better title for the locations section
      const locationSectionTitle = container.querySelector('div.mt-6 > h3');
      if (locationSectionTitle) {
        locationSectionTitle.innerHTML = '<i class="fas fa-globe-americas text-indigo-500 mr-2"></i> Top Target Regions';
      }
      
      // Change the layout to a more visual grid with flags/icons
      locationsContainer.className = 'grid grid-cols-1 md:grid-cols-3 gap-3 mt-3';
      
      if (data.ideal_locations && data.ideal_locations.length > 0) {
        // Limit to 5 locations
        data.ideal_locations.slice(0, 5).forEach(location => {
          // Get region code for flag (simple implementation)
          const regionCode = getRegionCode(location.country_region);
          
          locationsContainer.innerHTML += `
            <div class="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg p-3 shadow-sm border border-indigo-100 transform transition-transform hover:scale-105">
              <div class="flex items-center mb-2">
                <span class="text-xl mr-2">${getRegionEmoji(regionCode)}</span>
                <span class="font-semibold text-indigo-800">${location.country_region || 'Location'}</span>
              </div>
              <p class="text-sm text-gray-600">${location.reason || 'No reason provided'}</p>
            </div>
          `;
        });
      } else if (data.search_keywords && data.search_keywords.length > 0) {
        // If no locations, show keywords instead (limited to 5)
        data.search_keywords.slice(0, 5).forEach(keyword => {
          locationsContainer.innerHTML += `
            <div class="bg-gradient-to-r from-indigo-50 to-blue-50 rounded-lg p-3 shadow-sm border border-indigo-100">
              <div class="flex items-center">
                <span class="text-indigo-500 mr-2"><i class="fas fa-tag"></i></span>
                <span class="font-semibold text-indigo-800">${keyword}</span>
              </div>
            </div>
          `;
        });
      }
    }
  } catch (error) {
    console.error('Error updating analysis results:', error);
  }
}

// Function to update leads table
function updateLeadsTable(leads) {
  const leadsTable = document.querySelector('#leads-tab table tbody');
  if (!leadsTable) {
    console.error("Could not find leads table");
    return;
  }
  
  // Clear existing rows
  leadsTable.innerHTML = '';
  
  // Check if leads is empty or not an array
  if (!leads || !Array.isArray(leads) || leads.length === 0) {
    leadsTable.innerHTML = `
      <tr>
        <td colspan="7" class="py-4 text-center text-gray-500">No leads found</td>
      </tr>
    `;
    return;
  }
  
  // Add new rows
  leads.forEach(lead => {
    leadsTable.innerHTML += `
      <tr class="border-b border-gray-200 hover:bg-gray-50" data-id="${lead.id || ''}">
        <td class="py-3 px-4 text-left">
          <input type="checkbox" class="form-checkbox h-4 w-4 text-indigo-600" data-id="${lead.id || ''}">
        </td>
        <td class="py-3 px-4 text-left">${lead.name || 'N/A'}</td>
        <td class="py-3 px-4 text-left">${lead.company || 'N/A'}</td>
        <td class="py-3 px-4 text-left">${lead.title || 'N/A'}</td>
        <td class="py-3 px-4 text-left">${lead.email || 'N/A'}</td>
        <td class="py-3 px-4 text-left">${lead.insight || 'No insight available'}</td>
        <td class="py-3 px-4 text-center">
          <button class="view-lead-btn text-blue-500 hover:text-blue-700 mr-2 p-1 rounded hover:bg-blue-100 transition">
            <i class="fas fa-eye"></i>
          </button>
          <button class="email-lead-btn text-green-500 hover:text-green-700 p-1 rounded hover:bg-green-100 transition">
            <i class="fas fa-envelope"></i>
          </button>
        </td>
      </tr>
    `;
  });
  
  // Update count
  const countDisplay = document.querySelector('#leads-tab .text-gray-600');
  if (countDisplay) {
    countDisplay.textContent = `Showing ${leads.length} of ${leads.length} leads`;
  }
  
  // Set up lead action buttons
  setupLeadActionButtons();
}

// Set up select all checkbox functionality
function setupSelectAllCheckbox() {
  const selectAllCheckbox = document.getElementById('select-all-leads');
  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', function() {
      const allCheckboxes = document.querySelectorAll('#leads-tab table tbody input[type="checkbox"]');
      allCheckboxes.forEach(checkbox => {
        checkbox.checked = selectAllCheckbox.checked;
      });
    });
  }
}

// Set up lead action buttons
function setupLeadActionButtons() {
  // View lead buttons
  const viewButtons = document.querySelectorAll('.view-lead-btn');
  viewButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const row = this.closest('tr');
      const leadId = row.getAttribute('data-id');
      
      // Get lead data from the row
      const lead = {
        id: leadId,
        name: row.cells[1].textContent,
        company: row.cells[2].textContent,
        title: row.cells[3].textContent,
        email: row.cells[4].textContent,
        insight: row.cells[5].textContent
      };
      
      // Show lead details in an alert (for now)
      alert(`Lead Details:\nName: ${lead.name}\nCompany: ${lead.company}\nTitle: ${lead.title}\nEmail: ${lead.email}\nInsight: ${lead.insight}`);
    });
  });
  
  // Email lead buttons
  const emailButtons = document.querySelectorAll('.email-lead-btn');
  emailButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      const row = this.closest('tr');
      
      // Check the checkbox for this row
      const checkbox = row.querySelector('input[type="checkbox"]');
      if (checkbox) {
        checkbox.checked = true;
      }
      
      // Switch to sequence tab
      const sequenceTabLink = document.querySelector('.tab-link[data-tab="sequence"]');
      if (sequenceTabLink) {
        sequenceTabLink.click();
      }
    });
  });
}

// Helper function to get region emoji
function getRegionEmoji(region) {
  // Simple mapping of common regions to emojis
  const regionMap = {
    'United States': '🇺🇸',
    'USA': '🇺🇸',
    'North America': '🌎',
    'Canada': '🇨🇦',
    'Europe': '🇪🇺',
    'UK': '🇬🇧',
    'United Kingdom': '🇬🇧',
    'Australia': '🇦🇺',
    'Asia': '🌏',
    'China': '🇨🇳',
    'Japan': '🇯🇵',
    'India': '🇮🇳',
    'Brazil': '🇧🇷',
    'South America': '🌎',
    'Africa': '🌍',
    'Middle East': '🌍',
    'Global': '🌐'
  };
  
  // Default globe emoji if no match
  return regionMap[region] || '🌐';
}

// Helper function to get region code
function getRegionCode(region) {
  // For simplicity - we'll just return the region name
  return region;
}