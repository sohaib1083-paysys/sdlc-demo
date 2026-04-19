// Get the sdlc-phases div
const sdlcPhasesDiv = document.getElementById('sdlc-phases');

// Fetch the SDLC phases data
fetch('/sdlc_phases')
    .then(response => response.json())
    .then(data => {
        // Create a phase div for each phase
        data.forEach(phase => {
            const phaseDiv = document.createElement('div');
            phaseDiv.classList.add('phase');
            phaseDiv.innerHTML = `
                <span class="handle">&#9776;</span>
                <span>${phase.name}</span>
                <p>${phase.description}</p>
            `;
            sdlcPhasesDiv.appendChild(phaseDiv);
        });

        // Add drag and drop functionality
        const dragula = require('dragula');
        dragula([sdlcPhasesDiv], {
            moves: (el, container, handle) => handle.classList.contains('handle'),
            accepts: (el, target, source, sibling) => true,
        });

        // Update the infographic when the phases are reordered
        sdlcPhasesDiv.addEventListener('dragend', (e) => {
            const phases = sdlcPhasesDiv.children;
            const reorderedPhases = Array.from(phases).map((phase) => phase.textContent);
            updateInfographic(reorderedPhases);
        });
    })
    .catch(error => console.error('Error fetching SDLC phases:', error));

// Update the infographic
function updateInfographic(phases) {
    console.log('Updating infographic with phases:', phases);
    // TO DO: implement infographic update logic
}
