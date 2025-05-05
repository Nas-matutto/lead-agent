// Sequences JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Get create sequence button
    const createSequenceBtn = document.querySelector('#leads-tab button:has(.fa-envelope)');
    
    if (createSequenceBtn) {
        createSequenceBtn.addEventListener('click', function() {
            // Get selected leads
            const selectedLeads = getSelectedLeads();
            
            if (selectedLeads.length === 0) {
                alert('Please select at least one lead first');
                return;
            }
            
            // Check if email is connected
            checkEmailConnection()
                .then(connected => {
                    if (connected) {
                        // Switch to sequence tab
                        document.querySelector('.tab-link[data-tab="sequence"]').click();
                        
                        // Update selected leads display
                        updateSelectedLeadsDisplay(selectedLeads);
                    } else {
                        // Email not connected, prompt user to connect
                        if (confirm('You need to connect an email account to create sequences. Go to Settings?')) {
                            // Switch to settings tab
                            document.querySelector('.tab-link[data-tab="settings"]').click();
                        }
                    }
                })
                .catch(error => {
                    console.error('Error checking email connection:', error);
                    alert('Error: Could not check email connection status');
                });
        });
    }
    
    // Send sequence button
    const sendSequenceBtn = document.querySelector('#sequence-tab button:has(.fa-paper-plane)');
    
    if (sendSequenceBtn) {
        sendSequenceBtn.addEventListener('click', function() {
            // Get sequence details
            const subject = document.querySelector('#sequence-tab input[type="text"]').value;
            const template = document.querySelector('#sequence-tab textarea').value;
            const selectedLeads = getSelectedLeadsFromDisplay();
            
            if (!subject || !template || selectedLeads.length === 0) {
                alert('Please fill in the subject, template, and select at least one lead');
                return;
            }
            
            // Check if email is connected
            checkEmailConnection()
                .then(connected => {
                    if (connected) {
                        // Show loading state
                        sendSequenceBtn.disabled = true;
                        sendSequenceBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Creating Sequence...';
                        
                        // Get leads data
                        const leadsData = [];
                        selectedLeads.forEach(id => {
                            const lead = findLeadById(id);
                            if (lead) {
                                leadsData.push(lead);
                            }
                        });
                        
                        // Create sequence
                        fetch('/api/email/sequence', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                name: `Sequence - ${new Date().toLocaleDateString()}`,
                                subject: subject,
                                template: template,
                                leads: leadsData
                            })
                        })
                        .then(response => response.json())
                        .then(data => {
                            sendSequenceBtn.disabled = false;
                            sendSequenceBtn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i> Send Sequences';
                            
                            if (data.success) {
                                alert('Sequence created successfully! Emails will be sent according to your schedule settings.');
                                
                                // Clear form
                                document.querySelector('#sequence-tab input[type="text"]').value = '';
                                document.querySelector('#sequence-tab textarea').value = '';
                                document.querySelector('#sequence-tab .flex.flex-wrap.gap-2').innerHTML = '';
                                
                                // Update count label
                                document.querySelector('#sequence-tab label.block.text-gray-700.font-medium.mb-2').textContent = 'Selected Leads (0)';
                                
                                // Hide preview section
                                const previewSection = document.querySelector('#sequence-tab .bg-white:nth-child(2)');
                                if (previewSection) {
                                    previewSection.style.display = 'none';
                                }
                            } else {
                                alert('Error creating sequence: ' + (data.error || 'Unknown error'));
                            }
                        })
                        .catch(error => {
                            sendSequenceBtn.disabled = false;
                            sendSequenceBtn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i> Send Sequences';
                            alert('Error: ' + error.message);
                        });
                    } else {
                        // Email not connected, prompt user to connect
                        if (confirm('You need to connect an email account to send sequences. Go to Settings?')) {
                            // Switch to settings tab
                            document.querySelector('.tab-link[data-tab="settings"]').click();
                        }
                    }
                })
                .catch(error => {
                    console.error('Error checking email connection:', error);
                    alert('Error: Could not check email connection status');
                });
        });
    }
    
    // Helper function to check email connection
    function checkEmailConnection() {
        return fetch('/api/email/status')
            .then(response => response.json())
            .then(data => {
                return data.connected;
            });
    }
    
    // Helper function to find lead by ID
    function findLeadById(id) {
        const row = document.querySelector(`#leads-tab tr[data-id="${id}"]`);
        if (row) {
            return {
                id: id,
                name: row.cells[1].textContent,
                company: row.cells[2].textContent,
                title: row.cells[3].textContent,
                email: row.cells[4].textContent,
                insight: row.cells[5].textContent
            };
        }
        return null;
    }
});