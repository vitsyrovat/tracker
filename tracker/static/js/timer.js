function formatSeconds(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    const seconds = totalSeconds % 60;
    // Returns format 0h 00m 00s for a more "live" feel
    return `${hours}h ${minutes.toString().padStart(2, '0')}m ${seconds.toString().padStart(2, '0')}s`;
}

function formatHoursMinutes(totalSeconds) {
    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
}

function secondsToClockInput(totalSeconds) {
    const safeSeconds = Math.max(0, Number(totalSeconds) || 0);
    const hours = Math.floor(safeSeconds / 3600);
    const minutes = Math.floor((safeSeconds % 3600) / 60);
    return `${hours}:${minutes.toString().padStart(2, '0')}`;
}

function clockInputToSeconds(value) {
    const trimmed = String(value || '').trim();
    if (!trimmed) {
        return null;
    }

    if (/^\d+$/.test(trimmed)) {
        return Number(trimmed) * 60;
    }

    const match = /^(\d+):(\d{1,2})$/.exec(trimmed);
    if (!match) {
        return null;
    }

    const hours = Number(match[1]);
    const minutes = Number(match[2]);
    if (minutes > 59) {
        return null;
    }
    return (hours * 3600) + (minutes * 60);
}

function setNameDisplay(element, nameValue) {
    const trimmed = String(nameValue || '').trim();
    if (!trimmed) {
        element.classList.add('is-empty');
        element.textContent = element.dataset.placeholder || 'Click to add name';
        return;
    }

    element.classList.remove('is-empty');
    element.textContent = trimmed;
}

function setDurationDisplay(element, totalSeconds, isRunning = false) {
    if (totalSeconds === '' || totalSeconds === null || totalSeconds === undefined) {
        if (element.dataset.placeholder) {
            element.classList.add('is-empty');
            element.textContent = element.dataset.placeholder;
            return;
        }
        totalSeconds = 0;
    }

    const numericSeconds = Number(totalSeconds) || 0;
    element.classList.remove('is-empty');
    element.textContent = isRunning
        ? formatSeconds(numericSeconds)
        : formatHoursMinutes(numericSeconds);
}

function showInlineEditError(element, message) {
    element.classList.add('has-edit-error');
    if (message) {
        element.title = message;
    }
}

function updateDayTotal(column) {
    if (!column) return;
    const totalEl = column.closest('.activities-with-total')?.querySelector('.total-time');
    if (!totalEl) return;

    let totalSeconds = 0;
    let anyRunning = false;
    column.querySelectorAll('.live-timer[data-field="duration_seconds"]').forEach(timer => {
        totalSeconds += parseInt(timer.dataset.seconds || '0', 10) || 0;
        if (timer.dataset.running === 'true') anyRunning = true;
    });

    totalEl.textContent = anyRunning ? formatSeconds(totalSeconds) : formatHoursMinutes(totalSeconds);
}

function updateTimers() {
    const timers = document.querySelectorAll('.live-timer[data-running="true"]');
    const affectedColumns = new Set();

    timers.forEach(timer => {
        // Increment the stored seconds
        let currentSeconds = parseInt(timer.getAttribute('data-seconds'));
        currentSeconds += 1;

        // Update both the attribute and the text on screen
        timer.setAttribute('data-seconds', currentSeconds);
        timer.setAttribute('data-value', currentSeconds);
        timer.textContent = formatSeconds(currentSeconds);
        const col = timer.closest('.activities-column');
        if (col) affectedColumns.add(col);
    });

    affectedColumns.forEach(updateDayTotal);
}

async function persistFieldValue(activityId, field, value) {
    const response = await fetch(`/activity/${activityId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ field, value })
    });

    const payload = await response.json().catch(() => ({}));
    if (!response.ok || !payload.ok) {
        throw new Error(payload.error || 'Could not save.');
    }
    return payload.activity;
}

async function createActivity(day, payload) {
    const response = await fetch('/activities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ day, ...payload })
    });

    const responsePayload = await response.json().catch(() => ({}));
    if (!response.ok || !responsePayload.ok) {
        throw new Error(responsePayload.error || 'Could not create activity.');
    }
    return responsePayload.activity;
}

function getActionButtonsMarkup(activityId, isRunning, options = {}) {
    const allowStart = options.allowStart !== false;
    const showDelete = options.showDelete !== false;

    const timerButton = isRunning
        ? `
            <form method="post" action="/activities/${activityId}/stop" class="inline-form">
                <button type="submit" class="btn-action btn-stop btn-icon" aria-label="Stop activity" title="Stop activity">
                    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                        <rect x="7" y="7" width="10" height="10" rx="1.5" fill="currentColor"></rect>
                    </svg>
                </button>
            </form>
        `
        : allowStart ? `
            <form method="post" action="/activities/${activityId}/start" class="inline-form">
                <button type="submit" class="btn-action btn-run btn-icon" aria-label="Start activity" title="Start activity">
                    <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                        <polygon points="8,6 18,12 8,18" fill="currentColor"></polygon>
                    </svg>
                </button>
            </form>
        ` : '';

    const deleteButton = showDelete ? `
        <button type="button" 
                data-delete-id="${activityId}" 
                class="btn-action btn-delete btn-icon" 
                aria-label="Delete activity" 
                title="Delete activity">
            <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
                <path d="M9 3h6l1 2h4v2H4V5h4l1-2zm1 6h2v8h-2V9zm4 0h2v8h-2V9zM7 9h2v8H7V9z" fill="currentColor"></path>
            </svg>
        </button>
    ` : '';

    return `
        ${timerButton}
        ${deleteButton}
    `;
}

function promoteCreateRow(row, activity) {
    row.removeAttribute('data-create-row');
    row.classList.remove('activity-row-create');

    const nameElement = row.querySelector('.inline-edit[data-field="name"]');
    const durationElement = row.querySelector('.inline-edit[data-field="duration_seconds"]');
    const buttonsContainer = row.querySelector('.activity-buttons');
    const totalDurationSeconds = activity.total_duration_seconds ?? activity.duration_seconds ?? 0;
    const allowStart = row.dataset.allowStart !== 'false';
    const showDelete = row.dataset.showDelete !== 'true';

    nameElement.dataset.activityId = String(activity.id);
    nameElement.dataset.value = activity.name || '';
    delete nameElement.dataset.placeholder;
    setNameDisplay(nameElement, activity.name || '');

    durationElement.classList.add('live-timer');
    durationElement.dataset.activityId = String(activity.id);
    durationElement.dataset.value = String(totalDurationSeconds);
    durationElement.dataset.seconds = String(totalDurationSeconds);
    durationElement.dataset.running = activity.is_running ? 'true' : 'false';
    delete durationElement.dataset.placeholder;
    setDurationDisplay(durationElement, totalDurationSeconds, activity.is_running);

    buttonsContainer.innerHTML = getActionButtonsMarkup(activity.id, activity.is_running, {
        allowStart,
        showDelete,
    });
}

function ensureCreateRow(container) {
    if (!container) {
        return;
    }

    if (container.querySelector('.activity-row[data-create-row="true"]')) {
        return;
    }

    const template = container.querySelector('.new-activity-row-template');
    if (!template) {
        return;
    }

    const row = template.content.firstElementChild.cloneNode(true);
    container.appendChild(row);
    initInlineEditing();
}

function ensureCreateRows() {
    document.querySelectorAll('.activities-column').forEach((container) => {
        ensureCreateRow(container);
    });
}

function applyInlineEdit(element) {
    if (element.dataset.editing === 'true') {
        return;
    }

    const activityId = element.dataset.activityId;
    const field = element.dataset.field;
    const originalRawValue = element.dataset.value || '';
    const createRow = element.closest('.activity-row[data-create-row="true"]');
    const isCreateRow = Boolean(createRow);

    element.dataset.editing = 'true';
    element.classList.add('is-editing');
    element.classList.remove('has-edit-error');
    element.removeAttribute('title');

    const input = document.createElement('input');
    input.className = 'inline-edit-input';

    if (field === 'duration_seconds') {
        input.type = 'text';
        input.placeholder = 'h:mm or minutes';
        input.value = isCreateRow && !originalRawValue
            ? ''
            : secondsToClockInput(Number(originalRawValue));
    } else {
        input.type = 'text';
        input.value = originalRawValue;
    }

    element.replaceChildren(input);
    input.focus();
    input.select();

    const finish = async (shouldSave) => {
        if (element.dataset.editing !== 'true') {
            return;
        }

        element.dataset.editing = 'false';
        element.classList.remove('is-editing');

        if (!shouldSave) {
            if (field === 'name') {
                setNameDisplay(element, originalRawValue);
            } else {
                setDurationDisplay(element, originalRawValue, element.dataset.running === 'true');
            }
            return;
        }

        let nextRawValue = input.value.trim();

        if (isCreateRow) {
            if (field === 'name') {
                if (!nextRawValue) {
                    setNameDisplay(element, '');
                    return;
                }
            }

            if (field === 'duration_seconds') {
                if (!nextRawValue) {
                    setDurationDisplay(element, '');
                    return;
                }

                const parsed = clockInputToSeconds(nextRawValue);
                if (parsed === null) {
                    setDurationDisplay(element, '');
                    showInlineEditError(element, 'Use h:mm or enter minutes only.');
                    return;
                }
                nextRawValue = parsed;
            }

            element.classList.add('is-saving');

            try {
                const created = await createActivity(createRow.dataset.day, field === 'name'
                    ? { name: nextRawValue }
                    : { duration_seconds: nextRawValue });
                const column = createRow.closest('.activities-column');
                promoteCreateRow(createRow, created);
                updateDayTotal(column);
                ensureCreateRow(column);
            } catch (error) {
                if (field === 'name') {
                    setNameDisplay(element, '');
                } else {
                    setDurationDisplay(element, '');
                }
                showInlineEditError(element, error.message);
            } finally {
                element.classList.remove('is-saving');
            }
            return;
        }

        if (field === 'name') {
            if (!nextRawValue) {
                setNameDisplay(element, originalRawValue);
                showInlineEditError(element, 'Name cannot be empty.');
                return;
            }
        }

        if (field === 'duration_seconds') {
            const parsed = clockInputToSeconds(nextRawValue);
            if (parsed === null) {
                setDurationDisplay(element, originalRawValue, element.dataset.running === 'true');
                showInlineEditError(element, 'Use h:mm or enter minutes only.');
                return;
            }
            nextRawValue = parsed;
        }

        element.classList.remove('has-edit-error');
        element.classList.add('is-saving');

        try {
            const updated = await persistFieldValue(activityId, field, nextRawValue);
            if (field === 'name') {
                element.dataset.value = updated.name || '';
                setNameDisplay(element, updated.name || '');
            } else {
                const totalDurationSeconds = updated.total_duration_seconds ?? updated.duration_seconds;
                element.dataset.value = String(totalDurationSeconds);
                element.setAttribute('data-seconds', String(totalDurationSeconds));
                element.dataset.running = updated.is_running ? 'true' : 'false';
                setDurationDisplay(element, totalDurationSeconds, updated.is_running);
                updateDayTotal(element.closest('.activities-column'));
            }
        } catch (error) {
            element.dataset.value = originalRawValue;
            if (field === 'duration_seconds') {
                element.setAttribute('data-seconds', originalRawValue);
            }
            if (field === 'name') {
                setNameDisplay(element, originalRawValue);
            } else {
                setDurationDisplay(element, originalRawValue, element.dataset.running === 'true');
            }
            showInlineEditError(element, error.message);
        } finally {
            element.classList.remove('is-saving');
        }
    };

    input.addEventListener('blur', () => finish(true), { once: true });
    input.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            event.preventDefault();
            input.blur();
        }
        if (event.key === 'Escape') {
            event.preventDefault();
            finish(false);
        }
    });
}

function initInlineEditing() {
    const editableElements = document.querySelectorAll('.inline-edit[data-field]');
    editableElements.forEach((element) => {
        if (element.dataset.inlineEditBound === 'true') {
            return;
        }
        element.dataset.inlineEditBound = 'true';
        element.addEventListener('click', () => applyInlineEdit(element));
    });
}

// Run the update function every 1000ms (1 second)
setInterval(updateTimers, 1000);
initInlineEditing();
ensureCreateRows();

// --- Run confirmation modal ---
(function () {
    const modal = document.getElementById('confirm-modal');
    const btnCancel = document.getElementById('modal-cancel');
    const btnOk = document.getElementById('modal-ok');

    let pendingHref = null;

    function openModal(href) {
        pendingHref = href;
        modal.hidden = false;
        btnOk.focus();
    }

    function closeModal() {
        modal.hidden = true;
        pendingHref = null;
    }

    function isAnyRunning() {
        return document.querySelector('.live-timer[data-running="true"]') !== null;
    }

    // Intercept all start-button clicks via event delegation
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.btn-run');
        if (!btn) return;
        if (!isAnyRunning()) return; // nothing running — let it through normally
        e.preventDefault();
        openModal(btn.href);
    });

    btnOk.addEventListener('click', function () {
        const href = pendingHref;
        closeModal();
        if (href) window.location.href = href;
    });

    btnCancel.addEventListener('click', closeModal);

    // Close on backdrop click
    modal.addEventListener('click', function (e) {
        if (e.target === modal) closeModal();
    });

    // Close on Escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !modal.hidden) closeModal();
    });
}());

// Handle delete button clicks with event delegation
document.addEventListener('click', async (e) => {
    const deleteBtn = e.target.closest('button[data-delete-id]');
    if (!deleteBtn) return;

    e.preventDefault();
    e.stopPropagation();

    const activityId = deleteBtn.dataset.deleteId;
    if (!confirm('Are you sure you want to delete this activity?')) {
        return;
    }

    try {
        const response = await fetch(`/activities/${activityId}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            window.location.href = '/';
        } else {
            alert('Failed to delete activity');
        }
    } catch (error) {
        console.error('Error deleting activity:', error);
        alert('Error deleting activity');
    }
});

