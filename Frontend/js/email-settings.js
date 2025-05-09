// Email Settings JavaScript
document.addEventListener('DOMContentLoaded', function() {
  // Email provider selection
  const providerBoxes = document.querySelectorAll('.email-provider');
  const emailForms = document.querySelectorAll('.email-form');
  
  // Hide all email forms except the active one
  function showSelectedProviderForm(providerName) {
    // Hide all forms
    emailForms.forEach(form => {
      form.classList.add('hidden');
    });
    
    // Remove active class from all providers
    providerBoxes.forEach(box => {
      box.classList.remove('active', 'border-indigo-500');
      box.classList.add('border-gray-200');
    });
    
    // Show selected form
    const selectedForm = document.getElementById(`${providerName}-form`);
    if (selectedForm) {
      selectedForm.classList.remove('hidden');
    }
    
    // Add active class to selected provider
    const selectedProvider = document.querySelector(`.email-provider[data-provider="${providerName}"]`);
    if (selectedProvider) {
      selectedProvider.classList.add('active', 'border-indigo-500');
      selectedProvider.classList.remove('border-gray-200');
    }
  }
  
  // Add click event to provider boxes
  providerBoxes.forEach(box => {
    box.addEventListener('click', function() {
      const providerName = this.getAttribute('data-provider');
      showSelectedProviderForm(providerName);
    });
  });
  
  // Connect Gmail button
  const connectGmailBtn = document.getElementById('connect-gmail');
  if (connectGmailBtn) {
      connectGmailBtn.addEventListener('click', function() {
          // Redirect to Gmail OAuth endpoint
          window.location.href = '/api/email/oauth/gmail';
      });
  }
  
  // Connect Outlook button
  const connectOutlookBtn = document.getElementById('connect-outlook');
  if (connectOutlookBtn) {
      connectOutlookBtn.addEventListener('click', function() {
          // Redirect to Outlook OAuth endpoint
          window.location.href = '/api/email/oauth/outlook';
      });
  }
  
  // Connect SMTP button
  const connectSmtpBtn = document.getElementById('connect-smtp');
  if (connectSmtpBtn) {
      connectSmtpBtn.addEventListener('click', function() {
          const email = document.getElementById('smtp-email').value;
          const password = document.getElementById('smtp-password').value;
          const server = document.getElementById('smtp-server').value;
          const port = document.getElementById('smtp-port').value;
          const useSSL = document.getElementById('smtp-ssl').checked;
          
          if (!email || !password || !server || !port) {
              alert('Please fill in all SMTP details');
              return;
          }

          // Show loading state
          connectSmtpBtn.disabled = true;
          connectSmtpBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Connecting...';
          
          // Connect via SMTP
          fetch('/api/email/smtp', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                  email: email,
                  password: password,
                  server: server,
                  port: port,
                  use_ssl: useSSL
              })
          })
          .then(response => response.json())
          .then(data => {
              connectSmtpBtn.disabled = false;
              connectSmtpBtn.innerHTML = '<i class="fas fa-plug mr-2"></i> Connect Email Account';
              
              if (data.success) {
                  showConnectedState(data.email, 'SMTP');
              } else {
                  alert('Error connecting: ' + (data.error || 'Unknown error'));
              }
          })
          .catch(error => {
              connectSmtpBtn.disabled = false;
              connectSmtpBtn.innerHTML = '<i class="fas fa-plug mr-2"></i> Connect Email Account';
              alert('Error: ' + error.message);
          });
      });
  }
  
  // Simulate OAuth connection (in a real app this would be handled by the OAuth provider)
  function simulateOAuthConnection(provider) {
    // Show a loading state
    const button = provider === 'Gmail' ? connectGmailBtn : connectOutlookBtn;
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Connecting...';
    
    // Simulate API delay
    setTimeout(() => {
      button.disabled = false;
      button.innerHTML = originalText;
      
      // Show connected state
      const email = provider === 'Gmail' ? 'you@gmail.com' : 'you@outlook.com';
      showConnectedState(email, provider);
    }, 1500);
  }
  
  // Show connected state
  function showConnectedState(email, provider) {
    // Find the email forms if they exist
    const emailFormsElements = document.querySelectorAll('.email-form');

    // Hide provider selection and forms
    const providerSelection = document.querySelector('.border-b.border-gray-200.pb-5.mb-5');
    if (providerSelection) {
      providerSelection.style.display = 'none';
    }
    
    if (emailFormsElements.length > 0) {
      emailFormsElements.forEach(form => {
        form.classList.add('hidden');
      });
    }
    
    // Update connected email info
    const connectedEmailInfo = document.getElementById('connected-email-info');
    if (connectedEmailInfo) {
      connectedEmailInfo.textContent = 
        `Your ${provider} account (${email}) is now connected. All sequences will be sent from this address.`;
    }
    
    // Show connected state and sequence settings
    const emailConnected = document.getElementById('email-connected');
    if (emailConnected) {
      emailConnected.classList.remove('hidden');
    }
    
    const sequenceSettings = document.getElementById('sequence-settings');
    if (sequenceSettings) {
      sequenceSettings.classList.remove('hidden');
    }
  }
  
  // Disconnect email
  const disconnectBtn = document.getElementById('disconnect-email');
  if (disconnectBtn) {
      disconnectBtn.addEventListener('click', function() {
          // Show confirmation dialog
          if (!confirm('Are you sure you want to disconnect this email account?')) {
              return;
          }
          
          // Reset the UI
          const providerSelection = document.querySelector('.border-b.border-gray-200.pb-5.mb-5');
          if (providerSelection) {
              providerSelection.style.display = 'block';
          }
          
          const emailConnected = document.getElementById('email-connected');
          if (emailConnected) {
              emailConnected.classList.add('hidden');
          }
          
          const sequenceSettings = document.getElementById('sequence-settings');
          if (sequenceSettings) {
              sequenceSettings.classList.add('hidden');
          }
          
          // Show the default provider form
          showSelectedProviderForm('gmail');
          
          // In a real app, this would call the API
          fetch('/api/email/disconnect', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              }
          })
          .catch(error => {
              console.error('Error disconnecting email:', error);
          });
      });
  }
  
  // Toggle follow-up options visibility
  const autoFollowup = document.getElementById('auto-followup');
  const followupOptions = document.getElementById('followup-options');
  
  if (autoFollowup && followupOptions) {
    autoFollowup.addEventListener('change', function() {
      followupOptions.style.display = this.checked ? 'block' : 'none';
    });
    
    // Initialize visibility
    followupOptions.style.display = autoFollowup.checked ? 'block' : 'none';
  }
  
  // Save settings button
  const saveSettingsBtn = document.getElementById('save-settings');
  if (saveSettingsBtn) {
      saveSettingsBtn.addEventListener('click', function() {
          // Gather settings
          const settings = {
              sendTime: document.getElementById('sequence-time').value,
              timezone: document.getElementById('sequence-timezone').value,
              autoFollowup: document.getElementById('auto-followup').checked,
              followupDelay: document.getElementById('followup-delay').value,
              followupCount: document.getElementById('followup-count').value
          };
          
          // Show loading state
          saveSettingsBtn.disabled = true;
          saveSettingsBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Saving...';
          
          // Save settings
          fetch('/api/email/settings', {
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              },
              body: JSON.stringify(settings)
          })
          .then(response => response.json())
          .then(data => {
              saveSettingsBtn.disabled = false;
              saveSettingsBtn.innerHTML = '<i class="fas fa-save mr-2"></i> Save Settings';
              
              if (data.success) {
                  alert('Settings saved successfully!');
              } else {
                  alert('Error saving settings: ' + (data.error || 'Unknown error'));
              }
          })
          .catch(error => {
              saveSettingsBtn.disabled = false;
              saveSettingsBtn.innerHTML = '<i class="fas fa-save mr-2"></i> Save Settings';
              alert('Error: ' + error.message);
          });
      });
  }

  // Initialize the email settings UI
  function initializeEmailSettings() {
      // By default, show the provider selection and hide the connected state
      const providerSelection = document.querySelector('.border-b.border-gray-200.pb-5.mb-5');
      if (providerSelection) {
          providerSelection.style.display = 'block';
      }
      
      const emailConnected = document.getElementById('email-connected');
      if (emailConnected) {
          emailConnected.classList.add('hidden');
      }
      
      const sequenceSettings = document.getElementById('sequence-settings');
      if (sequenceSettings) {
          sequenceSettings.classList.add('hidden');
      }
      
      // Show the default email provider form (Gmail)
      showSelectedProviderForm('gmail');
  }
  
  // Call initialization function when the page loads
  initializeEmailSettings();
});