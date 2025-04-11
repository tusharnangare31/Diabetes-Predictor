// Main JavaScript file for Diabetes Predictor

document.addEventListener('DOMContentLoaded', function() {
    // Add input validation
    const formInputs = document.querySelectorAll('input[type="number"]');
    formInputs.forEach(input => {
        input.addEventListener('input', function() {
            validateInput(this);
        });
    });

    // Function to validate input
    function validateInput(input) {
        const value = parseFloat(input.value);
        const min = parseFloat(input.getAttribute('min'));
        
        if (value < min) {
            input.value = min;
        }
    }

    // Add tooltips to form fields
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute z-10 px-3 py-2 text-sm text-white bg-gray-900 rounded-md shadow-lg -mt-10';
            tooltip.textContent = this.getAttribute('data-tooltip');
            this.appendChild(tooltip);
        });
        
        trigger.addEventListener('mouseleave', function() {
            const tooltip = this.querySelector('div');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });

    // Add animation to the prediction button
    const predictButton = document.querySelector('button[type="submit"]');
    if (predictButton) {
        predictButton.addEventListener('mouseenter', function() {
            this.classList.add('pulse-animation');
        });
        
        predictButton.addEventListener('mouseleave', function() {
            this.classList.remove('pulse-animation');
        });
    }

    // Add smooth scrolling to anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add a BMI calculator
    const bmiCalculator = document.getElementById('bmi-calculator');
    if (bmiCalculator) {
        const heightInput = document.getElementById('height');
        const weightInput = document.getElementById('weight');
        const calculateButton = document.getElementById('calculate-bmi');
        const bmiResult = document.getElementById('bmi-result');
        const bmiInput = document.getElementById('bmi');
        
        calculateButton.addEventListener('click', function() {
            const height = parseFloat(heightInput.value) / 100; // Convert cm to m
            const weight = parseFloat(weightInput.value);
            
            if (height && weight) {
                const bmi = (weight / (height * height)).toFixed(1);
                bmiResult.textContent = bmi;
                bmiInput.value = bmi;
                
                // Update BMI category
                let category = '';
                if (bmi < 18.5) {
                    category = 'Underweight';
                } else if (bmi < 25) {
                    category = 'Normal weight';
                } else if (bmi < 30) {
                    category = 'Overweight';
                } else {
                    category = 'Obese';
                }
                
                document.getElementById('bmi-category').textContent = category;
            }
        });
    }
}); 