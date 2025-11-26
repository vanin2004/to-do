// API Base URL
const API_BASE_URL = '/api';

// Utility functions
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('ru-RU');
}

// API functions
async function createList(name) {
    const response = await fetch(`${API_BASE_URL}/lists/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: name
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to create list');
    }

    return await response.json();
}

async function getListBySlug(slug) {
    const response = await fetch(`${API_BASE_URL}/lists/${slug}`);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to fetch list');
    }

    return await response.json();
}

async function updateList(slug, name) {
    const response = await fetch(`${API_BASE_URL}/lists/${slug}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            name: name
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to update list');
    }

    return await response.json();
}

async function deleteList(slug) {
    const response = await fetch(`${API_BASE_URL}/lists/${slug}`, {
        method: 'DELETE'
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to delete list');
    }

    return await response.json();
}

async function createTask(slug, task, isDone = false) {
    const response = await fetch(`${API_BASE_URL}/lists/${slug}/tasks`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            task: task,
            is_done: isDone
        })
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to create task');
    }

    return await response.json();
}

async function updateTask(slug, taskId, data) {
    console.log('[API] Updating task:', taskId.slice(0, 8), 'Data:', data);
    const response = await fetch(`${API_BASE_URL}/lists/${slug}/tasks/${taskId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to update task');
    }

    const result = await response.json();
    console.log('[API] Task updated, server response:', {
        id: result.id.slice(0, 8),
        task: result.task,
        is_done: result.is_done,
        weight: result.weight
    });
    return result;
}

async function deleteTask(slug, taskId) {
    const response = await fetch(`${API_BASE_URL}/lists/${slug}/tasks/${taskId}`, {
        method: 'DELETE'
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'Failed to delete task');
    }

    return await response.json();
}

// UI State
let currentListSlug = null;
let autoRefreshInterval = null;
let isUserInteracting = false;
let showCompletedTasks = false;

// Auto-refresh every 3 seconds
function startAutoRefresh() {
    stopAutoRefresh();
    autoRefreshInterval = setInterval(async () => {
        if (currentListSlug && !isUserInteracting) {
            await loadList(currentListSlug, true);
        }
    }, 3000);
    console.log('[AutoRefresh] Auto-refresh started (3s interval)');
}

function stopAutoRefresh() {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }
}

function pauseAutoRefresh() {
    isUserInteracting = true;
}

function resumeAutoRefresh() {
    isUserInteracting = false;
}

// UI functions
function renderTask(task) {
    const taskDiv = document.createElement('div');
    taskDiv.className = `task-item ${task.is_done ? 'completed' : ''}`;
    taskDiv.dataset.taskId = task.id;
    taskDiv.dataset.weight = task.weight;
    taskDiv.dataset.isDone = task.is_done;
    taskDiv.draggable = true;
    
    // Hide completed tasks if showCompletedTasks is false
    if (task.is_done && !showCompletedTasks) {
        taskDiv.style.display = 'none';
    }

    taskDiv.innerHTML = `
        <div class="task-header">
            <div class="drag-handle">⋮⋮</div>
            <div class="task-checkbox ${task.is_done ? 'checked' : ''}" role="checkbox" aria-checked="${task.is_done}"></div>
            <div class="task-content">
                <div class="task-title">${escapeHtml(task.task)}</div>
            </div>
            <div class="task-actions">
                <button class="btn btn-small btn-secondary edit-task-btn">✏️</button>
                <button class="btn btn-small btn-danger delete-task-btn">🗑️</button>
            </div>
        </div>
        <div class="edit-task-form hidden">
            <div class="form-group">
                <label>Задача:</label>
                <input type="text" class="edit-task-text" value="${escapeHtml(task.task)}">
            </div>
            <div class="form-buttons">
                <button class="btn btn-primary save-task-btn">Сохранить</button>
                <button class="btn btn-secondary cancel-edit-task-btn">Отмена</button>
            </div>
        </div>
    `;

    // Drag and drop handlers
    taskDiv.addEventListener('dragstart', handleDragStart);
    taskDiv.addEventListener('dragend', handleDragEnd);
    taskDiv.addEventListener('dragover', handleDragOver);
    taskDiv.addEventListener('drop', handleDrop);
    taskDiv.addEventListener('dragenter', handleDragEnter);
    taskDiv.addEventListener('dragleave', handleDragLeave);

    // Toggle complete - click on checkbox
    taskDiv.querySelector('.task-checkbox').addEventListener('click', async function() {
        pauseAutoRefresh();
        try {
            // Read current state from DOM
            const taskItem = this.closest('.task-item');
            const currentlyDone = taskItem.classList.contains('completed');
            console.log('[Toggle] Task:', task.id, 'Current state:', currentlyDone ? 'completed' : 'active', 'Weight:', task.weight);
            
            // Immediate visual feedback
            if (currentlyDone) {
                this.classList.remove('checked');
                taskItem.classList.remove('completed');
            } else {
                this.classList.add('checked');
                taskItem.classList.add('completed');
            }
            
            await updateTask(currentListSlug, task.id, {
                is_done: !currentlyDone
            });
            
            console.log('[Toggle] Task updated, new state:', !currentlyDone ? 'completed' : 'active');
            console.log('[Toggle] Reloading list...');
            
            await loadList(currentListSlug);
            showNotification('Статус задачи обновлен');
        } catch (error) {
            console.error('[Toggle] Error:', error);
            showNotification(error.message, 'error');
        } finally {
            resumeAutoRefresh();
        }
    });

    // Edit task
    const editBtn = taskDiv.querySelector('.edit-task-btn');
    const editForm = taskDiv.querySelector('.edit-task-form');
    const cancelEditBtn = taskDiv.querySelector('.cancel-edit-task-btn');

    editBtn.addEventListener('click', () => {
        const isOpening = editForm.classList.contains('hidden');
        editForm.classList.toggle('hidden');
        if (isOpening) {
            pauseAutoRefresh();
        } else {
            resumeAutoRefresh();
        }
    });

    cancelEditBtn.addEventListener('click', () => {
        editForm.classList.add('hidden');
        resumeAutoRefresh();
    });

    // Save task
    taskDiv.querySelector('.save-task-btn').addEventListener('click', async () => {
        const taskText = taskDiv.querySelector('.edit-task-text').value;

        try {
            await updateTask(currentListSlug, task.id, {
                task: taskText
            });
            editForm.classList.add('hidden');
            await loadList(currentListSlug);
            showNotification('Задача обновлена');
        } catch (error) {
            showNotification(error.message, 'error');
        } finally {
            resumeAutoRefresh();
        }
    });

    // Delete task
    taskDiv.querySelector('.delete-task-btn').addEventListener('click', async () => {
        if (confirm('Вы уверены, что хотите удалить эту задачу?')) {
            pauseAutoRefresh();
            try {
                await deleteTask(currentListSlug, task.id);
                await loadList(currentListSlug);
                showNotification('Задача удалена');
            } catch (error) {
                showNotification(error.message, 'error');
            } finally {
                resumeAutoRefresh();
            }
        }
    });

    return taskDiv;
}

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

async function loadList(slug, silent = false) {
    try {
        console.log('[LoadList] Loading list:', slug, 'Silent:', silent);
        const list = await getListBySlug(slug);
        currentListSlug = slug;

        // Update UI
        document.getElementById('listTitle').textContent = list.name;
        document.getElementById('listSlugDisplay').textContent = list.slug;
        
        // Update edit form
        document.getElementById('editListName').value = list.name;

        console.log('[LoadList] Raw tasks from server:', list.tasks?.map(t => ({ id: t.id.slice(0, 8), task: t.task, is_done: t.is_done, weight: t.weight })));

        // Sort tasks: active tasks by weight first, then completed tasks by weight
        const sortedTasks = list.tasks ? [...list.tasks].sort((a, b) => {
            // Completed tasks go to the bottom
            if (a.is_done !== b.is_done) {
                return a.is_done ? 1 : -1;
            }
            // Within same status, sort by weight
            return a.weight - b.weight;
        }) : [];
        
        console.log('[LoadList] Sorted tasks:', sortedTasks.map(t => ({ id: t.id.slice(0, 8), task: t.task, is_done: t.is_done, weight: t.weight })));

        // Render tasks without flickering
        const tasksList = document.getElementById('tasksList');
        const existingTaskIds = new Set(
            Array.from(tasksList.querySelectorAll('.task-item')).map(el => el.dataset.taskId)
        );
        const newTaskIds = new Set(sortedTasks.map(task => task.id));

        // Remove tasks that no longer exist
        Array.from(tasksList.querySelectorAll('.task-item')).forEach(taskEl => {
            if (!newTaskIds.has(taskEl.dataset.taskId)) {
                taskEl.remove();
            }
        });

        if (sortedTasks.length > 0) {
            // Separate active and completed tasks
            const activeTasks = sortedTasks.filter(t => !t.is_done);
            const completedTasks = sortedTasks.filter(t => t.is_done);
            
            // Remove existing completed section header if exists
            const existingHeader = tasksList.querySelector('.completed-section-header');
            if (existingHeader) {
                existingHeader.remove();
            }
            
            let headerInserted = false;
            
            // Update or add tasks in correct order
            sortedTasks.forEach((task, index) => {
                let existingTaskEl = tasksList.querySelector(`[data-task-id="${task.id}"]`);
                
                if (existingTaskEl) {
                    // Update existing task if needed
                    const currentWeight = existingTaskEl.dataset.weight;
                    if (currentWeight !== task.weight.toString()) {
                        existingTaskEl.dataset.weight = task.weight;
                    }
                    
                    const oldIsDone = existingTaskEl.dataset.isDone;
                    existingTaskEl.dataset.isDone = task.is_done;
                    
                    // Check if task needs to be moved (comparing only task items, not header)
                    const taskItems = Array.from(tasksList.querySelectorAll('.task-item'));
                    const currentIndex = taskItems.indexOf(existingTaskEl);
                    if (currentIndex !== index) {
                        console.log('[LoadList] Moving task:', task.id.slice(0, 8), 'from position', currentIndex, 'to', index, '| is_done:', task.is_done, 'weight:', task.weight);
                        
                        // Find the target position (accounting for header if present)
                        if (index < taskItems.length) {
                            tasksList.insertBefore(existingTaskEl, taskItems[index]);
                        } else {
                            tasksList.appendChild(existingTaskEl);
                        }
                    } else if (oldIsDone !== task.is_done.toString()) {
                        console.log('[LoadList] Task status changed but position stayed:', task.id.slice(0, 8), '| is_done:', task.is_done, 'position:', index, 'weight:', task.weight);
                    }
                    
                    // Insert completed section header before first completed task
                    if (!headerInserted && task.is_done && completedTasks.length > 0) {
                        const headerDiv = document.createElement('div');
                        headerDiv.className = 'completed-section-header';
                        headerDiv.innerHTML = `Завершенные <span class="count">${completedTasks.length}</span>`;
                        tasksList.insertBefore(headerDiv, existingTaskEl);
                        headerInserted = true;
                    }
                    
                    // Update task content (text, completion status)
                    const titleEl = existingTaskEl.querySelector('.task-title');
                    if (titleEl && titleEl.textContent !== task.task) {
                        titleEl.textContent = task.task;
                    }
                    
                    // Update completion status
                    const checkboxEl = existingTaskEl.querySelector('.task-checkbox');
                    if (task.is_done && !existingTaskEl.classList.contains('completed')) {
                        existingTaskEl.classList.add('completed');
                        if (checkboxEl) checkboxEl.classList.add('checked');
                    } else if (!task.is_done && existingTaskEl.classList.contains('completed')) {
                        existingTaskEl.classList.remove('completed');
                        if (checkboxEl) checkboxEl.classList.remove('checked');
                    }
                    
                    // Update visibility based on completion status
                    if (task.is_done && !showCompletedTasks) {
                        existingTaskEl.style.display = 'none';
                    } else {
                        existingTaskEl.style.display = '';
                    }
                } else {
                    // New task, add it
                    console.log('[LoadList] Adding new task:', task.id.slice(0, 8), 'at position', index, '| is_done:', task.is_done, 'weight:', task.weight);
                    const newTaskEl = renderTask(task);
                    
                    // Insert completed section header before first completed task
                    if (!headerInserted && task.is_done && completedTasks.length > 0) {
                        const headerDiv = document.createElement('div');
                        headerDiv.className = 'completed-section-header';
                        headerDiv.innerHTML = `Завершенные <span class="count">${completedTasks.length}</span>`;
                        tasksList.appendChild(headerDiv);
                        headerInserted = true;
                    }
                    
                    const taskItems = Array.from(tasksList.querySelectorAll('.task-item'));
                    if (index < taskItems.length) {
                        tasksList.insertBefore(newTaskEl, taskItems[index]);
                    } else {
                        tasksList.appendChild(newTaskEl);
                    }
                }
            });
        } else {
            tasksList.innerHTML = '<p style="text-align: center; color: var(--text-secondary);">Задач пока нет</p>';
        }

        // Update completed tasks counter
        const completedCount = sortedTasks.filter(t => t.is_done).length;
        const toggleCompletedBtn = document.getElementById('toggleCompletedBtn');
        const completedCounter = document.getElementById('completedCounter');
        const completedHeader = tasksList.querySelector('.completed-section-header');
        
        if (completedCount > 0) {
            completedCounter.textContent = completedCount;
            toggleCompletedBtn.style.display = 'inline-flex';
            toggleCompletedBtn.querySelector('.toggle-text').textContent = showCompletedTasks ? 'Скрыть' : 'Показать';
            
            // Show/hide completed section header based on visibility toggle
            if (completedHeader) {
                completedHeader.style.display = showCompletedTasks ? 'flex' : 'none';
            }
        } else {
            toggleCompletedBtn.style.display = 'none';
            if (completedHeader) {
                completedHeader.style.display = 'none';
            }
        }

        // Show list section
        document.getElementById('todoListSection').classList.remove('hidden');
        document.getElementById('editListForm').classList.add('hidden');

        // Start auto-refresh
        startAutoRefresh();

        // Update URL without reload
        if (!silent) {
            history.pushState(null, '', `/${slug}`);
        }

    } catch (error) {
        if (!silent) {
            showNotification(error.message, 'error');
        }
    }
}

// Event listeners
document.getElementById('createListForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('listName').value;

    try {
        const list = await createList(name);
        showNotification('Список успешно создан');
        
        // Clear form
        document.getElementById('listName').value = '';
        document.getElementById('listSlug').value = '';

        // Load the created list
        await loadList(list.slug);
    } catch (error) {
        showNotification(error.message, 'error');
    }
});

document.getElementById('searchBtn').addEventListener('click', async () => {
    const slug = document.getElementById('searchSlug').value.trim();
    if (slug) {
        await loadList(slug);
    }
});

document.getElementById('searchSlug').addEventListener('keypress', async (e) => {
    if (e.key === 'Enter') {
        const slug = document.getElementById('searchSlug').value.trim();
        if (slug) {
            await loadList(slug);
        }
    }
});

document.getElementById('manualRefreshBtn').addEventListener('click', async () => {
    if (currentListSlug) {
        console.log('[Manual Refresh] Refreshing list...');
        await loadList(currentListSlug);
        showNotification('Список обновлён');
    }
});

document.getElementById('editListBtn').addEventListener('click', () => {
    const editForm = document.getElementById('editListForm');
    const isOpening = editForm.classList.contains('hidden');
    editForm.classList.toggle('hidden');
    if (isOpening) {
        pauseAutoRefresh();
    } else {
        resumeAutoRefresh();
    }
});

document.getElementById('cancelEditListBtn').addEventListener('click', () => {
    document.getElementById('editListForm').classList.add('hidden');
    resumeAutoRefresh();
});

document.getElementById('saveListBtn').addEventListener('click', async () => {
    const name = document.getElementById('editListName').value;

    try {
        await updateList(currentListSlug, name);
        await loadList(currentListSlug);
        showNotification('Список обновлен');
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        resumeAutoRefresh();
    }
});

document.getElementById('deleteListBtn').addEventListener('click', async () => {
    if (confirm('Вы уверены, что хотите удалить этот список и все его задачи?')) {
        pauseAutoRefresh();
        try {
            await deleteList(currentListSlug);
            showNotification('Список удален');
            
            // Hide list section
            document.getElementById('todoListSection').classList.add('hidden');
            stopAutoRefresh();
            currentListSlug = null;
        } catch (error) {
            showNotification(error.message, 'error');
            resumeAutoRefresh();
        }
    }
});

document.getElementById('addTaskForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const task = document.getElementById('taskTitle').value;

    pauseAutoRefresh();
    try {
        await createTask(currentListSlug, task);
        await loadList(currentListSlug);
        showNotification('Задача добавлена');
        
        // Clear form
        document.getElementById('taskTitle').value = '';
    } catch (error) {
        showNotification(error.message, 'error');
    } finally {
        resumeAutoRefresh();
    }
});

// Pause auto-refresh when user is typing
document.getElementById('taskTitle').addEventListener('focus', () => {
    pauseAutoRefresh();
});

document.getElementById('taskTitle').addEventListener('blur', () => {
    // Only resume if form is not being submitted
    setTimeout(() => {
        if (document.activeElement.id !== 'taskTitle') {
            resumeAutoRefresh();
        }
    }, 100);
});

// Auto-generate slug from name (removed - API generates slug automatically)

// Drag and Drop functionality
let draggedElement = null;

function handleDragStart(e) {
    draggedElement = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
    pauseAutoRefresh();
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    
    // Remove all drag-over classes
    document.querySelectorAll('.task-item').forEach(item => {
        item.classList.remove('drag-over');
    });
    
    // Resume auto-refresh after a short delay to allow API call to complete
    setTimeout(() => {
        resumeAutoRefresh();
    }, 500);
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnter(e) {
    if (this !== draggedElement) {
        this.classList.add('drag-over');
    }
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

async function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    e.preventDefault();

    if (draggedElement !== this) {
        const draggedId = draggedElement.dataset.taskId;
        const targetId = this.dataset.taskId;
        const draggedWeight = parseFloat(draggedElement.dataset.weight);
        const targetWeight = parseFloat(this.dataset.weight);

        // Determine position
        const tasksList = document.getElementById('tasksList');
        const allTasks = Array.from(tasksList.querySelectorAll('.task-item'));
        const draggedIndex = allTasks.indexOf(draggedElement);
        const targetIndex = allTasks.indexOf(this);
        
        const movePosition = draggedIndex < targetIndex ? 'after' : 'before';

        // Calculate temporary weight for instant UI update
        let tempWeight;
        if (movePosition === 'before') {
            const prevTask = this.previousElementSibling;
            const prevWeight = prevTask && prevTask !== draggedElement ? parseFloat(prevTask.dataset.weight) : targetWeight - 1;
            tempWeight = (prevWeight + targetWeight) / 2;
        } else {
            const nextTask = this.nextElementSibling;
            const nextWeight = nextTask && nextTask !== draggedElement ? parseFloat(nextTask.dataset.weight) : targetWeight + 1;
            tempWeight = (targetWeight + nextWeight) / 2;
        }

        // Update weight instantly for UI
        draggedElement.dataset.weight = tempWeight;

        // Move element in DOM instantly
        if (movePosition === 'before') {
            tasksList.insertBefore(draggedElement, this);
        } else {
            tasksList.insertBefore(draggedElement, this.nextSibling);
        }

        // Send update to API
        try {
            const updatedTask = await updateTask(currentListSlug, draggedId, {
                target_task: targetId,
                move_position: movePosition
            });
            
            // Update with real weight from server
            draggedElement.dataset.weight = updatedTask.weight;
            
            // Reload to get correct order from server
            await loadList(currentListSlug, true);
        } catch (error) {
            showNotification(error.message, 'error');
            // Reload on error to restore correct state
            await loadList(currentListSlug);
        }
    }

    this.classList.remove('drag-over');
    return false;
}

// Toggle completed tasks visibility
document.getElementById('toggleCompletedBtn').addEventListener('click', () => {
    showCompletedTasks = !showCompletedTasks;
    
    // Update visibility of completed tasks
    const tasksList = document.getElementById('tasksList');
    tasksList.querySelectorAll('.task-item').forEach(taskEl => {
        const isDone = taskEl.dataset.isDone === 'true';
        if (isDone) {
            taskEl.style.display = showCompletedTasks ? '' : 'none';
        }
    });
    
    // Update button text
    const toggleBtn = document.getElementById('toggleCompletedBtn');
    toggleBtn.querySelector('.toggle-text').textContent = showCompletedTasks ? 'Скрыть' : 'Показать';
});

// Check URL on load
window.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;
    if (path && path !== '/') {
        const slug = path.substring(1); // Remove leading slash
        if (slug) {
            loadList(slug);
        }
    }
});

// Handle browser back/forward
window.addEventListener('popstate', () => {
    const path = window.location.pathname;
    if (path && path !== '/') {
        const slug = path.substring(1);
        if (slug) {
            loadList(slug);
        }
    } else {
        stopAutoRefresh();
        document.getElementById('todoListSection').classList.add('hidden');
        currentListSlug = null;
    }
});
