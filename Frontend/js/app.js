// Lead Agent Frontend JavaScript

// API URL - change this to your server URL
const API_URL = 'http://127.0.0.1:8080/api';

document.addEventListener('DOMContentLoaded', function() {
    // Tab switching functionality
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabLinks.forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            
            // Remove active class from all tabs
            tabLinks.forEach(tab => tab.classList.remove('active', 'border-indigo-500', 'text-indigo-600'));
            tabLinks.forEach(tab => tab.classList.add('border-transparent', 'text-gray-500'));
            
            // Add active class to current tab
            e.target.closest('.tab-link').classList.add('active', 'border-indigo-500', 'text-indigo-600');
            e.target.closest('.tab-link').classList.remove('border-transparent', 'text-gray-500');
            
            // Hide all tab contents
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Show current tab content
            const tabName = e.target.closest('.tab-link').getAttribute('data-tab');
            document.getElementById(tabName + '-tab').classList.add('active');
        });
    });
    
    // Product Analysis Form
    const analyzeForm = document.querySelector('#analysis-results');
    const analysisResults = document.querySelector('#analysis-results');
    const analyzeButton = analyzeForm.querySelector('button');
    
    if (analyzeButton) {
        analyzeButton.addEventListener('click', function() {
        const productDescription = analyzeForm.querySelector('textarea').value;
        if (!productDescription) {
            alert('Please enter a product description');
            return;
        }
        
        console.log("Setting up analyze button handler");

document.addEventListener('DOMContentLoaded', function() {
  // Get the elements
  const analyzeButton = document.getElementById('analyze-button');
  console.log("Analyze button:", analyzeButton);
  
  // Add the event listener
  if (analyzeButton) {
    analyzeButton.addEventListener('click', function() {
      console.log("Analyze button clicked");
      
      const productDescTextarea = document.querySelector('#product-tab textarea');
      console.log("Product description element:", productDescTextarea);
      
      const productDescription = productDescTextarea ? productDescTextarea.value : "";
      console.log("Product description:", productDescription);
      
      if (!productDescription) {
        alert('Please enter a product description');
        return;
      }
      
      // Show loading state
      analyzeButton.disabled = true;
      analyzeButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Analyzing...';
      
      try {
        console.log("About to call API");
        
        // Call the API
        fetch(`${API_URL}/analyze-product`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ description: productDescription })
        })
        .then(response => {
          console.log("API Response:", response);
          if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
          }
          return response.json();
        })
        .then(analysis => {
          console.log("Analysis result:", analysis);
          
          // Get the analysis results container
          const analysisResults = document.querySelector('#analysis-results');
          console.log("Analysis results container:", analysisResults);
          
          if (!analysisResults) {
            throw new Error("Could not find analysis results container");
          }
          
          // Hide the product form
          const productForm = document.querySelector('#product-tab .bg-white:first-child');
          productForm.style.display = 'none';
          
          // Update and show analysis results
          updateAnalysisResults(analysis);
          analysisResults.style.display = 'block';
        })
        .catch(error => {
          console.error("Error:", error);
          alert(`Error analyzing product: ${error.message}`);
        })
        .finally(() => {
          // Reset button state
          analyzeButton.disabled = false;
          analyzeButton.innerHTML = '<i class="fas fa-magic mr-2"></i> Analyze Product';
        });
      } catch (error) {
        console.error("Exception:", error);
        alert(`Exception: ${error.message}`);
        
        // Reset button state
        analyzeButton.disabled = false;
        analyzeButton.innerHTML = '<i class="fas fa-magic mr-2"></i> Analyze Product';
      }
    });
  } else {
    console.error("Could not find analyze button");
  }
});

        // Show loading state
        analyzeButton.disabled = true;
        analyzeButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Analyzing...';
        
        // Call the API
        analyzeProduct(productDescription)
            .then(analysis => {
                // Update the UI with analysis results
                updateAnalysisResults(analysis);
                
                // Hide the input form
                analyzeForm.style.display = 'none';
                
                // Show the results section
                analysisResults.classList.add('fade-in');
                analysisResults.style.display = 'block';
            })
            .catch(error => {
                alert('Error analyzing product: ' + error.message);
            })
            .finally(() => {
                // Reset button state
                analyzeButton.disabled = false;
                analyzeButton.innerHTML = '<i class="fas fa-magic mr-2"></i> Analyze Product';
            });
    });
}
    
    // Generate Leads Button
        const generateLeadsButton = analysisResults.querySelector('button');
        if (generateLeadsButton) {
            generateLeadsButton.addEventListener('click', function() {
        // Switch to leads tab
        document.querySelector('.tab-link[data-tab="leads"]').click();
        
        // Get the target audience from the analysis
        const targetAudienceTitle = analysisResults.querySelector('.bg-gray-50 h4').textContent;
        const targetAudienceDesc = analysisResults.querySelector('.bg-gray-50 p').textContent;
        
        const targetAudience = {
            title: targetAudienceTitle,
            description: targetAudienceDesc
        };
        
        // Show loading state for leads
        const leadsTab = document.querySelector('#leads-tab');
        const leadsTable = leadsTab.querySelector('table tbody');
        leadsTable.innerHTML = '<tr><td colspan="7" class="py-4 text-center">Loading leads...</td></tr>';
        
        // Find leads
        findLeads(targetAudience, 10)
            .then(leads => {
                updateLeadsTable(leads);
            })
            .catch(error => {
                alert('Error finding leads: ' + error.message);
            });
        });
        }
    
        // Back button for analysis results
    const backButton = document.querySelector('#analysis-results button:has(.fa-arrow-left)');
    if (backButton) {
    backButton.addEventListener('click', function() {
        // Hide analysis results
        document.querySelector('#analysis-results').style.display = 'none';
        
        // Show product form
        document.querySelector('#product-tab .bg-white:first-child').style.display = 'block';
    });
}


    // Create Sequence Button
    const createSequenceButton = document.querySelector('#leads-tab button:has(.fa-envelope)');
    if (createSequenceButton) {
    createSequenceButton.addEventListener('click', function() {
        console.log('Create Sequence button clicked');
        
        // Get selected leads
        const selectedLeads = getSelectedLeads();
        
        if (selectedLeads.length === 0) {
            alert('Please select at least one lead first');
            return;
        }
        
        console.log('Selected leads:', selectedLeads);
        
        // Switch to sequence tab
        document.querySelector('.tab-link[data-tab="sequence"]').click();
        
        // Update selected leads display
        updateSelectedLeadsDisplay(selectedLeads);
    });
}

// Helper function to get selected leads
function getSelectedLeads() {
    const checkboxes = document.querySelectorAll('#leads-tab table input[type="checkbox"]:checked');
    const selectedLeads = [];
    
    checkboxes.forEach(checkbox => {
        const row = checkbox.closest('tr');
        selectedLeads.push({
            id: checkbox.getAttribute('data-id'),
            name: row.cells[1].textContent,
            company: row.cells[2].textContent,
            title: row.cells[3].textContent,
            email: row.cells[4].textContent,
            insight: row.cells[5].textContent
        });
    });
    
    return selectedLeads;
}

// Helper function to update selected leads display
function updateSelectedLeadsDisplay(leads) {
    const selectedLeadsContainer = document.querySelector('#sequence-tab .flex.flex-wrap.gap-2');
    selectedLeadsContainer.innerHTML = '';
    
    leads.forEach(lead => {
        selectedLeadsContainer.innerHTML += `
            <div class="bg-indigo-50 px-3 py-2 rounded-md flex items-center" data-id="${lead.id}">
                <span>${lead.name} (${lead.company})</span>
                <button class="ml-2 text-gray-500 hover:text-gray-700">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    });
    
    // Update count
    const countLabel = document.querySelector('#sequence-tab label.block.text-gray-700.font-medium.mb-2');
    countLabel.textContent = `Selected Leads (${leads.length})`;
    
    // Add event listeners to remove buttons
    selectedLeadsContainer.querySelectorAll('button').forEach(button => {
        button.addEventListener('click', function() {
            button.parentElement.remove();
            
            // Update count
            const remainingLeads = selectedLeadsContainer.querySelectorAll('div[data-id]').length;
            countLabel.textContent = `Selected Leads (${remainingLeads})`;
        });
    });
}
    
    // Preview Button
    const previewButton = document.querySelector('#sequence-tab button:has(.fa-eye)');
    if (previewButton) {
        previewButton.addEventListener('click', function() {
            // Get template and selected leads
            const template = document.querySelector('#sequence-tab textarea').value;
            const subject = document.querySelector('#sequence-tab input[type="text"]').value;
            const selectedLeads = getSelectedLeads();
            
            if (!template || !subject || selectedLeads.length === 0) {
                alert('Please fill in the template, subject, and select at least one lead');
                return;
            }
            
            // Show loading state
            previewButton.disabled = true;
            previewButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Generating...';
            
            // Personalize messages
            personalizeMessages(selectedLeads, template)
                .then(messages => {
                    // Show the preview section
                    const previewSection = document.querySelector('#sequence-tab .bg-white:nth-child(2)');
                    previewSection.classList.add('fade-in');
                    previewSection.style.display = 'block';
                    
                    // Update preview content
                    updatePreviewContent(messages, subject, selectedLeads);
                    
                    // Scroll to preview
                    setTimeout(() => {
                        previewSection.scrollIntoView({ behavior: 'smooth' });
                    }, 100);
                })
                .catch(error => {
                    alert('Error personalizing messages: ' + error.message);
                })
                .finally(() => {
                    // Reset button state
                    previewButton.disabled = false;
                    previewButton.innerHTML = '<i class="fas fa-eye mr-1"></i> Preview';
                });
        });
    }
    
    // Send Sequences Button
    const sendButton = document.querySelector('#sequence-tab .bg-white:nth-child(2) button');
    if (sendButton) {
        sendButton.addEventListener('click', function() {
            alert('In a real application, this would send the messages to the selected leads.');
        });
    }
    
    // Save Settings Button
    const saveSettingsButton = document.querySelector('#settings-tab button');
    if (saveSettingsButton) {
        saveSettingsButton.addEventListener('click', function() {
            alert('Settings saved successfully!');
        });
    }
});
    

    // Add select all functionality
    const selectAllCheckbox = document.getElementById('select-all-leads');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
    const allCheckboxes = document.querySelectorAll('#leads-tab table input[type="checkbox"]');
        allCheckboxes.forEach(checkbox => {
      checkbox.checked = selectAllCheckbox.checked;
    });
    
    // Update count in the footer
    const countDisplay = document.querySelector('#leads-tab .text-gray-600');
    const totalLeads = allCheckboxes.length - 1; // Subtract 1 for the header checkbox
    const selectedLeads = selectAllCheckbox.checked ? totalLeads : 0;
    countDisplay.textContent = `Selected ${selectedLeads} of ${totalLeads} leads`;
  });
}
    // Helper Functions

    function updateAnalysisResults(analysis) {
        console.log("Updating analysis results with:", analysis);
        const resultsSection = document.querySelector('#analysis-results');
  
  if (!resultsSection) {
    console.error("Results section not found");
    return;
  }
  
  try {
    // Update target audience
    const targetAudienceSection = resultsSection.querySelector('div:nth-child(2) > div:first-child .bg-gray-50');
    if (targetAudienceSection) {
      targetAudienceSection.querySelector('h4').textContent = analysis.target_audience.title;
      targetAudienceSection.querySelector('p').textContent = analysis.target_audience.description;
    }
    
    // Update fields
    const fields = resultsSection.querySelectorAll('.bg-indigo-50');
    if (fields.length >= 4) {
      fields[0].querySelector('p').textContent = analysis.target_audience.industry || "Technology";
      fields[1].querySelector('p').textContent = analysis.target_audience.company_size || "50-500 employees";
      fields[2].querySelector('p').textContent = analysis.target_audience.role || "Decision Maker";
      fields[3].querySelector('p').textContent = analysis.target_audience.pain_point || "Workflow Inefficiency";
    }
    
    // Update markets
    const marketsSection = resultsSection.querySelector('div:nth-child(2) > div:nth-child(2) .bg-gray-50 ul');
    if (marketsSection) {
      marketsSection.innerHTML = '';
      
      analysis.markets.slice(0, 3).forEach((market, index) => {
        marketsSection.innerHTML += `
          <li class="flex">
            <span class="bg-indigo-100 text-indigo-800 rounded-full h-6 w-6 flex items-center justify-center font-semibold mr-2">${index + 1}</span>
            <div>
              <h4 class="font-bold">${market.name}</h4>
              <p class="text-gray-600 text-sm">${market.description}</p>
            </div>
          </li>
        `;
      });
    }
    
    // Update ideal locations (formerly keywords)
    const locationsSection = resultsSection.querySelector('div.mt-6 > div.flex.flex-col');
    if (locationsSection) {
      locationsSection.innerHTML = '';
      
      (analysis.ideal_locations || []).slice(0, 10).forEach((location, index) => {
        locationsSection.innerHTML += `
          <div class="bg-gray-100 p-2 rounded-md">
            <span class="font-medium">${location.country_region}</span>
            <p class="text-sm text-gray-600">${location.reason}</p>
          </div>
        `;
      });
    }
  } catch (error) {
    console.error("Error updating analysis results:", error);
  }
}

function updateLeadsTable(leads) {
    const leadsTable = document.querySelector('#leads-tab table tbody');
    leadsTable.innerHTML = '';
    
    leads.forEach(lead => {
        leadsTable.innerHTML += `
            <tr class="border-b border-gray-200 hover:bg-gray-50" data-id="${lead.id}">
                <td class="py-3 px-4 text-left">
                    <input type="checkbox" class="form-checkbox h-4 w-4 text-indigo-600" data-id="${lead.id}">
                </td>
                <td class="py-3 px-4 text-left">${lead.name || 'N/A'}</td>
                <td class="py-3 px-4 text-left">${lead.company || 'N/A'}</td>
                <td class="py-3 px-4 text-left">${lead.title || 'N/A'}</td>
                <td class="py-3 px-4 text-left">${lead.email || 'N/A'}</td>
                <td class="py-3 px-4 text-left">${lead.insight || 'No insight available'}</td>
                <td class="py-3 px-4 text-center">
                    <button class="text-blue-500 hover:text-blue-700 mr-2">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="text-green-500 hover:text-green-700">
                        <i class="fas fa-envelope"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    // Update count
    const countDisplay = document.querySelector('#leads-tab .text-gray-600');
    countDisplay.textContent = `Showing ${leads.length} of ${leads.length} leads`;
}

function getSelectedLeads() {
    const checkboxes = document.querySelectorAll('#leads-tab table input[type="checkbox"]:checked');
    const selectedLeads = [];
    
    checkboxes.forEach(checkbox => {
        const leadId = checkbox.getAttribute('data-id');
        const row = checkbox.closest('tr');
        
        selectedLeads.push({
            id: leadId,
            name: row.cells[1].textContent,
            company: row.cells[2].textContent,
            title: row.cells[3].textContent,
            email: row.cells[4].textContent,
            insight: row.cells[5].textContent
        });
    });
    
    return selectedLeads;
}

function updateSelectedLeadsDisplay(leads) {
    const selectedLeadsContainer = document.querySelector('#sequence-tab .flex.flex-wrap.gap-2');
    selectedLeadsContainer.innerHTML = '';
    
    leads.forEach(lead => {
        selectedLeadsContainer.innerHTML += `
            <div class="bg-indigo-50 px-3 py-2 rounded-md flex items-center">
                <span>${lead.name} (${lead.company})</span>
                <button class="ml-2 text-gray-500 hover:text-gray-700" data-id="${lead.id}">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    });
    
    // Update count
    const countLabel = document.querySelector('#sequence-tab label.block.text-gray-700.font-medium.mb-2');
    countLabel.textContent = `Selected Leads (${leads.length})`;
}

function updatePreviewContent(messages, subject, leads) {
    const previewContainer = document.querySelector('#sequence-tab .bg-white:nth-child(2)');
    const messageContainer = previewContainer.querySelector('.border.border-gray-200');
    
    // Get the first lead and its personalized message
    const firstLead = leads[0];
    const firstLeadId = firstLead.id;
    const message = messages[firstLeadId];
    
    // Update header
    messageContainer.querySelector('p.font-medium').textContent = `To: ${firstLead.name} (${firstLead.email})`;
    messageContainer.querySelector('p.text-gray-500').textContent = `Subject: ${subject}`;
    
    // Update message content
    const messageContent = messageContainer.querySelector('.bg-gray-50');
    messageContent.innerHTML = message.replace(/\n/g, '<br>');
    
    // Update button text
    previewContainer.querySelector('button').textContent = `Send All (${leads.length})`;
}

// API Functions

async function analyzeProduct(description) {
    try {
        const response = await fetch(`${API_URL}/analyze-product`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ description })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to analyze product');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error analyzing product:', error);
        throw error;
    }
}

async function findLeads(targetAudience, count = 10) {
    try {
        const response = await fetch(`${API_URL}/find-leads`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ target_audience: targetAudience, count })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to find leads');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error finding leads:', error);
        throw error;
    }
}

async function personalizeMessages(leads, template) {
    try {
        const response = await fetch(`${API_URL}/personalize-messages`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ leads, template })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to personalize messages');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error personalizing messages:', error);
        throw error;
    }
}

async function saveLeads(leads, format = 'csv') {
    try {
        const response = await fetch(`${API_URL}/save-leads`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ leads, format })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to save leads');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error saving leads:', error);
        throw error;
    }
}

async function getSettings() {
    try {
        const response = await fetch(`${API_URL}/settings`);
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to get settings');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error getting settings:', error);
        throw error;
    }
}

async function updateSettings(settings) {
    try {
        const response = await fetch(`${API_URL}/settings`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(settings)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to update settings');
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error updating settings:', error);
        throw error;
    }
}

// Add functionality to lead action buttons
function setupLeadActionButtons() {
    // View lead buttons
    const viewButtons = document.querySelectorAll('.view-lead-btn');
    viewButtons.forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        const row = this.closest('tr');
        const leadId = row.getAttribute('data-id');
        viewLeadDetails(leadId);
      });
    });
    
    // Email lead buttons
    const emailButtons = document.querySelectorAll('.email-lead-btn');
    emailButtons.forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        const row = this.closest('tr');
        const leadId = row.getAttribute('data-id');
        
        // Set the checkbox to checked
        const checkbox = row.querySelector('input[type="checkbox"]');
        checkbox.checked = true;
        
        // Switch to sequence tab and pre-select this lead
        document.querySelector('.tab-link[data-tab="sequence"]').click();
        
        // Get the lead data and update selected leads display
        const lead = {
          id: leadId,
          name: row.cells[1].textContent,
          company: row.cells[2].textContent,
          title: row.cells[3].textContent,
          email: row.cells[4].textContent,
          insight: row.cells[5].textContent
        };
        
        updateSelectedLeadsDisplay([lead]);
      });
    });
  }
  
  // View lead details
  function viewLeadDetails(leadId) {
    // Find the lead data
    const row = document.querySelector(`tr[data-id="${leadId}"]`);
    if (!row) return;
    
    const lead = {
      id: leadId,
      name: row.cells[1].textContent,
      company: row.cells[2].textContent,
      title: row.cells[3].textContent,
      email: row.cells[4].textContent,
      insight: row.cells[5].textContent
    };
    
    // Create modal to display lead details
    const modal = document.createElement('div');
    modal.className = 'fixed inset-0 flex items-center justify-center z-50';
    modal.innerHTML = `
      <div class="fixed inset-0 bg-black opacity-50"></div>
      <div class="bg-white rounded-lg p-8 max-w-lg w-full relative z-10">
        <button class="absolute top-4 right-4 text-gray-500 hover:text-gray-800">
          <i class="fas fa-times"></i>
        </button>
        <h2 class="text-2xl font-bold mb-4">${lead.name}</h2>
        <div class="grid grid-cols-1 gap-4">
          <div class="border-b pb-2">
            <label class="font-medium text-gray-700">Company:</label>
            <p>${lead.company}</p>
          </div>
          <div class="border-b pb-2">
            <label class="font-medium text-gray-700">Title:</label>
            <p>${lead.title}</p>
          </div>
          <div class="border-b pb-2">
            <label class="font-medium text-gray-700">Email:</label>
            <p>${lead.email}</p>
          </div>
          <div class="border-b pb-2">
            <label class="font-medium text-gray-700">Insight:</label>
            <p>${lead.insight}</p>
          </div>
        </div>
        <div class="mt-6 flex justify-end">
          <button class="bg-indigo-600 text-white px-4 py-2 rounded-md font-medium hover:bg-indigo-700 transition">
            <i class="fas fa-envelope mr-2"></i> Send Message
          </button>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    
    // Add close button functionality
    const closeButton = modal.querySelector('button');
    closeButton.addEventListener('click', function() {
      document.body.removeChild(modal);
    });
    
    // Add send message button functionality
    const sendButton = modal.querySelector('.bg-indigo-600');
    sendButton.addEventListener('click', function() {
      document.body.removeChild(modal);
      
      // Switch to sequence tab and pre-select this lead
      document.querySelector('.tab-link[data-tab="sequence"]').click();
      
      // Update selected leads display
      updateSelectedLeadsDisplay([lead]);
    });
  }
  
  // Call this function after loading the leads
  document.addEventListener('DOMContentLoaded', function() {
    // Other initialization code...
    
    // Check if we're on the leads tab
    const leadsTab = document.getElementById('leads-tab');
    if (leadsTab) {
      setupLeadActionButtons();
    }
  });

