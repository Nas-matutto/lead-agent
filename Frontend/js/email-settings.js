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
        
        // In a real app, this would send the SMTP details to the server
        // For now, we'll simulate success
        showConnectedState(email, 'SMTP');
      });
    
    
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
      // Hide provider selection and forms
      document.querySelector('.border-b.border-gray-200.pb-5.mb-5').style.display = 'none';
      emailForms.forEach(form => {
        form.classList.add('hidden');
      });
      
      // Update connected email info
      document.getElementById('connected-email-info').textContent = 
        `Your ${provider} account (${email}) is now connected. All sequences will be sent from this address.`;
      
      // Show connected state and sequence settings
      document.getElementById('email-connected').classList.remove('hidden');
      document.getElementById('sequence-settings').classList.remove('hidden');
    }
    
    // Disconnect email
    const disconnectBtn = document.getElementById('disconnect-email');
      if (disconnectBtn) {
    disconnectBtn.addEventListener('click', function() {
        // Show confirmation dialog
        if (!confirm('Are you sure you want to disconnect this email account?')) {
            return;
        }
        
        // Disconnect email
        fetch('/api/email/disconnect', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reset the UI
                document.querySelector('.border-b.border-gray-200.pb-5.mb-5').style.display = 'block';
                document.getElementById('email-connected').classList.add('hidden');
                document.getElementById('sequence-settings').classList.add('hidden');
                
                // Show the default provider form
                showSelectedProviderForm('gmail');
            } else {
                alert('Error disconnecting: ' + (data.error || 'Unknown error'));
            }
        })
        .catch(error => {
            alert('Error: ' + error.message);
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

    // Load existing settings when page loads
document.addEventListener('DOMContentLoaded', function() {
  // Check URL parameters for OAuth callback
  const urlParams = new URLSearchParams(window.location.search);
  const connected = urlParams.get('connected');
  const email = urlParams.get('email');
  const provider = urlParams.get('provider');
  
  if (connected === 'true' && email && provider) {
      // Show connected state
      showConnectedState(email, provider);
      
      // Remove URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
  } else {
      // Load settings from API
      fetch('/api/email/settings')
      .then(response => response.json())
      .then(data => {
          if (data.connected) {
              // Show connected state
              showConnectedState(data.email, data.provider);
              
              // Update settings form
              document.getElementById('sequence-time').value = data.settings.sendTime || '9';
              document.getElementById('sequence-timezone').value = data.settings.timezone || 'America/New_York';
              document.getElementById('auto-followup').checked = data.settings.autoFollowup || false;
              document.getElementById('followup-delay').value = data.settings.followupDelay || '3';
              document.getElementById('followup-count').value = data.settings.followupCount || '1';
              
              // Update followup options visibility
              document.getElementById('followup-options').style.display = 
                  data.settings.autoFollowup ? 'block' : 'none';
          }
      })
      .catch(error => {
          console.error('Error loading settings:', error);
      });
    }
  });