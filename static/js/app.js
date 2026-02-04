/**
 * Sleep Tracker - Main JavaScript
 * ================================
 * Client-side functionality for the sleep tracking application
 */

// ----- Utility Functions -----

/**
 * Format a time string to 12-hour format
 * @param {string} time24 - Time in 24-hour format (HH:MM)
 * @returns {string} Time in 12-hour format (H:MM AM/PM)
 */
function formatTime12Hour(time24) {
    if (!time24) return '';
    
    const [hours, minutes] = time24.split(':').map(Number);
    const period = hours >= 12 ? 'PM' : 'AM';
    const hours12 = hours % 12 || 12;
    
    return `${hours12}:${minutes.toString().padStart(2, '0')} ${period}`;
}

/**
 * Calculate sleep duration between bed time and wake time
 * @param {string} bedTime - Bed time in HH:MM format
 * @param {string} wakeTime - Wake time in HH:MM format
 * @returns {object} Object with hours and minutes
 */
function calculateSleepDuration(bedTime, wakeTime) {
    if (!bedTime || !wakeTime) return null;
    
    let [bedH, bedM] = bedTime.split(':').map(Number);
    let [wakeH, wakeM] = wakeTime.split(':').map(Number);
    
    let bedMins = bedH * 60 + bedM;
    let wakeMins = wakeH * 60 + wakeM;
    
    // Assume next day if wake time is earlier than bed time
    if (wakeMins < bedMins) {
        wakeMins += 24 * 60;
    }
    
    const totalMins = wakeMins - bedMins;
    
    return {
        hours: Math.floor(totalMins / 60),
        minutes: totalMins % 60,
        totalMinutes: totalMins
    };
}

/**
 * Format duration object to string
 * @param {object} duration - Duration with hours and minutes
 * @returns {string} Formatted string like "7h 30m"
 */
function formatDuration(duration) {
    if (!duration) return '—';
    return `${duration.hours}h ${duration.minutes}m`;
}

/**
 * Get a color based on mood value (1-10)
 * @param {number} mood - Mood value from 1-10
 * @returns {string} CSS color value
 */
function getMoodColor(mood) {
    const colors = {
        1: '#ef4444',
        2: '#f97316',
        3: '#f59e0b',
        4: '#eab308',
        5: '#84cc16',
        6: '#22c55e',
        7: '#10b981',
        8: '#14b8a6',
        9: '#06b6d4',
        10: '#6366f1'
    };
    return colors[mood] || '#64748b';
}

/**
 * Get a descriptive label for mood value
 * @param {number} mood - Mood value from 1-10
 * @returns {string} Descriptive label
 */
function getMoodLabel(mood) {
    if (mood <= 2) return 'Very Low';
    if (mood <= 4) return 'Low';
    if (mood <= 6) return 'Okay';
    if (mood <= 8) return 'Good';
    return 'Excellent';
}

/**
 * Get a descriptive label for energy level
 * @param {number} energy - Energy value from 1-10
 * @returns {string} Descriptive label
 */
function getEnergyLabel(energy) {
    if (energy <= 2) return 'Drained';
    if (energy <= 4) return 'Tired';
    if (energy <= 6) return 'Moderate';
    if (energy <= 8) return 'Energized';
    return 'Very Energized';
}

// ----- DOM Ready -----

document.addEventListener('DOMContentLoaded', function() {
    // Add any global initialization here
    console.log('Sleep Tracker loaded successfully');
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
});

// ----- API Helper Functions -----

/**
 * Fetch data from an API endpoint
 * @param {string} url - API endpoint URL
 * @returns {Promise} JSON response data
 */
async function fetchData(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

/**
 * Post data to an API endpoint
 * @param {string} url - API endpoint URL
 * @param {object} data - Data to send
 * @returns {Promise} JSON response data
 */
async function postData(url, data) {
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Post error:', error);
        throw error;
    }
}

// ----- Export for use in other scripts -----

window.SleepTracker = {
    formatTime12Hour,
    calculateSleepDuration,
    formatDuration,
    getMoodColor,
    getMoodLabel,
    getEnergyLabel,
    fetchData,
    postData
};
