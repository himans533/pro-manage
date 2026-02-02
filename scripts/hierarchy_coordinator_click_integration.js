/**
 * INTEGRATION CODE FOR COORDINATOR CLICK IN HIERARCHY
 * 
 * This code should be added to the existing hierarchy modal JavaScript
 * to enable clicking on coordinators to view their details.
 * 
 * Add this after the existing loadHierarchyTree() function (around line 500)
 */

// ============================================================================
// COORDINATOR CLICK HANDLER
// ============================================================================

/**
 * Handle clicking on a coordinator node in the hierarchy tree
 * Opens the coordinator details modal with their team, projects, and tasks
 */
function handleCoordinatorClick(coordinatorId, coordinatorName) {
    console.log("[v0] Opening coordinator details for:", coordinatorName, "ID:", coordinatorId);
    
    // Close the hierarchy modal
    closeHierarchyModal();
    
    // Open the coordinator details modal
    openCoordinatorDetails(coordinatorId);
}


/**
 * MODIFICATION TO EXISTING loadHierarchyTree() FUNCTION
 * 
 * When rendering coordinator nodes in the hierarchy tree, add onclick handler
 * 
 * BEFORE:
 * <div class="hierarchy-node">
 *     <span class="hierarchy-node-title">Coordinator Name</span>
 * </div>
 * 
 * AFTER:
 * <div class="hierarchy-node" onclick="handleCoordinatorClick(2, 'Coordinator Name')" style="cursor: pointer;">
 *     <span class="hierarchy-node-title">Coordinator Name</span>
 * </div>
 * 
 * Add these attributes to coordinator nodes:
 * - onclick="handleCoordinatorClick(coordinatorId, coordinatorName)"
 * - style="cursor: pointer;"
 * - Add hover effect styling
 */

// ============================================================================
// EXAMPLE: MODIFY EXISTING HIERARCHY RENDERING CODE
// ============================================================================

/**
 * This is an EXAMPLE of how to modify the hierarchy tree rendering
 * to make coordinators clickable.
 * 
 * Find the renderCoordinatorNode function in your hierarchy code
 * and add the onclick handler and styling.
 */

function renderCoordinatorNodeWithClick(coordinator) {
    // Original node HTML
    const nodeHtml = `
        <div class="hierarchy-node-wrapper">
            <div class="hierarchy-node coordinator-clickable" 
                 onclick="handleCoordinatorClick(${coordinator.id}, '${coordinator.name}')"
                 style="cursor: pointer; transition: all 0.2s ease;">
                
                <span class="hierarchy-toggle" onclick="event.stopPropagation()">
                    <i class="fas fa-chevron-right"></i>
                </span>
                
                <span class="hierarchy-icon">
                    <i class="fas fa-user-tie"></i>
                </span>
                
                <span class="hierarchy-node-title">
                    ${coordinator.name}
                </span>
                
                <span class="hierarchy-info">
                    <small>${coordinator.email}</small>
                </span>
            </div>
            
            <div class="hierarchy-children">
                <!-- Team members will be rendered here -->
            </div>
        </div>
    `;
    
    return nodeHtml;
}


// ============================================================================
// CSS ADDITIONS FOR COORDINATOR CLICKABLE NODES
// ============================================================================

const coordinatorClickableStyles = `
    /* Make coordinator nodes clickable and interactive */
    .coordinator-clickable {
        cursor: pointer;
        transition: all 0.2s ease;
        padding: 8px 12px;
        border-radius: 6px;
    }
    
    .coordinator-clickable:hover {
        background: rgba(99, 102, 241, 0.1);
        border-left: 3px solid #6366f1;
        padding-left: 9px;
    }
    
    .coordinator-clickable:active {
        transform: scale(0.98);
    }
    
    /* Tooltip on hover (optional) */
    .coordinator-clickable::after {
        content: "Click to view details";
        position: absolute;
        bottom: 100%;
        left: 0;
        background: #1f2937;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        white-space: nowrap;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s ease;
        z-index: 100;
    }
    
    .coordinator-clickable:hover::after {
        opacity: 1;
    }
`;

// ============================================================================
// STEP-BY-STEP INTEGRATION INSTRUCTIONS
// ============================================================================

/**
 * STEP 1: Add the handleCoordinatorClick function (above)
 * 
 * STEP 2: Modify the existing hierarchy tree rendering code
 *         Add onclick="handleCoordinatorClick(id, name)" to coordinator nodes
 * 
 * STEP 3: Add CSS for clickable coordinator nodes (above)
 * 
 * STEP 4: Add the coordinator details modal to the page
 *         (from coordinator_details_modal.html)
 * 
 * STEP 5: Add the coordinator details backend endpoint
 *         (from coordinator_details_backend.py)
 * 
 * STEP 6: Test by clicking on a coordinator in the hierarchy
 */
